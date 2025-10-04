
CLUSTER_ID = 'M7-aurora-cluster'
ENGINE = 'aurora-mysql'
#INSTANCE_CLASS = 'db.t3.small'
INSTANCE_CLASS = 'db.t4g.medium' 
MASTER_USERNAME = 'adminuser'
MASTER_PASSWORD = 'XXXXXXXXXXXXXX'
DB_SUBNET_GROUP= 'default-db-subnet-group'
DEFAULT_DB_NAME = 'M7testdb'
DEFAULT_REGION = 'us-west-2'

# Custom DBInstanceIdentifier
PRIMARY_INSTANCE_ID= 'M7-aurora-primary'
READREPLICA_1_INSTANCE_ID ='M7-aurora-readreplica-1'
READREPLICA_2_INSTANCE_ID = 'M7-aurora-readreplica-2'

# Availability Zone for replica
READREPLICA_1_AZ ='us-west-2a'
READREPLICA_2_AZ ='us-west-2b'