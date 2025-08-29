# Module 5 VPC

### Problem Statement: 
You work for XYZ Corporation and, based on the expansion requirements of your corporation, you have been asked to create and set up a distinct Amazon VPC for the production and development teams. You are expected to perform the following tasks for the respective VPCs.

***

### Production Network

1.  **Design and build a 4-tier architecture.**
2.  **Create 5 subnets:** 4 private (`app1`, `app2`, `dbcache`, and `db`) and 1 public (`web`).
3.  **Launch instances** in all subnets and name them according to their respective subnet.
4.  **Allow `dbcache` instances and the `app1` subnet to send internet requests.**
5.  **Manage security groups and NACLs.**

***

### Development Network

1.  **Design and build a 2-tier architecture** with two subnets (`web` and `db`).
2.  **Launch instances** in both subnets and name them according to their respective subnet.
3.  **Ensure only the `web` subnet can send internet requests.**
4.  **Create a peering connection** between the production and development networks.
5.  **Set up a connection** between the `db` subnets of both the production and development networks.

***

### Approach: 
#### Production Network VPC

* **VPC CIDR:** `10.10.0.0/16`
    * `10.10.1.0/24` => web (**public subnet**)
    * `10.10.2.0/24` => app1 (**private subnet**)
    * `10.10.3.0/24` => app2 (**private subnet**)
    * `10.10.4.0/24` => dbcache (**private subnet**)
    * `10.10.5.0/24` => db (**private subnet**)

* **Initial Setup**
    * Create VPC
    * Create IGW (Internet Gateway)
    * Create private subnets for `app1`, `app2`, `dbcache`, and `db`
    * Create public subnet for `web`
    * Allocate Elastic IP
    * Create NAT Gateway

* **Route Tables**
    * Create route table for `app1` subnet, add default route with target as NAT GW
    * Create route table for `app2` subnet
    * Create route table for `dbcache` subnet, add default route with target as NAT GW
    * Create route table for `db` subnet
    * Create route table for `web` subnet, add default route with target as IGW

* **Security Groups**
    * **webserver EC2 instance**
        * Inbound SSH traffic: allow from any
        * Inbound HTTP traffic: allow from any
        * Inbound ICMP traffic: allow from any
    * **dbcache and app1 EC2 instances**
        * Inbound SSH traffic: allow from **Production network CIDR** and `webserver` security group
        * Inbound HTTP traffic: allow from **Production network CIDR** and `webserver` security group
        * Inbound PING traffic: allow from **Production network CIDR** and `webserver` security group
    * **dbcache and db EC2 instance**
        * Inbound SSH traffic: allow from **Development Network DB CIDR**
        * Inbound ICMP traffic: allow from **Development Network DB CIDR**
        * Inbound SSH traffic: allow from **Production Network Webserver CIDR**
        * Inbound ICMP traffic: allow from **Production Network Webserver CIDR**
    * **app2 EC2 instances**
        * Inbound PING traffic: allow from `webserver` security group

* NACL - default allow

***

#### Development Network VPC

* **VPC CIDR:** `10.20.0.0/16`
    * `10.20.1.0/24` => web (**public subnet**)
    * `10.20.2.0/24` => db (**private subnet**)

* **Initial Setup**
    * Create VPC
    * Create IGW
    * Create private subnet for `db`
    * Create public subnet for `web`

* **Route Tables**
    * Create route table for `db` subnet
    * Create route table for `web` subnet, add default route with target as IGW

* **Security Groups**
    * **webserver EC2 instance**
        * Inbound SSH traffic: allow from any
        * Inbound HTTP traffic: allow from any
        * Inbound PING traffic: allow from any
    * **db EC2 instance**
        * Inbound SSH traffic: allow from **Production Network DB CIDR**
        * Inbound ICMP traffic: allow from **Production Network DB CIDR**
        * Inbound SSH traffic: allow from **Production Network DBCache CIDR**
        * Inbound ICMP traffic: allow from **Production Network BCache CIDR**
        * Inbound SSH traffic: allow from **Development Network Webserver CIDR**
        * Inbound ICMP traffic: allow from **Development Network Webserver CIDR**

***

#### VPC Peering

* Create VPC peering between the Production and Development networks.
* **Add to/fro routes in route tables:**
    * **Production Network**
        * Add route in `dbcache` subnet route table: destination `development network CIDR`, target `peering id`
        * Add route in `db` subnet route table: destination `development network CIDR`, target `peering id`
    * **Development Network**
        * Add route in `db` subnet route table: destination `production network CIDR`, target `peering id`

***

#### Launch EC2 Instances

### a) Production Network

1.  Launch `webserver-prod` in `web` subnet.
2.  Launch `app1server` in `app1` subnet.
3.  Launch `app2server` in `app2` subnet.
4.  Launch `dbcacheserver` in `dbcache` subnet.
5.  Launch `dbserver` in `db-prod` subnet.

### b) Development Network

1.  Launch `webserver-dev` in `webserver-dev` subnet.
2.  Launch `dbserver-dev` in `db-dev` subnet.

***

# Test the Network

### i) Test internet access for `dbcache` instance

* SSH to `dbcache-prod` instance using `webserver-dev` as a jump host.
* Check if `ping www.google.com` works.
* Check if `curl www.google.com` works.

### ii) Test internet access for `app1` instance

* Check if SSH to `app1` instance using `webserver` as a jump host.
* Check if `ping www.google.com` works.
* Check if `curl www.google.com` works.

### iii) Make sure only the `web` subnet can send internet requests

* SSH to `webserver-dev` instance.
    * Check if `ping www.google.com` works.
    * Check if `curl www.google.com` works.
* SSH to `dbserver-dev` instance using `webserver-dev` as a jump host.
    * Check if `ping www.google.com` **does not work (expected)**.
    * Check if `curl www.google.com` **does not work (expected)**.

### iv) Setup connection between `db` subnets of both production and development networks

