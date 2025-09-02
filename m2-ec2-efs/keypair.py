import boto3
import traceback
import argparse
import os
import sys
import stat
import config

def main():
    parser = argparse.ArgumentParser(description='Manage AWS EC2 Key Pair')
    parser.add_argument('--action', required=True, choices=['create', 'delete'], help='Action to perform')
    parser.add_argument('--key-name', default='MyKeyPair', help='Key pair name')
    parser.add_argument('--key-file', default='MyKeyPair.pem', help='Local key file path')
    args = parser.parse_args()

    ec2_client = boto3.client('ec2', region_name=config.REGION)

    try:
        if args.action == 'create':
            response = ec2_client.create_key_pair(KeyName=args.key_name)
            private_key = response['KeyMaterial']

            with open(args.key_file, 'w', encoding='utf-8', newline='\n') as file:
                file.write(private_key)

            os.chmod(args.key_file, stat.S_IRUSR | stat.S_IWUSR)
            print(f"Created key pair {args.key_name} and saved private key to {args.key_file}")

        elif args.action == 'delete':
            if not args.key_name or not args.key_file:
                print("--key-name, --key-file are required for delete")
                sys.exit(1)

            ec2_client.delete_key_pair(KeyName=args.key_name)
            print(f"Deleted key pair: {args.key_name}")

            if os.path.isfile(args.key_file):
                os.remove(args.key_file)
                print(f"Deleted local key file: {args.key_file}")
            else:
                print(f"Local key file not found: {args.key_file}")

    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
    finally:
        print("Operation completed.")

if __name__ == '__main__':
    main()
