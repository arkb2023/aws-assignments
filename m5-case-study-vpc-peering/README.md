# Module 5 VPC 
Problem Statement:
You work for XYZ Corporation and based on the expansion requirements of your corporation you have been asked to create and set up a distinct Amazon VPC for the production and development team. You are expected to perform the following tasks for the respective VPCs.

Production Network:
1. Design and build a 4-tier architecture.
2. Create 5 subnets out of which 4 should be private named app1, app2, dbcache and db and one should be public, named web.
3. Launch instances in all subnets and name them as per the subnet that they have been launched in.
4. Allow dbcache instance and app1 subnet to send internet requests.
5. Manage security groups and NACLs

Development Network:
1. Design and build 2-tier architecture with two subnets named web and db and launch instances in both subnets and name them as per the subnet names.
2. Make sure only the web subnet can send internet requests.
3. Create peering connection between production network and development network.
4. Setup connection between db subnets of both production network and development network respectively.


Approach:
1) Production Network VPC
    CIDR=10.10.0.0/16 
    CIDR=10.10.1.0/24 => web (public subnet)
    CIDR=10.10.2.0/24 => app1 (private subnet)
    CIDR=10.10.3.0/24 => app2 (private subnet)
    CIDR=10.10.4.0/24 => dbcache (private subnet)
    CIDR=10.10.5.0/24 => db (private subnet)

    Create VPC
    Create IGW
    Create private subnet for app1
    Create private subnet for app2
    Create private subnet for dbcache
    Create private subnet for db
    Create public subnet for web
    Allocate elastic IP
    Create NAT gateway
    Create route table for app1 subnet, add default route with target as NAT GW
    Create route table for app2 subnet
    Create route table for dbcache subnet, add default route with target as NAT GW
    Create route table for db subnet
    Create route table for web subnet, add default route with target as IGW
    Create Security Group for webserver EC2 instance - TBD
        inbound ssh traffic allow from any
        inbound http traffic allow from any
        inbound ICMP traffic allow from any
    Create Security Group for dbcache and app1 EC2 instances - TBD
        inbound ssh traffic allow from any Prodcution network CIDR and associate webserver security group
        inbound http traffic allow from any Prodcution network CIDR and associate webserver security group
        inbound ping traffic allow from any Prodcution network CIDR and associate webserver security group        
    Create Security Group for dbcache and db EC2 instance - TBD
        inbound ssh traffic allow from Development Network DB CIDR
        inbound ICMP traffic allow from Development Network DB CIDR
    Create Security Group for app2 EC2 instances - TBD
        inbound ping traffic allow from webserver security group
    NACL - default allow

2) Development network VPC
    CIDR=10.20.0.0/16
    CIDR=10.20.1.0/24 => web (public subnet)
    CIDR=10.20.2.0/24 => db (private subnet)

    Create VPC
    Create IGW
    Create private subnet for db
    Create public subnet for web
    Create route table for db subnet
    Create route table for web subnet, add default route with target as IGW
    Create Security Group for webserver EC2 instance - TBD
        inbound ssh traffic allow from any
        inbound http traffic allow from any
        inbound ping traffic allow from any
    Create Security Group for db EC2 instance - TBD
        inbound ssh traffic allow from Production Network DB CIDR
        inbound ICMP traffic allow from Production Network DB CIDR

3) VPC peering
    Create VPC peering between Production network & Development network
    Add to/fro routes in route tables:
    Production network
      Add route in dbcache subnet route table with, destination as development network CIDR and target as peering id
      Add route in db subnet route table with, destination as development network CIDR and target as peering id
    Development network
      Add route in db subnet route table with, destination as production network CIDR and target as peering id

4) Launch EC2 instances 
    a) Production network
        i) Launch webserver-prod instance in web subnet and associate security group for webserver
        ii) Launch app1server instance in app1 subnet and associate security group for app1 
        iii) Launch app2server instance in app2 subnet and associate security group for app2
        iv) Launch dbcacheserver instance in dbcache subnet and associate security group for dbcache
        v) Launch dbserver instance in db-prod subnet and associate security group for db
    b) Development network
        i) Launch webserver-dev instance in webserver-dev subnet and associate security group for webserver
        ii) Launch dbserver-dev instance in db-dev subnet and associate security group for app1 

