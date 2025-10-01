# AWS CLI default region for all commands
export AWS_DEFAULT_REGION=us-west-2  # Oregon region, for sandbox/testing

# Security Group names
ASG_EC2_SG_NAME="M4-ASG-SecurityGroup"       # Security group for Auto Scaling Group instances
ALB_SG_NAME="M4-ALB-SecurityGroup"  # Security group for Application Load Balancer

# Launch template and AMI naming
LAUNCH_TEMPLATE_NAME="M4-SCALING-LAUNCH-TEMPLATE"
AMI_NAME="M4-AMI"

# Key pair details for EC2 instance access
KEY_NAME="M4-KeyPair"
PEM_FILE="${KEY_NAME}.pem"           # Private key file for SSH access

# Target Group and Load Balancer names
ASG_TARGET_GROUP="M4-ASG-TargetGroup"
ALB_NAME="M4-ALB"

# Auto Scaling Group name and scaling policy
ASG_NAME="M4-AutoScalingGroup"
ASG_SCALING_POLICY_NAME="M4-ASGCpuTargetTrackingPolicy"

# CloudFormation Stack name
CF_STACK_NAME="M4-CF-Stack"
