# AWS VPC + EC2 Infra Setup with Python & AWS CLI

This guide demonstrates how to provision a **VPC**, subnets, security groups, key pairs, EC2 instances, and networking components using Python scripts & AWS CLI.

It also covers how to connect to private EC2 instances using a jump server and finally how to clean up resources.

---

## 1. Set AWS Region
```bash
export AWS_DEFAULT_REGION=us-west-2
```

---

## 2. Create VPC and Networking Components
```bash
python3 vpc.py --action create
```

**Resources Created:**
- VPC  
- Internet Gateway (IGW)  
- Public and Private Subnets  
- Elastic IP & NAT Gateway  
- Route Tables (public & private)  

**Example Output:**
```bash
Created VPC m04Vpc with ID vpc-0fa2ddcb6e7185d9f
Created and attached IGW igw-060dff40b26cf0129
Created subnet app1 (subnet-0858669c9d938f179)
Created subnet web (subnet-04575024b41feb5a8)
Allocated Elastic IP: eipalloc-03591c16488c55c57
NAT Gateway nat-0cb5dbd934e44e779 is now available
Route tables created and associated with subnets
```

**Export resource IDs:**
```bash
export VPC_ID="vpc-099a608cd399058eb"
export PRIVATE_SUBNET_ID="subnet-0be101e665f49932e"
export PUBLIC_SUBNET_ID="subnet-0ffbb62fee115a5b5"
```

---

## 3. Create Security Groups
```bash
python3 securitygroups.py --vpc-id $VPC_ID --action create
```

**Output:**
```bash
Created security group PublicSG -> sg-0a0501bdd00176b4a
Created security group PrivateSG -> sg-0bd3f74905ab883d1
```

**Export variables:**
```bash
export PUBLIC_SG="sg-0a0501bdd00176b4a"
export PRIVATE_SG="sg-0bd3f74905ab883d1"
```

---

## 4. Generate SSH Key Pair
```bash
python keypair.py --action create
```

**Result:**
- Key pair created  MyKeyPair (private key saved as `MyKeyPair.pem`)

```bash
export KEYPAIR="MyKeyPair"
```

---

## 5. Launch EC2 Instances

### Webserver (Public Subnet)
```bash
export WEBSERVER_INSTANCE_NAME="webserver"
python ec2instance.py --action create     --subnet-id $PUBLIC_SUBNET_ID     --sg-ids $PUBLIC_SG     --key-name $KEYPAIR     --instance-names $WEBSERVER_INSTANCE_NAME     --associate-public-ip
export WEBSERVER_INSTANCE_ID="i-02e7b28cb43dc0a52"
```

### App1 Server (Private Subnet)
```bash
export APP1SERVER_INSTANCE_NAME="app1server"
python ec2instance.py --action create     --subnet-id $PRIVATE_SUBNET_ID     --sg-ids $PRIVATE_SG     --key-name $KEYPAIR     --instance-names $APP1SERVER_INSTANCE_NAME
export APP1SERVER_INSTANCE_ID="i-06d79acf3095b6e1e"
```

### DBCache Server (Private Subnet)
```bash
export DBCACHESERVER_INSTANCE_NAME="dbcacheserver"
python ec2instance.py --action create     --subnet-id $PRIVATE_SUBNET_ID     --sg-ids $PRIVATE_SG     --key-name $KEYPAIR     --instance-names $DBCACHESERVER_INSTANCE_NAME
export DBCACHESERVER_INSTANCE_ID="i-0f843bc3435c5819e"
```

### App2 Server (Private Subnet)
```bash
export APP2SERVER_INSTANCE_NAME="app2server"
python ec2instance.py --action create     --subnet-id $PRIVATE_SUBNET_ID     --sg-ids $PRIVATE_SG     --key-name $KEYPAIR     --instance-names $APP2SERVER_INSTANCE_NAME
export APP2SERVER_INSTANCE_ID="i-0f7566c0b5d7cee04"
```

### Database Server (Private Subnet)
```bash
export DBSERVER_INSTANCE_NAME="dbserver"
python ec2instance.py --action create     --subnet-id $PRIVATE_SUBNET_ID     --sg-ids $PRIVATE_SG     --key-name $KEYPAIR     --instance-names $DBSERVER_INSTANCE_NAME
export DBSERVER_INSTANCE_ID="i-01e21a918bad2d466"
```

---

## 6. Fetch Instance IPs
```bash
# Webserver (public IP)
WEBSERVER_IP=$(aws ec2 describe-instances --instance-ids ${WEBSERVER_INSTANCE_ID}    --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
echo $WEBSERVER_IP

# App1, Cache, App2, DB private IPs
APP1SERVER_IP=$(aws ec2 describe-instances --instance-ids $APP1SERVER_INSTANCE_ID    --query "Reservations[0].Instances[0].PrivateIpAddress" --output text)
```

---

## 7. SSH Access

Start SSH agent and add key:
```bash
eval "$(ssh-agent -s)"
ssh-add MyKeyPair.pem
ssh-add -l
```

Connect to **App1 Server** via Webserver Jump Host:
```bash
ssh -J ec2-user@$WEBSERVER_IP ec2-user@$APP1SERVER_IP
Last login: Tue Aug 26 17:21:36 2025 from ip-10-10-1-88.us-west-2.compute.internal
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


[ec2-user@ip-10-10-2-177 ~]$

```

---

## 8. Verify Networking
Inside App1 server:
```bash
[ec2-user@ip-10-10-2-177 ~]$ ping www.google.com -c 3
PING www.google.com (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp_seq=3 ttl=116 time=8.00 ms

--- www.google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms
[ec2-user@ip-10-10-2-177 ~]

[ec2-user@ip-10-10-2-177 ~]$ ping -c 3 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=6.76 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=116 time=6.24 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=116 time=6.22 ms


[ec2-user@ip-10-10-2-177 ~]$ curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
[ec2-user@ip-10-10-2-177 ~]$ exit

```

---

## 9. List Running Instances
```bash
aws ec2 describe-instances   --filters "Name=instance-state-name,Values=running"   --query "Reservations[*].Instances[*].{InstanceId:InstanceId,InstanceType:InstanceType,Name:Tags[?Key=='Name'].Value|[0],PublicIp:PublicIpAddress,PrivateIp:PrivateIpAddress,SubnetId:SubnetId}"   --output table
```

---

## 10. Cleanup

### Terminate Instances
```bash
python ec2instance.py --action terminate --terminate-names $WEBSERVER_INSTANCE_NAME
python ec2instance.py --action terminate --terminate-names $APP1SERVER_INSTANCE_NAME
python ec2instance.py --action terminate --terminate-names $DBCACHESERVER_INSTANCE_NAME
python ec2instance.py --action terminate --terminate-names $APP2SERVER_INSTANCE_NAME
python ec2instance.py --action terminate --terminate-names $DBSERVER_INSTANCE_NAME
```

### Delete Security Groups
```bash
python3 securitygroups.py --vpc-id ${VPC_ID} --action delete     --private-sg-id $PRIVATE_SG     --public-sg-id $PUBLIC_SG
```

### Delete Key Pair
```bash
python keypair.py --action delete --key-name ${KEYPAIR} --key-file MyKeyPair.pem
```

### Delete VPC
```bash
python vpc.py --action delete
```

---

## [32m[1m✅ Summary[0m
This workflow provisions:
- VPC with public and private subnets  
- Security groups  
- EC2 instances (web, apps, db, cache)  
- NAT Gateway and Internet Gateway  

It also demonstrates **SSH access to private instances via a jump host** and cleans up resources after use.

---
