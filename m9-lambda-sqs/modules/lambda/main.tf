resource "aws_lambda_function" "sqs_handler" {
  function_name = "${var.prefix}-lambda-function"
  role          = var.role_arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"

  filename         = "${path.module}/../../lambda/function.zip"
  source_code_hash = filebase64sha256("${path.module}/../../lambda/function.zip")
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = var.sqs_arn
  function_name    = aws_lambda_function.sqs_handler.arn
  batch_size       = 10
  enabled          = true
}

resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sqs_handler.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = var.sqs_arn
}