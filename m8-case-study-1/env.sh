# Core naming prefix
STK_PREFIX="m8-cf"

# Environment context
ENV="Dev"

# Application name for tagging
APP_NAME="CF-m8-case-study-1-app"

# EC2 key pair, private key for SSH access
KEY_NAME="${STK_PREFIX}-KeyPair" 
PEM_FILE="${KEY_NAME}.pem"

# CIDR blocks (optional overrides)
VPC_CIDR="10.0.0.0/16"
PUB_SUBNET_CIDR="10.0.1.0/24"
PRIV_SUBNET_CIDR="10.0.10.0/24"


# Network and stack names (derived)
NETWORK_STACK_NAME="${STK_PREFIX}-${ENV}-network"
SG_STACK_NAME="${STK_PREFIX}-${ENV}-security-groups"
EC2_STACK_NAME="${STK_PREFIX}-${ENV}-ec2"
DB_STACK_NAME="${STK_PREFIX}-${ENV}-db"

HOSTED_ZONE_DOMAIN=module8-domain.com
DB_USER="admin"
DB_PASSWORD="StrongPass123"
