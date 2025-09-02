import boto3
import argparse
import sys
import json
import traceback
import os
import config

import boto3

def get_latest_ami(region, os):
    if os in ["amzn-linux", "ubuntu"]:
        # Use SSM Parameter Store aliases for Amazon Linux and Ubuntu
        ssm = boto3.client('ssm', region_name=region)
        if os == "amzn-linux":
            param_name = '/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-ebs'
        elif os == "ubuntu":
            param_name = '/aws/service/canonical/ubuntu/server/20.04/stable/current/amd64/hvm/ebs-gp2/ami-id'
        
        response = ssm.get_parameter(Name=param_name)
        return response['Parameter']['Value']

    elif os == "redhat":
        # No SSM alias for RHEL — query EC2 directly
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_images(
            Owners=['309956199498'],  # AWS official Red Hat AMI owner
            Filters=[
                {'Name': 'name', 'Values': ['RHEL-10*']},
                {'Name': 'architecture', 'Values': ['x86_64']},
                {'Name': 'root-device-type', 'Values': ['ebs']},
                {'Name': 'virtualization-type', 'Values': ['hvm']},
                {'Name': 'state', 'Values': ['available']}
            ]
        )

        # Sort by creation date to get the latest
        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
        if images:
            return images[0]['ImageId']
        else:
            raise Exception("No RHEL AMI found in this region.")

    else:
        raise ValueError(f"Invalid OS specified: {os}")
    

def get_user_data_script(region, os, efs_id):
    efs_dns = f"{efs_id}.efs.{region}.amazonaws.com"
    
    if os == "redhat" or os == "amzn-linux":
        user_data_script = f"""#!/bin/bash
# amazon-efs-utils does not work on redhat
# sudo yum install -y amazon-efs-utils
sudo yum install nfs-utils -y
sudo mkdir -p /mnt/efs
sudo mount -t efs {efs_dns}:/ /mnt/efs
"""
    elif os == "ubuntu":
        nfs_options="rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport"
        user_data_script = f"""#!/bin/bash
sudo apt-get update
sudo apt-get install -y nfs-common
sudo mkdir -p /mnt/efs
sudo mount -t nfs4 -o nfsvers=4.1,{nfs_options} {efs_dns}:/ /mnt/efs
"""
    else:
        raise ValueError(f"Invalid OS specified: {os}")

    return user_data_script


def create_instance(ec2, subnet_id, sg_ids, key_name, instance_type, name, os, associate_public_ip, efs_id):
    ami_id = get_latest_ami(ec2.meta.client.meta.region_name, os)
    print(f"OS: {os} AMI: {ami_id}")
    user_data_script = get_user_data_script(ec2.meta.client.meta.region_name, os, efs_id)

    instances = ec2.create_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MaxCount=1,
        MinCount=1,
        KeyName=key_name,
        NetworkInterfaces=[{
            'SubnetId': subnet_id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': associate_public_ip,
            'Groups': sg_ids
        }],
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': name}]
        }],
        UserData=user_data_script
    )
    instance = instances[0]
    print(f"Instance {name} created")
    instance.wait_until_running()
    instance.reload()
    print(f"Instance {name} running with ID: {instance.id}")
    return instance.id

def terminate_instances(ec2_client, instance_ids):
    for instance_id in instance_ids:
        try:
            print(f"Terminating instance {instance_id}")
            ec2_client.terminate_instances(InstanceIds=[instance_id])
            waiter = ec2_client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=[instance_id])
            print(f"Instance {instance_id} terminated")
        except Exception as e:
            print(f"Error terminating instance {instance_id}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Create or terminate multiple EC2 instances')
    parser.add_argument('--action', required=True, choices=['create', 'terminate'])
    parser.add_argument('--subnet-id', help='Subnet ID (required for create)')
    parser.add_argument('--sg-ids', nargs='+', help='Security group IDs (required for create)')
    parser.add_argument('--key-name', help='Key pair name (required for create)')
    parser.add_argument('--instance-type', default=config.INSTANCE_TYPE)
    parser.add_argument('--os', choices=['redhat', 'ubuntu', 'amzn-linux'])
    parser.add_argument('--associate-public-ip', default=True, help='Associate public IP (only for create)')
    parser.add_argument('--efs-id', help='EFS ID (required for create)')

    # For create: allow multiple instance logical names (e.g., ubuntu-server, redhat-server, amzn-linux-server)
    parser.add_argument('--instance-names', nargs='+', help='Logical names for instances (create only)')

    # For terminate: select which instance logical ids to terminate
    parser.add_argument('--terminate-ids', nargs='+', help='Instance ids to terminate (terminate only)')

    args = parser.parse_args()

    try:
        ec2 = boto3.resource('ec2', region_name=config.REGION)
        ec2_client = boto3.client('ec2', region_name=config.REGION)

        if args.action == 'create':
            required_params = [args.subnet_id, args.sg_ids, args.key_name, args.os, args.efs_id]
            if not all(required_params):
                print("For create, --subnet-id, --sg-ids, --key-name, --os and --efs-id are required")
                sys.exit(1)

            instance_id = create_instance(
                ec2=ec2,
                subnet_id=args.subnet_id,
                sg_ids=args.sg_ids,
                key_name=args.key_name,
                instance_type=args.instance_type,
                name=f"{args.os}_server",
                os=args.os,
                associate_public_ip=args.associate_public_ip,
                efs_id=args.efs_id
            )
                

    
        elif args.action == 'terminate':
            if not args.terminate_ids:
                parser.error("--terminate-ids are required for terminate")
            
            terminate_instances(ec2_client, args.terminate_ids)

    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
    finally:
        print("Operation completed.")

if __name__ == '__main__':
    main()