6) Test the network
    i) Test internet access for dbcache instance
       - ssh to dbcache-prod instance using webserver-dev as jump host
       - check if ping www.google.com works
       - check if curl www.google.com works
    ii) Test internet access for app1 instance
       - check if ssh to app1 instance using webserver as jump host
       - check if ping www.google.com works
       - check if curl www.google.com works
    iii) Make sure only the web subnet can send internet requests
       - ssh to webserver-dev instance
       - check if ping www.google.com works
       - check if curl www.google.com works
       - ssh to dbserver-dev instance using webserver-dev as jump host
       - check if ping www.google.com does not work (expected)
       - curl www.google.com does not work (expected)
    iv) Setup connection between db subnets of both production network and development network respectively.
        Test Prod to Dev connection
       - ssh to dbcache-prod instance using webserver-prod as jump host
       - from dbcache-prod, ping/ssh to dbserver-dev instance
       Test reverse Dev to Prod connection
       - ssh to db-prod instance using webserver-prod as jump host
       - from db-prod, ping/ssh to dbserver-dev instance
       - ssh to db-dev instance using webserver-dev as jump host
       - from db-dev, ping/ssh to dbcache-prod instance
       - from db-dev, ping/ssh to db-prod instance


Execution Details:
---

## Set AWS Region
```bash
export AWS_DEFAULT_REGION=us-west-2 # Oregon, for sandbox/testing
```

---
## Create VPC and Networking Components

**Create Production Network VPC**
```bash
python3 vpc.py --action create --network prod --resource-file "vpc_resources.json"
```
**Example Output:**
```bash
cat vpc_resources.json
<<TBD>>
```
**Export resource IDs:**
```bash
export PROD_NET_VPC_ID="vpc-0344aa02d0290721b"
export PROD_NET_PRIVATE_SUBNET_ID="subnet-090ee50b8d601a058"
export PROD_NET_PUBLIC_SUBNET_ID="subnet-0d7c597baded0a718"
```

**Create Development Network VPC**
```bash
python3 vpc.py --action create --network dev --resource-file "vpc_resources.json"
```
**Example Output:**
```bash
cat vpc_resources.json
<<TBD>>
```
**Export resource IDs:**
```bash
export DEV_NET_VPC_ID="vpc-0c5a76ffecf6356e2"
export DEV_NET_PRIVATE_SUBNET_ID="subnet-0da2e972445dde6ff"
export DEV_NET_PUBLIC_SUBNET_ID="subnet-0a5a12c7fa979c7c2"
```

**Create VPC peering between Production and Development Networks**
```bash
$ python3 vpc.py --action peer --prod-vpc-id $PROD_NET_VPC_ID --dev-vpc-id $DEV_NET_VPC_ID --resource-file "vpc_resources.json"
```
**Example Output:**
```bash
cat vpc_resources.json
<<TBD>>
```

---
## 3 Create Security Groups
```bash
$ python3 securitygroups.py --action create --prod-vpc-id $PROD_NET_VPC_ID --dev-vpc-id $DEV_NET_VPC_ID --resource-file sg_resources.json
```

****Example Output:**
```bash
Created security group Prod-Webserver-SG with ID sg-0dae050adef4996fd
Ingress rules set for Prod-Webserver-SG
Created security group Prod-Dbcache-App1-SG with ID sg-0ecddf4dd4e5b7830
Ingress rules set for Prod-Dbcache-App1-SG
Created security group Prod-Dbcache-DB-SG with ID sg-0a489955e060c0a45
Ingress rules set for Prod-Dbcache-DB-SG
Created security group Prod-App2-SG with ID sg-0ebf5948452b9f459
Ingress rules set for Prod-App2-SG
Created security group Dev-Webserver-SG with ID sg-02894f4027c95e918
Ingress rules set for Dev-Webserver-SG
Created security group Dev-DB-SG with ID sg-09b4281e37d17dccf
Ingress rules set for Dev-DB-SG
Saved security group IDs to sg_resources.json
```
```bash
$ cat sg_resources.json
{
  "prod_web_sg_id": "sg-0dae050adef4996fd",
  "prod_dbcache_app1_sg_id": "sg-0ecddf4dd4e5b7830",
  "prod_dbcache_db_sg_id": "sg-0a489955e060c0a45",
  "prod_app2_sg_id": "sg-0ebf5948452b9f459",
  "dev_web_sg_id": "sg-02894f4027c95e918",
  "dev_db_sg_id": "sg-09b4281e37d17dccf"
}$
```
**Export variables:**
```bash
export PROD_WEB_SG_ID="sg-0dae050adef4996fd"
export PROD_DBCACHE_APP1_SG_ID="sg-0ecddf4dd4e5b7830"
export PROD_DBCACHE_DB_SG_ID="sg-0a489955e060c0a45"
export PROD_APP2_SG_ID="sg-0ebf5948452b9f459"
export DEV_WEB_SG_ID="sg-02894f4027c95e918"
export DEV_DB_SG_ID="sg-09b4281e37d17dccf"
```

