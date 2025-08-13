## 1. Create a role which only lets user1 and user2 from task 1 to have complete access to VPCs and DynamoDB.

## Prerequisites
```
$ USER1="user1"
$ USER2="user2"
$ USER1_PASSWORD=<set-value>    ;# Set the value
$ USER2_PASSWORD=<set-value>    ;# Set the value
$ VPC_DYNDB_FULLACCESS_POLICY_NAME="VPCDynamoDBFullAccessPolicy"
$ VPC_DYNDB_FULLACCESS_POLICY_PROFILE="vpc-dynamodb-full-access.json"
$ VPC_DYNDB_ACCESS_ROLE_NAME="VPCDynamoDBAccessRole"
$ VPC_DYNDB_ACCESS_ROLE_PROFILE_WITHOUT_ARN="trust-policy.json"
$ VPC_DYNDB_ACCESS_ROLE_PROFILE_WITH_ARN="trust-policy_arn.secret.json"
$ FILE_PREFIX="file://"

```
**Create User2**
```
 $ aws iam create-user --user-name $USER1
{
    "User": {
        "Path": "/",
        "UserName": "user1",
        "UserId": "<REDACTED_USER_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:user/user1",
        "CreateDate": "2025-08-12T05:23:23Z"
    }
}
```
**Create Password**
```
 $ aws iam create-login-profile --user-name $USER1 --password $USER1_PASSWORD
{
    "LoginProfile": {
        "UserName": "user1",
        "CreateDate": "2025-08-12T06:46:09Z",
        "PasswordResetRequired": false
    }
}
```
**Create User2**
```
 $ aws iam create-user --user-name $USER2
{
    "User": {
        "Path": "/",
        "UserName": "user2",
        "UserId": "<REDACTED_USER_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:user/user2",
        "CreateDate": "2025-08-12T05:23:23Z"
    }
}
```
**Create Password**
```
 $ aws iam create-login-profile --user-name $USER2 --password $USER2_PASSWORD
{
    "LoginProfile": {
        "UserName": "user2",
        "CreateDate": "2025-08-12T06:46:09Z",
        "PasswordResetRequired": false
    }
}
```
**Get ARNs dynamically for user1 and user2**
```
USER1_ARN=$(aws iam get-user --user-name ${USER1} --query 'User.Arn' --output text)
USER2_ARN=$(aws iam get-user --user-name ${USER2} --query 'User.Arn' --output text)
```
# Replace placeholders in trust policy and save to a usable file
```
sed -e "s|<USER1_ARN>|$USER1_ARN|" -e "s|<USER2_ARN>|$USER2_ARN|" \
    ${VPC_DYNDB_ACCESS_ROLE_PROFILE_WITHOUT_ARN} > \
    ${VPC_DYNDB_ACCESS_ROLE_PROFILE_WITH_ARN}
```

## Creating the Policy
```
$ aws iam create-policy --policy-name ${VPC_DYNDB_FULLACCESS_POLICY_NAME} \
    --policy-document ${FILE_PREFIX}${VPC_DYNDB_FULLACCESS_POLICY_PROFILE}
{
    "Policy": {
        "PolicyName": "VPCDynamoDBFullAccessPolicy",
        "PolicyId": "<REDACTED_POLICY_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:policy/VPCDynamoDBFullAccessPolicy",
        "Path": "/",
        "DefaultVersionId": "v1",
        "AttachmentCount": 0,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2025-08-13T02:32:32Z",
        "UpdateDate": "2025-08-13T02:32:32Z"
    }
}
```
# fetch the policy ARN
```
$ POLICY_ARN=$(aws iam list-policies --scope Local \
    --query "Policies[?PolicyName=='${VPC_DYNDB_FULLACCESS_POLICY_NAME}'].Arn" \
    --output text)
```

## Create the Role
```
$ aws iam create-role --role-name ${VPC_DYNDB_ACCESS_ROLE_NAME} \
    --assume-role-policy-document ${FILE_PREFIX}${VPC_DYNDB_ACCESS_ROLE_PROFILE_WITH_ARN}
{
    "Role": {
        "Path": "/",
        "RoleName": "VPCDynamoDBAccessRole",
        "RoleId": "<REDACTED_ROLE_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:role/VPCDynamoDBAccessRole",
        "CreateDate": "2025-08-13T02:37:55Z",
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            "arn:aws:iam::<REDACTED_ACCOUNT_ID>:user/user1",
                            "arn:aws:iam::<REDACTED_ACCOUNT_ID>:user/user2"
                        ]
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    }
}    
```
Kane
## Attach the Policy to the Role
```
$ aws iam attach-role-policy --role-name ${VPC_DYNDB_ACCESS_ROLE_NAME} \
    --policy-arn $POLICY_ARN
```


