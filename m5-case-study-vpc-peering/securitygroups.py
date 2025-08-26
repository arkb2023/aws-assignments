import boto3
import traceback
import argparse
import sys
import json
import os

region = 'us-west-2'  # Oregon, for sandbox/testing

def create_security_group(ec2_client, vpc_id, name, description, inbound_rules):
    """Create a security group with given inbound rules."""
    response = ec2_client.create_security_group(
        GroupName=name,
        Description=description,
        VpcId=vpc_id
    )
    sg_id = response['GroupId']
    print(f"Created security group {name} with ID {sg_id}")

    ip_permissions = []
    for rule in inbound_rules:
        ip_permissions.append({
            'IpProtocol': rule['protocol'],
            'FromPort': rule['from_port'],
            'ToPort': rule['to_port'],
            'IpRanges': [{'CidrIp': rule['cidr']}],
            'UserIdGroupPairs': rule.get('user_group_pairs', [])
        })

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=ip_permissions
    )
    #print(f"Ingress rules set for {name}")
    return sg_id

def main():
    parser = argparse.ArgumentParser(description='Manage Security groups')
    parser.add_argument('--vpc-id', required=True, help='VPC ID')
    parser.add_argument('--action', required=True, choices=['create', 'delete'])
    parser.add_argument('--resource-file', default='sg_resources.json', help='Path to saved resource IDs JSON file (for delete)')
    parser.add_argument('--private-sg-id', help='Private Security group ID (required for delete)')
    parser.add_argument('--public-sg-id', help='Public Security group ID (required for delete)')
    args = parser.parse_args()

    ec2_client = boto3.client('ec2', region_name=region)

    public_sg_name = 'PublicSG'
    private_sg_name = 'PrivateSG'
    output_file = args.resource_file

    try:
        if args.action == 'create':
            public_subnet_inbound_rules = [
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': '0.0.0.0/0'},
                {'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr': '0.0.0.0/0'}
            ]
            public_sg_id = create_security_group(
                ec2_client, args.vpc_id,
                public_sg_name, 'Allow SSH and HTTP from anywhere',
                public_subnet_inbound_rules
            )
            private_sg_id = create_security_group(
                ec2_client, args.vpc_id,
                private_sg_name, 'Allow SSH and ICMP from PublicSG',
                [
                    {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': '0.0.0.0/0', 'user_group_pairs': [{'GroupId': public_sg_id}]},
                    {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': '0.0.0.0/0', 'user_group_pairs': [{'GroupId': public_sg_id}]}
                ]
            )
            security_groups_created = {
                public_sg_name: public_sg_id,
                private_sg_name: private_sg_id
            }
            with open(output_file, 'w') as f:
                json.dump(security_groups_created, f, indent=2)
            print(f"Saved all created resource IDs to {output_file}")

        else:  # action = delete
            print("Cleaning up created resources...")

            resource_ids = {}
            if args.resource_file and os.path.isfile(args.resource_file):
                with open(args.resource_file, 'r') as f:
                    resource_ids = json.load(f)
            else:
                if not args.private_sg_id or not args.public_sg_id:
                    print("Private and Public Security group IDs required for delete (either via --resource-file or args)")
                    sys.exit(1)
                resource_ids[private_sg_name] = args.private_sg_id
                resource_ids[public_sg_name] = args.public_sg_id

            if private_sg_name in resource_ids and resource_ids[private_sg_name]:
                ec2_client.delete_security_group(GroupId=resource_ids[private_sg_name])
                print(f"Deleted private security group {resource_ids[private_sg_name]}")
            else:
                print("Private security group ID missing; skipping deletion")

            if public_sg_name in resource_ids and resource_ids[public_sg_name]:
                ec2_client.delete_security_group(GroupId=resource_ids[public_sg_name])
                print(f"Deleted public security group {resource_ids[public_sg_name]}")
            else:
                print("Public security group ID missing; skipping deletion")

    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
    finally:
        print("Operation completed.")

if __name__ == '__main__':
    main()
