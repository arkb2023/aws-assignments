import boto3
import traceback
import argparse
import sys
import json
import os
import config

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

def revoke_sg_references(ec2_client, sg_id):
    """Remove all ingress rules referencing other security groups from this SG."""
    response = ec2_client.describe_security_groups(GroupIds=[sg_id])
    sg = response['SecurityGroups'][0]
    ingress_permissions = sg.get('IpPermissions', [])

    # Filter for UserIdGroupPairs (SG references)
    revoke_permissions = []
    for perm in ingress_permissions:
        if 'UserIdGroupPairs' in perm and perm['UserIdGroupPairs']:
            revoke_permissions.append(perm)

    if revoke_permissions:
        ec2_client.revoke_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=revoke_permissions
        )
        print(f"Revoked SG references from {sg_id}")


def delete_security_groups_in_order(ec2_client, resource_ids):
    # For prod SGs - first revoke refs, then delete in order to avoid dependency violation
    prod_sg_keys = [k for k in resource_ids if k.startswith('prod_')]
    for key in prod_sg_keys:
        sg_id = resource_ids[key]
        if sg_id:
            revoke_sg_references(ec2_client, sg_id)

    for key in prod_sg_keys:
        sg_id = resource_ids[key]
        if sg_id:
            try:
                ec2_client.delete_security_group(GroupId=sg_id)
                print(f"Deleted production security group {key} with ID {sg_id}")
            except Exception as e:
                print(f"Error deleting SG {sg_id}: {e}")

    # For dev SGs - do the same
    dev_sg_keys = [k for k in resource_ids if k.startswith('dev_')]
    for key in dev_sg_keys:
        sg_id = resource_ids[key]
        if sg_id:
            revoke_sg_references(ec2_client, sg_id)

    for key in dev_sg_keys:
        sg_id = resource_ids[key]
        if sg_id:
            try:
                ec2_client.delete_security_group(GroupId=sg_id)
                print(f"Deleted development security group {key} with ID {sg_id}")
            except Exception as e:
                print(f"Error deleting SG {sg_id}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Manage Security groups')
    parser.add_argument('--prod-vpc-id', required=True, help='Production VPC ID')
    parser.add_argument('--dev-vpc-id', required=True, help='Development VPC ID')
    parser.add_argument('--action', required=True, choices=['create', 'delete'])
    parser.add_argument('--resource-file', default='sg_resources.json', help='Path to save/load SG IDs JSON')
    args = parser.parse_args()

    ec2_client = boto3.client('ec2', region_name=config.REGION)

    # Define security groups for Production network
    prod_sgs = {
        "WebserverSG": {
            "name": "Prod-Webserver-SG",
            "description": "Inbound SSH, HTTP, ICMP from anywhere",
            "inbound_rules": [
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.ANY_CIDR},
                {'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr': config.ANY_CIDR},
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': config.ANY_CIDR},
            ],
        },
        "Dbcache_App1_SG": {
            "name": "Prod-Dbcache-App1-SG",
            "description": "SSH, HTTP, ICMP from Prod CIDR and Webserver SG",
            "inbound_rules": [
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.PROD_NET_VPC_CIDR},  # Production CIDR
                {'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr': config.PROD_NET_VPC_CIDR},
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': config.PROD_NET_VPC_CIDR},
                # 'user_group_pairs' will be added after WebserverSG creation
            ],
        },
        "Dbcache_DB_SG": {
            "name": "Prod-Dbcache-DB-SG",
            "description": "SSH and ICMP from Dev DB CIDR & Prod Webserver",
            "inbound_rules": [
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.DEV_NET_VPC_PVT_DBSUBNET},  # Dev DB subnet CIDR
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': config.DEV_NET_VPC_PVT_DBSUBNET},
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.PROD_NET_VPC_PUBLIC_WEBSUBNET},  # Prod webserver subnet CIDR
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': config.PROD_NET_VPC_PUBLIC_WEBSUBNET},
            ],
        },
        "App2_SG": {
            "name": "Prod-App2-SG",
            "description": "ICMP (ping) from Webserver SG only",
            "inbound_rules": [
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'user_group_pairs': []},  # Webserver SG to be added later
            ],
        }
    }

    # Security groups for Development network
    dev_sgs = {
        "WebserverSG": {
            "name": "Dev-Webserver-SG",
            "description": "Inbound SSH, HTTP, ICMP from anywhere",
            "inbound_rules": [
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.ANY_CIDR},
                {'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr': config.ANY_CIDR},
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': config.ANY_CIDR},
            ],
        },
        "DB_SG": {
            "name": "Dev-DB-SG",
            "description": "SSH and ICMP from Prod DB & DBCache CIDR, also from Dev webserver",
            "inbound_rules": [
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.PROD_NET_VPC_PVT_DBCACHESUBNET},  # Prod dbcache subnet CIDR
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': config.PROD_NET_VPC_PVT_DBCACHESUBNET},
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.PROD_NET_VPC_PVT_DBSUBNET},  # Prod db subnet CIDR
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': config.PROD_NET_VPC_PVT_DBSUBNET},
                {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr': config.DEV_NET_VPC_PUBLIC_WEBSUBNET},  # Dev webserver subnet CIDR
                {'protocol': 'icmp', 'from_port': -1, 'to_port': -1, 'cidr': config.DEV_NET_VPC_PUBLIC_WEBSUBNET },                
            ],
        }
    }

    try:
        if args.action == 'create':
            # Create production Webserver SG first (others reference this)
            prod_web_sg_id = create_security_group(ec2_client, args.prod_vpc_id,
                                                   prod_sgs["WebserverSG"]["name"],
                                                   prod_sgs["WebserverSG"]["description"],
                                                   prod_sgs["WebserverSG"]["inbound_rules"])

            # Update other prod SGs user_group_pairs with the above ID
            prod_sgs["Dbcache_App1_SG"]["inbound_rules"].append({
                'protocol': '-1', 'from_port': -1, 'to_port': -1,
                'user_group_pairs': [{'GroupId': prod_web_sg_id}]
            })
            prod_sgs["App2_SG"]["inbound_rules"][0]['user_group_pairs'] = [{'GroupId': prod_web_sg_id}]

            # Create other production SGs
            prod_dbcache_app1_sg_id = create_security_group(ec2_client, args.prod_vpc_id,
                                                           prod_sgs["Dbcache_App1_SG"]["name"],
                                                           prod_sgs["Dbcache_App1_SG"]["description"],
                                                           prod_sgs["Dbcache_App1_SG"]["inbound_rules"])
            prod_dbcache_db_sg_id = create_security_group(ec2_client, args.prod_vpc_id,
                                                         prod_sgs["Dbcache_DB_SG"]["name"],
                                                         prod_sgs["Dbcache_DB_SG"]["description"],
                                                         prod_sgs["Dbcache_DB_SG"]["inbound_rules"])
            prod_app2_sg_id = create_security_group(ec2_client, args.prod_vpc_id,
                                                    prod_sgs["App2_SG"]["name"],
                                                    prod_sgs["App2_SG"]["description"],
                                                    prod_sgs["App2_SG"]["inbound_rules"])

            # Create development SGs
            dev_web_sg_id = create_security_group(ec2_client, args.dev_vpc_id,
                                                 dev_sgs["WebserverSG"]["name"],
                                                 dev_sgs["WebserverSG"]["description"],
                                                 dev_sgs["WebserverSG"]["inbound_rules"])
            dev_db_sg_id = create_security_group(ec2_client, args.dev_vpc_id,
                                                dev_sgs["DB_SG"]["name"],
                                                dev_sgs["DB_SG"]["description"],
                                                dev_sgs["DB_SG"]["inbound_rules"])

            # Save all SG IDs
            sg_resources = {
                'prod_web_sg_id': prod_web_sg_id,
                'prod_dbcache_app1_sg_id': prod_dbcache_app1_sg_id,
                'prod_dbcache_db_sg_id': prod_dbcache_db_sg_id,
                'prod_app2_sg_id': prod_app2_sg_id,
                'dev_web_sg_id': dev_web_sg_id,
                'dev_db_sg_id': dev_db_sg_id,
            }
            with open(args.resource_file, 'w') as f:
                json.dump(sg_resources, f, indent=2)
            print(f"Saved security group IDs to {args.resource_file}")

        else:  # delete
            if os.path.isfile(args.resource_file):
                resource_ids={}
                with open(args.resource_file, 'r') as f:
                    resource_ids = json.load(f)
                delete_security_groups_in_order(ec2_client, resource_ids)
            else:
                print("Resource file not found. Provide security group IDs for deletion.")
                sys.exit(1)

    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
    finally:
        print("Operation completed.")

if __name__ == '__main__':
    main()
