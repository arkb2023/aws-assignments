![AWS CLI](https://img.shields.io/badge/AWS-CLI-blue?logo=amazon-aws)
![Shell Scripted](https://img.shields.io/badge/Scripted-Bash-green?logo=gnu-bash)
![Verified via Console](https://img.shields.io/badge/Verified-AWS%20Console-yellow?logo=amazon-aws)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

# 📘 Module 4: CloudWatch Alarms

---
## Tasks To Be Performed:
1. Manage the scaling requirements of the company by  
    a. Deploying multiple compute resources on the cloud as soon as the `load increases` and the `CPU utulization exceeds 80%`.
    b. Remove the resources when the `CPU utilization goes under 60%`
2. Create a `load balancer` to distribute the load between compute resources
3. Route the traffic to the `company's domain`



Set environment variables

Get VPC, subnet IDs, and public IP

Create key pair
Create security group and add rules
  1) ALB Security Group: Allows inbound HTTP/HTTPS from internet.
  2) EC2 Security Group: Allows inbound HTTP from ALB security group only and SSH access from client IP
Create CloudFormation stack (if using CloudFormation) or skip if manual

Create launch template (fix JSON syntax)

Create ALB (use space separated subnet IDs)

Capture ALB ARN

Create target group

Capture target group ARN

Create listener on ALB forwarding to target group

Create Auto Scaling Group referencing launch template, target group, subnets

Configure scaling policies with JSON file

Optionally add notifications, tags

Clean up resources when done

source config.sh

# Store default VPC ID in a variable
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
echo $VPC_ID

# Get all subnet IDs for the VPC as a space-separated list
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[].SubnetId" --output text)
echo "All Subnet IDs: $SUBNET_IDS"

# Extract the first subnet ID (for CloudFormation stack)
SUBNET_ID=$(echo $SUBNET_IDS | awk '{print $1}')
echo "First Subnet ID: $SUBNET_ID"

# Convert space-separated subnet IDs to comma-separated string (for ASG vpc-zone-identifier)
VPC_SUBNETS=$(echo $SUBNET_IDS | tr ' ' ',')
echo "Comma-separated Subnets: $VPC_SUBNETS"

# Store your current public IP with /32 suffix in a variable
MY_IP="$(curl -s https://checkip.amazonaws.com)/32"
echo $MY_IP

aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > $PEM_FILE
chmod 400 $PEM_FILE

<!--
Security group creation and rules configuration for ALB
-->
# Create ALB security group
ALB_SG_ID=$(aws ec2 create-security-group \
  --group-name $ALB_SG_NAME \
  --description "Security group for ALB SG" \
  --vpc-id $VPC_ID \
  --query GroupId \
  --output text)
# Add Ingress Rule to Allow HTTP (Port 80) Traffic
aws ec2 authorize-security-group-ingress --group-name $ALB_SG_NAME --protocol tcp --port 80 --cidr 0.0.0.0/0

<!--
Security group creation and rules configuration for ASG AND EC2
-->
# create a new Security Group for your Auto Scaling Group 
ASG_EC2_SG_ID=$(aws ec2 create-security-group \
  --group-name $ASG_EC2_SG_NAME \
  --description "Security group for Auto Scaling group instances" \
  --vpc-id $VPC_ID \
  --query GroupId --output text)
echo $ASG_EC2_SG_ID

# Add Ingress Rule to Allow HTTP (Port 80) Traffic from ALB
aws ec2 authorize-security-group-ingress \
  --group-id $ASG_EC2_SG_ID \
  --protocol tcp \
  --port 80 \
  --source-group $ALB_SG_ID


# Add SSH Access for Management
aws ec2 authorize-security-group-ingress \
  --group-name $ASG_EC2_SG_NAME \
  --protocol tcp \
  --port 22 \
  --cidr $MY_IP


<!--
Create the CloudFormation stack
-->
# Use variables to create the CloudFormation stack
aws cloudformation create-stack \
  --stack-name $CF_STACK_NAME \
  --template-body file://EC2-Auto-Scaling-Lab.yaml \
  --parameters ParameterKey=MyVPC,ParameterValue=$VPC_ID ParameterKey=PublicSubnet,ParameterValue=$SUBNET_ID ParameterKey=MyIP,ParameterValue=$MY_IP \
  --capabilities CAPABILITY_NAMED_IAM
![alt text](images/cf-create-stack-success.png)

# Fetch the Security group created from the CF template
# set the security group name as per CloudFormation YAML
<!-- WEBHOST_SG_NAME="${CF_STACK_NAME} - Website Security Group"
WEBHOST_SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$WEBHOST_SG_NAME" "Name=vpc-id,Values=$VPC_ID" --query "SecurityGroups[0].GroupId" --output text)
echo $WEBHOST_SG_ID -->

<!--
Create a custom machine image for our auto scaling group. 
This will create an image of our web host that will be used by our Auto Scaling group to spin up multiple instances based on server load.
-->
# Store Instance ID in variable
INSTANCE_ID=$(aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[0].Instances[0].InstanceId" --output text)
echo $INSTANCE_ID
# Use the stored Instance ID to create an AMI
AMI_ID=$(aws ec2 create-image --instance-id $INSTANCE_ID --name $AMI_NAME --description "AMI created from CLI" --no-reboot --query 'ImageId' --output text)
# Check the created AMI -- << not required >>
aws ec2 describe-images --image-ids $AMI_ID --query 'Images[*].{ImageId:ImageId,State:State}' --output table


# create the Launch Template for an EC2 Auto Scaling Group.
<!-- aws ec2 create-launch-template \
  --launch-template-name $LAUNCH_TEMPLATE_NAME \
  --version-description "Auto scaling launch template version 1" \
  --launch-template-data '{
    "ImageId": $AMI_ID,
    "InstanceType": "t2.micro",
    "KeyName": $KEY_NAME,
    "SecurityGroupIds": [$ASG_EC2_SG_ID],
    "Monitoring": { "Enabled": true }
  }' -->

<!--
A Launch Template is a feature of EC2 Auto Scaling that allows a way to templatize your launch requests. 
It enables you to store launch parameters so that you do not have to specify them every time you launch an instance. 
For example, 
  a specific Amazon Machine Image, 
  instance type, 
  storage, 
  networking
For each Launch Template, you can create one or more numbered Launch Template Versions. Each version can have different launch parameters.
-->
<!-- aws ec2 create-launch-template \
  --launch-template-name $LAUNCH_TEMPLATE_NAME \
  --version-description "Auto scaling launch template v1" \
  --launch-template-data "{\"ImageId\":\"$AMI_ID\",\"InstanceType\":\"t2.micro\",\"KeyName\":\"$KEY_NAME\",\"SecurityGroupIds\":[\"$ASG_EC2_SG_ID\"],\"Monitoring\":{\"Enabled\":true}}"
# aws ec2 describe-security-groups --filters "Name=group-name,Values=WebhostSecurityGroup" "Name=vpc-id,Values=$VPC_ID" --query "SecurityGroups[0].GroupId" --output text -->

aws ec2 create-launch-template \
  --launch-template-name $LAUNCH_TEMPLATE_NAME \
  --version-description "v1" \
  --launch-template-data "{
    \"ImageId\":\"$AMI_ID\",
    \"InstanceType\":\"t2.micro\",
    \"KeyName\":\"$KEY_NAME\",
    \"SecurityGroupIds\":[\"$ASG_EC2_SG_ID\"],
    \"Monitoring\": { \"Enabled\": true }
  }"


