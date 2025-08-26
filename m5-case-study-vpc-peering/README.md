
\$ export AWS\_DEFAULT\_REGION=us-west-2

# VPC create

\$ python3 vpc.py --action create
Created VPC m04Vpc with ID vpc-0fa2ddcb6e7185d9f
Created and attached IGW igw-060dff40b26cf0129 to VPC vpc-0fa2ddcb6e7185d9f
Created subnet app1 with ID subnet-0858669c9d938f179
Created subnet web with ID subnet-04575024b41feb5a8
Allocated Elastic IP: Name: publicWebSubnetNatGW-EIP, AllocationId: eipalloc-03591c16488c55c57
Waiting for NAT Gateway nat-0cb5dbd934e44e779 to become available...
NAT Gateway nat-0cb5dbd934e44e779 is now available
Created route table privateApp1RouteTable with ID rtb-084dff301e7b278d8
Associated route table rtb-084dff301e7b278d8 with subnet subnet-0858669c9d938f179
Created route 0.0.0.0/0 => nat-0cb5dbd934e44e779 in rtb-084dff301e7b278d8
Created route table publicWebRouteTable with ID rtb-006ddb7f0cba98887
Associated route table rtb-006ddb7f0cba98887 with subnet subnet-04575024b41feb5a8
Created route 0.0.0.0/0 => igw-060dff40b26cf0129 in rtb-006ddb7f0cba98887
--- Creation Summary ---
VPC ID: vpc-099a608cd399058eb
IGW ID: igw-03b68d628832f7f74
Private Subnet ID: subnet-0be101e665f49932e
Public Subnet ID: subnet-0ffbb62fee115a5b5
Elastic IP Allocation ID: eipalloc-09333e26c3cf312ce
NAT Gateway ID: nat-002a01425724dd893
Private Route Table ID: rtb-0dee9f631008610a6
Public Route Table ID: rtb-0553d9975c9091553
\$ export VPC\_ID="vpc-099a608cd399058eb"
\$ export PRIVATE\_SUBNET\_ID="subnet-0be101e665f49932e"
\$ export PUBLIC\_SUBNET\_ID="subnet-0ffbb62fee115a5b5"

# Create Security groups for EC2 instances

\$ python3 securitygroups.py --vpc-id \$VPC\_ID --action create
Created security group PublicSG with ID sg-0a0501bdd00176b4a
Created security group PrivateSG with ID sg-0bd3f74905ab883d1
Saved all created resource IDs to sg\_resources.json
\$ export PUBLIC\_SG="sg-0a0501bdd00176b4a"
\$ export PRIVATE\_SG="sg-0bd3f74905ab883d1"

# Generate Key pair

\$ python keypair.py --action create
Created key pair MyKeyPair and saved private key to MyKeyPair.pem
\$ export KEYPAIR="MyKeyPair"

# Create Webserver

\$ export WEBSERVER\_INSTANCE\_NAME="webserver"
\$ python ec2instance.py --action create \\
--subnet-id \$PUBLIC\_SUBNET\_ID \\
--sg-ids \$PUBLIC\_SG \\
--key-name \$KEYPAIR \\
--instance-names \$WEBSERVER\_INSTANCE\_NAME \\
--associate-public-ip
Created instance webserver with ID: i-0313d8b346b9c803b
\$ export WEBSERVER\_INSTANCE\_ID="i-02e7b28cb43dc0a52"

# Create App1server

\$ export APP1SERVER\_INSTANCE\_NAME="app1server"
\$ python ec2instance.py --action create \\
--subnet-id \$PRIVATE\_SUBNET\_ID \\
--sg-ids \$PRIVATE\_SG \\
--key-name \$KEYPAIR \\
--instance-names \$APP1SERVER\_INSTANCE\_NAME
Created instance app1server with ID: i-06d79acf3095b6e1e
\$ export APP1SERVER\_INSTANCE\_ID="i-06d79acf3095b6e1e"

# Create DBcacheserver

