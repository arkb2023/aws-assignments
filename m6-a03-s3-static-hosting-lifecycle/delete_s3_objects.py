import boto3
import sys

def delete_all_objects_versions(bucket_name):
    s3 = boto3.client('s3')

    # Delete all object versions
    paginator = s3.get_paginator('list_object_versions')
    print(f"Deleting all object versions and delete markers from bucket: {bucket_name}")

    try:
        for page in paginator.paginate(Bucket=bucket_name):
            objects_to_delete = []

            # Add versions to delete list
            versions = page.get('Versions', [])
            for version in versions:
                objects_to_delete.append({'Key': version['Key'], 'VersionId': version['VersionId']})

            # Add delete markers to delete list
            delete_markers = page.get('DeleteMarkers', [])
            for marker in delete_markers:
                objects_to_delete.append({'Key': marker['Key'], 'VersionId': marker['VersionId']})

            if objects_to_delete:
                # AWS allows deleting up to 1000 objects per request
                for i in range(0, len(objects_to_delete), 1000):
                    chunk = objects_to_delete[i:i+1000]
                    response = s3.delete_objects(Bucket=bucket_name, Delete={'Objects': chunk})
                    deleted = response.get('Deleted', [])
                    print(f"Deleted {len(deleted)} objects/versions in this batch")
            else:
                print("No objects or versions found to delete.")
                break

        print("Deletion of all object versions and delete markers completed.")

    except Exception as e:
        print(f"Error during deletion: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <bucket-name>")
        sys.exit(1)
    bucket = sys.argv[1]
    delete_all_objects_versions(bucket)