---
## 4. Generate SSH Key Pair
```bash
python keypair.py --action create --resource-file "keypair_resources.json"
```
```bash
$ cat keypair_resources.json
<<TBD>>
```
**Export variables:**
```bash
export KEYPAIR="MyKeyPair"
```
# Start the SSH agent:
$ eval "$(ssh-agent -s)"
Agent pid 12345

# Add private key
$ ssh-add MyKeyPair.pem
Identity added: MyKeyPair.pem (MyKeyPair.pem)

# Verify the key was added
$ ssh-add -l
2048 SHA256:3dM/d0pmvuwAoNTRVRYbAgdRaPRMhm/eIj3X2eQlNYI MyKeyPair.pem (RSA)

## 5.a Launch EC2 Instances in Production Network

### Webserver (Public Subnet)
```bash
export PROD_NET_WEBSERVER_INSTANCE_NAME="prod-net-webserver"
python ec2instance.py --action create     --subnet-id $PROD_NET_PUBLIC_SUBNET_ID     --sg-ids $PROD_WEB_SG_ID     --key-name $KEYPAIR     --instance-names $PROD_NET_WEBSERVER_INSTANCE_NAME     --associate-public-ip
export PROD_NET_WEBSERVER_INSTANCE_ID="i-0c17eac8724fbacc9"
```

### App1 Server (Private Subnet)
```bash
export PROD_NET_APP1SERVER_INSTANCE_NAME="prod-net-app1server"
python ec2instance.py --action create \
  --subnet-id $PROD_NET_PRIVATE_SUBNET_ID \
  --sg-ids $PROD_DBCACHE_APP1_SG_ID  $PROD_DBCACHE_DB_SG_ID \
  --key-name $KEYPAIR \
  --instance-names $PROD_NET_APP1SERVER_INSTANCE_NAME
export PROD_NET_APP1SERVER_INSTANCE_ID="i-087c2afe42c6f403f"
```

### DBCache Server (Private Subnet)
```bash
export PROD_NET_DBCACHESERVER_INSTANCE_NAME="prod-net-dbcacheserver"
python ec2instance.py --action create     --subnet-id $PROD_NET_PRIVATE_SUBNET_ID     --sg-ids $PROD_DBCACHE_APP1_SG_ID   $PROD_DBCACHE_DB_SG_ID  --key-name $KEYPAIR     --instance-names $PROD_NET_DBCACHESERVER_INSTANCE_NAME
export PROD_NET_DBCACHESERVER_INSTANCE_ID="i-0f843bc3435c5819e"
```

### App2 Server (Private Subnet)
```bash
export PROD_NET_APP2SERVER_INSTANCE_NAME="prod-net-app2server"
python ec2instance.py --action create     --subnet-id $PROD_NET_PRIVATE_SUBNET_ID     --sg-ids $PROD_APP2_SG_ID     --key-name $KEYPAIR     --instance-names $PROD_NET_APP2SERVER_INSTANCE_NAME
export PROD_NET_APP2SERVER_INSTANCE_ID="i-0f7566c0b5d7cee04"
```

### Database Server (Private Subnet)
```bash
export PROD_NET_DBSERVER_INSTANCE_NAME="prod-net-dbserver"
python ec2instance.py --action create     --subnet-id $PROD_NET_PRIVATE_SUBNET_ID     --sg-ids $PROD_DBCACHE_DB_SG_ID     --key-name $KEYPAIR     --instance-names $PROD_NET_DBSERVER_INSTANCE_NAME
export PROD_NET_DBSERVER_INSTANCE_ID="i-01e21a918bad2d466"
```

## 5.b Launch EC2 Instances in Development Network

### Webserver (Public Subnet)
```bash
export DEV_NET_WEBSERVER_INSTANCE_NAME="dev-net-webserver"
$ python ec2instance.py --action create     --subnet-id $DEV_NET_PUBLIC_SUBNET_ID     --sg-ids $DEV_WEB_SG_ID     --key-name $KEYPAIR     --instance-names $DEV_NET_WEBSERVER_INSTANCE_NAME     --associate-public-ip
Created instance dev-net-webserver with ID: i-0ab5a58f75a6dbb7c
export DEV_NET_WEBSERVER_INSTANCE_ID="i-0abb670ebbaba546b"
```