## 2. Login into user1 and shift to the role to test out the feature

```
Use console to download user1's Access Key ID and Secret

$ aws configure --profile ${USER1}
<<Enter credentials when prompted>>
```
# Use sts assume-role to get temporary credentials for the role
```
$ ROLE_ARN=$(aws iam get-role --role-name ${VPC_DYNDB_ACCESS_ROLE_NAME} \
    --query 'Role.Arn' --output text)
$ aws sts assume-role --role-arn "$ROLE_ARN" \
  --role-session-name testSession --profile ${USER1}
{
    "Credentials": {
        "AccessKeyId": "<REDACTED_ACCESSKEYID>",
        "SecretAccessKey": "<REDACTED_SECRETACCESSKEY>",
        "SessionToken": "<REDACTED_SESSIONTOKEN>",
        "Expiration": "2025-08-13T04:33:57Z"
    },
    "AssumedRoleUser": {
        "AssumedRoleId": "<REDACTED_ASSUMEDROLEID>:testSession",
        "Arn": "arn:aws:sts::<REDACTED_ACCOUNTID>:assumed-role/VPCDynamoDBAccessRole/testSession"
    }
}
```
# Activate the assumed role by setting environment variables
```
$ export AWS_ACCESS_KEY_ID='<AccessKeyId from sts output>'
$ export AWS_SECRET_ACCESS_KEY='<SecretAccessKey from sts output>'
$ export AWS_SESSION_TOKEN='<SessionToken from sts output>'
```
## Test Role Permissions
```
# Describe VPC action is allowed
$ aws ec2 describe-vpcs
{
    "Vpcs": [
        {
            "OwnerId": "<REDACTED_ACCOUNT_ID>",
            "InstanceTenancy": "default",
            "CidrBlockAssociationSet": [
                {
                    "AssociationId": "vpc-cidr-assoc-0a18afaa04b8b73a1",
                    "CidrBlock": "172.31.0.0/16",
                    "CidrBlockState": {
                        "State": "associated"
                    }
                }
            ],
            "IsDefault": true,
            "BlockPublicAccessStates": {
                "InternetGatewayBlockMode": "off"
            },
            "VpcId": "vpc-08f99ebea88dffd75",
            "State": "available",
            "CidrBlock": "172.31.0.0/16",
            "DhcpOptionsId": "dopt-08f82c8f88afaef58"
        }
    ]
}

# DynamoDB table list is allowed
$ aws dynamodb list-tables
{
    "TableNames": []
}

# S3 bucket list is not allowed
$ aws s3 ls
An error occurred (AccessDenied) when calling the ListBuckets operation: User: arn:aws:sts::<REDACTED_ACCOUNTID>:assumed-role/VPCDynamoDBAccessRole/testSession is not authorized to perform: s3:ListAllMyBuckets because no identity-based policy allows the s3:ListAllMyBuckets action

# repeat the same tests with user2
```

## Clean Up
```
# clear assumed role environment
$ unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

# clear role and policy
$ aws iam detach-role-policy --role-name ${VPC_DYNDB_ACCESS_ROLE_NAME} \
    --policy-arn "$POLICY_ARN"
$ aws iam delete-role --role-name ${VPC_DYNDB_ACCESS_ROLE_NAME}
$ aws iam delete-policy --policy-arn "$POLICY_ARN"

# delete user1
$ aws iam list-access-keys --user-name ${USER1} \
    --query "AccessKeyMetadata[].AccessKeyId" --output text
<ACCESSKEY>
$ aws iam delete-access-key --user-name ${USER1} \
    --access-key-id <ACCESSKEY>
$ aws iam delete-login-profile --user-name ${USER1}
$ aws iam delete-user --user-name ${USER1}

# delete user2
$ aws iam list-access-keys --user-name ${USER2} \
    --query "AccessKeyMetadata[].AccessKeyId" --output text
<ACCESSKEY>
$ aws iam delete-access-key --user-name ${USER2} \
    --access-key-id <ACCESSKEY>
$ aws iam delete-login-profile --user-name ${USER2}
$ aws iam delete-user --user-name ${USER2}

```