* **Test Prod to Dev connection**
    * SSH to `dbcache-prod` instance using `webserver-prod` as a jump host.
    * From `dbcache-prod`, ping/SSH to `dbserver-dev` instance.
* **Test reverse Dev to Prod connection**
    * SSH to `db-prod` instance using `webserver-prod` as a jump host.
    * From `db-prod`, ping/SSH to `dbserver-dev` instance.
    * SSH to `db-dev` instance using `webserver-dev` as a jump host.
    * From `db-dev`, ping/SSH to `dbcache-prod` instance.
    * From `db-dev`, ping/SSH to `db-prod` instance.
    
Execution Details:
---

## Set AWS Region
```bash
export AWS_DEFAULT_REGION=us-west-2 # Oregon, for sandbox/testing
```
**Export resource IDs:**
```bash
export VPC_RESOURCES_STORE_FILE="vpc_resources.json"
export SG_RESOURCES_STORE_FILE="sg_resources.json"
export EC2_RESOURCES_STORE_FILE="instances_resource.json"
export KEYPAIR_RESOURCES_STORE_FILE="keypair_resources.json"
export KEYPAIR_PEM_FILE="MyKeyPair.pem"
- Delete any contents of resources files generated out of previous executions (rm *.json)
```
## Create VPC and Networking Components

**Create Production Network VPC**
```bash
python3 vpc.py --action create-vpc --network prod --resource-file $VPC_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Created VPC vpc-production-network with ID vpc-09bf4173a6e995da7
Created and attached IGW igw-04563d290b76f697d to VPC vpc-09bf4173a6e995da7
Created subnet prod-net-pub-websubnet with ID subnet-036eca3812b3e0f7c
Created subnet prod-net-pvt-app1subnet with ID subnet-080d8a41a4d3a6710
Created subnet prod-net-pvt-app2subnet with ID subnet-09b57bb14226ee4fa
Created subnet prod-net-pvt-dbcachesubnet with ID subnet-02b890faf53f56987
Created subnet prod-net-pvt-dbsubnet with ID subnet-0a1ea33470bc08827
Allocated Elastic IP: Name: ProdNet-PublicWebSubnetNatGW-EIP, AllocationId: eipalloc-03fb11cc6a9eb2d7a
Waiting for NAT Gateway nat-0eab8642ebe753bf1 to become available...
NAT Gateway nat-0eab8642ebe753bf1 is now available
Created route table ProdNet-PvtApp1RouteTable with ID rtb-072e0e8e58b28727a
Associated route table rtb-072e0e8e58b28727a with subnet subnet-080d8a41a4d3a6710
Created route table ProdNet-PvtApp2RouteTable with ID rtb-0979a49a3614db48a
Associated route table rtb-0979a49a3614db48a with subnet subnet-09b57bb14226ee4fa
Created route table ProdNet-PvtDBCacheRouteTable with ID rtb-098dffe9d9176e376
Associated route table rtb-098dffe9d9176e376 with subnet subnet-02b890faf53f56987
Created route table ProdNet-PvtDBRouteTable with ID rtb-09b1271b4ffa14c0d
Associated route table rtb-09b1271b4ffa14c0d with subnet subnet-0a1ea33470bc08827
Created route 0.0.0.0/0 => nat-0eab8642ebe753bf1 in rtb-072e0e8e58b28727a
Created route 0.0.0.0/0 => nat-0eab8642ebe753bf1 in rtb-098dffe9d9176e376
Created route table ProdNet-PublicWebRouteTable with ID rtb-080da1a4e8250c02a
Associated route table rtb-080da1a4e8250c02a with subnet subnet-036eca3812b3e0f7c
Created route 0.0.0.0/0 => igw-04563d290b76f697d in rtb-080da1a4e8250c02a

--- Production Network Resources Summary ---
VPC ID: vpc-09bf4173a6e995da7
IGW ID: igw-04563d290b76f697d
Public Websubnet ID: subnet-036eca3812b3e0f7c
Private App1subnet ID: subnet-080d8a41a4d3a6710
Private App2subnet ID: subnet-09b57bb14226ee4fa
Private dbcachesubnet ID: subnet-02b890faf53f56987
Private dbsubnet ID: subnet-0a1ea33470bc08827
Elastic IP Allocation ID: eipalloc-03fb11cc6a9eb2d7a
NAT Gateway ID: nat-0eab8642ebe753bf1
Public Web subnet route Table ID: rtb-080da1a4e8250c02a
Private App1 subnet route Table ID: rtb-072e0e8e58b28727a
Private App2 subnet route Table ID: rtb-0979a49a3614db48a
Private DBCache subnet route Table ID: rtb-098dffe9d9176e376
Private DB subnet route Table ID: rtb-09b1271b4ffa14c0d
Merged and saved vpc-production-network resource info to vpc_resources.json
```
**Create Development Network VPC**
```bash
python3 vpc.py --action create-vpc --network dev --resource-file $VPC_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Created VPC vpc-development-network with ID vpc-0f7bf0210131834ff
Created and attached IGW igw-059c7d88ec647d53c to VPC vpc-0f7bf0210131834ff
Created subnet dev-net-pub-websubnet with ID subnet-0682b5d394a3d13df
Created subnet dev-net-pvt-dbsubnet with ID subnet-045b969f3e578de3c
Created route table DevNet-PrivateApp1RouteTable with ID rtb-0fe0180e91db77465
Associated route table rtb-0fe0180e91db77465 with subnet subnet-045b969f3e578de3c
Created route table DevNet-PublicWebRouteTable with ID rtb-00f958831657a1ff1
Associated route table rtb-00f958831657a1ff1 with subnet subnet-0682b5d394a3d13df
Created route 0.0.0.0/0 => igw-059c7d88ec647d53c in rtb-00f958831657a1ff1

--- Development Network Resources Summary ---
VPC ID: vpc-0f7bf0210131834ff
IGW ID: igw-059c7d88ec647d53c
Public web subnet ID: subnet-0682b5d394a3d13df
Private db subnet ID: subnet-045b969f3e578de3c
Public web subnet Route Table ID: rtb-00f958831657a1ff1
Private db subnet Route Table ID: rtb-0fe0180e91db77465
Merged and saved vpc-development-network resource info to vpc_resources.json
```
```bash
$ python gen_exports.py $VPC_RESOURCES_STORE_FILE > exports_vpc.sh
```
```bash
$ cat exports_vpc.sh
export PNET_VPC_ID="vpc-09bf4173a6e995da7"
export PNET_IGW_ID="igw-04563d290b76f697d"
export PNET_PUB_WEBSUBNET_ID="subnet-036eca3812b3e0f7c"
export PNET_PVT_APP1SUBNET_ID="subnet-080d8a41a4d3a6710"
export PNET_PVT_APP2SUBNET_ID="subnet-09b57bb14226ee4fa"
export PNET_PVT_DBCACHESUBNET_ID="subnet-02b890faf53f56987"
export PNET_PVT_DBSUBNET_ID="subnet-0a1ea33470bc08827"
export PNET_PUB_WEBSUBNET_RT_ID="rtb-080da1a4e8250c02a"
export PNET_PVT_APP1SUBNET_RT_ID="rtb-072e0e8e58b28727a"
export PNET_PVT_APP2SUBNET_RT_ID="rtb-0979a49a3614db48a"
export PNET_PVT_DBCACHESUBNET_RT_ID="rtb-098dffe9d9176e376"
export PNET_PVT_DBSUBNET_RT_ID="rtb-09b1271b4ffa14c0d"
export PNET_EIP_ID="eipalloc-03fb11cc6a9eb2d7a"
export PNET_NATGW_ID="nat-0eab8642ebe753bf1"
export DNET_VPC_ID="vpc-0f7bf0210131834ff"
export DNET_IGW_ID="igw-059c7d88ec647d53c"
export DNET_PUB_WEBSUBNET_ID="subnet-0682b5d394a3d13df"
export DNET_PVT_DBSUBNET_ID="subnet-045b969f3e578de3c"
export DNET_PUB_WEBSUBNET_RT_ID="rtb-00f958831657a1ff1"
export DNET_PVT_DBSUBNET_RT_ID="rtb-0fe0180e91db77465"
```
```bash
$ source exports_vpc.sh
```

