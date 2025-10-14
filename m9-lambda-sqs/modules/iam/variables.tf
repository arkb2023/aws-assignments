variable "prefix" {
  description = "Prefix for naming IAM resources"
  type        = string
}

variable "sqs_arn" {
  description = "ARN of the SQS queue Lambda needs access to"
  type        = string
}