\$ export DBCACHESERVER\_INSTANCE\_NAME="dbcacheserver"
\$ python ec2instance.py --action create \\
--subnet-id \$PRIVATE\_SUBNET\_ID \\
--sg-ids \$PRIVATE\_SG \\
--key-name \$KEYPAIR \\
--instance-names \$DBCACHESERVER\_INSTANCE\_NAME
Created instance app1server with ID: i-0f843bc3435c5819e
\$ export DBCACHESERVER\_INSTANCE\_ID="i-0f843bc3435c5819e"

# Create App2server

\$ export APP2SERVER\_INSTANCE\_NAME="app2server"
\$ python ec2instance.py --action create \\
--subnet-id \$PRIVATE\_SUBNET\_ID \\
--sg-ids \$PRIVATE\_SG \\
--key-name \$KEYPAIR \\
--instance-names \$APP2SERVER\_INSTANCE\_NAME
Created instance app2server with ID: i-0f7566c0b5d7cee04
\$ export APP2SERVER\_INSTANCE\_ID="i-0f7566c0b5d7cee04"

# Create DBserver

# --------------------

\$ export DBSERVER\_INSTANCE\_NAME="dbserver"
\$ python ec2instance.py --action create \\
--subnet-id \$PRIVATE\_SUBNET\_ID \\
--sg-ids \$PRIVATE\_SG \\
--key-name \$KEYPAIR \\
--instance-names \$DBSERVER\_INSTANCE\_NAME
Created instance dbserver with ID: i-01e21a918bad2d466
\$ export DBSERVER\_INSTANCE\_ID="i-01e21a918bad2d466"

# get the ip address of webserver