**Create VPC peering between Production and Development Networks**
```bash
$ python3 vpc.py --action create-peer --prod-vpc-id $PNET_VPC_ID --dev-vpc-id $DNET_VPC_ID --resource-file $VPC_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
prod_vpc_id vpc-09bf4173a6e995da7 dev_vpc_id vpc-0f7bf0210131834ff
Created peering request: pcx-0f1419ff8351a0964
Accepted peering connection.
Merged and saved vpc-peering resource info to vpc_resources.json
Added route to 10.20.0.0/16 via peering connection pcx-0f1419ff8351a0964
Added route to 10.20.0.0/16 via peering connection pcx-0f1419ff8351a0964
Added route to 10.10.0.0/16 via peering connection pcx-0f1419ff8351a0964
```
```bash
$ cat vpc_resources.json
{
  "pnet_vpc_id": "vpc-09bf4173a6e995da7",
  "pnet_igw_id": "igw-04563d290b76f697d",
  "pnet_pub_websubnet_id": "subnet-036eca3812b3e0f7c",
  "pnet_pvt_app1subnet_id": "subnet-080d8a41a4d3a6710",
  "pnet_pvt_app2subnet_id": "subnet-09b57bb14226ee4fa",
  "pnet_pvt_dbcachesubnet_id": "subnet-02b890faf53f56987",
  "pnet_pvt_dbsubnet_id": "subnet-0a1ea33470bc08827",
  "pnet_pub_websubnet_rt_id": "rtb-080da1a4e8250c02a",
  "pnet_pvt_app1subnet_rt_id": "rtb-072e0e8e58b28727a",
  "pnet_pvt_app2subnet_rt_id": "rtb-0979a49a3614db48a",
  "pnet_pvt_dbcachesubnet_rt_id": "rtb-098dffe9d9176e376",
  "pnet_pvt_dbsubnet_rt_id": "rtb-09b1271b4ffa14c0d",
  "pnet_eip_id": "eipalloc-03fb11cc6a9eb2d7a",
  "pnet_natgw_id": "nat-0eab8642ebe753bf1",
  "dnet_vpc_id": "vpc-0f7bf0210131834ff",
  "dnet_igw_id": "igw-059c7d88ec647d53c",
  "dnet_pub_websubnet_id": "subnet-0682b5d394a3d13df",
  "dnet_pvt_dbsubnet_id": "subnet-045b969f3e578de3c",
  "dnet_pub_websubnet_rt_id": "rtb-00f958831657a1ff1",
  "dnet_pvt_dbsubnet_rt_id": "rtb-0fe0180e91db77465",
  "peering_id": "pcx-0f1419ff8351a0964"
}$
```
---
## 3 Create Security Groups
```bash
$ python3 securitygroups.py --action create --prod-vpc-id $PNET_VPC_ID --dev-vpc-id $DNET_VPC_ID --resource-file $SG_RESOURCES_STORE_FILE
```

