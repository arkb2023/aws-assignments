import boto3
import time

rds = boto3.client('rds')

def create_aurora_cluster_and_instances():
    cluster_id = 'my-aurora-cluster'
    master_username = 'adminuser'
    master_password = 'yourStrongPassword123'  # Use secure storage in production
    db_subnet_group = 'your-db-subnet-group'   # Replace with your subnet group
    security_group_ids = ['sg-xxxxxxxx']        # Replace with your security group IDs
    engine = 'aurora-mysql'
    instance_class = 'db.t3.small' # db.t3.small indicates a smaller, 
                                    # cost-efficient instance typically 
                                    # used for development or testing.
    # MultiAZ=True # not required for dev/test template
    # EngineMode='provisioned' # not required for "Aurora Standard" cluster configuration
    # 1. Create DB cluster
    print("Creating Aurora DB cluster...")
    rds.create_db_cluster(
        DBClusterIdentifier=cluster_id,
        Engine=engine,
        MasterUsername=master_username,
        MasterUserPassword=master_password,
        DBSubnetGroupName=db_subnet_group,
        VpcSecurityGroupIds=security_group_ids,
        DatabaseName='testdb',  # Optional database to create
        StorageEncrypted=True
    )

    # Wait briefly for the cluster to be available
    time.sleep(20)

    # 2. Create primary writer instance
    print("Creating primary DB instance...")
    rds.create_db_instance(
        DBInstanceIdentifier='my-aurora-primary',
        DBClusterIdentifier=cluster_id,
        Engine=engine,
        DBInstanceClass=instance_class,
        PubliclyAccessible=False,
        Tags=[{'Key': 'Name', 'Value': 'PrimaryInstance'}]
    )

    # 3. Create first read replica in another AZ
    print("Creating first read replica...")
    rds.create_db_instance(
        DBInstanceIdentifier='my-aurora-readreplica-1',
        DBClusterIdentifier=cluster_id,
        Engine=engine,
        DBInstanceClass=instance_class,
        AvailabilityZone='us-west-2a',  # Replace by your AZ
        PubliclyAccessible=False,
        Tags=[{'Key': 'Name', 'Value': 'ReadReplica1'}]
    )

    # 4. Create second read replica in different AZ
    print("Creating second read replica...")
    rds.create_db_instance(
        DBInstanceIdentifier='my-aurora-readreplica-2',
        DBClusterIdentifier=cluster_id,
        Engine=engine,
        DBInstanceClass=instance_class,
        AvailabilityZone='us-west-2b',  # Replace by your AZ
        PubliclyAccessible=False,
        Tags=[{'Key': 'Name', 'Value': 'ReadReplica2'}]
    )

    print("Aurora cluster and instances creation initiated.")

def cleanup_aurora_resources():
    cluster_id = 'my-aurora-cluster'
    instance_ids = [
        'my-aurora-primary',
        'my-aurora-readreplica-1',
        'my-aurora-readreplica-2'
    ]

    # Delete instances first
    for instance_id in instance_ids:
        print(f"Deleting DB instance: {instance_id} ...")
        try:
            rds.delete_db_instance(
                DBInstanceIdentifier=instance_id,
                SkipFinalSnapshot=True,  # or False to take snapshot
                DeleteAutomatedBackups=True
            )
        except Exception as e:
            print(f"Error deleting instance {instance_id}: {e}")

    # Wait for instances to be deleted before deleting cluster
    print("Waiting for DB instances to delete (this may take several minutes)...")
    waiter = rds.get_waiter('db_instance_deleted')
    for instance_id in instance_ids:
        try:
            waiter.wait(DBInstanceIdentifier=instance_id)
            print(f"DB instance {instance_id} deleted.")
        except Exception as e:
            print(f"Waiter error for instance {instance_id}: {e}")

    # Delete DB cluster
    print(f"Deleting DB cluster: {cluster_id} ...")
    try:
        rds.delete_db_cluster(
            DBClusterIdentifier=cluster_id,
            SkipFinalSnapshot=True
        )
        print("DB cluster deletion initiated.")
    except Exception as e:
        print(f"Error deleting DB cluster: {e}")


if __name__ == "__main__":
    create_aurora_cluster_and_instances()
    #cleanup_aurora_resources()
