![Provisioned via AWS CloudFormation](https://img.shields.io/badge/Provisioned-AWS%20CloudFormation%20CLI-blue?logo=amazon-aws)
![Executed from Bash Prompt](https://img.shields.io/badge/Executed-Bash%20Prompt-green?logo=gnu-bash)
![Verified via AWS Console](https://img.shields.io/badge/Verified-AWS%20Console-yellow?logo=amazon-aws)
![Status: Completed](https://img.shields.io/badge/Status-Completed-brightgreen)


## Project-1: Deploying a Multi-Tier Website Using AWS EC2

### Description:
Amazon Elastic Compute Cloud (Amazon EC2) provides scalable computing capacity in the Amazon Web Services (AWS) cloud. Using Amazon EC2 eliminates your need to invest in hardware up front so you can develop and deploy applications faster. You can use Amazon EC2 to launch as many or as
few virtual servers as you need, configure security and networking, and manage storage. Amazon EC2 enables you to scale up or down to handle changes in requirements or spikes in popularity, reducing your need to forecast traffic.

### Problem Statement:
Company ABC wants to move their product to AWS. They have the following things set up right now:  
1. MySQL DB  
2. Website (PHP)  

The company wants high availability on this product, therefore wants Auto Scaling to be enabled on this website.  
Steps To Solve:  
1. Launch an EC2 Instance  
2. Enable Auto Scaling on these instances (minimum 2)  
3. Create an RDS Instance  
4. Create Database & Table in RDS instance:  
   a. Database name: intel  
   b. Table name: data  
   c. Database password: intel123  
5. Change hostname in website  
6. Allow traffic from EC2 to RDS instance  
7. Allow all-traffic to EC2 instance  

### Solution Overview

To fulfill the project requirements, this solution adopts a modular, multi-tier infrastructure deployment strategy using `AWS CloudFormation`. The architecture is organized into several main CloudFormation stacks, each responsible for a distinct layer of the environment:

1) `VPC resources` 
3) `EC2 resources`
4) `RDS MySQL database`
4) `S3 bucket resources`  

All stacks are parameterized for flexibility, automate resource provisioning, and export resource handles as outputs for seamless inter-stack communication and validation.

---

### **Project Repository Structure**

The repository is organized to facilitate modular infrastructure-as-code and application deployment. The structure is as follows:

- **[src/vpc.yaml](src/vpc.yaml):**  
  CloudFormation template defining the **networking layer**—creates a custom VPC with public/private subnets, route tables, internet and NAT gateways, and DHCP options.

- **[src/sg.yaml](src/sg.yaml):**  
  CloudFormation template for **security groups**, managing inbound and outbound traffic rules for EC2 instances, RDS databases, and load balancer to enforce network security.

- **[src/db.yaml](src/db.yaml):**  
  CloudFormation template provisioning an **Amazon RDS MySQL database**, including instance settings, credentials, and outputting connection endpoints for use by the application stack.

- **[src/s3.yaml](src/s3.yaml):**  
  CloudFormation template creating the **Amazon S3 bucket** used for application code storage.

- **[src/app.yaml](src/app.yaml):**  
  CloudFormation template implementing the **application layer**, including Auto Scaling Group, Load Balancer, HTTP Listener, Target Group, EC2 Launch Template, IAM Instance Profile, and IAM Roles for automated, scalable deployment of the PHP web app.

- **[php-web-app/index.php](php-web-app/index.php):**  
  The source code for the **PHP web application** deployed on EC2 instances.

- **[README.md](README.md):**  
  Step-by-step guide for provisioning, testing, validation, screenshots, and teardown of the infrastructure and applications.

- **[images/](images):**  
  Directory containing **screenshot files** used for documentation and verification.

---

### **Prerequisites**

```bash
# Set AWS region
export AWS_DEFAULT_REGION=us-west-2 # Oregon, for sandbox/testing
```

