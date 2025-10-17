# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
import time
import subprocess
import json
import boto3
import logging
import argparse
import botocore.exceptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


USERS_MOCK_TABLE_NAME = 'Users'
UUID_MOCK_VALUE_JOHN = 'f8216640-91a2-11eb-8ab9-57aa454facef'
UUID_MOCK_VALUE_JANE = '31a9f940-917b-11eb-9054-67837e2c40b0'
CONTAINER_PORT = os.getenv('DYNAMODB_CONTAINER_PORT', '8000')
DYNAMODB_ENDPOINT_URL = os.getenv('DYNAMODB_ENDPOINT_URL', f'http://localhost:{CONTAINER_PORT}')
CONTAINER_NAME = os.getenv('DYNAMODB_CONTAINER_NAME', 'pytest-dynamodb-local')


import time
import boto3
import botocore.exceptions
import logging

logger = logging.getLogger(__name__)

def wait_for_dynamodb_ready(endpoint_url, timeout_seconds=30, poll_interval=1):
    client = boto3.client('dynamodb', endpoint_url=endpoint_url, region_name='us-west-2')
    start_time = time.time()

    while True:
        try:
            client.list_tables(Limit=1)
            logger.info("DynamoDB Local is ready")
            break
        except botocore.exceptions.EndpointConnectionError:
            # DynamoDB Local not ready yet
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                logger.error(f"DynamoDB Local did not become ready within {timeout_seconds} seconds")
                raise TimeoutError(f"DynamoDB Local did not respond within {timeout_seconds} seconds")
            logger.debug(f"Waiting for DynamoDB Local... {elapsed:.1f}s elapsed")
            time.sleep(poll_interval)


def set_up_dynamodb_local_container():
    logger.info("Running DynamoDB local Docker container")
    subprocess.run([
        "docker", "run", "-d", "--rm",
        "-p", f"{CONTAINER_PORT}:8000",
        "--name", CONTAINER_NAME,
        "amazon/dynamodb-local"
    ], check=True)
    
    wait_for_dynamodb_ready(DYNAMODB_ENDPOINT_URL)



def clean_up_dynamodb_local_container():
    logger.info(f"Stopping Docker container {CONTAINER_NAME}")
    subprocess.run(["docker", "stop", CONTAINER_NAME], check=True)


def set_up_dynamodb(conn):
    try:
        logger.info(f"Creating DynamoDB table: {USERS_MOCK_TABLE_NAME}")
        conn.create_table(
            TableName=USERS_MOCK_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'userid', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'userid', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        logger.info("Waiting for table to become active")
        waiter = conn.get_waiter('table_exists')
        waiter.wait(TableName=USERS_MOCK_TABLE_NAME)
        logger.info("Table created and active")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logger.warning(f"Table {USERS_MOCK_TABLE_NAME} already exists, skipping creation.")
        else:
            logger.error(f"Error creating DynamoDB table: {e}")
            raise


def clean_up_dynamodb(conn):
    try:
        logger.info(f"Deleting DynamoDB table: {USERS_MOCK_TABLE_NAME}")
        conn.delete_table(TableName=USERS_MOCK_TABLE_NAME)
        waiter = conn.get_waiter('table_not_exists')
        waiter.wait(TableName=USERS_MOCK_TABLE_NAME)
        logger.info("Table deleted successfully")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.warning(f"Table {USERS_MOCK_TABLE_NAME} already deleted.")
        else:
            logger.error(f"Error deleting DynamoDB table: {e}")
            raise


def put_data_dynamodb(conn):
    logger.info(f"Inserting data item for user {UUID_MOCK_VALUE_JOHN}")
    conn.put_item(
        TableName=USERS_MOCK_TABLE_NAME,
        Item={
            'userid': {'S': UUID_MOCK_VALUE_JOHN},
            'name': {'S': 'John Doe'},
            'timestamp': {'S': '2021-03-30T21:57:49.860Z'}
        }
    )
    logger.info(f"Inserting data item for user {UUID_MOCK_VALUE_JANE}")
    conn.put_item(
        TableName=USERS_MOCK_TABLE_NAME,
        Item={
            'userid': {'S': UUID_MOCK_VALUE_JANE},
            'name': {'S': 'Jane Doe'},
            'timestamp': {'S': '2021-03-30T17:13:06.516Z'}
        }
    )

def list_users(dynamodb):
    table = dynamodb.Table(USERS_MOCK_TABLE_NAME)
    response = table.scan()
    items = response['Items']
    logger.info(f"User list:\n{items}")


def list_dynamodb_tables(client):
    response = client.list_tables()
    table_names = response.get('TableNames', [])
    
    if table_names:
        logger.info("Tables in DynamoDB:")
        for name in table_names:
            logger.info(f" - {name}")
    else:
        logger.info("No tables found in DynamoDB.")

def setup(dynamodb_client):
    logger.info("Starting DynamoDB Local container")
    set_up_dynamodb_local_container()

    try:
        logger.info("Setting up DynamoDB table")
        set_up_dynamodb(dynamodb_client)
        logger.info("Populating DynamoDB table with test data")
        put_data_dynamodb(dynamodb_client)

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise    


def cleanup(dynamodb_client):
    
    logger.info("Cleaning up DynamoDB table")
    clean_up_dynamodb(dynamodb_client)
    
    logger.info("Stopping DynamoDB Local container")
    clean_up_dynamodb_local_container()

def main():
    parser = argparse.ArgumentParser(description='Manage local DynamoDB lifecycle')
    parser.add_argument('--region', default='us-west-2')
    parser.add_argument('--action', required=True, choices=['create', 'list-tables', 'list-users', 'terminate'])
    args = parser.parse_args()
    
    dynamodb_client = boto3.client('dynamodb', endpoint_url=DYNAMODB_ENDPOINT_URL, region_name=args.region)
    dynamodb_resource = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT_URL, region_name=args.region)
    logger.info(f"Connecting to DynamoDB endpoint: {DYNAMODB_ENDPOINT_URL}")

    try:
        if args.action == 'create':
            setup(dynamodb_client)
        elif args.action == 'list-tables':
            list_dynamodb_tables(dynamodb_client)
        elif args.action == 'list-users':
            list_users(dynamodb_resource)
        elif args.action == 'terminate':
            cleanup(dynamodb_client)
        else:
            logger.error("Invalid action specified")
            exit(1)
    except Exception as e:
        logger.error(f"Exception occurred during {args.action}: {e}")
        if args.action == 'create':
            cleanup(dynamodb_client)
        exit(1)
    
if __name__ == '__main__':
    main()


# 
# python3 dynamodb.py --action create
# python3 dynamodb.py --action list-tables
# python3 dynamodb.py --action list-users
# python3 dynamodb.py --action terminate