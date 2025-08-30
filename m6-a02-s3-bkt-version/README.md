```markdown
## Module 6: S3 Bucket Creation

### Problem Statement
You work for XYZ Corporation. Their application requires a storage service that can store files and publicly share them if required. Implement S3 for the same.

### Tasks To Be Performed
1. Enable versioning for the bucket created in task 1
2. Re-upload any 2 files already uploaded to verify if versioning works
```
---
### Solution
```bash
# Set AWS region
export AWS_DEFAULT_REGION=us-west-2 # Oregon, for sandbox/testing
```
---
### Prequisite
```
Create bucket and upload files as per <repo>/m6-a01-s3-bkt-create/README.md
```

```bash
# check the current version
$ aws s3api list-object-versions --bucket $bkt_name --prefix example.txt --query "Versions[].{Key: Key, VersionId: VersionId, Size: Size, LastModified: LastModified, ETag: ETag}" --output json
# Example Output
[
    {
        "Key": "example.txt",
        "VersionId": "null",
        "Size": 232,
        "LastModified": "2025-08-30T09:24:04.000Z",
        "ETag": "\"d7a96bb599e6e9d6d9eb7368f0cfb6f4\""
    }
]
$ aws s3api list-object-versions --bucket $bkt_name --prefix example.csv --query "Versions[].{Key: Key, VersionId: VersionId, Size: Size, LastModified: LastModified, ETag: ETag}" --output json
[
    {
        "Key": "example.csv",
        "VersionId": "null",
        "Size": 15799,
        "LastModified": "2025-08-30T09:24:32.000Z",
        "ETag": "\"2229607d9006b37d3dae647e63d8b1b6\""
    }
]
```
### Enable versioning on bucket
```bash
$ aws s3api put-bucket-versioning --bucket $bkt_name --versioning-configuration Status=Enabled
```
```bash
# Confirmed versioning enabled on bucket
$ aws s3api get-bucket-versioning --bucket $bkt_name
{
    "Status": "Enabled"
}
```
---
2. Re-upload any 2 files already uploaded to verify if versioning works

```bash
$ aws s3api put-object --bucket $bkt_name --key example.txt --body ../m6-a01-s3-bkt-create/example.txt
{
    "ETag": "\"d7a96bb599e6e9d6d9eb7368f0cfb6f4\"",
    "ChecksumCRC32": "GB+HSg==",
    "ChecksumType": "FULL_OBJECT",
    "ServerSideEncryption": "AES256",
    "VersionId": "wCYf3iF_N3v0XHwU7eAxd71TIGcFlstW"
}
```
```bash
$ aws s3api put-object --bucket $bkt_name --key example.csv --body ../m6-a01-s3-bkt-create/example.csv
{
    "ETag": "\"2229607d9006b37d3dae647e63d8b1b6\"",
    "ChecksumCRC32": "40Ibrw==",
    "ChecksumType": "FULL_OBJECT",
    "ServerSideEncryption": "AES256",
    "VersionId": "aOJ2e0y7kGnEQcpIlHSdDIqRnLq1fqHY"
}
```
### Verify Uploaded Files
```bash
$ aws s3api list-object-versions --bucket $bkt_name --prefix example.csv --query "Versions[].{Key: Key, VersionId: VersionId, Size: Size, LastModified: LastModified, ETag: ETag}" --output json
[
    {
        "Key": "example.csv",
        "VersionId": "aOJ2e0y7kGnEQcpIlHSdDIqRnLq1fqHY",
        "Size": 15799,
        "LastModified": "2025-08-30T10:47:56.000Z",
        "ETag": "\"2229607d9006b37d3dae647e63d8b1b6\""
    },
    {
        "Key": "example.csv",
        "VersionId": "null",
        "Size": 15799,
        "LastModified": "2025-08-30T09:24:32.000Z",
        "ETag": "\"2229607d9006b37d3dae647e63d8b1b6\""
    }
]

$ aws s3api list-object-versions --bucket $bkt_name --prefix example.txt --query "Versions[].{Key: Key, VersionId: VersionId, Size: Size, LastModified: LastModified, ETag: ETag}" --output json
[
    {
        "Key": "example.txt",
        "VersionId": "wCYf3iF_N3v0XHwU7eAxd71TIGcFlstW",
        "Size": 232,
        "LastModified": "2025-08-30T10:46:26.000Z",
        "ETag": "\"d7a96bb599e6e9d6d9eb7368f0cfb6f4\""
    },
    {
        "Key": "example.txt",
        "VersionId": "null",
        "Size": 232,
        "LastModified": "2025-08-30T09:24:04.000Z",
        "ETag": "\"d7a96bb599e6e9d6d9eb7368f0cfb6f4\""
    }
]
```