### App1 Server (Private Subnet)
```bash
export DEV_NET_DBSERVER_INSTANCE_NAME="dev-net-dbserver"
$ python3 ec2instance.py --action create     --subnet-id $DEV_NET_PRIVATE_SUBNET_ID     --sg-ids $DEV_DB_SG_ID    --key-name $KEYPAIR     --instance-names $DEV_NET_DBSERVER_INSTANCE_NAME
Created instance dev-net-dbserver with ID: i-0be18fb0ce893e1b2
export DEV_NET_DBSERVER_INSTANCE_ID="i-0b36bc7b0d20a7757"
```

---
## 6. Fetch the Instance details
```bash
$ aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query "Reservations[*].Instances[*].{InstanceId:InstanceId,InstanceState:State.Name,InstanceType:InstanceType,Name:Tags[?Key=='Name'].Value|[0],PublicIp:PublicIpAddress,PrivateIp:PrivateIpAddress,SubnetId:SubnetId}" \
    --output table
```
****Example Output:**
```bash
<<TBD>>
```
**Export resource IDs:**
```bash
$ export PROD_NET_WEBSERVER_IP=<<TBD>>
$ export PROD_NET_APP1SERVER_IP=<<TBD>>
$ export PROD_NET_APP2SERVER_IP=<<TBD>>
$ export PROD_NET_DBCACHESERVER_IP=<<TBD>>
$ export PROD_NET_DBSERVER_IP=<<TBD>>
$ export DEV_NET_WEBSERVER_IP=<<TBD>>
$ export DEV_NET_DBSERVER_IP=<<TBD>>
```
---

## 7. Test the network

**Start SSH agent and add key**
```bash
$ eval "$(ssh-agent -s)"
Agent pid 14525
$ ssh-add MyKeyPair.pem
Identity added: MyKeyPair.pem (MyKeyPair.pem)
$ ssh-add -l
2048 SHA256:PYkbdX6VwErNy4MWr3V7FKPjJkc7CTrMjQIjs/nZyvY MyKeyPair.pem (RSA)
```

**i) Test internet access for dbcache instance**
```bash
$ ssh -J ec2-user@$PROD_NET_WEBSERVER_IP ec2-user@$PROD_NET_DBCACHESERVER_IP
```
** Inside dbcache instance **
```bash
[ec2-user@ip-10-10-2-177 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=116 time=8.00 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms

[ec2-user@ip-10-10-2-177 ~]$ curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>

# Ping to DB server of Development network works due to VPC peering
[ec2-user@ip-10-10-2-237 ~]$ ping 10.20.2.152 -c 3
PING 10.20.2.152 (10.20.2.152) 56(84) bytes of data.
64 bytes from 10.20.2.152: icmp_seq=1 ttl=255 time=1.27 ms
64 bytes from 10.20.2.152: icmp_seq=2 ttl=255 time=0.957 ms
64 bytes from 10.20.2.152: icmp_seq=3 ttl=255 time=0.910 ms

--- 10.20.2.152 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 0.910/1.046/1.273/0.165 ms

```
**ii) Test internet access for app1 instance**
```bash
$ ssh -J ec2-user@$PROD_NET_WEBSERVER_IP ec2-user@$PROD_NET_APP1SERVER_IP
```
** Inside app1 instance **
```bash
[ec2-user@ip-10-10-2-177 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=116 time=8.00 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms

[ec2-user@ip-10-10-2-177 ~]$ curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>

```

**iii) Make sure only the web subnet can send internet requests**

```bash
$ ssh -J ec2-user@$DEV_NET_WEBSERVER_IP
```
** Inside app1 instance **
```bash
[ec2-user@ip-10-10-2-177 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=116 time=8.00 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms

[ec2-user@ip-10-10-2-177 ~]$ curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
```
# ssh to dbserver-dev instance using webserver-dev as jump host
```bash
$ ssh -J ec2-user@$DEV_NET_WEBSERVER_IP ec2-user@$DEV_NET_DBSERVER_IP
```
** Inside db instance **
# check if ping www.google.com does not work (expected)
```bash
# Ping to google fails as no NAT GW configured
[ec2-user@ip-10-20-2-152 ~]$ ping www.google.com -c 3
PING www.google.com (142.251.33.68) 56(84) bytes of data.

--- www.google.com ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2055ms

[ec2-user@ip-10-20-2-152 ~]$

# curl www.google.com does not work (expected)
[ec2-user@ip-10-20-2-152 ~]$  curl google.com
^C
[ec2-user@ip-10-20-2-152 ~]$ ^C
```
**iv) Setup connection between db subnets of both production network and development network respectively.**
Test Prod to Dev connection
- ssh to dbcache-prod instance using webserver-prod as jump host
```bash
$ ssh -J ec2-user@$PROD_NET_WEBSERVER_IP ec2-user@$PROD_NET_DBCACHESERVER_IP
```
** Inside dbcache instance **
- from dbcache-prod, ping/ssh to dbserver-dev instance
```bash
[ec2-user@ip-10-10-2-177 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=116 time=8.00 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms
```

