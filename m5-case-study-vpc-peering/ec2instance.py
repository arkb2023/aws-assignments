import boto3
import argparse
import sys
import json
import traceback
import os

def get_latest_amazon_linux_ami(region):
    ssm = boto3.client('ssm', region_name=region)
    response = ssm.get_parameter(Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-ebs')
    return response['Parameter']['Value']

def create_instance(ec2, subnet_id, sg_ids, key_name, instance_type, name, associate_public_ip):
    ami_id = get_latest_amazon_linux_ami(ec2.meta.client.meta.region_name)

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
        }]
    )
    instance = instances[0]
    print(f"Created instance {name}")
    instance.wait_until_running()
    instance.reload()
    print(f"Created instance {name} with ID: {instance.id}")
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

def save_resource_file(instances_dict, filename='instances_resource.json'):
    with open(filename, 'w') as f:
        json.dump(instances_dict, f, indent=2)
    print(f"Saved instances info to {filename}")

def load_resource_file(filename='instances_resource.json'):
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        return {}

def main():
    parser = argparse.ArgumentParser(description='Create or terminate multiple EC2 instances')
    parser.add_argument('--region', default='us-west-2')
    parser.add_argument('--action', required=True, choices=['create', 'terminate'])
    parser.add_argument('--subnet-id', help='Subnet ID (required for create)')
    parser.add_argument('--sg-ids', nargs='+', help='Security group IDs (required for create)')
    parser.add_argument('--key-name', help='Key pair name (required for create)')
    parser.add_argument('--instance-type', default='t2.micro')
    parser.add_argument('--associate-public-ip', action='store_true', help='Associate public IP (only for create)')
    parser.add_argument('--resource-file', default='instances_resource.json', help='File to save/load instances info')

    # For create: allow multiple instance logical names (e.g., webserver, dbserver)
    parser.add_argument('--instance-names', nargs='+', help='Logical names for instances (create only)')

    # For terminate: select which instance logical names to terminate
    parser.add_argument('--terminate-names', nargs='+', help='Instance logical names to terminate (terminate only)')

    args = parser.parse_args()

    try:
        ec2 = boto3.resource('ec2', region_name=args.region)
        ec2_client = boto3.client('ec2', region_name=args.region)

        if args.action == 'create':
            required_params = [args.subnet_id, args.sg_ids, args.key_name, args.instance_names]
            if not all(required_params):
                print("For create, --subnet-id, --sg-ids, --key-name, and --instance-names are required")
                sys.exit(1)

            instances_info = {}
            for inst_name in args.instance_names:
                instance_id = create_instance(
                    ec2=ec2,
                    subnet_id=args.subnet_id,
                    sg_ids=args.sg_ids,
                    key_name=args.key_name,
                    instance_type=args.instance_type,
                    name=inst_name,
                    associate_public_ip=args.associate_public_ip
                )
                instances_info[inst_name] = instance_id

            save_resource_file(instances_info, filename=args.resource_file)

        elif args.action == 'terminate':
            instances_info = load_resource_file(filename=args.resource_file)
            if not instances_info:
                print(f"No instance information found in {args.resource_file}. Cannot terminate.")
                sys.exit(1)

            to_terminate = []
            if args.terminate_names:
                # Terminate only specified instances
                for name in args.terminate_names:
                    instance_id = instances_info.get(name)
                    if instance_id:
                        to_terminate.append(instance_id)
                    else:
                        print(f"No instance ID found for name '{name}' in resource file")
            else:
                # If no names provided, terminate ALL saved instances
                to_terminate = list(instances_info.values())
                print("No specific instance names provided, terminating all saved instances")

            if not to_terminate:
                print("No instances to terminate. Exiting.")
                sys.exit(0)

            terminate_instances(ec2_client, to_terminate)

    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
    finally:
        print("Operation completed.")

if __name__ == '__main__':
    main()
