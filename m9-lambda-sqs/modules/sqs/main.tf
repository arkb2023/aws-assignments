resource "aws_sqs_queue" "demo_queue" {
  name = "${var.prefix}-sqs-queue"
}