**Example Output:**
```bash
Created security group Prod-Webserver-SG with ID sg-02ba028566e5b4f44
Ingress rules set for Prod-Webserver-SG
Created security group Prod-Dbcache-App1-SG with ID sg-0b21e0edcacc04bad
Ingress rules set for Prod-Dbcache-App1-SG
Created security group Prod-Dbcache-DB-SG with ID sg-0a55d42a94bcb2155
Ingress rules set for Prod-Dbcache-DB-SG
Created security group Prod-App2-SG with ID sg-0258ea6e48303c30b
Ingress rules set for Prod-App2-SG
Created security group Dev-Webserver-SG with ID sg-01924026995d45ad3
Ingress rules set for Dev-Webserver-SG
Created security group Dev-DB-SG with ID sg-0a5746e4fbe0f5435
Ingress rules set for Dev-DB-SG
Saved security group IDs to sg_resources.json
```
```bash
$ cat sg_resources.json
{
  "prod_web_sg_id": "sg-02ba028566e5b4f44",
  "prod_dbcache_app1_sg_id": "sg-0b21e0edcacc04bad",
  "prod_dbcache_db_sg_id": "sg-0a55d42a94bcb2155",
  "prod_app2_sg_id": "sg-0258ea6e48303c30b",
  "dev_web_sg_id": "sg-01924026995d45ad3",
  "dev_db_sg_id": "sg-0a5746e4fbe0f5435"
}
```
**Export variables:**
```bash
$ python gen_exports.py $SG_RESOURCES_STORE_FILE > exports_sg.sh
```
```bash
$ cat exports_sg.sh
export PROD_WEB_SG_ID="sg-02ba028566e5b4f44"
export PROD_DBCACHE_APP1_SG_ID="sg-0b21e0edcacc04bad"
export PROD_DBCACHE_DB_SG_ID="sg-0a55d42a94bcb2155"
export PROD_APP2_SG_ID="sg-0258ea6e48303c30b"
export DEV_WEB_SG_ID="sg-01924026995d45ad3"
export DEV_DB_SG_ID="sg-0a5746e4fbe0f5435"
```
```bash
$ source exports_sg.sh
```
---
## 4. Generate SSH Key Pair
```bash
$ python3 keypair.py --action create --resource-file $KEYPAIR_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Created key pair MyKeyPair and saved private key to MyKeyPair.pem
Saved key pair info to keypair_resources.json
```
```bash
$ cat $KEYPAIR_RESOURCES_STORE_FILE
{
  "key_name": "MyKeyPair",
  "key_file": "MyKeyPair.pem"
}$
```
**Export variables:**
```bash
export KEYPAIR="MyKeyPair"
```
```bash
# Start the SSH agent:
$ eval "$(ssh-agent -s)"
Agent pid 63080

# Add private key
$ ssh-add MyKeyPair.pem
Identity added: MyKeyPair.pem (MyKeyPair.pem)

# Verify the key was added
$ ssh-add -l
2048 SHA256:wCwjgfzd4/H74AaCeiO99ZqgK1SENwg+yupKBtMJWDU MyKeyPair.pem (RSA)
```
## 5.a Launch EC2 Instances in Production Network

### Webserver (Public Subnet)
```bash
$ export PROD_NET_WEBSERVER_INSTANCE_NAME="prod_net_webserver"
$ python3 ec2instance.py --action create --subnet-id $PNET_PUB_WEBSUBNET_ID \
    --sg-ids $PROD_WEB_SG_ID --key-name $KEYPAIR \
    --instance-names $PROD_NET_WEBSERVER_INSTANCE_NAME \
    --associate-public-ip --resource-file $EC2_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Instance prod_net_webserver created
Instance prod_net_webserver running with ID: i-0dacfc74b8f161150
Merged and saved ec2-instance resource info to instances_resource.json
```
### App1 Server (Private Subnet)
```bash
$ export PROD_NET_APP1SERVER_INSTANCE_NAME="prod_net_app1server"
$ python ec2instance.py --action create --subnet-id $PNET_PVT_APP1SUBNET_ID \
  --sg-ids $PROD_DBCACHE_APP1_SG_ID  $PROD_DBCACHE_DB_SG_ID \
  --key-name $KEYPAIR --instance-names $PROD_NET_APP1SERVER_INSTANCE_NAME \
  --resource-file $EC2_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Instance prod_net_app1server created
Instance prod_net_app1server running with ID: i-03d3ce3d9bb517870
Merged and saved ec2-instance resource info to instances_resource.json
```
### DBCache Server (Private Subnet)
```bash
$ export PROD_NET_DBCACHESERVER_INSTANCE_NAME="prod_net_dbcacheserver"
$ python3 ec2instance.py --action create --subnet-id $PNET_PVT_DBCACHESUBNET_ID \
    --sg-ids $PROD_DBCACHE_APP1_SG_ID $PROD_DBCACHE_DB_SG_ID \
    --key-name $KEYPAIR --instance-names $PROD_NET_DBCACHESERVER_INSTANCE_NAME \
    --resource-file $EC2_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Instance prod_net_dbcacheserver created
Instance prod_net_dbcacheserver running with ID: i-025530d868f300722
Merged and saved ec2-instance resource info to instances_resource.json
```
### App2 Server (Private Subnet)
```bash
$ export PROD_NET_APP2SERVER_INSTANCE_NAME="prod_net_app2server"
$ python3 ec2instance.py --action create     --subnet-id $PNET_PVT_APP2SUBNET_ID     --sg-ids $PROD_APP2_SG_ID     --key-name $KEYPAIR     --instance-names $PROD_NET_APP2SERVER_INSTANCE_NAME --resource-file $EC2_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Instance prod_net_app2server created
Instance prod_net_app2server running with ID: i-0b61ad56fbf3b7e56
Merged and saved ec2-instance resource info to instances_resource.json
```
### Database Server (Private Subnet)
```bash
$ export PROD_NET_DBSERVER_INSTANCE_NAME="prod_net_dbserver"
$ python3 ec2instance.py --action create --subnet-id $PNET_PVT_DBSUBNET_ID \
    --sg-ids $PROD_DBCACHE_DB_SG_ID --key-name $KEYPAIR \
    --instance-names $PROD_NET_DBSERVER_INSTANCE_NAME \
    --resource-file $EC2_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Instance prod_net_dbserver created
Instance prod_net_dbserver running with ID: i-063208bd70e1c875c
Merged and saved ec2-instance resource info to instances_resource.json
```

## 5.b Launch EC2 Instances in Development Network

