## 1. Create policy number 1 which lets the users to:
**a. Access S3 completely**

**b. Only create EC2 instances**

**c. Full access to RDS**

<!-- Use https://awspolicygen.s3.amazonaws.com/policygen.html to generate json formatted polcy -->
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Statement1",
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    },
    {
      "Sid": "Statement2",
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Statement3",
      "Effect": "Allow",
      "Action": "rds:*",
      "Resource": "*"
    }
  ]
}
```
```
# Set POLICY_NUMBER1 env variable
  $ aws iam create-policy --policy-name $POLICY_NUMBER1 --policy-document file://policy1.json
{
    "Policy": {
        "PolicyName": "PolicyNumber1",
        "PolicyId": "<REDACTED_POLICY_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:policy/PolicyNumber1",
        "Path": "/",
        "DefaultVersionId": "v1",
        "AttachmentCount": 0,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2025-08-12T08:57:47Z",
        "UpdateDate": "2025-08-12T08:57:47Z"
    }
}
```
## 2. Create a policy number 2 which allows the users to:
**a. Access CloudWatch and billing completely**
**b. Can only list EC2 and S3 resources**
<!-- Use https://awspolicygen.s3.amazonaws.com/policygen.html to generate json formatted polcy -->
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Statement1",
      "Effect": "Allow",
      "Action": "cloudwatch:*",
      "Resource": "*"
    },
    {
      "Sid": "Statement2",
      "Effect": "Allow",
      "Action": "billing:*",
      "Resource": "*"
    },
    {
      "Sid": "Statement3",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Statement4",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "*"
    }
  ]
}
```
```
 $ aws iam create-policy --policy-name $POLICY_NUMBER2 --policy-document file://policy2.json
{
    "Policy": {
        "PolicyName": "PolicyNumber2",
        "PolicyId": "<REDACTED_POLICY_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:policy/PolicyNumber2",
        "Path": "/",
        "DefaultVersionId": "v1",
        "AttachmentCount": 0,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2025-08-12T09:11:06Z",
        "UpdateDate": "2025-08-12T09:11:06Z"
    }
}
```

## 3. Attach policy number 1 to the Dev Team from Task 1
```
# Get the ARN for Policy1
 $ POLICY1_ARN=$(aws iam list-policies --scope Local --query "Policies[?PolicyName=='${POLICY_NUMBER1}'].Arn" --output text)
 $ aws iam attach-group-policy --group-name $DEV_TEAM_GROUP --policy-arn "${POLICY1_ARN}"
```
## 4. Attach policy number 2 to the Ops Team from Task 1
# Get the ARN for Policy2
 $ POLICY2_ARN=$(aws iam list-policies --scope Local --query "Policies[?PolicyName=='${POLICY_NUMBER2}'].Arn" --output text)
 $ aws iam attach-group-policy --group-name $OPS_TEAM_GROUP --policy-arn "${POLICY2_ARN}"
 ```