Override the defaults defined in [config.sh](config.sh).  
```bash
# Core naming prefix
STK_PREFIX="project1"

# Environment context
ENV="Dev"

# Application name for tagging
APP_NAME="project1"

# EC2 key pair, private key for SSH access
KEY_NAME="${STK_PREFIX}-KeyPair"
PEM_FILE="${KEY_NAME}.pem"

# CIDR blocks (optional overrides)
VPC_CIDR="10.0.0.0/16"
PUB_SUBNET_CIDR="10.0.1.0/24"
PRIV_SUBNET_CIDR="10.0.10.0/24"

# Stack names (derived)
NETWORK_STACK_NAME="${STK_PREFIX}-network"
SG_STACK_NAME="${STK_PREFIX}-security-group"
S3_STACK_NAME="${STK_PREFIX}-s3"
EC2_STACK_NAME="${STK_PREFIX}-ec2"
DB_STACK_NAME="${STK_PREFIX}-db"

DB_USER="intel"
DB_PASSWORD="intel123"
DB_NAME="intel"
```

Load the environment

```bash
source config.sh
```

***

### **1. Deploy the Stacks**

Provision the infrastructure components using the following AWS CLI commands. Each stack automates deployment for a distinct layer of the environment.

**VPC (Network) Stack**  
Deploy networking resources using [`src/vpc.yaml`](src/vpc.yaml):

```bash
aws cloudformation deploy --template-file src/vpc.yaml \
  --stack-name "${NETWORK_STACK_NAME}" \
  --parameter-overrides \
    AppNameTagValue="${APP_NAME}" \
    Env="${ENV}" \
    VpcIpv4Cidr="${VPC_CIDR}" \
    PublicSubnetIpv4Cidr="${PUB_SUBNET_CIDR}" \
    PrivateSubnetIpv4Cidr="${PRIV_SUBNET_CIDR}" \
  --capabilities CAPABILITY_NAMED_IAM
```


**Security Groups Stack**  
Define security rules using [`src/sg.yaml`](src/sg.yaml):

```bash
aws cloudformation deploy --template-file src/sg.yaml \
  --stack-name "${SG_STACK_NAME}" \
  --parameter-overrides \
    AppNameTagValue="${APP_NAME}" \
    Env="${ENV}" \
    NetworkStackName="${NETWORK_STACK_NAME}" \
  --capabilities CAPABILITY_NAMED_IAM
```

**S3 Stack**  
Provision the S3 bucket using [`src/s3.yaml`](src/s3.yaml):

```bash
aws cloudformation deploy --template-file src/s3.yaml \
  --stack-name "$S3_STACK_NAME" \
  --parameter-overrides \
    AppNameTagValue="${APP_NAME}" \
    Env="${ENV}" \
  --capabilities CAPABILITY_NAMED_IAM
```

**Database Stack**  
Deploy the RDS MySQL database using [`src/db.yaml`](src/db.yaml):

```bash
aws cloudformation deploy --template-file db/db.yaml \
  --stack-name "${DB_STACK_NAME}" \
  --parameter-overrides \
    AppNameTagValue="${APP_NAME}" \
    Env="${ENV}" \
    NetworkStackName="${NETWORK_STACK_NAME}" \
    SecurityGroupStackName="${SG_STACK_NAME}" \
    DBUsername="${DB_USER}" \
    DBPassword="${DB_PASSWORD}" \
    DBInstanceClass="db.t3.micro" \
    DBName="${DB_NAME}" \
    DBAllocatedStorage="20" \
  --capabilities CAPABILITY_NAMED_IAM
```

**EC2 (Application) Stack**  
Prepare application prerequisites before running the EC2 stack:

1. **Package the Application:**
   ```bash
   zip -r php-web-app.zip php-web-app/
   ```

2. **Upload the Package to S3:**
   ```bash
   BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name "$S3_STACK_NAME" \
     --query "Stacks[0].Outputs[?OutputKey=='PhpAppBucketName'].OutputValue" --output text)
   
   aws s3 cp php-web-app.zip s3://${BUCKET_NAME}/php-web-app.zip
   ```

3. **Fetch the Database Endpoint:**
   ```bash
   RDSInstanceEndpoint=$(aws cloudformation describe-stacks \
     --stack-name "${DB_STACK_NAME}" \
     --query "Stacks[0].Outputs[?OutputKey=='RDSInstanceEndpoint'].OutputValue" \
     --output text)
   ```

4. **Generate an EC2 SSH Key Pair:**
   ```bash
   aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > $PEM_FILE
   chmod 400 $PEM_FILE
   ```