### Webserver (Public Subnet)
```bash
$ export DEV_NET_WEBSERVER_INSTANCE_NAME="dev_net_webserver"
$ python3 ec2instance.py --action create --subnet-id $DNET_PUB_WEBSUBNET_ID \
    --sg-ids $DEV_WEB_SG_ID --key-name $KEYPAIR \
    --instance-names $DEV_NET_WEBSERVER_INSTANCE_NAME \
    --associate-public-ip --resource-file $EC2_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Instance dev_net_webserver created
Instance dev_net_webserver running with ID: i-0538b233d00a200a7
Merged and saved ec2-instance resource info to instances_resource.json
```
### App1 Server (Private Subnet)
```bash
$ export DEV_NET_DBSERVER_INSTANCE_NAME="dev_net_dbserver"
$ python3 ec2instance.py --action create --subnet-id $DNET_PVT_DBSUBNET_ID \
    --sg-ids $DEV_DB_SG_ID  --key-name $KEYPAIR \
    --instance-names $DEV_NET_DBSERVER_INSTANCE_NAME \
    --resource-file $EC2_RESOURCES_STORE_FILE
```
**Example Output**
```bash
Instance dev_net_dbserver created
Instance dev_net_dbserver running with ID: i-0931773ba62654ffa
Merged and saved ec2-instance resource info to instances_resource.json
```
**Example instance IDs stored in the resource file**
```bash
$ cat instances_resource.json
{
  "prod_net_webserver_id": "i-0dacfc74b8f161150",
  "prod_net_app1server_id": "i-03d3ce3d9bb517870",
  "prod_net_dbcacheserver_id": "i-025530d868f300722",
  "prod_net_app2server_id": "i-0b61ad56fbf3b7e56",
  "prod_net_dbserver_id": "i-063208bd70e1c875c",
  "dev_net_webserver_id": "i-0538b233d00a200a7",
  "dev_net_dbserver_id": "i-0931773ba62654ffa"
}
```
**Export variables:**
```bash
$ python gen_exports.py $EC2_RESOURCES_STORE_FILE > exports_inst.sh
```
```bash
$ cat exports_inst.sh
export PROD_NET_WEBSERVER_ID="i-0dacfc74b8f161150"
export PROD_NET_APP1SERVER_ID="i-03d3ce3d9bb517870"
export PROD_NET_DBCACHESERVER_ID="i-025530d868f300722"
export PROD_NET_APP2SERVER_ID="i-0b61ad56fbf3b7e56"
export PROD_NET_DBSERVER_ID="i-063208bd70e1c875c"
export DEV_NET_WEBSERVER_ID="i-0538b233d00a200a7"
export DEV_NET_DBSERVER_ID="i-0931773ba62654ffa"
```
```bash
$ source exports_inst.sh
```

---
## 6. Fetch the Instance details
```bash
$ aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query "Reservations[*].Instances[*].{InstanceId:InstanceId,InstanceState:State.Name,InstanceType:InstanceType,Name:Tags[?Key=='Name'].Value|[0],PublicIp:PublicIpAddress,PrivateIp:PrivateIpAddress,SubnetId:SubnetId}" \
    --output table
```
**Example Output:**
```bash
-------------------------------------------------------------------------------------------------------------------------------------------------
|                                                               DescribeInstances                                                               |
+---------------------+----------------+---------------+-------------------------+--------------+------------------+----------------------------+
|     InstanceId      | InstanceState  | InstanceType  |          Name           |  PrivateIp   |    PublicIp      |         SubnetId           |
+---------------------+----------------+---------------+-------------------------+--------------+------------------+----------------------------+
|  i-03d3ce3d9bb517870|  running       |  t2.micro     |  prod_net_app1server    |  10.10.2.110 |  None            |  subnet-080d8a41a4d3a6710  |
|  i-025530d868f300722|  running       |  t2.micro     |  prod_net_dbcacheserver |  10.10.4.50  |  None            |  subnet-02b890faf53f56987  |
|  i-0dacfc74b8f161150|  running       |  t2.micro     |  prod_net_webserver     |  10.10.1.204 |  44.251.0.89     |  subnet-036eca3812b3e0f7c  |
|  i-063208bd70e1c875c|  running       |  t2.micro     |  prod_net_dbserver      |  10.10.5.101 |  None            |  subnet-0a1ea33470bc08827  |
|  i-0b61ad56fbf3b7e56|  running       |  t2.micro     |  prod_net_app2server    |  10.10.3.27  |  None            |  subnet-09b57bb14226ee4fa  |
|  i-0538b233d00a200a7|  running       |  t2.micro     |  dev_net_webserver      |  10.20.1.15  |  44.246.143.193  |  subnet-0682b5d394a3d13df  |
|  i-0931773ba62654ffa|  running       |  t2.micro     |  dev_net_dbserver       |  10.20.2.182 |  None            |  subnet-045b969f3e578de3c  |
+---------------------+----------------+---------------+-------------------------+--------------+------------------+----------------------------+
$
```
**Export resource IDs:**
```bash
# use the ip addresses from the table and set the environment variables
$ export PROD_NET_WEBSERVER_IP="44.251.0.89"
$ export PROD_NET_APP1SERVER_IP="10.10.2.110"
$ export PROD_NET_APP2SERVER_IP="10.10.3.27"
$ export PROD_NET_DBCACHESERVER_IP="10.10.4.50"
$ export PROD_NET_DBSERVER_IP="10.10.5.101"
$ export DEV_NET_WEBSERVER_IP="44.246.143.193"
$ export DEV_NET_DBSERVER_IP="10.20.2.182"
```
---

## 7. Test the network

