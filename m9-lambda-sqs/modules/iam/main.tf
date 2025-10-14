resource "aws_iam_role" "lambda_role" {
  name = "${var.prefix}-lambda-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com",
      },
    }],
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_sqs_access" {
  name = "${var.prefix}-lambda-sqs-policy"
  role = aws_iam_role.lambda_role.id

  policy = templatefile("${path.module}/lambda-sqs-policy.json", {
    sqs_arn = var.sqs_arn
  })
}