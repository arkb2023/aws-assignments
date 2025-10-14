variable "prefix" {
  description = "Prefix for naming the Lambda function"
  type        = string
}

variable "role_arn" {
  description = "IAM role ARN for Lambda execution"
  type        = string
}

variable "sqs_arn" {
  description = "ARN of the SQS queue to trigger Lambda"
  type        = string
}