**i) Test internet access for dbcache instance**
```bash
# ssh to dbcache instance through webserver as jump host
$ ssh -J ec2-user@$PROD_NET_WEBSERVER_IP ec2-user@$PROD_NET_DBCACHESERVER_IP
```
**Example Output**  
```bash
The authenticity of host '44.251.0.89 (44.251.0.89)' can't be established.
ED25519 key fingerprint is SHA256:T9H+qceUVsZFwOP8giPD3pc2EE3DA2owNwTGwuzt7Ss.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '44.251.0.89' (ED25519) to the list of known hosts.
The authenticity of host '10.10.4.50 (<no hostip for proxy command>)' can't be established.
ED25519 key fingerprint is SHA256:VHO7hfNP/1oAhUBuuiqRNDQ71fatOr16zBc7Kxz6vUs.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.4.50' (ED25519) to the list of known hosts.
   ,     #_
   ~\_  ####_        Amazon Linux 2
  ~~  \_#####\
  ~~     \###|       AL2 End of Life is 2026-06-30.
  ~~       \#/ ___
   ~~       V~' '->
    ~~~         /    A newer version of Amazon Linux is available!
      ~~._.   _/
         _/ _/       Amazon Linux 2023, GA and supported until 2028-03-15.
       _/m/'           https://aws.amazon.com/linux/amazon-linux-2023/

```
```bash
# Internet access works
[ec2-user@ip-10-10-4-50 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.217.68) 56(84) bytes of data.
64 bytes from sea09s29-in-f4.1e100.net (142.250.217.68): icmp_seq=1 ttl=116 time=8.65 ms
64 bytes from sea09s29-in-f4.1e100.net (142.250.217.68): icmp_seq=2 ttl=116 time=7.82 ms
64 bytes from sea09s29-in-f4.1e100.net (142.250.217.68): icmp_seq=3 ttl=116 time=7.89 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.821/8.123/8.652/0.389 ms
```
```bash
# Internet access works
[ec2-user@ip-10-10-4-50 ~]$ curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
```
```bash
# Ping to DB server of Development network works due to VPC peering
[ec2-user@ip-10-10-4-50 ~]$ ping 10.20.2.182 -c 3
PING 10.20.2.182 (10.20.2.182) 56(84) bytes of data.
64 bytes from 10.20.2.182: icmp_seq=1 ttl=255 time=1.73 ms
64 bytes from 10.20.2.182: icmp_seq=2 ttl=255 time=0.919 ms
64 bytes from 10.20.2.182: icmp_seq=3 ttl=255 time=1.05 ms

--- 10.20.2.182 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 0.919/1.235/1.732/0.356 ms
[ec2-user@ip-10-10-4-50 ~]$ exit
logout
Connection to 10.10.4.50 closed.
```
**ii) Test internet access for app1 instance**
```bash
$ ssh -J ec2-user@$PROD_NET_WEBSERVER_IP ec2-user@$PROD_NET_APP1SERVER_IP
```
**Example Output**
```bash
The authenticity of host '10.10.2.110 (<no hostip for proxy command>)' can't be established.
ED25519 key fingerprint is SHA256:2zfpBP8emt0nBlY9ddz86Zxbe1EVBX8eiBGJpk1PwQg.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.2.110' (ED25519) to the list of known hosts.
   ,     #_
   ~\_  ####_        Amazon Linux 2
  ~~  \_#####\
  ~~     \###|       AL2 End of Life is 2026-06-30.
  ~~       \#/ ___
   ~~       V~' '->
    ~~~         /    A newer version of Amazon Linux is available!
      ~~._.   _/
         _/ _/       Amazon Linux 2023, GA and supported until 2028-03-15.
       _/m/'           https://aws.amazon.com/linux/amazon-linux-2023/
```
```bash
# Internet access works
[ec2-user@ip-10-10-2-110 ~]$ ping www.google.com -c 3
PING www.google.com (142.251.215.228) 56(84) bytes of data.
64 bytes from sea09s35-in-f4.1e100.net (142.251.215.228): icmp_seq=1 ttl=116 time=7.16 ms
64 bytes from sea09s35-in-f4.1e100.net (142.251.215.228): icmp_seq=2 ttl=116 time=6.59 ms
64 bytes from sea09s35-in-f4.1e100.net (142.251.215.228): icmp_seq=3 ttl=116 time=6.60 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 6.599/6.789/7.165/0.265 ms
```
```bash
# Internet access works
[ec2-user@ip-10-10-2-110 ~]$ curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
[ec2-user@ip-10-10-2-110 ~]$ exit
logout
Connection to 10.10.2.110 closed.
```

**iii) Make sure only the web subnet can send internet requests**

```bash
$ ssh ec2-user@$DEV_NET_WEBSERVER_IP
```
**Example Output**
```bash
The authenticity of host '44.246.143.193 (44.246.143.193)' can't be established.
ED25519 key fingerprint is SHA256:RqgvJd3lj0Dgt485nX8l326E6EeVb2FkWBL11QTWlFQ.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '44.246.143.193' (ED25519) to the list of known hosts.
   ,     #_
   ~\_  ####_        Amazon Linux 2
  ~~  \_#####\
  ~~     \###|       AL2 End of Life is 2026-06-30.
  ~~       \#/ ___
   ~~       V~' '->
    ~~~         /    A newer version of Amazon Linux is available!
      ~~._.   _/
         _/ _/       Amazon Linux 2023, GA and supported until 2028-03-15.
       _/m/'           https://aws.amazon.com/linux/amazon-linux-2023/
```
```bash
# Internet access works
[ec2-user@ip-10-20-1-15 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=117 time=5.70 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=117 time=5.73 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=117 time=5.73 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 5.702/5.723/5.737/0.063 ms
```
```bash
# Internet access works
[ec2-user@ip-10-20-1-15 ~]$ curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
[ec2-user@ip-10-20-1-15 ~]$ exit
logout
Connection to 44.246.143.193 closed.
```
- ssh to dbserver-dev instance using webserver-dev as jump host
```bash
$ ssh -J ec2-user@$DEV_NET_WEBSERVER_IP ec2-user@$DEV_NET_DBSERVER_IP
```
**Example Output**
```bash
The authenticity of host '10.20.2.182 (<no hostip for proxy command>)' can't be established.
ED25519 key fingerprint is SHA256:buXkSbYi/fuweHLvAQiJqA7zu+te58pZ3anOAFXaps8.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.20.2.182' (ED25519) to the list of known hosts.
   ,     #_
   ~\_  ####_        Amazon Linux 2
  ~~  \_#####\
  ~~     \###|       AL2 End of Life is 2026-06-30.
  ~~       \#/ ___
   ~~       V~' '->
    ~~~         /    A newer version of Amazon Linux is available!
      ~~._.   _/
         _/ _/       Amazon Linux 2023, GA and supported until 2028-03-15.
       _/m/'           https://aws.amazon.com/linux/amazon-linux-2023/

```
```bash
# Ping to google fails as no NAT GW configured
[ec2-user@ip-10-20-2-182 ~]$  ping www.google.com -c 3
PING www.google.com (142.251.33.68) 56(84) bytes of data.

--- www.google.com ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2038ms
```
```bash
# curl www.google.com does not work (expected)
[ec2-user@ip-10-20-2-182 ~]$ curl google.com
^C
[ec2-user@ip-10-20-2-182 ~]$ exit
logout
Connection to 10.20.2.182 closed.
```
**iv) Setup connection between db subnets of both production network and development network respectively.**  

