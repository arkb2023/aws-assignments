import boto3
import traceback
import argparse
import json
import os
import sys
import config



def init_ec2(region=config.REGION):
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

def create_subnet(vpc, cidr, name, az):
    subnet = vpc.create_subnet(
        CidrBlock=cidr,
        AvailabilityZone=az,
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

def save_resource_file(new_resources, resource_type="undef", output_file='vpc_resources.json'):
    # Load existing data if file exists
    if os.path.isfile(output_file):
        with open(output_file, 'r') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # Update existing data with new resources (e.g., 'pnet_*' or 'dnet_*' keys)
    existing_data.update(new_resources)

    # Write back the merged JSON data
    with open(output_file, 'w') as f:
        json.dump(existing_data, f, indent=2)
    print(f"Merged and saved {resource_type} resource info to {output_file}")


def xxsave_resource_file(instances_dict, resource_type="undef", filename='noname.json'):
    if os.path.exists(filename):
        with open(filename, 'a') as f:
            json.dump(instances_dict, f, indent=2)
        print(f"Appended {resource_type} resource info to {filename}")
    else:
        with open(filename, 'w') as f:
            json.dump(instances_dict, f, indent=2)
        print(f"Saved {resource_type} resource info to {filename}")

def create_peering(ec2_client, prod_vpc_id, dev_vpc_id):
    # 1. Create peering request
    response = ec2_client.create_vpc_peering_connection(VpcId=prod_vpc_id, PeerVpcId=dev_vpc_id)
    peering_id = response['VpcPeeringConnection']['VpcPeeringConnectionId']
    print(f"Created peering request: {peering_id}")
    
    # 2. Accept peering request
    ec2_client.accept_vpc_peering_connection(VpcPeeringConnectionId=peering_id)
    print("Accepted peering connection.")
    return peering_id

def add_peering_routes(ec2_client, route_table_id, destination_cidr, peering_id):
    ec2_client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock=destination_cidr,
        VpcPeeringConnectionId=peering_id,
    )
    print(f"Added route to {destination_cidr} via peering connection {peering_id}")

