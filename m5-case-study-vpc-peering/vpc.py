import boto3
import traceback
import argparse
import json
import os

region = 'us-west-2'  # Oregon, for sandbox/testing
AvailabilityZone='us-west-2a'

def init_ec2(region='us-west-2'):
    ec2 = boto3.resource('ec2', region_name=region)
    ec2_client = boto3.client('ec2', region_name=region)
    return ec2, ec2_client

def create_vpc(ec2, cidr='10.10.0.0/16', name='m04Vpc'):
    vpc = ec2.create_vpc(CidrBlock=cidr)
    vpc.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
    vpc.modify_attribute(EnableDnsHostnames={'Value': True})
    vpc.modify_attribute(EnableDnsSupport={'Value': True})
    print(f"Created VPC {name} with ID {vpc.id}")
    return vpc

def create_internet_gateway(ec2, vpc, name='m04VpcInternetGateway'):
    igw = ec2.create_internet_gateway()
    igw.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
    igw.attach_to_vpc(VpcId=vpc.id)
    print(f"Created and attached IGW {igw.id} to VPC {vpc.id}")
    return igw

def create_subnet(vpc, cidr, name):
    subnet = vpc.create_subnet(
        CidrBlock=cidr,
        AvailabilityZone='us-west-2a',
        TagSpecifications=[{
            'ResourceType': 'subnet',
            'Tags': [{'Key': 'Name', 'Value': name}]
        }]
    )
    print(f"Created subnet {name} with ID {subnet.id}")
    return subnet

def allocate_eip(ec2_client, name):
    allocation = ec2_client.allocate_address(
        Domain='vpc',
        TagSpecifications=[{
            'ResourceType': 'elastic-ip',
            'Tags': [{'Key': 'Name', 'Value': name}]
        }]
    )
    print(f"Allocated Elastic IP: Name: {name}, AllocationId: {allocation['AllocationId']}")
    return allocation['AllocationId']

def create_nat_gateway(ec2_client, subnet_id, allocation_id, name='publicWebSubnetNatGW'):
    response = ec2_client.create_nat_gateway(
        SubnetId=subnet_id,
        AllocationId=allocation_id,
        TagSpecifications=[{
            'ResourceType': 'natgateway',
            'Tags': [{'Key': 'Name', 'Value': name}]
        }]
    )
    natgw_id = response['NatGateway']['NatGatewayId']
    waiter = ec2_client.get_waiter('nat_gateway_available')
    print(f"Waiting for NAT Gateway {natgw_id} to become available...")
    waiter.wait(NatGatewayIds=[natgw_id])
    print(f"NAT Gateway {natgw_id} is now available")
    return natgw_id

def create_route_table(vpc, name):
    rt = vpc.create_route_table(
        TagSpecifications=[{
            'ResourceType': 'route-table',
            'Tags': [{'Key': 'Name', 'Value': name}]
        }]
    )
    print(f"Created route table {name} with ID {rt.id}")
    return rt

def associate_route_table(route_table, subnet):
    assoc = route_table.associate_with_subnet(SubnetId=subnet.id)
    print(f"Associated route table {route_table.id} with subnet {subnet.id}")
    return assoc

def create_route(route_table, destination_cidr, natgw_id=None, gateway_id=None):
    kwargs = {'DestinationCidrBlock': destination_cidr}
    if natgw_id:
        kwargs['NatGatewayId'] = natgw_id
    elif gateway_id:
        kwargs['GatewayId'] = gateway_id
    route_table.create_route(**kwargs)
    print(f"Created route {destination_cidr} => {natgw_id or gateway_id} in {route_table.id}")

def cleanup_natgw(ec2_client, natgw_id):
    print(f"Deleting NAT Gateway: {natgw_id}")
    ec2_client.delete_nat_gateway(NatGatewayId=natgw_id)
    waiter = ec2_client.get_waiter('nat_gateway_deleted')
    waiter.wait(NatGatewayIds=[natgw_id])

def release_eip(ec2_client, eip_id):
    print(f"Releasing Elastic IP: {eip_id}")
    ec2_client.release_address(AllocationId=eip_id)

def cleanup_routetables(ec2_client, rt_ids):
    for rt_id in rt_ids:
        try:
            rt = ec2_client.describe_route_tables(RouteTableIds=[rt_id])['RouteTables'][0]
            for assoc in rt.get('Associations', []):
                if not assoc.get('Main'):
                    assoc_id = assoc['RouteTableAssociationId']
                    print(f"Disassociating route table {rt_id} association {assoc_id}")
                    ec2_client.disassociate_route_table(AssociationId=assoc_id)
            print(f"Deleting route table {rt_id}")
            ec2_client.delete_route_table(RouteTableId=rt_id)
        except Exception as e:
            print(f"Error cleaning route table {rt_id}: {e}")

def cleanup_subnets(ec2, subnet_ids):
    for subnet_id in subnet_ids:
        try:
            subnet = ec2.Subnet(subnet_id)
            subnet.delete()
            print(f"Deleted subnet {subnet_id}")
        except Exception as e:
            print(f"Error deleting subnet {subnet_id}: {e}")