\$ WEBSERVER\_IP=\$(aws ec2 describe-instances --instance-ids \${WEBSERVER\_INSTANCE\_ID} --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
\$ echo \$WEBSERVER\_IP
35.87.120.55

# get the ip address of app1server

\$ APP1SERVER\_IP=\$(aws ec2 describe-instances --instance-ids \$APP1SERVER\_INSTANCE\_ID --query "Reservations[0].Instances[0].PrivateIpAddress" --output text)
\$ echo \$APP1SERVER\_IP
10.10.2.177

# get the ip address of dbcacheserver

\$ DBCACHESERVER\_IP=\$(aws ec2 describe-instances --instance-ids \$DBCACHESERVER\_INSTANCE\_ID --query "Reservations[0].Instances[0].PrivateIpAddress" --output text)
\$ echo \$DBCACHESERVER\_IP
10.10.2.60

# get the ip address of app2server

\$ APP2SERVER\_IP=\$(aws ec2 describe-instances --instance-ids \$APP2SERVER\_INSTANCE\_ID --query "Reservations[0].Instances[0].PrivateIpAddress" --output text)
\$ echo \$APP2SERVER\_IP
10.10.2.21

# get the ip address of dbserver

\$ DBSERVER\_IP=\$(aws ec2 describe-instances --instance-ids \$DBSERVER\_INSTANCE\_ID --query "Reservations[0].Instances[0].PrivateIpAddress" --output text)
\$ echo \$DBSERVER\_IP
10.10.1.88

# Start the SSH agent:

\$ eval "\$(ssh-agent -s)"
Agent pid 12345

# Add private key

\$ ssh-add MyKeyPair.pem
Identity added: MyKeyPair.pem (MyKeyPair.pem)

# Verify the key was added

\$ ssh-add -l
2048 SHA256:3dM/d0pmvuwAoNTRVRYbAgdRaPRMhm/eIj3X2eQlNYI MyKeyPair.pem (RSA)

# Ssh into app1server through Webserver (jumpServer)

\$ ssh -J ec2-user@$WEBSERVER\_IP ec2-user@$APP1SERVER\_IP
Last login: Tue Aug 26 17:21:36 2025 from ip-10-10-1-88.us-west-2.compute.internal
,      \#\_
\~\_  \#\#\#\#\_       Amazon Linux 2
\~\~  \_\#\#\#\#\#\\
\~\~     \\#\#\#|       AL2 End of Life is 2026-06-30.
\~\~      \\#/ \_\_\_
\~\~       V\~' '->
\~\~\~        /      A newer version of Amazon Linux is available!
\~\~.\_. \_/
\_/ \_/       Amazon Linux 2023, GA and supported until 2028-03-15.
\_/m/'           [https://aws.amazon.com/linux/amazon-linux-2023/](https://aws.amazon.com/linux/amazon-linux-2023/)
(reverse-i-search)\`': ^C
[ec2-user@ip-10-10-2-177 \~]\$ ping [www.google.com](https://www.google.com) -c 3
PING [www.google.com](https://www.google.com) (142.250.73.132) 56(84) bytes of data.
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp\_seq=1 ttl=116 time=8.25 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp\_seq=2 ttl=116 time=7.91 ms
64 bytes from pnseaa-ao-in-f4.1e100.net (142.250.73.132): icmp\_seq=3 ttl=116 time=8.00 ms
--- [www.google.com](https://www.google.com) ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 7.919/8.058/8.256/0.161 ms
[ec2-user@ip-10-10-2-177 \~]
[ec2-user@ip-10-10-2-177 \~]\$ ping -c 3 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp\_seq=1 ttl=116 time=6.76 ms
64 bytes from 8.8.8.8: icmp\_seq=2 ttl=116 time=6.24 ms
64 bytes from 8.8.8.8: icmp\_seq=3 ttl=116 time=6.22 ms
--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 6.225/6.410/6.762/0.257 ms
[ec2-user@ip-10-10-2-177 \~]\$
[ec2-user@ip-10-10-2-177 \~]\$ curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
[ec2-user@ip-10-10-2-177 \~]\$ exit
\$ aws ec2 describe-instances \\
--filters "Name=instance-state-name,Values=running" \\
--query "Reservations[\*].Instances[\*].{InstanceId:InstanceId,InstanceType:InstanceType,Name:Tags[?Key=='Name'].Value|[0],PublicIp:PublicIpAddress,PrivateIp:PrivateIpAddress,SubnetId:SubnetId}" \\
--output table
---------------------------------------------------------------------------------------------------------------------
|                                                         DescribeInstances                                           |
+---------------------+---------------+----------------+--------------+----------------+----------------------------+
|     InstanceId      | InstanceType  |      Name      |  PrivateIp   |   PublicIp     |          SubnetId          |
+---------------------+---------------+----------------+--------------+----------------+----------------------------+
|  i-02e7b28cb43dc0a52|  t2.micro     |  webserver     |  10.10.1.88  |  35.87.120.55  |  subnet-0ffbb62fee115a5b5  |
|  i-0d137839739912937|  t2.micro     |  app1server    |  10.10.2.177 |  None          |  subnet-0be101e665f49932e  |
|  i-0f843bc3435c5819e|  t2.micro     |  dbcacheserver |  10.10.2.60  |  None          |  subnet-0be101e665f49932e  |
|  i-0f7566c0b5d7cee04|  t2.micro     |  app2server    |  10.10.2.21  |  None          |  subnet-0be101e665f49932e  |
|  i-01e21a918bad2d466|  t2.micro     |  dbserver      |  10.10.2.28  |  None          |  subnet-0be101e665f49932e  |
+---------------------+---------------+----------------+--------------+----------------+----------------------------+

# clean up

# Terminate instances

\$ python ec2instance.py --action terminate --terminate-names \${WEBSERVER\_INSTANCE\_NAME}
Terminating instance i-02e7b28cb43dc0a52
Instance i-02e7b28cb43dc0a52 terminated
\$ python ec2instance.py --action terminate --terminate-names \${APP1SERVER\_INSTANCE\_NAME}
Terminating instance i-0d137839739912937
Instance i-0d137839739912937 terminated
\$ python ec2instance.py --action terminate --terminate-names \${DBCACHESERVER\_INSTANCE\_NAME}
Terminating instance i-0f843bc3435c5819e
Instance i-0f843bc3435c5819e terminated
\$ python ec2instance.py --action terminate --terminate-names \${APP2SERVER\_INSTANCE\_NAME}
Terminating instance i-0f7566c0b5d7cee04
Instance i-0f7566c0b5d7cee04 terminated
\$ python ec2instance.py --action terminate --terminate-names \${DBSERVER\_INSTANCE\_NAME}
Terminating instance i-01e21a918bad2d466
Instance i-01e21a918bad2d466 terminated

# Delete Security groups

\$ python3 securitygroups.py --vpc-id \${VPC\_ID} --action delete --private-sg-id \$PRIVATE\_SUBNET\_ID --public-sg-id \$PUBLIC\_SUBNET\_ID
Deleted private security group sg-0bd3f74905ab883d1
Deleted public security group sg-0a0501bdd00176b4a
Operation completed.

# Delete Key pair

\$ python keypair.py --action delete --key-name \${KEYPAIR} --key-file MyKeyPair.pem
Deleted key pair: MyKeyPair
Deleted local key file: MyKeyPair.pem

# VPC delete

\$ python vpc.py --action delete


```markdown
# AWS VPC + EC2 Infra Setup with Python & AWS CLI

This guide demonstrates how to provision a **VPC**, subnets, security groups, key pairs, EC2 instances, and networking components using Python scripts & AWS CLI.  

It also covers how to connect to private EC2 instances using a jump server and finally how to clean up resources.

---

## 1. Set AWS Region
```

export AWS_DEFAULT_REGION=us-west-2

```

---

## 2. Create VPC and Networking Components
```

python3 vpc.py --action create

```

**Resources Created:**
- VPC  
- Internet Gateway (IGW)  
- Public and Private Subnets  
- Elastic IP & NAT Gateway  
- Route Tables (public & private)  

**Example Output:**
```

Created VPC m04Vpc with ID vpc-0fa2ddcb6e7185d9f
Created and attached IGW igw-060dff40b26cf0129
Created subnet app1 (subnet-0858669c9d938f179)
Created subnet web (subnet-04575024b41feb5a8)
Allocated Elastic IP: eipalloc-03591c16488c55c57
NAT Gateway nat-0cb5dbd934e44e779 is now available
Route tables created and associated with subnets

```

**Export resource IDs:**
```

export VPC_ID="vpc-099a608cd399058eb"
export PRIVATE_SUBNET_ID="subnet-0be101e665f49932e"
export PUBLIC_SUBNET_ID="subnet-0ffbb62fee115a5b5"

```

---

## 3. Create Security Groups
```

python3 securitygroups.py --vpc-id \$VPC_ID --action create

```

**Output:**
```

Created security group PublicSG -> sg-0a0501bdd00176b4a
Created security group PrivateSG -> sg-0bd3f74905ab883d1

```

**Export variables:**
```

export PUBLIC_SG="sg-0a0501bdd00176b4a"
export PRIVATE_SG="sg-0bd3f74905ab883d1"

```

---

## 4. Generate SSH Key Pair
```

python keypair.py --action create

```

**Result:**
- Key pair created → `MyKeyPair` (private key saved as `MyKeyPair.pem`)

```

export KEYPAIR="MyKeyPair"

```

---

## 5. Launch EC2 Instances

### Webserver (Public Subnet)
```

export WEBSERVER_INSTANCE_NAME="webserver"
python ec2instance.py --action create \
--subnet-id \$PUBLIC_SUBNET_ID \
--sg-ids \$PUBLIC_SG \
--key-name \$KEYPAIR \
--instance-names \$WEBSERVER_INSTANCE_NAME \
--associate-public-ip
export WEBSERVER_INSTANCE_ID="i-02e7b28cb43dc0a52"

```

### App1 Server (Private Subnet)
```

export APP1SERVER_INSTANCE_NAME="app1server"
python ec2instance.py --action create \
--subnet-id \$PRIVATE_SUBNET_ID \
--sg-ids \$PRIVATE_SG \
--key-name \$KEYPAIR \
--instance-names \$APP1SERVER_INSTANCE_NAME
export APP1SERVER_INSTANCE_ID="i-06d79acf3095b6e1e"

```

### DBCache Server (Private Subnet)
```

export DBCACHESERVER_INSTANCE_NAME="dbcacheserver"
python ec2instance.py --action create \
--subnet-id \$PRIVATE_SUBNET_ID \
--sg-ids \$PRIVATE_SG \
--key-name \$KEYPAIR \
--instance-names \$DBCACHESERVER_INSTANCE_NAME
export DBCACHESERVER_INSTANCE_ID="i-0f843bc3435c5819e"

```

### App2 Server (Private Subnet)
```

export APP2SERVER_INSTANCE_NAME="app2server"
python ec2instance.py --action create \
--subnet-id \$PRIVATE_SUBNET_ID \
--sg-ids \$PRIVATE_SG \
--key-name \$KEYPAIR \
--instance-names \$APP2SERVER_INSTANCE_NAME
export APP2SERVER_INSTANCE_ID="i-0f7566c0b5d7cee04"

```

### Database Server (Private Subnet)
```

export DBSERVER_INSTANCE_NAME="dbserver"
python ec2instance.py --action create \
--subnet-id \$PRIVATE_SUBNET_ID \
--sg-ids \$PRIVATE_SG \
--key-name \$KEYPAIR \
--instance-names \$DBSERVER_INSTANCE_NAME
export DBSERVER_INSTANCE_ID="i-01e21a918bad2d466"

```

---

## 6. Fetch Instance IPs
```


# Webserver (public IP)

WEBSERVER_IP=\$(aws ec2 describe-instances --instance-ids \${WEBSERVER_INSTANCE_ID} \
--query "Reservations.Instances.PublicIpAddress" --output text)
echo \$WEBSERVER_IP

# App1, Cache, App2, DB private IPs

APP1SERVER_IP=\$(aws ec2 describe-instances --instance-ids \$APP1SERVER_INSTANCE_ID \
--query "Reservations.Instances.PrivateIpAddress" --output text)

```

---

## 7. SSH Access

Start SSH agent and add key:
```

eval "\$(ssh-agent -s)"
ssh-add MyKeyPair.pem
ssh-add -l

```

Connect to **App1 Server** via Webserver Jump Host:
```

ssh -J ec2-user@$WEBSERVER_IP ec2-user@$APP1SERVER_IP

```

---

## 8. Verify Networking
Inside App1 server:
```

ping -c 3 www.google.com
ping -c 3 8.8.8.8
curl google.com

```

---

## 9. List Running Instances
```

aws ec2 describe-instances \
--filters "Name=instance-state-name,Values=running" \
--query "Reservations[*].Instances[*].{InstanceId:InstanceId,InstanceType:InstanceType,Name:Tags[?Key=='Name'].Value|,PublicIp:PublicIpAddress,PrivateIp:PrivateIpAddress,SubnetId:SubnetId}" \
--output table

```

---

## 10. Cleanup

### Terminate Instances
```

python ec2instance.py --action terminate --terminate-names \$WEBSERVER_INSTANCE_NAME
python ec2instance.py --action terminate --terminate-names \$APP1SERVER_INSTANCE_NAME
python ec2instance.py --action terminate --terminate-names \$DBCACHESERVER_INSTANCE_NAME
python ec2instance.py --action terminate --terminate-names \$APP2SERVER_INSTANCE_NAME
python ec2instance.py --action terminate --terminate-names \$DBSERVER_INSTANCE_NAME

```

### Delete Security Groups
```

python3 securitygroups.py --vpc-id \${VPC_ID} --action delete \
--private-sg-id \$PRIVATE_SG \
--public-sg-id \$PUBLIC_SG

```

### Delete Key Pair
```

python keypair.py --action delete --key-name \${KEYPAIR} --key-file MyKeyPair.pem

```

### Delete VPC
```

python vpc.py --action delete

```

---

## ✅ Summary
This workflow provisions:
- VPC with public and private subnets  
- Security groups  
- EC2 instances (web, apps, db, cache)  
- NAT Gateway and Internet Gateway  

It also demonstrates **SSH access to private instances via a jump host** and cleans up resources after use.

---
```


***