def create_resources(network, output_file='vpc_resources.json', skip_expensive=False):
    ec2, ec2_client = init_ec2()

    resources_data = {}
    if network == 'prod':
        # VPC - Production Network
        # -------------------------
        pnet_vpc = create_vpc(ec2, cidr=config.PROD_NET_VPC_CIDR, name='vpc-production-network')
        pnet_igw = create_internet_gateway(ec2, pnet_vpc, name='igw-production-network')

        pnet_pub_websubnet = create_subnet(pnet_vpc, config.PROD_NET_VPC_PUBLIC_WEBSUBNET, 'prod-net-pub-websubnet', config.AVAILABILITYZONE)
        pnet_pvt_app1subnet = create_subnet(pnet_vpc, config.PROD_NET_VPC_PVT_APP1SUBNET, 'prod-net-pvt-app1subnet', config.AVAILABILITYZONE)
        pnet_pvt_app2subnet = create_subnet(pnet_vpc, config.PROD_NET_VPC_PVT_APP2SUBNET, 'prod-net-pvt-app2subnet', config.AVAILABILITYZONE)
        pnet_pvt_dbcachesubnet = create_subnet(pnet_vpc, config.PROD_NET_VPC_PVT_DBCACHESUBNET, 'prod-net-pvt-dbcachesubnet', config.AVAILABILITYZONE)
        pnet_pvt_dbsubnet = create_subnet(pnet_vpc, config.PROD_NET_VPC_PVT_DBSUBNET, 'prod-net-pvt-dbsubnet', config.AVAILABILITYZONE)

        # Set the flag to use NAT and EIP
        if not skip_expensive:
            pnet_eip_allocation_id = allocate_eip(ec2_client, "ProdNet-PublicWebSubnetNatGW-EIP")
            pnet_natgw_id = create_nat_gateway(ec2_client, pnet_pub_websubnet.id, pnet_eip_allocation_id, name="natgw-production-network")

        # Create route tables for private subnets
        pnet_pvt_app1subnet_rt = create_route_table(pnet_vpc, 'ProdNet-PvtApp1RouteTable')
        associate_route_table(pnet_pvt_app1subnet_rt, pnet_pvt_app1subnet)
        pnet_pvt_app2subnet_rt = create_route_table(pnet_vpc, 'ProdNet-PvtApp2RouteTable')
        associate_route_table(pnet_pvt_app2subnet_rt, pnet_pvt_app2subnet)
        pnet_pvt_dbcachesubnet_rt = create_route_table(pnet_vpc, 'ProdNet-PvtDBCacheRouteTable')
        associate_route_table(pnet_pvt_dbcachesubnet_rt, pnet_pvt_dbcachesubnet)
        pnet_pvt_dbsubnet_rt = create_route_table(pnet_vpc, 'ProdNet-PvtDBRouteTable')
        associate_route_table(pnet_pvt_dbsubnet_rt, pnet_pvt_dbsubnet)
        
        # Set the flag to use NAT and EIP
        if not skip_expensive:
            # 4. Allow dbcache instance and app1 subnet to send internet requests.
            # attach NAT GW
            create_route(pnet_pvt_app1subnet_rt, '0.0.0.0/0', natgw_id=pnet_natgw_id)
            create_route(pnet_pvt_dbcachesubnet_rt, '0.0.0.0/0', natgw_id=pnet_natgw_id)

        # Create route tables public subnet
        pnet_pub_websubnet_rt = create_route_table(pnet_vpc, 'ProdNet-PublicWebRouteTable')
        associate_route_table(pnet_pub_websubnet_rt, pnet_pub_websubnet)
        # attach internet gateway to route internet traffic
        create_route(pnet_pub_websubnet_rt, '0.0.0.0/0', gateway_id=pnet_igw.id)

        print("\n--- Production Network Resources Summary ---")
        print(f"VPC ID: {pnet_vpc.id}")
        print(f"IGW ID: {pnet_igw.id}")
        print(f"Public Websubnet ID: {pnet_pub_websubnet.id}")
        print(f"Private App1subnet ID: {pnet_pvt_app1subnet.id}")
        print(f"Private App2subnet ID: {pnet_pvt_app2subnet.id}")
        print(f"Private dbcachesubnet ID: {pnet_pvt_dbcachesubnet.id}")
        print(f"Private dbsubnet ID: {pnet_pvt_dbsubnet.id}")
        # Set the flag to use NAT and EIP
        if not skip_expensive:
            print(f"Elastic IP Allocation ID: {pnet_eip_allocation_id}")
            print(f"NAT Gateway ID: {pnet_natgw_id}")
        else:
            print("Test Mode: NAT GW configuration skipped!")

        print(f"Public Web subnet route Table ID: {pnet_pub_websubnet_rt.id}")
        print(f"Private App1 subnet route Table ID: {pnet_pvt_app1subnet_rt.id}")
        print(f"Private App2 subnet route Table ID: {pnet_pvt_app2subnet_rt.id}")
        print(f"Private DBCache subnet route Table ID: {pnet_pvt_dbcachesubnet_rt.id}")
        print(f"Private DB subnet route Table ID: {pnet_pvt_dbsubnet_rt.id}")

        # Save resource IDs to file
        resources_data = {
            'pnet_vpc_id': pnet_vpc.id,
            'pnet_igw_id': pnet_igw.id,
            
            'pnet_pub_websubnet_id': pnet_pub_websubnet.id,
            'pnet_pvt_app1subnet_id': pnet_pvt_app1subnet.id,
            'pnet_pvt_app2subnet_id': pnet_pvt_app2subnet.id,
            'pnet_pvt_dbcachesubnet_id': pnet_pvt_dbcachesubnet.id,
            'pnet_pvt_dbsubnet_id': pnet_pvt_dbsubnet.id,
            
            'pnet_pub_websubnet_rt_id': pnet_pub_websubnet_rt.id,
            'pnet_pvt_app1subnet_rt_id': pnet_pvt_app1subnet_rt.id,
            'pnet_pvt_app2subnet_rt_id': pnet_pvt_app2subnet_rt.id,
            'pnet_pvt_dbcachesubnet_rt_id': pnet_pvt_dbcachesubnet_rt.id,
            'pnet_pvt_dbsubnet_rt_id': pnet_pvt_dbsubnet_rt.id,
        }
        if not skip_expensive:
            resources_data.update({
                'pnet_eip_id': pnet_eip_allocation_id,
                'pnet_natgw_id': pnet_natgw_id,
            })

        save_resource_file(resources_data, resource_type="vpc-production-network", output_file=output_file)


    if network == 'dev':
        # VPC - Development Network
        # -------------------------
        dnet_vpc = create_vpc(ec2, cidr=config.DEV_NET_VPC_CIDR, name='vpc-development-network')
        dnet_igw = create_internet_gateway(ec2, dnet_vpc, name='igw-development-network')

        dnet_pub_websubnet = create_subnet(dnet_vpc, config.DEV_NET_VPC_PUBLIC_WEBSUBNET, 'dev-net-pub-websubnet', 'us-west-2b')
        dnet_pvt_dbsubnet = create_subnet(dnet_vpc, config.DEV_NET_VPC_PVT_DBSUBNET, 'dev-net-pvt-dbsubnet', 'us-west-2b')


        dnet_pvt_dbsubnet_rt = create_route_table(dnet_vpc, 'DevNet-PrivateApp1RouteTable')
        associate_route_table(dnet_pvt_dbsubnet_rt, dnet_pvt_dbsubnet)

        dnet_pub_websubnet_rt = create_route_table(dnet_vpc, 'DevNet-PublicWebRouteTable')
        associate_route_table(dnet_pub_websubnet_rt, dnet_pub_websubnet)
        create_route(dnet_pub_websubnet_rt, '0.0.0.0/0', gateway_id=dnet_igw.id)


        print("\n--- Development Network Resources Summary ---")
        print(f"VPC ID: {dnet_vpc.id}")
        print(f"IGW ID: {dnet_igw.id}")
        print(f"Public web subnet ID: {dnet_pub_websubnet.id}")
        print(f"Private db subnet ID: {dnet_pvt_dbsubnet.id}")
        print(f"Public web subnet Route Table ID: {dnet_pub_websubnet_rt.id}")
        print(f"Private db subnet Route Table ID: {dnet_pvt_dbsubnet_rt.id}")

        # Save resource IDs to file
        # 'dnet_eip_id': dnet_eip_allocation_id,
        #'dnet_natgw_id': dnet_natgw_id,
        resources_data = {
            'dnet_vpc_id': dnet_vpc.id,
            'dnet_igw_id': dnet_igw.id,
    
            'dnet_pub_websubnet_id': dnet_pub_websubnet.id,
            'dnet_pvt_dbsubnet_id': dnet_pvt_dbsubnet.id,
    
            'dnet_pub_websubnet_rt_id': dnet_pub_websubnet_rt.id,
            'dnet_pvt_dbsubnet_rt_id': dnet_pvt_dbsubnet_rt.id,            
        }
        save_resource_file(resources_data, resource_type="vpc-development-network", output_file=output_file)

