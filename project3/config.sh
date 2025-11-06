# Core naming prefix
STK_PREFIX="project3"

# Environment context
ENV="Dev"

# Application name for tagging
APP_NAME="project3"

# EC2 key pair, private key for SSH access
KEY_NAME="${STK_PREFIX}-KeyPair" 
PEM_FILE="${KEY_NAME}.pem"

# CIDR blocks (optional overrides)
VPC_CIDR="10.0.0.0/16"
PUB_SUBNET_CIDR="10.0.1.0/24"
PRIV_SUBNET_CIDR="10.0.10.0/24"


# Network and stack names (derived)
MAIN_STACK_NAME="${STK_PREFIX}-main"
NETWORK_STACK_NAME="${STK_PREFIX}-network"
SG_STACK_NAME="${STK_PREFIX}-security-group"
S3_STACK_NAME="${STK_PREFIX}-s3"
EC2_STACK_NAME="${STK_PREFIX}-ec2"
DB_STACK_NAME="${STK_PREFIX}-db"
