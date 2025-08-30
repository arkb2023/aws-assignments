

# Enable static website hosting on your bucket:
aws s3 website s3://$bkt_name/ --index-document index.html --error-document error.html

# Upload the index.html and error.html files:
aws s3 cp index.html s3://$bkt_name/index.html
aws s3 cp error.html s3://$bkt_name/error.html

# Policy to Disable Block Public Access at Bucket Level
$ cat block-public-access.json
{
  "BlockPublicAcls": false,
  "IgnorePublicAcls": false,
  "BlockPublicPolicy": false,
  "RestrictPublicBuckets": false
}
$
# Apply the settings
aws s3api put-public-access-block --bucket $bkt_name --public-access-block-configuration file://block-public-access.json

# Make the objects publicly readable by applying this bucket policy
$ cat public-read-policy.json
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
# Replace <bkt_name> with the actual bucket name in the JSON file
$ sed "s/<bkt_name>/$bkt_name/g" public-read-policy.json > tmp-policy.json
$ cat tmp-policy.json
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
# Apply the policy
$ aws s3api put-bucket-policy --bucket $bkt_name --policy file://tmp-policy.json

# Fetch website configuration
$ aws s3api get-bucket-website --bucket $bkt_name
{
    "IndexDocument": {
        "Suffix": "index.html"
    },
    "ErrorDocument": {
        "Key": "error.html"
    }
}

# Fetch the index.html page content.
$ curl -i http://$bkt_name.s3-website-$AWS_DEFAULT_REGION.amazonaws.com | head -n 20
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
$

# To test the error page (e.g., a non-existent path):
$ curl -i http://$bkt_name.s3-website-$AWS_DEFAULT_REGION.amazonaws.com/nonexistent.html | head -n 5
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   783  100   783    0     0   1022      0 --:--:-- --:--:-- --:--:--  1022
HTTP/1.1 404 Not Found
Last-Modified: Sat, 30 Aug 2025 17:18:31 GMT
x-amz-version-id: .L9k0FWwLSaSADXyntupnchyLRTQOSG4
ETag: "aacf4ed89973dad8c5bd0945b81efee5"
x-amz-error-code: NoSuchKey
$


----------

cat lifecycle.json
$ aws s3api put-bucket-lifecycle-configuration --bucket $bkt_name --lifecycle-configuration file://lifecycle.json
{
    "TransitionDefaultMinimumObjectSize": "all_storage_classes_128K"
}
$ aws s3api get-bucket-lifecycle-configuration --bucket $bkt_name
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


# Cleanup
# Delete all object versions
$ python3 delete_s3_objects.py $bkt_name
Deleting all object versions and delete markers from bucket: bkt-20250830140412
Deleted 13 objects/versions in this batch
Deletion of all object versions and delete markers completed.

# Removes all lifecycle rules configured on the bucket.
$ aws s3api delete-bucket-lifecycle --bucket $bkt_name

# Delete the bucket policy
aws s3api delete-bucket-policy --bucket $bkt_name

# Remove static website hosting configuration
$ aws s3api delete-bucket-website --bucket $bkt_name

# Delete the bucket
$ aws s3api delete-bucket --bucket $bkt_name
