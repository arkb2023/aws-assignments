
```markdown
## Module 6: S3 Website Hosting

### Problem Statement
You work for XYZ Corporation. Their application requires a storage service that
can store files and publicly share them if required. Implement S3 for the same.

### Tasks To Be Performed
1. Use the created bucket in the previous task to host static websites, upload an index.html file and error.html page.
2. Add a lifecycle rule for the bucket:
    a. Transition from Standard to Standard-IA in 60 days
    b. Expiration in 200 days

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
Create bucket and upload files as per 
  i) <repo>/m6-a01-s3-bkt-create/README.md
  ii) <repo>/m6-a02-s3-bkt-create/README.md
```
## Enable Static Website Hosting on S3 Bucket
```bash
aws s3 website s3://$bkt_name/ --index-document index.html --error-document error.html
```

---

## Upload Website Files

```bash
aws s3 cp index.html s3://$bkt_name/index.html
aws s3 cp error.html s3://$bkt_name/error.html
```

---

## Disable Block Public Access at Bucket Level

### `block-public-access.json`

```json
{
  "BlockPublicAcls": false,
  "IgnorePublicAcls": false,
  "BlockPublicPolicy": false,
  "RestrictPublicBuckets": false
}
```

### Apply Settings

```bash
aws s3api put-public-access-block --bucket $bkt_name --public-access-block-configuration file://block-public-access.json
```

---

## Make Objects Publicly Readable

### `public-read-policy.json`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::<bkt_name>/*"
    }
  ]
}
```

### Replace Placeholder and Apply Policy

```bash
sed "s/<bkt_name>/$bkt_name/g" public-read-policy.json > tmp-policy.json
cat tmp-policy.json
```

Output:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::bkt-20250830140412/*"
    }
  ]
}
```

```bash
aws s3api put-bucket-policy --bucket $bkt_name --policy file://tmp-policy.json
```

---

## Verify Website Configuration

```bash
aws s3api get-bucket-website --bucket $bkt_name
```

Output:

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  },
  "ErrorDocument": {
    "Key": "error.html"
  }
}
```

---

## Test Website Access

### Fetch `index.html`

```bash
curl -i http://$bkt_name.s3-website-$AWS_DEFAULT_REGION.amazonaws.com | head -n 20
```

Output:

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1520  100  1520    0     0   2010      0 --:--:-- --:--:-- --:--:--  2010
HTTP/1.1 200 OK
x-amz-id-2: pzWAY78AQZINJLRzKaICBkryxULNG9zFEwH9zcn/f/HULsmlz7eo5WYo1u5UHboFin8znh76ZDo=
x-amz-request-id: 763T7BTQ1ABR3Z30
Date: Sat, 30 Aug 2025 17:39:58 GMT
Last-Modified: Sat, 30 Aug 2025 17:18:36 GMT
x-amz-version-id: SeOtZt8JQiiKy5dJaAjyMMU4fJaVXzEU
ETag: "7e2277780fd6a5a42d74dc17dc744ff0"
Content-Type: text/html
Content-Length: 1520
Server: AmazonS3

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample file for testing</title>
    <META NAME="robots" CONTENT="noindex,nofollow">
</head>
```

---

### Test Error Page

```bash
curl -i http://$bkt_name.s3-website-$AWS_DEFAULT_REGION.amazonaws.com/nonexistent.html | head -n 5
```

Output:

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   783  100   783    0     0   1022      0 --:--:-- --:--:-- --:--:--  1022
HTTP/1.1 404 Not Found
Last-Modified: Sat, 30 Aug 2025 17:18:31 GMT
x-amz-version-id: .L9k0FWwLSaSADXyntupnchyLRTQOSG4
ETag: "aacf4ed89973dad8c5bd0945b81efee5"
x-amz-error-code: NoSuchKey
```

---

## Lifecycle Configuration

### Apply Lifecycle Rules

```bash
aws s3api put-bucket-lifecycle-configuration --bucket $bkt_name --lifecycle-configuration file://lifecycle.json
```

Output:

```json
{
  "TransitionDefaultMinimumObjectSize": "all_storage_classes_128K"
}
```

### Verify Lifecycle Rules

```bash
aws s3api get-bucket-lifecycle-configuration --bucket $bkt_name
```

Output:

```json
{
  "TransitionDefaultMinimumObjectSize": "all_storage_classes_128K",
  "Rules": [
    {
      "ID": "Standard to Standard-IA transition rule",
      "Filter": {},
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 60,
          "StorageClass": "STANDARD_IA"
        }
      ]
    },
    {
      "Expiration": {
        "Days": 200
      },
      "ID": "200 days expiry rule",
      "Filter": {},
      "Status": "Enabled"
    }
  ]
}
```

---

## Cleanup Steps

### Delete All Object Versions

```bash
python3 delete_s3_objects.py $bkt_name
```

Output:

```
Deleting all object versions and delete markers from bucket: bkt-20250830140412
Deleted 13 objects/versions in this batch
Deletion of all object versions and delete markers completed.
```

### Remove Lifecycle Rules

```bash
aws s3api delete-bucket-lifecycle --bucket $bkt_name
```

### Delete Bucket Policy

```bash
aws s3api delete-bucket-policy --bucket $bkt_name
```

### Remove Website Hosting Configuration

```bash
aws s3api delete-bucket-website --bucket $bkt_name
```

### Delete the Bucket

```bash
aws s3api delete-bucket --bucket $bkt_name
```
```