5. **Deploy the EC2 Stack:**
   ```bash
   aws cloudformation deploy --template-file src/app.yaml \
     --stack-name "${EC2_STACK_NAME}" \
     --parameter-overrides \
       AppNameTagValue="${APP_NAME}" \
       Env="${ENV}" \
       KeyName="${KEY_NAME}" \
       NetworkStackName="${NETWORK_STACK_NAME}" \
       SecurityGroupStackName="${SG_STACK_NAME}" \
       S3BucketName="${BUCKET_NAME}" \
       RDSInstanceEndpoint="${RDSInstanceEndpoint}" \
     --capabilities CAPABILITY_NAMED_IAM
   ```

***

#### **Provisioned Infrastructure Screenshots**

Below are visual records of the provisioned infrastructure using the cloud formation stacks.

  - Shows the deployed CloudFormation stacks - `network` `security-groups` `s3` `ec2` and `db`  
  ![CloudFormation stacks](images/01-cf-stacks.png)  

  - Shows events for creating the network stack.  
  ![VPC stack events](images/vpc/01-vpc-cf-stack-events-view.png)  

  - Resources provisioned in the network stack.  
  ![VPC stack resources](images/vpc/02-vpc-cf-stack-resources-view.png)  
  
  - Output values exported from the network stack.  
  ![VPC stack outputs](images/vpc/03-vpc-cf-stack-outputs-view.png)  
  
  - Parameters used to configure the network stack.  
  ![VPC stack parameters](images/vpc/04-vpc-cf-stack-parameters-view.png)  
  
  - Depicts the newly created VPC  
  ![VPC created](images/vpc/11-vpc-created.png)  
  
  - Visualizes the subnets established within the VPC.  
  ![VPC subnets](images/vpc/12-subnets-created.png)  

  - Displays route tables configured for the VPC.  
  ![VPC route tables](images/vpc/13-routetables-created.png)  
  
  - Shows the Internet Gateway for external connectivity.  
  ![VPC Internet Gateway](images/vpc/14-internetgateway-created.png)  
  
  - Highlights security groups defined for VPC resources.  
  ![VPC security groups](images/vpc/15-securitygroups-created.png)  
  
  - Shows CloudFormation events for the security groups stack.  
  ![Security Groups stack events](images/sg/01-sg-cf-stack-events-view.png)  
  
  - Resources managed in the security groups stack.  
  ![Security Groups stack resources](images/sg/02-sg-cf-stack-resources-view.png)  
  
  - Outputs produced from the security groups stack.  
  ![Security Groups stack outputs](images/sg/03-sg-cf-stack-outputs-view.png)  
  
  - Displays S3 stack CloudFormation events.  
  ![S3 stack events](images/s3/01-s3-cf-stack-events-view.png)  
  
  - Resources provisioned within the S3 stack.  
  ![S3 stack resources](images/s3/02-s3-cf-stack-resources-view.png)  
  
  - Outputs published by the S3 stack.  
  ![S3 stack outputs](images/s3/03-s3-cf-stack-outputs-view.png)  
  
  - Shows the newly created S3 bucket.  
  ![S3 bucket created](images/s3/11-s3-bucket-created.png)  
  
  - Visualizes the uploaded application object inside S3 bucket.  
  ![S3 bucket object view](images/s3/12-s3-bucket-object-view.png)  
  
  - Shows CloudFormation events for the database stack.  
  ![DB stack events](images/db/01-db-cf-stack-events-view.png)  
  
  - Resources provisioned as part of the DB stack.  
  ![DB stack resources](images/db/02-db-cf-stack-resources-view.png)  
  
  - Displays output values exported by the DB stack.  
  ![DB stack outputs](images/db/03-db-cf-stack-outputs-view.png)  
  
  - Parameters used for DB stack provisioning.  
  ![DB stack parameters](images/db/04-db-cf-stack-parameters-view.png)  
  
  - Depicts the newly created RDS database instance.  
  ![RDS DB created](images/db/11-db-created.png)  
  
  - Shows the DB subnet group created.  
  ![DB subnet group](images/db/12-db-subnet-group-created.png)  
  
  - Shows CloudFormation events for deploying the EC2 app stack.  
  ![EC2 app stack events](images/ec2/02-ec2-cf-stack-events-view.png)  
  
  - Displays EC2 stack output values.  
  ![EC2 app stack outputs](images/ec2/03-ec2-cf-stack-outputs-view.png)  
  
  - Lists resources provisioned under the EC2 stack.  
  ![EC2 app stack resources](images/ec2/04-ec2-cf-stack-resources-view.png)  
  
  - Shows EC2 stack parameter values.  
  ![EC2 app stack parameters](images/ec2/05-ec2-cf-stack-parameters-view.png)  
  
  - Depicts the Auto Scaling Group created for the app.  
  ![ASG created](images/ec2/11-asg-created.png)  
  
  - Displays the Elastic Load Balancer setup for the application.  
  ![Load Balancer created](images/ec2/12-loadbalancer-created.png)  
  
  - Shows the EC2 target group for load balancing with two healthy instances.  
  ![EC2 target group](images/ec2/13-ec2-target-group-created.png)  
  
  - Displays details of the EC2 launch template.  
  ![Launch template created](images/ec2/14-ec2-launch-template-created.png)  
  
  - Shows the two EC2 instances launched for the application layer.  
  ![EC2 instances created](images/ec2/15-ec2-instances-created.png)  


