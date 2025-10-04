![Configured via AWS CLI](https://img.shields.io/badge/Configured-AWS%20CLI-blue?logo=amazon-aws)
![Scripted in Python](https://img.shields.io/badge/Scripted-Python-green?logo=python)
![Verified via AWS Console](https://img.shields.io/badge/Verified-AWS%20Console-yellow?logo=amazon-aws)
![Status: Completed](https://img.shields.io/badge/Status-Completed-brightgreen)

## Module 7: AuroraDB

### Problem Statement
You work for XYZ Corporation. Their application requires a SQL service that can store data which can be retrieved if required. Implement a suitable RDS engine for the same.  
While migrating, you are asked to perform the following tasks:  
1. Create an AuroraDB Engine based RDS Database.  
2. Create 2 Read Replicas in different availability zones for better infrastructure availability.  

### Solution Overview

This solution automates the provisioning of Aurora RDS resources using a Python script powered by the `boto3` SDK. The approach includes:

- Creating a DB subnet group using default VPC subnets  
- Launching an Aurora cluster with a primary instance  
- Adding two read replicas in distinct availability zones  
- Capturing each step with AWS Console screenshots  
- Cleaning up all resources after validation  

### Project Repository

This repository contains the essential components to automate the provisioning of an Aurora MySQL–based Amazon RDS cluster. It includes:

- Scripts to create the primary database and two read replicas across distinct availability zones for high availability.
- Configuration files defining engine parameters, instance classes, and network settings.
- Screenshot documentation capturing each provisioning step for validation and review.

```bash
$ tree
.
├── README.md
├── aurora.py
├── config.py
└── images
    ├── 01-db-subnet-group-created.png
    ├── 02-db-cluster-created.png
    ├── 03-db-primary-instance-created.png
    ├── 04-db-readreplica1-instance-created.png
    ├── 05-db-readreplica2-instance-created.png
    └── 06-db-cleanup.png
```
| Filename | Description |
|----------|-------------|
| [`README.md`](./README.md) | Guide to provisioning an AuroraDB cluster with one primary and two read replicas. Includes Python script usage, AWS Console screenshots, and cleanup steps. |
| [`aurora.py`](./aurora.py) | Automation script to provision Aurora DB cluster and instances via AWS SDK |
| [`config.py`](./config.py) | Configuration file containing constants like DB identifiers, region, and instance class |
| [`images/`](./images/) | Folder containing screenshots of each provisioning step for visual validation |

## Screenshot Files in `images/` Folder

| Filename | Description |
|----------|-------------|
| [`01-db-subnet-group-created.png`](./images/01-db-subnet-group-created.png) | Screenshot showing successful creation of DB subnet group using default VPC subnets |
| [`02-db-cluster-created.png`](./images/02-db-cluster-created.png) | Screenshot showing Aurora DB cluster in "available" state, successfully created in the `us-west-2` region |
| [`03-db-primary-instance-created.png`](./images/03-db-primary-instance-created.png) | Primary DB instance launched and attached to the Aurora cluster |
| [`04-db-readreplica1-instance-created.png`](./images/04-db-readreplica1-instance-created.png) | First read replica created in Availability Zone `us-west-2a` |
| [`05-db-readreplica2-instance-created.png`](./images/05-db-readreplica2-instance-created.png) | Second read replica created in Availability Zone `us-west-2b` |
| [`06-db-cleanup.png`](./images/06-db-cleanup.png) | Final cleanup step showing deletion of DB instances and cluster |


Here is a reviewed and refined version of your Prerequisites section with improved clarity, formatting, and logical flow:

***

### Prerequisites

Set the AWS region environment variable to ensure all commands execute in the desired region:

```bash
# Set AWS region for sandbox/testing environment (Oregon)
export AWS_DEFAULT_REGION=us-west-2
```

Verify that all required environment-specific variables are properly defined in the [`config.py`](./config.py) file. This file contains essential configuration parameters that customize the AWS setup for this project, including database identifiers, instance classes, subnet groups, and availability zones.

```bash
cat config.py
```

Sample `config.py` variables:

```python
CLUSTER_ID = 'M7-aurora-cluster'
ENGINE = 'aurora-mysql'
#INSTANCE_CLASS = 'db.t3.small'
INSTANCE_CLASS = 'db.t4g.medium'
MASTER_USERNAME = 'adminuser'
MASTER_PASSWORD = 'XXXXXXXXXXXXXX'
DB_SUBNET_GROUP= 'default-db-subnet-group'
DEFAULT_DB_NAME = 'M7testdb'
DEFAULT_REGION = 'us-west-2'

# Custom DB Instance Identifiers
PRIMARY_INSTANCE_ID= 'M7-aurora-primary'
READREPLICA_1_INSTANCE_ID ='M7-aurora-readreplica-1'
READREPLICA_2_INSTANCE_ID = 'M7-aurora-readreplica-2'

# Availability Zones for replicas
READREPLICA_1_AZ ='us-west-2a'
READREPLICA_2_AZ ='us-west-2b'
```

Ensure that these variables are properly set before running any provisioning or connection commands to avoid configuration errors.

### Cluster Creation Step

The following command initiates the creation of an Aurora MySQL–based RDS cluster using the Python automation script:

```bash
python3 aurora.py create-cluster
```
The script performs the following actions:
- Creates a DB subnet group using four subnets across multiple availability zones.
- Provisions an Aurora DB cluster named `M7-aurora-cluster` with engine `aurora-mysql`, linked to the subnet group and security group.
- Waits for the cluster to reach the `available` state before confirming success.
#### Script Output
```bash
Creating DB subnet group using ['subnet-00a20055b4212c22c', 'subnet-02ba2dc8dbdb3c1f1', 'subnet-02f7b58b6b3525cea', 'subnet-03c6cd6a44ab7fce8']
Creating Aurora DB cluster: M7-aurora-cluster, Engine=aurora-mysql, DBSubnetGroupName=default-db-subnet-group, VpcSecurityGroupIds=['sg-0836ee196577764b2'], DatabaseName=M7testdb
Waiting for cluster M7-aurora-cluster to become available...
Cluster is now available.
Cluster M7-aurora-cluster created with DB M7testdb and subnet group default-db-subnet-group
```

*AWS Console Screenshot showing successful creation of the subnet group used for the cluster*  

![`01-db-subnet-group-created.png`](./images/01-db-subnet-group-created.png)

*AWS Console Screenshot showing Aurora DB Cluster in the `available` state in the `us-west-2` region*  

![`02-db-cluster-created.png`](./images/02-db-cluster-created.png)


### Instance Provisioning

After successfully creating the Aurora DB cluster, the following steps provision the primary instance, two read replicas in separate availability zones

#### Primary Instance Creation

```bash
python3 aurora.py create-primary
```
- Launches the primary DB instance `M7-aurora-primary`.
- Waits until the instance reaches the `available` state.
- Confirms deployment in Availability Zone `us-west-2c`.
#### Script Output
```bash
Creating DB instance M7-aurora-primary...
Waiting for instance M7-aurora-primary to become available...
Instance M7-aurora-primary is now available.
Instance M7-aurora-primary launched in AZ: us-west-2c
```

*AWS Console Screenshot showing Primary instance in us-west-2c*  

![`03-db-primary-instance-created.png`](./images/03-db-primary-instance-created.png)

#### Read Replica 1 Creation

```bash
python3 aurora.py create-replica-1
```
- Creates read replica `M7-aurora-readreplica-1`.
- Waits for availability.
- Confirms deployment in Availability Zone `us-west-2a`.
#### Script Output
```bash
Creating DB instance M7-aurora-readreplica-1...
Waiting for instance M7-aurora-readreplica-1 to become available...
Instance M7-aurora-readreplica-1 is now available.
Instance M7-aurora-readreplica-1 launched in AZ: us-west-2a
```

*AWS Console Screenshot showing Read Replica 1 in us-west-2a*  

![`04-db-readreplica1-instance-created.png`](./images/04-db-readreplica1-instance-created.png)

#### Read Replica 2 Creation

```bash
python3 aurora.py create-replica-2
```
- Creates read replica `M7-aurora-readreplica-2`.
- Waits for availability.
- Confirms deployment in Availability Zone `us-west-2b`.
#### Script Output
```bash
Creating DB instance M7-aurora-readreplica-2...
Waiting for instance M7-aurora-readreplica-2 to become available...
Instance M7-aurora-readreplica-2 is now available.
Instance M7-aurora-readreplica-2 launched in AZ: us-west-2b
```

*AWS Console Screenshot showing Read Replica 2 in us-west-2b*  

![`05-db-readreplica2-instance-created.png`](./images/05-db-readreplica2-instance-created.png)

#### Cleanup

Steps to perform full cleanup of all provisioned resources.

```bash
python3 aurora.py cleanup
```
- Deletes all DB instances: primary and replicas.
- Waits for deletion to complete.
- Deletes the Aurora cluster and associated DB subnet group.
#### Script Output
```bash
Deleting DB instance: M7-aurora-primary ...
Deleting DB instance: M7-aurora-readreplica-1 ...
Deleting DB instance: M7-aurora-readreplica-2 ...
Waiting for DB instances to delete...
DB instance M7-aurora-primary deleted.
DB instance M7-aurora-readreplica-1 deleted.
DB instance M7-aurora-readreplica-2 deleted.
Deleting DB cluster: M7-aurora-cluster ...
DB cluster deletion initiated.
DB cluster M7-aurora-cluster deleted.
Subnet group default-db-subnet-group deleted.
```

*AWS Console Screenshot showing DB resource getting deleted*  

![`06-db-cleanup.png`](./images/06-db-cleanup.png)