Test Prod to Dev connection
  
```bash
# ssh to dbcache-prod instance using webserver-prod as jump host
$ ssh -J ec2-user@$PROD_NET_WEBSERVER_IP ec2-user@$PROD_NET_DBCACHESERVER_IP
```
**Example Output**
```bash
Last login: Fri Aug 29 09:50:58 2025 from ip-10-10-1-204.us-west-2.compute.internal
   ,     #_
   ~\_  ####_        Amazon Linux 2
  ~~  \_#####\
  ~~     \###|       AL2 End of Life is 2026-06-30.
  ~~       \#/ ___
   ~~       V~' '->
    ~~~         /    A newer version of Amazon Linux is available!
      ~~._.   _/
         _/ _/       Amazon Linux 2023, GA and supported until 2028-03-15.
       _/m/'           https://aws.amazon.com/linux/amazon-linux-2023/

```
```bash
# from dbcache-prod, ping/ssh to dbserver-dev instance
```bash
[ec2-user@ip-10-10-4-50 ~]$ ping 10.20.2.182 -c 3
PING 10.20.2.182 (10.20.2.182) 56(84) bytes of data.
64 bytes from 10.20.2.182: icmp_seq=1 ttl=255 time=0.915 ms
64 bytes from 10.20.2.182: icmp_seq=2 ttl=255 time=0.981 ms
64 bytes from 10.20.2.182: icmp_seq=3 ttl=255 time=0.946 ms

--- 10.20.2.182 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2022ms
rtt min/avg/max/mdev = 0.915/0.947/0.981/0.036 ms
[ec2-user@ip-10-10-4-50 ~]$ exit
logout
Connection to 10.10.4.50 closed.
```

Test Prod Dev to connection
```bash
# ssh to db-prod instance using webserver-prod as jump host
$ ssh -J ec2-user@$PROD_NET_WEBSERVER_IP ec2-user@$PROD_NET_DBSERVER_IP
```
**Example Output**
```bash
The authenticity of host '10.10.5.101 (<no hostip for proxy command>)' can't be established.
ED25519 key fingerprint is SHA256:CA28ijjPkYyjgSJ8Zre3Cr+mD5R33u/JoNvkjQzSGqs.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.5.101' (ED25519) to the list of known hosts.
   ,     #_
   ~\_  ####_        Amazon Linux 2
  ~~  \_#####\
  ~~     \###|       AL2 End of Life is 2026-06-30.
  ~~       \#/ ___
   ~~       V~' '->
    ~~~         /    A newer version of Amazon Linux is available!
      ~~._.   _/
         _/ _/       Amazon Linux 2023, GA and supported until 2028-03-15.
       _/m/'           https://aws.amazon.com/linux/amazon-linux-2023/
```
```bash
# from db-prod, ping/ssh to dbserver-dev instance
[ec2-user@ip-10-10-5-101 ~]$ ping -c 3 10.20.2.182
PING 10.20.2.182 (10.20.2.182) 56(84) bytes of data.
64 bytes from 10.20.2.182: icmp_seq=1 ttl=255 time=2.35 ms
64 bytes from 10.20.2.182: icmp_seq=2 ttl=255 time=1.04 ms
64 bytes from 10.20.2.182: icmp_seq=3 ttl=255 time=0.800 ms

--- 10.20.2.182 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 0.800/1.400/2.355/0.683 ms
[ec2-user@ip-10-10-5-101 ~]$ exit
logout
Connection to 10.10.5.101 closed.
```
```bash
# ssh to db-dev instance using webserver-dev as jump host
$ ssh -J ec2-user@$DEV_NET_WEBSERVER_IP ec2-user@$DEV_NET_DBSERVER_IP
```
```bash
# from db-dev, ping/ssh to dbcache-prod instance
[ec2-user@ip-10-20-2-182 ~]$ ping -c 3 10.10.4.50
PING 10.10.4.50 (10.10.4.50) 56(84) bytes of data.
64 bytes from 10.10.4.50: icmp_seq=1 ttl=255 time=0.917 ms
64 bytes from 10.10.4.50: icmp_seq=2 ttl=255 time=0.979 ms
64 bytes from 10.10.4.50: icmp_seq=3 ttl=255 time=0.968 ms

--- 10.10.4.50 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 0.917/0.954/0.979/0.044 ms
```
```bash
# from db-dev, ping/ssh to db-prod instance
[ec2-user@ip-10-20-2-182 ~]$ ping -c 3 10.10.5.101
PING 10.10.5.101 (10.10.5.101) 56(84) bytes of data.
64 bytes from 10.10.5.101: icmp_seq=1 ttl=255 time=0.801 ms
64 bytes from 10.10.5.101: icmp_seq=2 ttl=255 time=0.912 ms
64 bytes from 10.10.5.101: icmp_seq=3 ttl=255 time=1.05 ms