Test reverse Dev to Prod connection
- ssh to db-prod instance using webserver-prod as jump host
```bash
$ ssh -J ec2-user@$PROD_NET_WEBSERVER_IP ec2-user@$PROD_NET_DBSERVER_IP
```
** Inside db instance **
- from db-prod, ping/ssh to dbserver-dev instance
```bash
[ec2-user@ip-10-10-2-177 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=116 time=8.00 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms
```
- ssh to db-dev instance using webserver-dev as jump host
```bash
$ ssh -J ec2-user@$DEV_NET_WEBSERVER_IP ec2-user@$DEV_NET_DBSERVER_IP
```
** Inside db instance **
- from db-dev, ping/ssh to dbcache-prod instance
```bash
[ec2-user@ip-10-10-2-177 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=116 time=8.00 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms
```
- from db-dev, ping/ssh to db-prod instance
```bash
[ec2-user@ip-10-10-2-177 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=116 time=8.00 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms
```

## 8. Cleanup

### Terminate Instances in Production Network
```bash
python3 ec2instance.py --action terminate --terminate-names \
  $PROD_NET_WEBSERVER_INSTANCE_NAME  \
  $PROD_NET_APP1SERVER_INSTANCE_NAME \
  $PROD_NET_DBCACHESERVER_INSTANCE_NAME \
  $PROD_NET_APP2SERVER_INSTANCE_NAME \
  $PROD_NET_DBSERVER_INSTANCE_NAME \
  $DEV_NET_WEBSERVER_INSTANCE_NAME \
  $DEV_NET_DBSERVER_INSTANCE_NAME
```
### Delete Security Groups
```bash
$ python3 securitygroups.py --action delete --prod-vpc-id $PROD_NET_VPC_ID --dev-vpc-id $DEV_NET_VPC_ID --resource-file sg_resources.json
```

### Delete Key Pair
```bash
python keypair.py --action delete --key-name ${KEYPAIR} --key-file MyKeyPair.pem
```

### Delete VPC
```bash
$ python3 vpc.py --action delete --network prod --resource-file "vpc_resources.json"
```
**Example Output:**
```bash
Deleting NAT Gateway: nat-0701b5da2a348198a
Releasing Elastic IP: eipalloc-0ecf45571c30c7095
Disassociating route table rtb-006140a06f17a6901 association rtbassoc-0bcaae38ab48a85ef
Deleting route table rtb-006140a06f17a6901
Disassociating route table rtb-083a4c221296cfc64 association rtbassoc-0d92f2545f053eda7
Deleting route table rtb-083a4c221296cfc64
Deleted subnet subnet-0f3e29e95c3007ca7
Deleted subnet subnet-07b6b61e05869d955
Detached IGW igw-0236760e80279ddeb from VPC vpc-0b6aae0543c464f77
Deleted IGW igw-0236760e80279ddeb
Deleted VPC vpc-0b6aae0543c464f77
```
```bash
$ python3 vpc.py --action delete --network dev --resource-file "vpc_resources.json"
```
**Example Output:**
```bash
Disassociating route table rtb-08c4cb2675d6e39cf association rtbassoc-0b8ece295c5c98bb6
Deleting route table rtb-08c4cb2675d6e39cf
Disassociating route table rtb-0a215f10ad8bf9e9e association rtbassoc-0bffe70dcbbd88c6d
Deleting route table rtb-0a215f10ad8bf9e9e
Deleted subnet subnet-001920cfde75ac77c
Deleted subnet subnet-0c64529b029bb9bd4
Detached IGW igw-0e3042332781c6a64 from VPC vpc-0755a91712ad80b05
Deleted IGW igw-0e3042332781c6a64
Deleted VPC vpc-0755a91712ad80b05
```
