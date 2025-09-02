# config.py
REGION = 'us-west-2'  # Oregon, for sandbox/testing
AVAILABILITYZONE='us-west-2a'

ANY_CIDR = '0.0.0.0/0'

VPC_NAME="m2-vpc"
VPC_CIDR = '10.10.0.0/16'
VPC_SUBNET_NAME="m2-vpc-pvt-subnet"
VPC_PVT_SUBNET = '10.10.1.0/24'

INSTANCE_TYPE='t2.micro'
EFS_NAME='m2-efs'