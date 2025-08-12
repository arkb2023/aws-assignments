## 1) Create 4 IAM users named “Dev1”, “Dev2”, “Test1”, and "Test2" 
**Create Dev1 User**
```
 $ aws iam create-user --user-name $DEV1_USER
{
    "User": {
        "Path": "/",
        "UserName": "Dev1",
        "UserId": "<REDACTED_USER_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:user/Dev1",
        "CreateDate": "2025-08-12T05:23:23Z"
    }
}
```
**Create Password**
```
 $ aws iam create-login-profile --user-name $DEV1_USER --password $DEV1_PASSWORD
{
    "LoginProfile": {
        "UserName": "Dev1",
        "CreateDate": "2025-08-12T06:46:09Z",
        "PasswordResetRequired": false
    }
}
```
**Create Dev2 User**
```
 $ aws iam create-user --user-name $DEV2_USER
{
    "User": {
        "Path": "/",
        "UserName": "Dev2",
        "UserId": "<REDACTED_USER_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:user/Dev2",
        "CreateDate": "2025-08-12T05:25:26Z"
    }
}
```
**Create Password**
```
 $ aws iam create-login-profile --user-name $DEV2_USER --password $DEV2_PASSWORD
{
    "LoginProfile": {
        "UserName": "Dev2",
        "CreateDate": "2025-08-12T06:48:22Z",
        "PasswordResetRequired": false
    }
}
```
**Create Test1 User**
```
 $ aws iam create-user --user-name $TEST1_USER
{
    "User": {
        "Path": "/",
        "UserName": "Test1",
        "UserId": "<REDACTED_USER_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:user/Test1",
        "CreateDate": "2025-08-12T07:10:13Z"
    }
}
```
**Create Password**
```
 $ aws iam create-login-profile --user-name $TEST1_USER --password $TEST1_PASSWORD
{
    "LoginProfile": {
        "UserName": "Test1",
        "CreateDate": "2025-08-12T07:11:28Z",
        "PasswordResetRequired": false
    }
}
```
**Create Test2 User**
```
 $ aws iam create-user --user-name $TEST2_USER
{
    "User": {
        "Path": "/",
        "UserName": "Test2",
        "UserId": "<REDACTED_USER_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:user/Test2",
        "CreateDate": "2025-08-12T07:10:13Z"
    }
}
```
**Create Password**
```
 $ aws iam create-login-profile --user-name $TEST2_USER --password $TEST2_PASSWORD
{
    "LoginProfile": {
        "UserName": "Test2",
        "CreateDate": "2025-08-12T07:11:28Z",
        "PasswordResetRequired": false
    }
}
```
## 2) Create 2 groups named “Dev Team” and “Ops Team”.
**Create Dev Team group**
```
 $ aws iam create-group --group-name $DEV_TEAM_GROUP
{
    "Group": {
        "Path": "/",
        "GroupName": "DevTeamGroup",
        "GroupId": "<REDACTED_GROUP_ID>,
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:group/DevTeamGroup",
        "CreateDate": "2025-08-12T06:54:36Z"
    }
}
```
**Create Ops Team group**
```
 $ aws iam create-group --group-name $OPS_TEAM_GROUP
{
    "Group": {
        "Path": "/",
        "GroupName": "OpsTeamGroup",
        "GroupId": "<REDACTED_GROUP_ID>",
        "Arn": "arn:aws:iam::<REDACTED_ACCOUNT_ID>:group/OpsTeamGroup",
        "CreateDate": "2025-08-12T06:56:05Z"
    }
}
```
## 3) Add Dev1 and Dev2 to the Dev Team.
**Add Dev1 user to DevTeam Group**  
```
$ aws iam add-user-to-group --group-name $DEV_TEAM_GROUP --user-name $DEV1_USER
```
**Add Dev2 user to DevTeam Group**  
```
$ aws iam add-user-to-group --group-name $DEV_TEAM_GROUP --user-name $DEV2_USER
```

## 4) Add Dev1, Test1 and Test2 to the Ops Team.

**Add Dev1 user to OpsTeam Group**  
```
$ aws iam add-user-to-group --group-name $OPS_TEAM_GROUP --user-name $DEV1_USER
```
**Add Test1 user to OpsTeam Group**  
```
$ aws iam add-user-to-group --group-name $OPS_TEAM_GROUP --user-name $TEST1_USER
```
**Add Test2 user to OpsTeam Group**  
```
$ aws iam add-user-to-group --group-name $OPS_TEAM_GROUP --user-name $TEST2_USER
```