def cleanup_igw(ec2, igw_id, vpc_id):
    try:
        igw = ec2.InternetGateway(igw_id)
        igw.detach_from_vpc(VpcId=vpc_id)
        print(f"Detached IGW {igw_id} from VPC {vpc_id}")
        igw.delete()
        print(f"Deleted IGW {igw_id}")
    except Exception as e:
        print(f"Error deleting IGW {igw_id}: {e}")

def cleanup_vpc(ec2, vpc_id):
    try:
        vpc = ec2.Vpc(vpc_id)
        vpc.delete()
        print(f"Deleted VPC {vpc_id}")
    except Exception as e:
        print(f"Error deleting VPC {vpc_id}: {e}")

def create_resources(output_file='vpc_resources.json'):
    ec2, ec2_client = init_ec2()

    vpc = create_vpc(ec2, name='vpc-production-network')
    igw = create_internet_gateway(ec2, vpc, name='igw-production-network')

    private_subnet = create_subnet(vpc, '10.10.2.0/24', 'app1')
    public_subnet = create_subnet(vpc, '10.10.1.0/24', 'web')

    eip_allocation_id = allocate_eip(ec2_client, "publicWebSubnetNatGW-EIP")
    natgw_id = create_nat_gateway(ec2_client, public_subnet.id, eip_allocation_id)

    private_rt = create_route_table(vpc, 'privateApp1RouteTable')
    associate_route_table(private_rt, private_subnet)
    create_route(private_rt, '0.0.0.0/0', natgw_id=natgw_id)

    public_rt = create_route_table(vpc, 'publicWebRouteTable')
    associate_route_table(public_rt, public_subnet)
    create_route(public_rt, '0.0.0.0/0', gateway_id=igw.id)

    print("\n--- Creation Summary ---")
    print(f"VPC ID: {vpc.id}")
    print(f"IGW ID: {igw.id}")
    print(f"Private Subnet ID: {private_subnet.id}")
    print(f"Public Subnet ID: {public_subnet.id}")
    print(f"Elastic IP Allocation ID: {eip_allocation_id}")
    print(f"NAT Gateway ID: {natgw_id}")
    print(f"Private Route Table ID: {private_rt.id}")
    print(f"Public Route Table ID: {public_rt.id}")

    # Save resource IDs to file
    resources_data = {
        'vpc_id': vpc.id,
        'igw_id': igw.id,
        'private_subnet_id': private_subnet.id,
        'public_subnet_id': public_subnet.id,
        'eip_id': eip_allocation_id,
        'natgw_id': natgw_id,
        'private_rt_id': private_rt.id,
        'public_rt_id': public_rt.id,
    }
    with open(output_file, 'w') as f:
        json.dump(resources_data, f, indent=2)
    print(f"\nResource IDs saved to {output_file}")

def cleanup_resources(args):
    ec2, ec2_client = init_ec2()

    # Load resource IDs from file if specified and file exists
    resource_ids = {}
    if args.resource_file and os.path.isfile(args.resource_file):
        with open(args.resource_file, 'r') as f:
            resource_ids = json.load(f)
    else:
        # Fallback: read from CLI args
        resource_ids = {
            'vpc_id': args.vpc_id,
            'igw_id': args.igw_id,
            'private_subnet_id': args.private_subnet_id,
            'public_subnet_id': args.public_subnet_id,
            'eip_id': args.eip_id,
            'natgw_id': args.natgw_id,
            'private_rt_id': args.private_rt_id,
            'public_rt_id': args.public_rt_id,
        }

    # Validate loaded IDs present
    missing = [k for k,v in resource_ids.items() if not v]
    if missing:
        print(f"Missing required resource IDs to delete: {', '.join(missing)}")
        return

    cleanup_natgw(ec2_client, resource_ids['natgw_id'])
    release_eip(ec2_client, resource_ids['eip_id'])
    cleanup_routetables(ec2_client, [resource_ids['private_rt_id'], resource_ids['public_rt_id']])
    cleanup_subnets(ec2, [resource_ids['private_subnet_id'], resource_ids['public_subnet_id']])
    cleanup_igw(ec2, resource_ids['igw_id'], resource_ids['vpc_id'])
    cleanup_vpc(ec2, resource_ids['vpc_id'])



def main():
    parser = argparse.ArgumentParser(description='Manage AWS VPC environment')
    parser.add_argument('--action', required=True, choices=['create', 'delete'], help='Action to perform')
    parser.add_argument('--resource-file', default='vpc_resources.json', help='Path to saved resource IDs JSON file (for delete)')

    # Old delete params made optional now
    parser.add_argument('--vpc-id', help='VPC ID')
    parser.add_argument('--igw-id', help='Internet Gateway ID')
    parser.add_argument('--private-subnet-id', help='Private Subnet ID')
    parser.add_argument('--public-subnet-id', help='Public Subnet ID')
    parser.add_argument('--eip-id', help='Elastic IP Allocation ID')
    parser.add_argument('--natgw-id', help='NAT Gateway ID')
    parser.add_argument('--private-rt-id', help='Private Route Table ID')
    parser.add_argument('--public-rt-id', help='Public Route Table ID')

    args = parser.parse_args()

    if args.action == 'create':
        try:
            create_resources(output_file=args.resource_file)
        except Exception as e:
            print(f"Exception during resource creation: {e}")
            traceback.print_exc()
    elif args.action == 'delete':
        try:
            cleanup_resources(args)
        except Exception as e:
            print(f"Exception during cleanup: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    main()
