output "role_arn" {
  description = "ARN of the Lambda execution role"
  value       = module.iam.role_arn
}

output "role_name" {
  description = "Name of the Lambda execution role"
  value       = module.iam.role_name
}

output "lambda_role_policy_name" {
  description = "Name of the inline IAM policy that grants Lambda access to SQS"
  value       = module.iam.lambda_role_policy_name
}

output "sqs_queue_name" {
  description = "Name of the deployed SQS function"
  value = module.sqs.queue_name
}

output "sqs_queue_url" {
  description = "URL of the SQS queue"
  value       = module.sqs.queue_url
}

output "lambda_function_name" {
  description = "Name of the deployed Lambda function"
  value       = module.lambda.function_name
}

output "lambda_function_arn" {
  description = "ARN of the deployed Lambda function"
  value = module.lambda.function_arn
}