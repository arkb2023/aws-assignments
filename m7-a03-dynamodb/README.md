![Configured via AWS CLI](https://img.shields.io/badge/Configured-AWS%20CLI-blue?logo=amazon-aws)
![Scripted in Python](https://img.shields.io/badge/Scripted-Python-green?logo=python)
![Verified via AWS Console](https://img.shields.io/badge/Verified-AWS%20Console-yellow?logo=amazon-aws)
![Status: Completed](https://img.shields.io/badge/Status-Completed-brightgreen)

## Module 7: DynamoDB

### Problem Statement
You work for XYZ Corporation. Their application requires a database service that can store data which can be retrieved if required. Implement a suitable service for the same.  
While migrating, you are asked to perform the following tasks:  
1. Create a DynamoDB table with partition key as ID.  
2. Add 5 items to the DynamoDB table.  
3. Take backup and delete the table.  

### Solution Overview

This solution automates the provisioning and lifecycle management of a DynamoDB table using a Python CLI powered by the `boto3` SDK.

To simulate a real-world use case, we assume a **chat service application** where two users exchange messages. To support this, a DynamoDB table named `Messages` is provisioned to store chat interactions.

The table schema is designed as follows:

- `ConversationId` — **Partition key**: uniquely identifies the conversation between two users (e.g., `tom#jerry`)
- `SentAt` — **Sort key**: stores the timestamp of each message to maintain chronological order
- `Body` — stores the actual message content
- `FromUser` — name of the sender
- `ToUser` — name of the recipient
- `MessageId` — unique identifier for each message (UUID)

The Python CLI performs the following operations:
1. Provisions a DynamoDB table (`Messages`), structured with a partition key (`ConversationId`), and sort key (`SentAt`).
2. Populates the table with chat messages, dynamically formatted and loaded from [`config.yaml`](./config.yaml) file, simulating a conversation between two users.
3. Creates an on-demand backup of the table
4. Deletes the table
5. Deletes the backup

This workflow demonstrates end-to-end automation of a DynamoDB-backed messaging service, including provisioning, data insertion, backup, and cleanup — all verifiable via the AWS Console.


### Project Repository

This repository contains all components required to provision and manage a DynamoDB table:

- Python script to automate table operations
- YAML configuration file for user and message data
- Screenshot documentation for validation and review

```bash
$ tree
.
├── README.md
├── chat_cli.py
├── config.yaml
└── images
    ├── 01-table-created.png
    ├── 02-table-items.png
    └── 03-table-backup.png
```

| Filename | Description |
|----------|-------------|
| [`README.md`](./README.md) | Guide to provisioning a DynamoDB table using Python and AWS Console. Includes script usage and cleanup steps. |
| [`chat_cli.py`](./chat_cli.py) | Python CLI script to create table, insert messages, create/delete backup, and delete table |
| [`config.yaml`](./config.yaml) | Configuration file containing AWS region, user aliases, and message templates |
| [`images/`](./images/) | Folder containing screenshots of each provisioning step for visual validation |

## Screenshot Files in `images/` Folder

| Filename | Description |
|----------|-------------|
| [`01-table-created.png`](./images/01-table-created.png) | Screenshot showing successful creation of the DynamoDB table |
| [`02-table-items.png`](./images/02-table-items.png) | Screenshot showing 5 chat messages inserted as table items |
| [`03-table-backup.png`](./images/03-table-backup.png) | Screenshot showing successful creation of on-demand backup |


### Prerequisites

Set the AWS region environment variable to ensure all commands execute in the desired region:

```bash
# Set AWS region for sandbox/testing environment (Oregon)
export AWS_DEFAULT_REGION=us-west-2
```

### Table Design and Purpose

The table is named `Messages` and uses:
- `ConversationId` as the partition key (e.g., `tom#jerry`)
- `SentAt` as the sort key (ISO 8601 timestamp)

This schema supports chronological retrieval of messages between any two users.

### Configuration File: [`config.yaml`](./config.yaml)

Defines:
- AWS region
- User aliases (`user1`, `user2`)
- Message templates with `{from}` and `{to}` placeholders for dynamic formatting

Example:
```yaml
users:
  user1: Tom
  user2: Jerry

messages:
  - from: user1
    to: user2
    body: "Hey {to}, are you free?"
```

### Create Table

Creates the DynamoDB table with the required schema.

```bash
python chat_cli.py create-table
```

#### Script Output
```bash
Creating table 'Messages'...
  Partition key: ConversationId (type: String)
  Sort key: SentAt (type: String)
Table created.
```

*AWS Console Screenshot showing successful creation of the `Messages` table*

![`01-table-created.png`](./images/01-table-created.png)


### Add 5 Items to the Table

Inserts 5 chat messages between Tom and Jerry using the config file.

```bash
python3 chat_cli.py send-messages
```

#### Script Output
```bash
Sending messages...
   Tom → Jerry: Hey Jerry, are you free?
   Jerry → Tom: Yes, Jerry. What's up?
   Tom → Jerry: Need help with a script.
   Jerry → Tom: Sure, send it over.
   Tom → Jerry: Thanks! You're the best, Jerry.
All messages sent.
```

*AWS Console Screenshot showing 5 items added to the table*

![`02-table-items.png`](./images/02-table-items.png)

### Take Table Backup

Creates an on-demand backup of the table.

```bash
python3 chat_cli.py backup-table
```

#### Script Output
```bash
Creating backup...
Waiting for backup to become AVAILABLE...
  Backup status: AVAILABLE
Backup created: arn:aws:dynamodb:us-west-2:XXXXXXXXXXXX:table/Messages/backup/01759763974650-91e995a6
```

*AWS Console Screenshot showing table backup*

![`03-table-backup.png`](./images/03-table-backup.png)

### Delete Table

Deletes the DynamoDB table.

```bash
python3 chat_cli.py delete-table
```

#### Script Output
```bash
Deleting table...
Table deleted.
```

### Delete Backup

Deletes the previously created backup using the stored ARN.

```bash
python3 chat_cli.py delete-backup
```

#### Script Output
```bash
Deleting backup...
Backup deleted: arn:aws:dynamodb:us-west-2:XXXXXXXXXXXX:table/Messages/backup/01759763974650-91e995a6
```
