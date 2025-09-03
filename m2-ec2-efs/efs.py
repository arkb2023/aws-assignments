import boto3
import traceback
import argparse
import config


def main():
    parser = argparse.ArgumentParser(description='Manage EFS resources')
    parser.add_argument('--action', required=True, choices=['create-efs', 'create-mount-target', 'delete-efs', 'delete-mount-target'],
                        help='Action to perform')

    parser.add_argument('--efs-id', help='EFS FileSystem ID (required for mount target actions and delete-efs)')
    parser.add_argument('--subnet-id', help='Subnet ID (required for create-mount-target)')
    parser.add_argument('--sg-id', help='Security Group ID (required for create-mount-target)')
    parser.add_argument('--mount-target-id', help='Mount Target ID (required for delete-mount-target)')

    args = parser.parse_args()

    efs_client = boto3.client('efs', region_name=config.REGION)

    try:
        if args.action == 'create-efs':
            response = efs_client.create_file_system(
                PerformanceMode='generalPurpose',
                Tags=[{'Key': 'Name', 'Value': config.EFS_NAME}]
            )
            efs_id = response['FileSystemId']
            print(f"EFS FileSystemId: {efs_id}")

        elif args.action == 'create-mount-target':
            if not args.efs_id or not args.sg_id or not args.subnet_id:
                parser.error("--efs-id, --sg-id, and --subnet-id are required for create-mount-target")
            response = efs_client.create_mount_target(
                FileSystemId=args.efs_id,
                SubnetId=args.subnet_id,
                SecurityGroups=[args.sg_id]
            )
            print(f"Created mount target ID: {response['MountTargetId']} for EFS {args.efs_id}")

        elif args.action == 'delete-mount-target':
            if not args.mount_target_id:
                parser.error("--mount-target-id is required for delete-mount-target")
            efs_client.delete_mount_target(MountTargetId=args.mount_target_id)
            print(f"Deleted mount target {args.mount_target_id}")

        elif args.action == 'delete-efs':
            if not args.efs_id:
                parser.error("--efs-id is required for delete-efs")
            # Before deleting EFS, all mount targets must be deleted
            mount_targets = efs_client.describe_mount_targets(FileSystemId=args.efs_id).get('MountTargets', [])
            if mount_targets:
                print(f"Cannot delete EFS {args.efs_id} because it has mount targets. Please delete them first.")
                for mt in mount_targets:
                    print(f"Mount Target ID: {mt['MountTargetId']}, Subnet: {mt['SubnetId']}")
            else:
                efs_client.delete_file_system(FileSystemId=args.efs_id)
                print(f"Deleted EFS filesystem {args.efs_id}")

    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    main()
