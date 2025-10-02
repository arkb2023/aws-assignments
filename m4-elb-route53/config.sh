# AWS CLI default region
export AWS_DEFAULT_REGION=us-west-2  # Oregon region, for sandbox/testing

# Security Group names
ASG_EC2_SG_NAME="M4-ASG-SecurityGroup"       # For Auto Scaling Group instances
ALB_SG_NAME="M4-ALB-SecurityGroup"           # For Application Load Balancer

# Launch template and AMI naming
LAUNCH_TEMPLATE_NAME="M4-SCALING-LAUNCH-TEMPLATE"
AMI_NAME="M4-AMI"

# EC2 key pair details
KEY_NAME="M4-KeyPair"
PEM_FILE="${KEY_NAME}.pem"                   # Private key for SSH access

# Target Group and Load Balancer
ASG_TARGET_GROUP="M4-ASG-TargetGroup"
ALB_NAME="M4-ALB"

# Auto Scaling Group and scaling policies
ASG_NAME="M4-AutoScalingGroup"
ASG_SCALEOUT_POLICY_NAME="M4-ASG-Cpu-ScaleOut-Policy"
ASG_SCALEIN_POLICY_NAME="M4-ASG-Cpu-ScaleIn-Policy"

# CloudFormation stack
CF_STACK_NAME="M4-CF-Stack"

# CloudWatch alarms
CLOUDWATCH_HIGH_CPU_ALARM="$ASG_NAME-HighCPUAlarm"  # CPU > 80%
CLOUDWATCH_LOW_CPU_ALARM="$ASG_NAME-LowCPUAlarm"    # CPU < 60%