### **2. Configure the Database**

Follow these steps to connect to the RDS MySQL database and create the required table.

#### **Connect to the Database and Create Table**

```bash
# SSH into the EC2 instance and connect to the RDS database
mysql -h ${RDSInstanceEndpoint} -u intel -p

# List available databases
SHOW DATABASES;

# Switch to the 'intel' database
USE intel;

# Create the application table
CREATE TABLE IF NOT EXISTS data (
  id INT AUTO_INCREMENT PRIMARY KEY,
  firstname VARCHAR(255),
  email VARCHAR(255)
);
```

The following screenshot demonstrates successful MySQL table creation:
![Database table created - terminal view](images/db/01-database-table-created-terminal-view.png)

This step validates connectivity, authentication, and schema preparation before accessing the deployed app.

### **3. Access the website**
This section provides both front-end and back-end confirmation, demonstrating working infrastructure and application logic.

Access the deployed application using the Load Balancer URL exported from the outputs of the EC2 stack.

  - The screenshot below demonstrates successful access to the PHP web application and creation of a new record through the website’s frontend.  
  ![New client record created](images/client/01-new-record-created.png)  

  - Add multiple records through the website's frontend form to validate end-to-end functionality.

  - To verify that new records are inserted, inspect the backend database directly. The screenshot below shows records confirmed in the MySQL table from the EC2 terminal:  
  ![Database records created - terminal view](images/db/02-records-created-terminal-view.png)  

### **4. Cleanup**

Execute the following commands in order to tear down the infrastructure:

  - **Delete the EC2 Application Stack:**
  ```bash
  aws cloudformation delete-stack --stack-name "${EC2_STACK_NAME}"
  aws cloudformation wait stack-delete-complete --stack-name "${EC2_STACK_NAME}"
  ```

  - **Delete the RDS Database and Related Stack:**
  ```bash
  aws rds delete-db-instance --db-instance-identifier "project1-dev-rds" --skip-final-snapshot
  aws rds wait db-instance-deleted --db-instance-identifier "project1-dev-rds"

  aws rds delete-db-subnet-group --db-subnet-group-name "project1-db-dbsubnetgroup-dvnchehoguss"
  aws cloudformation delete-stack --stack-name "${DB_STACK_NAME}"
  aws cloudformation wait stack-delete-complete --stack-name "${DB_STACK_NAME}"
  ```

  - **Delete the Security Groups Stack:**
  ```bash
  aws cloudformation delete-stack --stack-name "${SG_STACK_NAME}"
  aws cloudformation wait stack-delete-complete --stack-name "${SG_STACK_NAME}"
  ```

  - **Delete the S3 Bucket Stack:**
  > **Important:**  
  > First empty/delete all objects from the S3 bucket in the AWS console before deleting the bucket stack.

  ```bash
  aws cloudformation delete-stack --stack-name "$S3_STACK_NAME"
  aws cloudformation wait stack-delete-complete --stack-name "$S3_STACK_NAME"
  ```

  - **Delete the VPC (Network) Stack:**
  ```bash
  aws cloudformation delete-stack --stack-name "${NETWORK_STACK_NAME}"
  aws cloudformation wait stack-delete-complete --stack-name "${NETWORK_STACK_NAME}"
  ```

---