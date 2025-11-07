# Core naming prefix
STK_PREFIX="project3"

# EC2 key pair, private key for SSH access
KEY_NAME="${STK_PREFIX}-KeyPair" 
PEM_FILE="${KEY_NAME}.pem"

# Stack names
MAIN_STACK_NAME="${STK_PREFIX}-main"
S3_STACK_NAME="${STK_PREFIX}-s3"

