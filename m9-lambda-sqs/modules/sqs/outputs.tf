output "queue_arn" {
  description = "ARN of the SQS queue named with prefix"
  value       = aws_sqs_queue.demo_queue.arn
}

output "queue_url" {
  description = "URL of the SQS queue named with prefix"
  value       = aws_sqs_queue.demo_queue.id
}

output "queue_name" {
  description = "Name of the SQS queue"
  value       = aws_sqs_queue.demo_queue.name
}