#  Create an Internet-facing Application Load Balancer (ALB)
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name $ALB_NAME \
  --subnets $SUBNET_IDS \
  --security-groups $ALB_SG_ID \
  --scheme internet-facing \
  --type application \
  --query "LoadBalancers[0].LoadBalancerArn" \
  --output text)

echo $ALB_ARN



<!--
You will first create a target group that will be used for your load balancer. Target groups route requests to individual registered targets, such as EC2 instances, using the protocol and port number that you specify. You can register a target with multiple target groups. You can configure health checks on a per target group basis. Health checks are performed on all targets registered to a target group that is specified in a listener rule for your load balancer.
-->

# Create a target group 
TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
  --name $ASG_TARGET_GROUP \
  --protocol HTTP \
  --port 80 \
  --target-type instance \
  --vpc-id $VPC_ID \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 5 \
  --unhealthy-threshold-count 2 \
  --matcher HttpCode=200 \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text)

echo $TARGET_GROUP_ARN


# Create a Listener on the ALB forwarding traffic to your Target Group
# This step maps the ALB’s listener (usually on port 80) to forward requests to your target group.
LISTENER_ARN=$(aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN \
  --query 'Listeners[0].ListenerArn' \
  --output text)
echo $LISTENER_ARN


<!--
You have created a Launch Template, which defines the parameters of the instances launched. Now we will create an Auto Scaling Group so that you can define how many EC2 instances should be launched and where to launch them.
-->
# Create an Auto Scaling Group and attach the launch template
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name $ASG_NAME \
  --launch-template LaunchTemplateName=$LAUNCH_TEMPLATE_NAME,Version=1 \
  --min-size 1 \
  --max-size 3 \
  --desired-capacity 2 \
  --vpc-zone-identifier $VPC_SUBNETS \
  --target-group-arns $TARGET_GROUP_ARN \
  --health-check-type ELB \
  --health-check-grace-period 120 \
  --tags Key=Name,Value=MyAutoScalingInstance,PropagateAtLaunch=true

aws autoscaling put-scaling-policy \
  --auto-scaling-group-name $ASG_NAME \
  --policy-name $ASG_SCALING_POLICY_NAME \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://target-tracking-config.json

### 
GET http://M4-ALB-215013799.us-west-2.elb.amazonaws.com


# Cleanup section
# Delete Auto Scaling Scaling Policy & Auto Scaling Group
aws autoscaling delete-policy --auto-scaling-group-name $ASG_NAME --policy-name $ASG_SCALING_POLICY_NAME
aws autoscaling delete-auto-scaling-group --auto-scaling-group-name $ASG_NAME --force-delete

# Delete Listener, Load Balancer & target group
aws elbv2 delete-listener --listener-arn $LISTENER_ARN
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
aws elbv2 delete-target-group --target-group-arn $TARGET_GROUP_ARN

# Delete Launch Template
aws ec2 delete-launch-template --launch-template-name $LAUNCH_TEMPLATE_NAME

# Deregister/Delete AMI and Associated Snapshot if any
aws ec2 deregister-image --image-id $AMI_ID


# Delete CloudFormation Stack
aws cloudformation delete-stack --stack-name $CF_STACK_NAME

# Delete Security Group
aws ec2 delete-security-group --group-id $ASG_EC2_SG_ID
aws ec2 delete-security-group --group-id $ALB_SG_ID

# Delete Key Pair
aws ec2 delete-key-pair --key-name $KEY_NAME
