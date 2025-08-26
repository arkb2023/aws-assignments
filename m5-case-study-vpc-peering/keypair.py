import boto3
import traceback
import argparse
import os
import stat
import json

region = 'us-west-2'  # Oregon
RESOURCE_FILE_DEFAULT = 'keypair_resources.json'

def save_keypair_info(key_name, key_file, filename=RESOURCE_FILE_DEFAULT):
    data = {
        'key_name': key_name,
        'key_file': key_file
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved key pair info to {filename}")

def load_keypair_info(filename=RESOURCE_FILE_DEFAULT):
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data.get('key_name'), data.get('key_file')
    else:
        return None, None

def main():
    parser = argparse.ArgumentParser(description='Manage AWS EC2 Key Pair')
    parser.add_argument('--action', required=True, choices=['create', 'delete'], help='Action to perform')
    parser.add_argument('--key-name', default='MyKeyPair', help='Key pair name')
    parser.add_argument('--key-file', default='MyKeyPair.pem', help='Local key file path')
    parser.add_argument('--resource-file', default=RESOURCE_FILE_DEFAULT, help='JSON file to save/load key pair info')
    args = parser.parse_args()

    ec2_client = boto3.client('ec2', region_name=region)

    try:
        if args.action == 'create':
            response = ec2_client.create_key_pair(KeyName=args.key_name)
            private_key = response['KeyMaterial']

            with open(args.key_file, 'w', encoding='utf-8', newline='\n') as file:
                file.write(private_key)

            os.chmod(args.key_file, stat.S_IRUSR | stat.S_IWUSR)
            print(f"Created key pair {args.key_name} and saved private key to {args.key_file}")

            save_keypair_info(args.key_name, args.key_file, filename=args.resource_file)

        elif args.action == 'delete':
            # Load key pair info from file if it exists
            key_name, key_file = load_keypair_info(filename=args.resource_file)

            # Fallback to CLI args if file missing or incomplete
            if not key_name:
                key_name = args.key_name
            if not key_file:
                key_file = args.key_file

            ec2_client.delete_key_pair(KeyName=key_name)
            print(f"Deleted key pair: {key_name}")

            if os.path.isfile(key_file):
                os.remove(key_file)
                print(f"Deleted local key file: {key_file}")
            else:
                print(f"Local key file not found: {key_file}")

    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
    finally:
        print("Operation completed.")

if __name__ == '__main__':
    main()
