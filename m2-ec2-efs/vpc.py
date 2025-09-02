import boto3
import traceback
import argparse
import config

def create_vpc(ec2, cidr=config.VPC_CIDR, name=config.VPC_NAME):
    vpc = ec2.create_vpc(CidrBlock=cidr)
    vpc.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
    vpc.modify_attribute(EnableDnsHostnames={'Value': True})
    vpc.modify_attribute(EnableDnsSupport={'Value': True})
    print(f"Created VPC {name} with ID {vpc.id} and CIDR {cidr}")
    return vpc

def create_internet_gateway(ec2, vpc, name='m04VpcInternetGateway'):
    igw = ec2.create_internet_gateway()
    igw.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
    igw.attach_to_vpc(VpcId=vpc.id)
    print(f"Created and attached IGW {igw.id} to VPC {vpc.id}")
    return igw

def create_subnet(vpc, cidr=config.VPC_CIDR, name=config.VPC_SUBNET_NAME, az=config.AVAILABILITYZONE):
    subnet = vpc.create_subnet(
        CidrBlock=cidr,
        AvailabilityZone=az,
        TagSpecifications=[{
            'ResourceType': 'subnet',
            'Tags': [{'Key': 'Name', 'Value': name}]
        }]
    )
    print(f"Created subnet {name} with ID {subnet.id} and CIDR {cidr}")
    return subnet

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

def cleanup_routetables(ec2_client, rt_id):
    try:
        rt = ec2_client.describe_route_tables(RouteTableIds=[rt_id])
        # 'RouteTables' is the key holding the list, not direct 'Associations'
        for route_table in rt.get('RouteTables', []):
            for assoc in route_table.get('Associations', []):
                if not assoc.get('Main', False):
                    assoc_id = assoc['RouteTableAssociationId']
                    print(f"Disassociating route table {rt_id} association {assoc_id}")
                    ec2_client.disassociate_route_table(AssociationId=assoc_id)
        print(f"Deleting route table {rt_id}")
        ec2_client.delete_route_table(RouteTableId=rt_id)
    except Exception as e:
        print(f"Error cleaning route table {rt_id}: {e}")


def xxxcleanup_routetables(ec2_client, rt_id):

    try:
        rt = ec2_client.describe_route_tables(RouteTableIds=[rt_id])
        for assoc in rt.get('Associations', []):
            if not assoc.get('Main'):
                assoc_id = assoc['RouteTableAssociationId']
                print(f"Disassociating route table {rt_id} association {assoc_id}")
                ec2_client.disassociate_route_table(AssociationId=assoc_id)
        print(f"Deleting route table {rt_id}")
        ec2_client.delete_route_table(RouteTableId=rt_id)
    except Exception as e:
        print(f"Error cleaning route table {rt_id}: {e}")


def cleanup_subnet(ec2, subnet_id):
    
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

def main():
    parser = argparse.ArgumentParser(description='Manage AWS VPC environment')
    parser.add_argument('--action', required=True, choices=['create-vpc', 'delete-vpc'], help='Action to perform')
    parser.add_argument('--vpc-cidr', default=config.VPC_CIDR , help='CIDR block for the VPC (required for create)')
    parser.add_argument('--subnet-cidr', default=config.VPC_PVT_SUBNET, help='CIDR block for the Subnet (required for create)')
    parser.add_argument('--subnet-az', default=config.AVAILABILITYZONE, help='Availability Zone for the subnet (default: us-west-2b)')

    parser.add_argument('--vpc-id', help='VPC ID (required for delete)')
    parser.add_argument('--igw-id', help='IGW ID (required for delete)')
    parser.add_argument('--subnet-id', help='Subnet ID (required for delete)')
    parser.add_argument('--rt-tbl-id', help='Route Table ID (required for delete)')

    args = parser.parse_args()

    ec2 = boto3.resource('ec2', region_name=config.REGION)
    ec2_client = boto3.client('ec2', region_name=config.REGION)

    if args.action == 'create-vpc':
        vpc = create_vpc(ec2, cidr=args.vpc_cidr, name='m2-vpc-network')
        igw = create_internet_gateway(ec2, vpc, name='m2-vpc-igw')
        subnet = create_subnet(vpc, cidr=args.subnet_cidr, name='m2-pub-subnet', az=args.subnet_az)
        rt_tbl = create_route_table(vpc, 'm2-pub-routetable')
        associate_route_table(rt_tbl, subnet)
        # attach internet gateway to route internet traffic
        create_route(rt_tbl, '0.0.0.0/0', gateway_id=igw.id)

        print("\n--- VPC Network Resources Summary ---")
        print(f"VPC ID: {vpc.id}")
        print(f"IGW ID: {igw.id}")
        print(f"Public Subnet ID: {subnet.id}")
        print(f"Public Route Table ID: {rt_tbl.id}")

    elif args.action == 'delete-vpc':
        #if not args.vpc_id or not args.igw_id or not args.subnet_id:
        if not args.vpc_id or not args.subnet_id:
            parser.error("--vpc-id, --igw-id and --subnet-id are required for delete-vpc")
        try:
            cleanup_routetables(ec2_client, args.rt_tbl_id)
            #cleanup_subnet(ec2, args.subnet_id)
            #cleanup_igw(ec2, args.igw_id, args.vpc_id)
            cleanup_vpc(ec2, args.vpc_id)
        except Exception as e:
            print(f"Exception during cleanup: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    main()