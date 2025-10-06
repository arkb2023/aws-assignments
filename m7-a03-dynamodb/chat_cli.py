#!/usr/bin/env python3
"""
ChatService CLI for DynamoDB:
- Create table
- Send messages from config
- Create backup
- Delete table
- Delete backup
"""

import argparse, yaml, boto3, uuid, time, sys, os
from datetime import datetime, timezone, timedelta

from botocore.exceptions import ClientError

# Load config.yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Constants for table schema
TABLE_NAME = "Messages"
PARTITION_KEY = "ConversationId"
SORT_KEY = "SentAt"

USERS = config["users"]
MESSAGES = config["messages"]
BACKUP_NAME = f"{TABLE_NAME}-backup-{int(time.time())}"
REGION = config["region"]
BACKUP_ARN_FILE="last_backup_arn.txt"

# Initialize clients
dynamodb = boto3.client("dynamodb", region_name=REGION)
ddb_resource = boto3.resource("dynamodb", region_name=REGION)

def create_table():
    """Create DynamoDB table with ConversationId + SentAt as primary key"""

    print(f"Creating table '{TABLE_NAME}'...")
    print(f"  Partition key: {PARTITION_KEY} (type: String)")
    print(f"  Sort key: {SORT_KEY} (type: String)")

    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {"AttributeName": PARTITION_KEY, "AttributeType": "S"},
                {"AttributeName": SORT_KEY, "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": PARTITION_KEY, "KeyType": "HASH"},
                {"AttributeName": SORT_KEY, "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        dynamodb.get_waiter("table_exists").wait(TableName=TABLE_NAME)
        print("Table created.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("Table already exists.")
        else:
            raise

def send_messages():
    """Insert messages from config.yaml into the table"""
    table = ddb_resource.Table(TABLE_NAME)
    now = datetime.now(timezone.utc)

    print("Sending messages...")
    for i, msg in enumerate(MESSAGES):
        sender = USERS[msg["from"]]
        recipient = USERS[msg["to"]]
        sent_at = (now + timedelta(milliseconds=i)).isoformat(timespec="milliseconds")


        # Format message body by replacing {from} and {to} placeholders
        body_template = msg["body"]
        body_vars = {"from": sender, "to": recipient}
        body = body_template.format(**body_vars)

        item = {
            # Ensure consistent partition key for any two-user conversation.
            # (e.g., alice → bob and bob → alice) always use the same ConversationId ("alice#bob").
            PARTITION_KEY: f"{min(sender, recipient)}#{max(sender, recipient)}",
            SORT_KEY: sent_at,
            "MessageId": str(uuid.uuid4()),
            "FromUser": sender,
            "ToUser": recipient,
            "Body": body,
            "Status": "SENT",
        }
        table.put_item(Item=item)
        print(f"   {sender} → {recipient}: {body}")
    print("All messages sent.")

def backup_table():
    """Create on-demand backup and return its ARN"""
    print("Creating backup...")
    try:
        resp = dynamodb.create_backup(TableName=TABLE_NAME, BackupName=BACKUP_NAME)
        #backup_arn = resp["Backup"]["BackupDetails"]["BackupArn"]
        backup_arn = resp["BackupDetails"]["BackupArn"]
        print("Waiting for backup to become AVAILABLE...")
        while True:
            status = dynamodb.describe_backup(BackupArn=backup_arn)["BackupDescription"]["BackupDetails"]["BackupStatus"]
            print("  Backup status:", status)
            if status == "AVAILABLE":
                break
            time.sleep(1)
        print("Backup created:", backup_arn)
        return backup_arn
    except ClientError as e:
        print("Backup failed:", e.response["Error"]["Message"])
        sys.exit(1)

def delete_backup(backup_arn):
    """Delete backup using its ARN"""
    print("Deleting backup...")
    try:
        dynamodb.delete_backup(BackupArn=backup_arn)
        print("Backup deleted:", backup_arn)
    except ClientError as e:
        print("Backup deletion failed:", e.response["Error"]["Message"])
        sys.exit(1)

def delete_table():
    """Delete the DynamoDB table"""
    print("Deleting table...")
    try:
        dynamodb.delete_table(TableName=TABLE_NAME)
        dynamodb.get_waiter("table_not_exists").wait(TableName=TABLE_NAME)
        print("Table deleted.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("Table not found.")
        else:
            raise

def main():
    parser = argparse.ArgumentParser(description="ChatService DynamoDB CLI")
    parser.add_argument("command", choices=[
        "create-table", "send-messages", "backup-table", "delete-table", "delete-backup"
    ])
    args = parser.parse_args()

    if args.command == "create-table":
        create_table()
    elif args.command == "send-messages":
        send_messages()
    elif args.command == "backup-table":
        backup_arn = backup_table()
        # Store ARN in a file for later use
        with open(BACKUP_ARN_FILE, "w") as f:
            f.write(backup_arn)
    elif args.command == "delete-table":
        delete_table()
    elif args.command == "delete-backup":
        try:
            with open(BACKUP_ARN_FILE) as f:
                backup_arn = f.read().strip()
            delete_backup(backup_arn)
            # cleanup ARN file
            os.remove(BACKUP_ARN_FILE) 

        except FileNotFoundError:
            print("No backup ARN found. Run backup-table first.")

if __name__ == "__main__":
    main()