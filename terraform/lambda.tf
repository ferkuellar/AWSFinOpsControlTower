data "archive_file" "finops_lambda_package" {
  type        = "zip"
  source_file = "${path.module}/lambda/finops_runner.py"
  output_path = "${path.module}/lambda/finops_runner.zip"
}

resource "aws_lambda_function" "finops_runner" {
  function_name = "${var.project_name}-${var.environment}-runner"
  description   = "AWS FinOps Control Tower execution layer. Non-destructive scheduled runner."

  role    = aws_iam_role.finops_execution_role.arn
  handler = "finops_runner.lambda_handler"
  runtime = var.lambda_runtime

  filename         = data.archive_file.finops_lambda_package.output_path
  source_code_hash = data.archive_file.finops_lambda_package.output_base64sha256

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      FINOPS_REPORT_BUCKET = aws_s3_bucket.finops_reports.bucket
      FINOPS_SNS_TOPIC_ARN = aws_sns_topic.finops_alerts.arn
      PROJECT_NAME         = var.project_name
      ENVIRONMENT          = var.environment
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.finops_read_policy_attachment,
    aws_cloudwatch_log_group.finops_lambda_logs
  ]
}

resource "aws_cloudwatch_log_group" "finops_lambda_logs" {
  name              = "/aws/lambda/${var.project_name}-${var.environment}-runner"
  retention_in_days = 30
}