--- 10.10.5.101 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2010ms
rtt min/avg/max/mdev = 0.801/0.922/1.054/0.106 ms
[ec2-user@ip-10-20-2-182 ~]$ exit
logout
Connection to 10.20.2.182 closed.
```

## 8. Cleanup


```bash
# Terminate Instances in Production and Devlopment Network
python3 ec2instance.py --action terminate --terminate-names \
  $PROD_NET_WEBSERVER_INSTANCE_NAME \
  $PROD_NET_APP1SERVER_INSTANCE_NAME \
  $PROD_NET_DBCACHESERVER_INSTANCE_NAME \
  $PROD_NET_APP2SERVER_INSTANCE_NAME \
  $PROD_NET_DBSERVER_INSTANCE_NAME \
  $DEV_NET_WEBSERVER_INSTANCE_NAME \
  $DEV_NET_DBSERVER_INSTANCE_NAME \
  --resource-file $EC2_RESOURCES_STORE_FILE
```
**Example Output**
```bash
Terminating instance i-0dacfc74b8f161150
Instance i-0dacfc74b8f161150 terminated
Terminating instance i-03d3ce3d9bb517870
Instance i-03d3ce3d9bb517870 terminated
Terminating instance i-025530d868f300722
Instance i-025530d868f300722 terminated
Terminating instance i-0b61ad56fbf3b7e56
Instance i-0b61ad56fbf3b7e56 terminated
Terminating instance i-063208bd70e1c875c
Instance i-063208bd70e1c875c terminated
Terminating instance i-0538b233d00a200a7
Instance i-0538b233d00a200a7 terminated
Terminating instance i-0931773ba62654ffa
Instance i-0931773ba62654ffa terminated
```
### Delete Security Groups
```bash
$ python3 securitygroups.py --action delete --prod-vpc-id $PNET_VPC_ID --dev-vpc-id $DNET_VPC_ID --resource-file $SG_RESOURCES_STORE_FILE
```
**Example Output**
```bash
Revoked SG references from sg-0b21e0edcacc04bad
Revoked SG references from sg-0258ea6e48303c30b
Deleted production security group prod_web_sg_id with ID sg-02ba028566e5b4f44
Deleted production security group prod_dbcache_app1_sg_id with ID sg-0b21e0edcacc04bad
Deleted production security group prod_dbcache_db_sg_id with ID sg-0a55d42a94bcb2155
Deleted production security group prod_app2_sg_id with ID sg-0258ea6e48303c30b
Revoked SG references from sg-0a5746e4fbe0f5435
Deleted development security group dev_web_sg_id with ID sg-01924026995d45ad3
Deleted development security group dev_db_sg_id with ID sg-0a5746e4fbe0f5435
```

### Delete Key Pair
```bash
$ python3 keypair.py --action delete --key-name ${KEYPAIR} --key-file $KEYPAIR_PEM_FILE --resource-file $KEYPAIR_RESOURCES_STORE_FILE
```
**Example Output**
```bash
Deleted key pair: MyKeyPair
Deleted local key file: MyKeyPair.pem
```
### Delete VPC peering
```bash
$ python3 vpc.py --action delete-peer --resource-file $VPC_RESOURCES_STORE_FILE
```
**Example Output**
```bash
Deleted route to 10.20.0.0/16 from route table rtb-098dffe9d9176e376
Deleted route to 10.20.0.0/16 from route table rtb-09b1271b4ffa14c0d
Deleted route to 10.10.0.0/16 from route table rtb-0fe0180e91db77465
Deleted VPC peering
```

### Delete VPC
```bash
$ python3 vpc.py --action delete-vpc --network prod --resource-file $VPC_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Deleting NAT Gateway: nat-0eab8642ebe753bf1
Releasing Elastic IP: eipalloc-03fb11cc6a9eb2d7a
Disassociating route table rtb-080da1a4e8250c02a association rtbassoc-009172ccf790669b5
Deleting route table rtb-080da1a4e8250c02a
Disassociating route table rtb-072e0e8e58b28727a association rtbassoc-0b5f887d0ce3d1272
Deleting route table rtb-072e0e8e58b28727a
Disassociating route table rtb-0979a49a3614db48a association rtbassoc-011ca9324eff8a49d
Deleting route table rtb-0979a49a3614db48a
Disassociating route table rtb-098dffe9d9176e376 association rtbassoc-068e5efac56d0cf66
Deleting route table rtb-098dffe9d9176e376
Disassociating route table rtb-09b1271b4ffa14c0d association rtbassoc-0d061a178204f4c9b
Deleting route table rtb-09b1271b4ffa14c0d
Deleted subnet subnet-080d8a41a4d3a6710
Deleted subnet subnet-09b57bb14226ee4fa
Deleted subnet subnet-02b890faf53f56987
Deleted subnet subnet-0a1ea33470bc08827
Deleted subnet subnet-036eca3812b3e0f7c
Detached IGW igw-04563d290b76f697d from VPC vpc-09bf4173a6e995da7
Deleted IGW igw-04563d290b76f697d
Deleted VPC vpc-09bf4173a6e995da7
```
```bash
$ python3 vpc.py --action delete-vpc --network dev --resource-file $VPC_RESOURCES_STORE_FILE
```
**Example Output:**
```bash
Disassociating route table rtb-0fe0180e91db77465 association rtbassoc-01ecb01cb30266df9
Deleting route table rtb-0fe0180e91db77465
Disassociating route table rtb-00f958831657a1ff1 association rtbassoc-04f574f8538dc2113
Deleting route table rtb-00f958831657a1ff1
Deleted subnet subnet-045b969f3e578de3c
Deleted subnet subnet-0682b5d394a3d13df
Detached IGW igw-059c7d88ec647d53c from VPC vpc-0f7bf0210131834ff
Deleted IGW igw-059c7d88ec647d53c
Deleted VPC vpc-0f7bf0210131834ff
```
```bash
# remove local copy of resource files
$ rm -rf *.json
```