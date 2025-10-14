output "role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}

output "role_name" {
  description = "Name of the Lambda execution role"
  value       = aws_iam_role.lambda_role.name
}

output "lambda_role_policy_name" {
  description = "Name of the inline IAM policy that grants Lambda access to SQS"
  value       = aws_iam_role_policy.lambda_sqs_access.name
}