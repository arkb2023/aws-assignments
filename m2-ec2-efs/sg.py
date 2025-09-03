import boto3
import argparse
import sys
import traceback
import config


def create_security_group(ec2_client, vpc_id, name, description, inbound_rules):
    """Create a security group with given inbound rules."""
    response = ec2_client.create_security_group(
        GroupName=f"group-{name}",
        Description=description,
        VpcId=vpc_id,
        TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name
                        },
                    ]
                },
            ],
    )
    sg_id = response['GroupId']
    print(f"Created security group {name} with ID {sg_id}")

    ip_permissions = []
    for rule in inbound_rules:
        perm = {
            'IpProtocol': rule['protocol'],
            'FromPort': rule['from_port'],
            'ToPort': rule['to_port'],
        }
        if 'cidr' in rule:
            perm['IpRanges'] = [{'CidrIp': rule['cidr']}]
        if 'user_group_pairs' in rule and rule['user_group_pairs']:
            perm['UserIdGroupPairs'] = rule['user_group_pairs']
        ip_permissions.append(perm)

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=ip_permissions
    )
    print(f"Ingress rules set for {name}")
    return sg_id


def delete_security_group(ec2_client, sg_id):
    """Delete security group by ID, handling errors."""
    try:
        ec2_client.delete_security_group(GroupId=sg_id)
        print(f"Deleted security group {sg_id}")
    except Exception as e:
        print(f"Error deleting security group {sg_id}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Create or delete minimal SGs for EFS mount and SSH')
    parser.add_argument('--action', required=True, choices=['create-sg', 'delete-sg'], help='Action to perform')
    parser.add_argument('--vpc-id', help='VPC ID (required for create-sg)')
    parser.add_argument('--subnet-cidr', default=config.VPC_PVT_SUBNET, help='Subnet CIDR for SSH and EFS mount')
    
    parser.add_argument('--efs-sg-id', help='Security group id for EFS mount (required for delete-sg)')
    parser.add_argument('--ec2-sg-id', help='Security group id for SSH to EC2 (required for delete-sg)')
    args = parser.parse_args()

    ec2_client = boto3.client('ec2', region_name=config.REGION)

    try:
        if args.action == 'create-sg':
            if not args.vpc_id:
                parser.error("--vpc-id required for create-sg")
            
            efs_inbound_rules = [
                # NFS for EFS mount inbound from subnet CIDR
                {'protocol': 'tcp', 'from_port': 2049, 'to_port': 2049, 'cidr': args.subnet_cidr}
            ]
            efs_sg_id = create_security_group(ec2_client, args.vpc_id,
                                             'sg-for-efs',
                                             'SG to allow EFS mount on EC2',
                                             efs_inbound_rules)

            ec2_inbound_rules = [
                # SSH inbound from subnet CIDR
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.ANY_CIDR}
            ]
            ec2_sg_id = create_security_group(ec2_client, args.vpc_id,
                                              'sg-for-ec2',
                                              'SG for SSH to EC2 from anywhere',
                                              ec2_inbound_rules)

        elif args.action == 'delete-sg':
            # Load SG IDs from file and delete them
            if not args.efs_sg_id or not args.ec2_sg_id:
                parser.error("--efs-sg-id and --ec2-sg-id are required for delete-sg")
            
            delete_security_group(ec2_client, args.efs_sg_id)
            delete_security_group(ec2_client, args.ec2_sg_id)
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
