![Provisioned via AWS CloudFormation](https://img.shields.io/badge/Provisioned-AWS%20CloudFormation%20CLI-blue?logo=amazon-aws)
![Executed from Bash Prompt](https://img.shields.io/badge/Executed-Bash%20Prompt-green?logo=gnu-bash)
![Verified via AWS Console](https://img.shields.io/badge/Verified-AWS%20Console-yellow?logo=amazon-aws)
![Status: Completed](https://img.shields.io/badge/Status-Completed-brightgreen)


## Project - 3: Publishing Amazon SNS Messages Privately

### **Description**

- **Industry:** Healthcare

- **Problem Statement:**  
  How to secure patient records online and send them privately to the intended party.

- **Topics:**  
  In this project, you will be working on a hospital initiative to send medical reports online and develop a platform enabling patients to access reports via mobile devices and push notifications. You will publish reports to Amazon SNS while maintaining security and privacy. Messages will be hosted on an EC2 instance within your Amazon VPC. By publishing messages privately, you can improve both message delivery and receipt through Amazon SNS.

- **Highlights:**  
  1. AWS CloudFormation to create a VPC  
  2. Connect VPC with AWS SNS  
  3. Publish messages privately using SNS

---

### **Solution Overview**

This solution implements a secure, modular, event-driven architecture for transmitting sensitive healthcare messages using AWS CloudFormation. By adopting infrastructure-as-code, the approach ensures consistent resource provisioning, enables auditable workflows and supports robust compliance with privacy and security requirements.

Key design principles include:

- **Infrastructure-as-Code:**  
  All AWS resources—networking, security, compute, messaging, and endpoints are defined as templates to ensure repeatability and compliance.
- **Private Message Transmission:**  
  Leveraging a VPC interface endpoint for SNS, sensitive data is only transmitted internally, eliminating exposure to the public internet.
- **Event-driven Processing:**  
  SNS notifications fan out to Lambda functions for secure, instantaneous event handling and logging.
- **Separation of Concerns:**  
  Each template and script in the repository represents a specific infrastructure module, enabling granular updates and easy troubleshooting.
- **Operational Clarity:**  
  The repository includes configuration scripts, documentation, and visual evidence (screenshots) supporting deployment and validation.

***

### Architecture Diagram

This diagram provides a high-level view of solution components and their interactions.

![Architecture Diagram](images/arch.png)


### **Project Repository Structure**

The root directory is organized for clarity, modularity, and operational readiness:

```
├── README.md          # Project documentation, architecture, instructions, and screenshots
├── config.sh          # Shell script for environment variables, deployment parameters, and helper automation
├── images             # Folder containing all deployment and validation screenshots for reporting
└── src/               # All CloudFormation templates for infrastructure modules
    ├── main.yaml          # Orchestration parent template (nests all subcomponents)
    ├── vpc.yaml           # VPC, subnet, routing
    ├── sg.yaml            # Security Groups
    ├── iam.yaml           # IAM roles, instance profiles
    ├── ec2.yaml           # EC2 instance provisioning
    ├── endpoint.yaml      # VPC SNS interface endpoint
    ├── lambda-sns.yaml    # SNS topic, Lambda functions, permissions
    ├── s3.yaml            # S3 bucket (template/code storage)
```

***

### **Prerequisites**

- **Set up your local working environment:**  
  Install and configure the AWS CLI, and ensure your credentials are available.

- **Use the default settings or customize them by editing [config.sh](config.sh):**
  ```bash 
  # Core naming prefix
  STK_PREFIX="project3"

  # EC2 key pair, private key for SSH access
  KEY_NAME="${STK_PREFIX}-KeyPair" 
  PEM_FILE="${KEY_NAME}.pem"

  # Stack names
  MAIN_STACK_NAME="${STK_PREFIX}-main"
  S3_STACK_NAME="${STK_PREFIX}-s3"
  ```
- **Create an S3 bucket:**  
  Provision a dedicated S3 bucket to store CloudFormation templates and related artifacts.
  
    ```bash
    aws cloudformation deploy --template-file src/s3.yaml \
    --stack-name "$S3_STACK_NAME" \
    --capabilities CAPABILITY_NAMED_IAM
    ```

  - Displays S3 stack CloudFormation events.  
  ![S3 stack events](images/infrastructure/71-cf-s3-stack-events-create-complete.png)  

  - Resources provisioned within the S3 stack.  
  ![S3 stack resources](images/infrastructure/72-cf-s3-stack-resources.png)  

  - Outputs published by the S3 stack.  
  ![S3 stack outputs](images/infrastructure/73-cf-s3-stack-outputs.png)  

  - Shows the newly created S3 bucket.  
  ![S3 bucket created](images/resources/s3/01-s3-bucket-created.png)  
    
- **Upload templates to the S3 bucket:**  
  Copy all infrastructure templates from local repo to the designated S3 bucket.

    ```bash
    # Get the bucket name
    BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name "$S3_STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue" --output text)

    # Upload stacks
    aws s3 cp src/vpc.yaml s3://${BUCKET_NAME}
    aws s3 cp src/sg.yaml s3://${BUCKET_NAME}
    aws s3 cp src/iam.yaml s3://${BUCKET_NAME}
    aws s3 cp src/ec2.yaml s3://${BUCKET_NAME}
    aws s3 cp src/lambda-sns.yaml s3://${BUCKET_NAME}
    aws s3 cp src/endpoint.yaml s3://${BUCKET_NAME}
    ```
  - Visualizes the uploaded template objects inside S3 bucket.  
  ![S3 bucket object view](images/resources/s3/02-s3-bucket-objects-shows-all-uploaded-stack-templates.png)  

- **Generate an EC2 Key Pair:**  
  Create a new key pair for secure SSH access to the EC2 instance.
  ```bash
  aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > $PEM_FILE
  chmod 400 $PEM_FILE
  ```
***

### **Deploy the Main Stack**

- **Launch the main CloudFormation stack:**  
  Use the main orchestration template [src/main.yaml](src/main.yaml) to provision all required AWS resources automatically.
  ```bash
  aws cloudformation deploy --template-file src/main.yaml \
    --stack-name "${MAIN_STACK_NAME}" \
    --parameter-overrides \
    S3BucketName="${BUCKET_NAME}" \
    KeyName="${KEY_NAME}" \
    --capabilities CAPABILITY_NAMED_IAM
    ```
  > The main stack employs nested CloudFormation stacks, where each module ([VPC](src/vpc.yaml), [security groups](src/sg.yaml), [IAM roles](src/iam.yaml), [EC2](src/ec2.yaml), [endpoint](src/endpoint.yaml), [Lambda and SNS](src/lambda-sns.yaml)) is deployed through a dedicated child template. 

#### **Provisioned Infrastructure Screenshots**

Visual records of stack creation and configuration follow below, illustrating the successfully provisioned AWS resources using nested CloudFormation stacks.

#### infrastructure

- All CloudFormation stacks provisioned  
  ![All CloudFormation stacks provisioned](images/infrastructure/01-cf-all-8-stacks.png)  
    
- Main stack events ("CREATE_COMPLETE")  
  ![Main stack creation events](images/infrastructure/02-cf-main-stack-events-create-complete.png)  

- Main stack resources  
  ![Main stack resources summary](images/infrastructure/03-cf-main-stack-resources.png)  

- VPC stack events ("CREATE_COMPLETE")  
  ![VPC stack creation events](images/infrastructure/11-cf-vpc-stack-events-create-complete.png)  

- VPC stack resources  
  ![VPC stack resources](images/infrastructure/12-cf-vpc-stack-resources.png)  
  
- VPC stack outputs  
  ![VPC stack outputs](images/infrastructure/13-cf-vpc-stack-outputs.png)  

- Security Group stack events ("CREATE_COMPLETE")   
  ![Security Group stack events](images/infrastructure/21-cf-sg-stack-events-create-complete.png)  
    
- Security Group stack resources  
  ![Security Group stack resources](images/infrastructure/22-cf-sg-stack-resources.png)  

- Security Group stack outputs  
  ![Security Group stack outputs](images/infrastructure/23-cf-sg-stack-outputs.png)  
  
- Security Group stack parameters  
  ![Security Group stack parameters](images/infrastructure/24-cf-sg-stack-parameters.png)  
  
- Endpoint stack events ("CREATE_COMPLETE")  
  ![Endpoint stack creation events](images/infrastructure/31-cf-endpoint-stack-events-create-complete.png)  

- Endpoint stack resources  
  ![Endpoint stack resources](images/infrastructure/32-cf-endpoint-stack-resources.png)  
  
- Endpoint stack outputs  
  ![Endpoint stack outputs](images/infrastructure/33-cf-endpoint-stack-outputs.png)  

- Endpoint stack parameters  
  ![Endpoint stack parameters](images/infrastructure/34-cf-endpoint-stack-parameters.png)  

- IAM stack events ("CREATE_COMPLETE")  
  ![IAM stack creation events](images/infrastructure/41-cf-iam-stack-events-create-complete.png)  

- IAM stack resources  
  ![IAM stack resources](images/infrastructure/42-cf-iam-stack-resources.png)
  
- IAM stack outputs  
  ![IAM stack outputs](images/infrastructure/43-cf-iam-stack-outputs.png)  

- EC2 stack events ("CREATE_COMPLETE")    
  ![EC2 stack creation events](images/infrastructure/51-cf-ec2-stack-events-create-complete.png)  

- EC2 stack resources  
  ![EC2 stack resources](images/infrastructure/52-cf-ec2-stack-resources.png)  

- EC2 stack parameters  
  ![EC2 stack parameters](images/infrastructure/53-cf-ec2-stack-parameters.png)
  
- Lambda/SNS stack events ("CREATE_COMPLETE")    
  ![Lambda/SNS stack creation events](images/infrastructure/61-cf-lambda-sns-stack-events-create-complete.png)  

- Lambda/SNS stack resources  
  ![Lambda/SNS stack resources](images/infrastructure/62-cf-lambda-sns-stack-resources.png)
  
- Lambda/SNS stack parameters  
  ![Lambda/SNS stack parameters](images/infrastructure/63-cf-lambda-sns-stack-parameters.png)  

***

#### resources/vpc

- VPC created  
  ![VPC created](images/resources/vpc/01-vpc-created.png)  
    
- Subnet created  
  ![VPC subnet created](images/resources/vpc/02-vpc-subnet-created.png)  
    
- Route table created  
  ![VPC route table](images/resources/vpc/03-vpc-routetable-created.png)
  
- Internet Gateway created  
  ![VPC Internet Gateway](images/resources/vpc/04-vpc-igw-created.png)  
    
- Security Group created  
  ![VPC Security Group](images/resources/vpc/05-vpc-sg-created.png)  
    
- VPC endpoint created  
  ![VPC Endpoint created for SNS](images/resources/vpc/06-vpc-endpoint-created.png)  
    
- VPC endpoint details  
  ![VPC Endpoint details](images/resources/vpc/07-vpc-endpoint-details.png)  
    
- VPC endpoint subnets  
  ![VPC Endpoint subnets](images/resources/vpc/08-vpc-endpoint-subnets.png)  
    
- VPC endpoint security group  
  ![VPC Endpoint security group](images/resources/vpc/09-vpc-endpoint-sg.png)  
    
- VPC endpoint policy  
  ![VPC Endpoint policy](images/resources/vpc/10-vpc-endpoint-policy.png)  
    
- VPC endpoint tags  
  ![VPC Endpoint tags](images/resources/vpc/11-vpc-endpoint-tags.png)  
    
***

#### resources/ec2

- EC2 instance running  
  ![Running EC2 instance](images/resources/ec2/01-ec2-instance-running.png)  
    

- EC2 instance details showing IAM role attached  
  ![EC2 instance details - IAM role attached](images/resources/ec2/02-ec2-instance-details-iam-role-attached.png)  
    

- EC2 instance security group attached  
  ![EC2 instance security group](images/resources/ec2/03-ec2-instance-security-group-attached.png)  
    

***

#### resources/iam

- IAM roles for EC2 and Lambda  
  ![IAM roles for EC2 and Lambda](images/resources/iam/01-iam-roles-ec2-lambda.png)  
    

- Lambda role policy attached  
  ![Lambda IAM role policy attached](images/resources/iam/02-iam-roles-lambda-role-policy-attached.png)  
    

- Lambda role trust relationship  
  ![Lambda IAM role trust relationship](images/resources/iam/03-iam-roles-lambda-role-trust-relationship-attached.png)
  
- EC2 role policy attached  
  ![EC2 IAM role policy attached](images/resources/iam/04-iam-roles-ec2-role-policy-attached.png)  
    

- EC2 role trust relationship  
  ![EC2 IAM role trust relationship](images/resources/iam/05-iam-roles-ec2-role-trust-relationship-attached.png)  
    

***

#### resources/lambda

- Lambda functions list (shows two functions)  
  ![List of Lambda functions](images/resources/lambda/01-lambda-functions-shows-2-functions.png)  
    

- Lambda 1 configuration showing SNS trigger  
  ![Lambda 1 configuration - SNS trigger](images/resources/lambda/02-lambda-functions-function1-configuration-triggers-sns.png)

- Lambda 1 execution role and resource-based policy  
  ![Lambda 1 permissions - execution role and resource policy](images/resources/lambda/03-lambda-functions-function1-configuration-permissions-execution-role-and-resource-based-policy.png)  
    
- Lambda 1 tags  
  ![Lambda 1 function tags](images/resources/lambda/04-lambda-functions-function1-configuration-tags.png)  
    
- Lambda 1 monitoring/log destination (CloudWatch)  
  ![Lambda 1 CloudWatch log destination](images/resources/lambda/05-lambda-functions-function1-configuration-monitoring-operations-log-destination-cloudwatch-loggroup.png)  
    

- Lambda 2 configuration showing SNS trigger  
  ![Lambda 2 configuration - SNS trigger](images/resources/lambda/11-lambda-functions-function2-configuration-triggers-sns.png)

- Lambda 2 execution role and resource-based policy  
  ![Lambda 2 permissions - execution role and resource policy](images/resources/lambda/12-lambda-functions-function2-configuration-permissions-execution-role-and-resource-based-policy.png)  
    
- Lambda 2 tags  
  ![Lambda 2 function tags](images/resources/lambda/13-lambda-functions-function2-configuration-tags.png)  
    

- Lambda 2 monitoring/log destination (CloudWatch)  
  ![Lambda 2 CloudWatch log destination](images/resources/lambda/14-lambda-functions-function2-configuration-monitoring-operations-log-destination-cloudwatch-loggroup.png)  
    

***

#### resources/sns

- SNS topic created  
  ![SNS topic created](images/resources/sns/01-sns-topic-created.png)  
    

- SNS topic subscriptions (shows two Lambda functions)  
  ![SNS topic subscriptions](images/resources/sns/02-sns-topic-subscriptions-2-lambda-functions.png)  
    

- SNS topic access policy  
  ![SNS topic access policy](images/resources/sns/03-sns-topic-access-policy.png)
  
- SNS topic tags  
  ![SNS topic tags](images/resources/sns/04-sns-topic-tags.png)  
    

***

#### resources/cloudwatch

- CloudWatch shows two Lambda log groups  
  ![CloudWatch log groups for Lambda functions](images/resources/cloudwatch/01-cloudwatch-loggroups-2-loggroups.png)  

- Lambda 1 log group tags  
  ![CloudWatch Lambda 1 log group tags](images/resources/cloudwatch/03-cloudwatch-loggroups-lambda1-tags.png)  
  
- Lambda 2 log group tags  
  ![CloudWatch Lambda 2 log group tags](images/resources/cloudwatch/05-cloudwatch-loggroups-lambda2-tags.png)  

***

### **Validate the Use Case**

 - **Publish a sample message from the EC2 instance:**  
   Use SSH to access the EC2 host, then validate the SNS workflow by executing the AWS CLI publish command.  
  ```bash
  aws sns publish --region ${REGION} --topic-arn arn:aws:sns:${REGION}:${ACCOUNT_ID}:project3-sns-Topic --message "Patient record update"
  ```

- Message published to SNS topic from EC2 instance:  
  ![Publish to SNS from EC2 - success](images/terminal/01-ec2-terminal-aws-sns-publish-message-success.png)
  
- **Verify message delivery:**  
  Confirm successful event processing by inspecting the CloudWatch logs for both subscribed Lambda functions.

- Lambda 1 latest log events show the published message:  
  ![CloudWatch log events - Lambda 1](images/resources/cloudwatch/02-cloudwatch-loggroups-lambda1-log-events.png)

- Lambda 2 latest log events show the published message:  
  ![CloudWatch log events - Lambda 2](images/resources/cloudwatch/04-cloudwatch-loggroups-lambda2-log-events.png)


***

### **Cleanup**

- **Remove all provisioned resources:**  
  Delete the main CloudFormation stack to automatically remove all associated AWS resources.

  ```bash
  aws cloudformation delete-stack --stack-name "${MAIN_STACK_NAME}"
  aws cloudformation wait stack-delete-complete --stack-name "${MAIN_STACK_NAME}"
  ```

- **Delete the S3 bucket stack:**  
  > **Important:**  
  > Before deleting the S3 bucket stack, manually empty the bucket or delete all objects from the AWS Console.  
  > CloudFormation cannot remove a bucket unless it is empty.

  ```bash
  aws cloudformation delete-stack --stack-name "${S3_STACK_NAME}"
  aws cloudformation wait stack-delete-complete --stack-name "${S3_STACK_NAME}"
  ```
***


> **Reference:**  
> *This project approach leverages best practices and configuration steps documented in the AWS tutorial: [Publishing an Amazon SNS message from Amazon VPC](https://docs.aws.amazon.com/sns/latest/dg/sns-vpc-tutorial.html#sns-vpc-prereqs).*

***
