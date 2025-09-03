```markdown
## Module 6: S3 Bucket Creation

### Problem Statement
You work for XYZ Corporation. Their application requires a storage service that can store files and publicly share them if required. Implement S3 for the same.

### Tasks To Be Performed
1. Create an S3 Bucket for file storage.  
2. Upload 5 objects with different file extensions.
```
---

### Solution
```bash
# Set AWS region
export AWS_DEFAULT_REGION=us-west-2 # Oregon, for sandbox/testing
```
```bash
# Generate a unique bucket name
bkt_name=bkt-$(date +%Y%m%d%H%M%S)
echo $bkt_name
# Example output:
bkt-20250830140412
```
### Create S3 bucket
```bash
aws s3api create-bucket --region $AWS_DEFAULT_REGION --bucket $bkt_name \
    --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION
# Example output:
{
    "Location": "http://bkt-20250830140412.s3.amazonaws.com/"
}
```
```bash
# List buckets
aws s3api list-buckets --query "Buckets[].Name"
# Example output:
[
    "bkt-20250830140412"
]
```

---

### Upload objects
```bash
ls -ltr
# Example output:
-rw-r--r-- 1 arkane arkane 102602 Sep  5  2021 example.pdf
-rw-r--r-- 1 arkane arkane  48396 Nov 21  2022 example.jpg
-rw-r--r-- 1 arkane arkane   1520 Mar 18  2023 index.html
-rw-r--r-- 1 arkane arkane    232 Jul 15  2024 example.txt
-rw-r--r-- 1 arkane arkane  15799 Jul 15  2024 example.csv
-rw-r--r-- 1 arkane arkane   5249 Aug 30 07:33 README.md
-rw-r--r-- 1 arkane arkane    783 Aug 30 09:13 error.html
-rw-r--r-- 1 arkane arkane 123422 Aug 30 09:16 example.zip
```

---

```bash
aws s3api put-object --bucket $bkt_name --key example.pdf --body example.pdf
# Example output:
{
    "ETag": "\"b1157391bc54f3a3b5289fbd65e1a0eb\"",
    "ChecksumCRC32": "rIQILg==",
    "ChecksumType": "FULL_OBJECT",
    "ServerSideEncryption": "AES256"
}
```
```bash
aws s3api put-object --bucket $bkt_name --key example.jpg --body example.jpg
# Example output:
{
    "ETag": "\"5df5fcf3b7bcbaf320081517b2aea397\"",
    "ChecksumCRC32": "I8Hp4Q==",
    "ChecksumType": "FULL_OBJECT",
    "ServerSideEncryption": "AES256"
}
```
```bash
aws s3api put-object --bucket $bkt_name --key example.txt --body example.txt
# Example output:
{
    "ETag": "\"d7a96bb599e6e9d6d9eb7368f0cfb6f4\"",
    "ChecksumCRC32": "GB+HSg==",
    "ChecksumType": "FULL_OBJECT",
    "ServerSideEncryption": "AES256"
}
```
```bash
aws s3api put-object --bucket $bkt_name --key example.csv --body example.csv
# Example output:
{
    "ETag": "\"2229607d9006b37d3dae647e63d8b1b6\"",
    "ChecksumCRC32": "40Ibrw==",
    "ChecksumType": "FULL_OBJECT",
    "ServerSideEncryption": "AES256"
}
```
```bash
aws s3api put-object --bucket $bkt_name --key example.zip --body example.zip
# Example output:
{
    "ETag": "\"1b39c3661286772bb74f40360e57de5d\"",
    "ChecksumCRC32": "b3MBLQ==",
    "ChecksumType": "FULL_OBJECT",
    "ServerSideEncryption": "AES256"
}
```

---

### Verify Uploaded Files

```bash
aws s3 ls s3://$bkt_name/
# Example output:
2025-08-30 09:24:32      15799 example.csv
2025-08-30 09:23:08      48396 example.jpg
2025-08-30 09:22:07     102602 example.pdf
2025-08-30 09:24:04        232 example.txt
2025-08-30 09:24:50     123422 example.zip
```