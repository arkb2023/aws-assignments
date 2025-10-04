import boto3
import argparse
from config import *

rds = boto3.client('rds', region_name=DEFAULT_REGION)
ec2 = boto3.client('ec2', region_name=DEFAULT_REGION)

def get_default_vpc_id():

    vpc_id = ec2.describe_vpcs(
        Filters=[{'Name': 'isDefault', 'Values': ['true']}]
    )['Vpcs'][0]['VpcId']

    return vpc_id

def get_default_subnet_ids(vpc_id):

    subnets = ec2.describe_subnets(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )['Subnets']

    return [s['SubnetId'] for s in subnets]

def get_default_security_group_id(vpc_id):

    # Get the default security group in that VPC
    sg_id = ec2.describe_security_groups(Filters=[
        {'Name': 'vpc-id', 'Values': [vpc_id]},
        {'Name': 'group-name', 'Values': ['default']}
    ])['SecurityGroups'][0]['GroupId']
    
    return sg_id

def wait_for_cluster_available(cluster_id):
    print(f"Waiting for cluster {cluster_id} to become available...")
    waiter = rds.get_waiter('db_cluster_available')
    waiter.wait(DBClusterIdentifier=cluster_id)
    print("Cluster is now available.")

def wait_for_instance_available(instance_id):
    print(f"Waiting for instance {instance_id} to become available...")
    waiter = rds.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=instance_id)
    print(f"Instance {instance_id} is now available.")
    
def create_cluster(cluster_id, db_name, db_subnet_grp, subnet_ids, sg_ids):
    
    try:
        print(f"Creating DB subnet group using {subnet_ids} ")
        rds.create_db_subnet_group(
            DBSubnetGroupName=db_subnet_grp,
            DBSubnetGroupDescription='Subnet group using default VPC subnets',
            SubnetIds=subnet_ids,
            Tags=[{'Key': 'Name', 'Value': db_subnet_grp}]
        )
    except Exception as e:
        print(f"Error creating subnet group: {e}")

    print(f"Creating Aurora DB cluster: {cluster_id}, \
        Engine={ENGINE}, DBSubnetGroupName={db_subnet_grp} \
        VpcSecurityGroupIds={sg_ids} DatabaseName={db_name}")
    rds.create_db_cluster(
        DBClusterIdentifier=cluster_id,
        Engine=ENGINE,
        MasterUsername=MASTER_USERNAME,
        MasterUserPassword=MASTER_PASSWORD,
        DBSubnetGroupName=db_subnet_grp,
        VpcSecurityGroupIds=sg_ids,
        DatabaseName=db_name,
        StorageEncrypted=True,
        Tags=[{'Key': 'Name', 'Value': cluster_id}]

    )
    wait_for_cluster_available(cluster_id)
    print(f"Cluster {cluster_id} created with DB {db_name} and subnet group {db_subnet_grp}")

def create_instance(cluster_id, instance_id, az=None, tag='Instance'):
    print(f"Creating DB instance {instance_id}...")
    params = {
        'DBInstanceIdentifier': instance_id,
        'DBClusterIdentifier': cluster_id,
        'Engine': ENGINE,
        'DBInstanceClass': INSTANCE_CLASS,
        'PubliclyAccessible': False,
        'Tags': [{'Key': 'Name', 'Value': tag}]
    }
    if az:
        params['AvailabilityZone'] = az

    rds.create_db_instance(**params)
    wait_for_instance_available(instance_id)

    # Print actual AZ
    response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
    actual_az = response['DBInstances'][0]['AvailabilityZone']
    print(f"Instance {instance_id} launched in AZ: {actual_az}")

def cleanup(cluster_id, db_subnet_grp, instance_ids):
    for instance_id in instance_ids:
        print(f"Deleting DB instance: {instance_id} ...")
        try:
            rds.delete_db_instance(
                DBInstanceIdentifier=instance_id,
                SkipFinalSnapshot=True,
                DeleteAutomatedBackups=True
            )
        except Exception as e:
            print(f"Error deleting instance {instance_id}: {e}")

    print("Waiting for DB instances to delete...")
    waiter = rds.get_waiter('db_instance_deleted')
    for instance_id in instance_ids:
        try:
            waiter.wait(DBInstanceIdentifier=instance_id)
            print(f"DB instance {instance_id} deleted.")
        except Exception as e:
            print(f"Waiter error for instance {instance_id}: {e}")

    print(f"Deleting DB cluster: {cluster_id} ...")
    try:
        rds.delete_db_cluster(
            DBClusterIdentifier=cluster_id,
            SkipFinalSnapshot=True
        )
        print("DB cluster deletion initiated.")
        
        waiter = rds.get_waiter('db_cluster_deleted')
        waiter.wait(DBClusterIdentifier=cluster_id)
        print(f"DB cluster {cluster_id} deleted.")
    except Exception as e:
        print(f"Error deleting DB cluster: {e}")

    # Delete subnet group
    try:
        rds.delete_db_subnet_group(DBSubnetGroupName=db_subnet_grp)
        print(f"Subnet group {db_subnet_grp} deleted.")
    except Exception as e:
        print(f"Error deleting subnet group {db_subnet_grp}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aurora DB cluster automation")
    parser.add_argument("action", choices=[
        "create-cluster", "create-primary", "create-replica-1", "create-replica-2", "cleanup"], 
        help="Specify the operation to perform")

    args = parser.parse_args()

    if args.action == "create-cluster":
        vpc_id = get_default_vpc_id()
        subnet_ids = get_default_subnet_ids(vpc_id)
        sg_id = get_default_security_group_id(vpc_id)
        create_cluster(CLUSTER_ID, DEFAULT_DB_NAME, DB_SUBNET_GROUP, subnet_ids, [sg_id])
    elif args.action == "create-primary":
        
        create_instance(CLUSTER_ID, PRIMARY_INSTANCE_ID, tag="PrimaryInstance")
    elif args.action == "create-replica-1":
        create_instance(CLUSTER_ID, READREPLICA_1_INSTANCE_ID, az=READREPLICA_1_AZ, tag="ReadReplica1")
    elif args.action == "create-replica-2":
        create_instance(CLUSTER_ID, READREPLICA_2_INSTANCE_ID, az=READREPLICA_2_AZ, tag="ReadReplica2")
    elif args.action == "cleanup":
        instance_ids = [
            PRIMARY_INSTANCE_ID,
            READREPLICA_1_INSTANCE_ID,
            READREPLICA_2_INSTANCE_ID
        ]
        cleanup(CLUSTER_ID, DB_SUBNET_GROUP, instance_ids)