def cleanup_resources(args, skip_expensive=False):
    ec2, ec2_client = init_ec2()

    # Load resource IDs from file if specified and file exists
    resource_ids = {}
    if args.resource_file and os.path.isfile(args.resource_file):
        with open(args.resource_file, 'r') as f:
            resource_ids = json.load(f)
    else:
        if args.network == 'prod':
            # Fallback: read from CLI args
            resource_ids = {
                'pnet_vpc_id': args.pnet_vpc_id,
                'pnet_igw_id': args.pnet_igw_id,

                'pnet_pub_websubnet_id': args.pnet_pub_websubnet_id,
                'pnet_pvt_app1subnet_id': args.pnet_pvt_app1subnet_id,

                'pnet_pub_websubnet_rt_id': args.pnet_pub_websubnet_rt_id,
                'pnet_pvt_app1subnet_rt_id': args.pnet_pvt_app1subnet_rt_id,
            }
            # Set the flag to use NAT and EIP
            if not skip_expensive:
                resource_ids.update({
                    'pnet_eip_id': args.pnet_eip_id,
                    'pnet_natgw_id': args.pnet_natgw_id,
                })
        if args.network == 'dev':
            # 'dnet_eip_id': args.dnet_eip_id,
            # 'dnet_natgw_id': args.dnet_natgw_id,
            resource_ids = {
                'dnet_vpc_id': args.dnet_vpc_id,
                'dnet_igw_id': args.dnet_igw_id,
                
                'dnet_pub_websubnet_id': args.dnet_pub_websubnet_id,
                'dnet_pvt_dbsubnet_id': args.dnet_pvt_dbsubnet_id,
                
                'dnet_pub_websubnet_rt_id': args.dnet_pub_websubnet_rt_id,
                'dnet_pvt_dbsubnet_rt_id': args.dnet_pvt_dbsubnet_rt_id,
            }

    # Validate loaded IDs present
    missing = [k for k,v in resource_ids.items() if not v]
    if missing:
        print(f"Missing required resource IDs to delete: {', '.join(missing)}")
        return
    
    if args.network == 'dev':    
        #cleanup_natgw(ec2_client, resource_ids['dnet_natgw_id'])
        #release_eip(ec2_client, resource_ids['dnet_eip_id'])
        cleanup_routetables(ec2_client, [resource_ids['dnet_pvt_dbsubnet_rt_id'], resource_ids['dnet_pub_websubnet_rt_id']])
        cleanup_subnets(ec2, [resource_ids['dnet_pvt_dbsubnet_id'], resource_ids['dnet_pub_websubnet_id']])
        cleanup_igw(ec2, resource_ids['dnet_igw_id'], resource_ids['dnet_vpc_id'])
        cleanup_vpc(ec2, resource_ids['dnet_vpc_id'])

    if args.network == 'prod':
        # Set the flag to use NAT and EIP
        if not skip_expensive:
            cleanup_natgw(ec2_client, resource_ids['pnet_natgw_id'])
            release_eip(ec2_client, resource_ids['pnet_eip_id'])
        cleanup_routetables(ec2_client, [
            resource_ids['pnet_pub_websubnet_rt_id'], 
            resource_ids['pnet_pvt_app1subnet_rt_id'],
            resource_ids['pnet_pvt_app2subnet_rt_id'], 
            resource_ids['pnet_pvt_dbcachesubnet_rt_id'], 
            resource_ids['pnet_pvt_dbsubnet_rt_id'] 
            ]
        )
        cleanup_subnets(ec2, [
            resource_ids['pnet_pvt_app1subnet_id'],
            resource_ids['pnet_pvt_app2subnet_id'],
            resource_ids['pnet_pvt_dbcachesubnet_id'],
            resource_ids['pnet_pvt_dbsubnet_id'],
            resource_ids['pnet_pub_websubnet_id']
            ]
        )
        cleanup_igw(ec2, resource_ids['pnet_igw_id'], resource_ids['pnet_vpc_id'])
        cleanup_vpc(ec2, resource_ids['pnet_vpc_id'])

def main():
    parser = argparse.ArgumentParser(description='Manage AWS VPC environment')
    parser.add_argument('--action', required=True, choices=['create-vpc', 'delete-vpc', 'create-peer','delete-peer'], help='Action to perform')
    parser.add_argument('--network', choices=['dev', 'prod'], help='VPC network type either development or production')
    parser.add_argument('--resource-file', default='vpc_resources.json', help='Path to saved resource IDs JSON file (for delete)')
    # If using peer, require both VPC IDs, or read them from resources file
    parser.add_argument('--prod-vpc-id', help='Production VPC ID')
    parser.add_argument('--dev-vpc-id', help='Development VPC ID')

    # Old delete params made optional now
    parser.add_argument('--pnet-vpc-id', help='Production network VPC ID')
    parser.add_argument('--pnet-igw-id', help='Production network Internet Gateway ID')
    parser.add_argument('--pnet-private-subnet-id', help='Private Subnet ID')
    parser.add_argument('--pnet-public-subnet-id', help='Public Subnet ID')
    parser.add_argument('--pnet-eip-id', help='Elastic IP Allocation ID')
    parser.add_argument('--pnet-natgw-id', help='NAT Gateway ID')
    parser.add_argument('--pnet-private-rt-id', help='Private Route Table ID')
    parser.add_argument('--pnet-public-rt-id', help='Public Route Table ID')

    # Old delete params made optional now
    parser.add_argument('--dnet-vpc-id', help='Development Network VPC ID')
    parser.add_argument('--dnet-igw-id', help='Development Network Internet Gateway ID')
    parser.add_argument('--dnet-private-subnet-id', help='Private Subnet ID')
    parser.add_argument('--dnet-public-subnet-id', help='Public Subnet ID')
    parser.add_argument('--dnet-eip-id', help='Elastic IP Allocation ID')
    parser.add_argument('--dnet-natgw-id', help='NAT Gateway ID')
    parser.add_argument('--dnet-private-rt-id', help='Private Route Table ID')
    parser.add_argument('--dnet-public-rt-id', help='Public Route Table ID')

    args = parser.parse_args()

    skip_expensive = os.environ.get('SKIP_EXPENSIVE', '0') == '1'
    
    if args.action == 'create-vpc':
        try:
            if not args.network:
                print(f"network not specified with create")
                sys.exit(1)
            create_resources(args.network, output_file=args.resource_file, skip_expensive=skip_expensive)
        except Exception as e:
            print(f"Exception during resource creation: {e}")
            traceback.print_exc()
    elif args.action == 'delete-vpc':
        try:
            if not args.network:
                print(f"network not specified with delete")
                sys.exit(1)

            cleanup_resources(args, skip_expensive=skip_expensive)
        except Exception as e:
            print(f"Exception during cleanup: {e}")
            traceback.print_exc()
    elif args.action == 'create-peer':
        ec2_client = boto3.client('ec2', region_name=config.REGION)
        resources = {}
        print(f"prod_vpc_id {args.prod_vpc_id} dev_vpc_id {args.dev_vpc_id}")
        # Load VPC IDs from file if not provided
        if not args.prod_vpc_id or not args.dev_vpc_id:
            with open(args.resource_file) as f:
                resources = json.load(f)
            prod_vpc_id = resources.get('pnet_vpc_id')
            dev_vpc_id = resources.get('dnet_vpc_id')
            print(f"resources: {resources}")
        else:
            with open(args.resource_file) as f:
                resources = json.load(f)
            prod_vpc_id = args.prod_vpc_id
            dev_vpc_id = args.dev_vpc_id

        peering_id = create_peering(ec2_client, prod_vpc_id, dev_vpc_id)
        resources_data = {'peering_id': peering_id}
        save_resource_file(resources_data, resource_type="vpc-peering", output_file=args.resource_file)

        # Get route table IDs and CIDRs similarly from resources file
        #print(f"resources: {resources}")
        pnet_pvt_dbcachesubnet_rt_id = resources.get('pnet_pvt_dbcachesubnet_rt_id')
        pnet_pvt_dbsubnet_rt_id = resources.get('pnet_pvt_dbsubnet_rt_id')
        dnet_pvt_dbsubnet_rt_id = resources.get('dnet_pvt_dbsubnet_rt_id')
        #print(f"pnet_pvt_app1subnet_rt_id {pnet_pvt_app1subnet_rt_id} dnet_pvt_dbsubnet_rt_id {dnet_pvt_dbsubnet_rt_id}")

        # 4. Setup connection between db subnets of both production network and development network respectively.
        # Add route in production network dbcache & db subnet route tables for DEV CIDR with destination peering id
        add_peering_routes(ec2_client, pnet_pvt_dbcachesubnet_rt_id, config.DEV_NET_VPC_CIDR, peering_id)
        add_peering_routes(ec2_client, pnet_pvt_dbsubnet_rt_id, config.DEV_NET_VPC_CIDR, peering_id)

        # Add route in development network  subnet route table for PROD CIDR with destination peering id
        add_peering_routes(ec2_client, dnet_pvt_dbsubnet_rt_id, config.PROD_NET_VPC_CIDR, peering_id)

    elif args.action == 'delete-peer':
        ec2_client = boto3.client('ec2', region_name=config.REGION)
        resources = json.load(open(args.resource_file))
        peering_id = resources.get('peering_id')
        pnet_pvt_dbcachesubnet_rt_id = resources.get('pnet_pvt_dbcachesubnet_rt_id')
        pnet_pvt_dbsubnet_rt_id = resources.get('pnet_pvt_dbsubnet_rt_id')
        dnet_pvt_dbsubnet_rt_id = resources.get('dnet_pvt_dbsubnet_rt_id')

        ec2_client.delete_route(RouteTableId=pnet_pvt_dbcachesubnet_rt_id, DestinationCidrBlock=config.DEV_NET_VPC_CIDR)
        print(f"Deleted route to {config.DEV_NET_VPC_CIDR} from route table {pnet_pvt_dbcachesubnet_rt_id}")
        ec2_client.delete_route(RouteTableId=pnet_pvt_dbsubnet_rt_id, DestinationCidrBlock=config.DEV_NET_VPC_CIDR)
        print(f"Deleted route to {config.DEV_NET_VPC_CIDR} from route table {pnet_pvt_dbsubnet_rt_id}")
        ec2_client.delete_route(RouteTableId=dnet_pvt_dbsubnet_rt_id, DestinationCidrBlock=config.PROD_NET_VPC_CIDR)
        print(f"Deleted route to {config.PROD_NET_VPC_CIDR} from route table {dnet_pvt_dbsubnet_rt_id}")
        
        ec2_client.delete_vpc_peering_connection(VpcPeeringConnectionId=peering_id)
        print(f"Deleted VPC peering")

if __name__ == '__main__':
    main()
