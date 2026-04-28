data "archive_file" "finops_lambda_package" {
  type        = "zip"
  source_file = "${path.module}/lambda/finops_runner.py"
  output_path = "${path.module}/lambda/finops_runner.zip"
}

resource "aws_cloudwatch_log_group" "finops_lambda_logs" {
  name              = "/aws/lambda/${var.project_name}-${var.environment}-runner"
  retention_in_days = 30
}

resource "aws_lambda_function" "finops_runner" {
  function_name = "${var.project_name}-${var.environment}-runner"
  description   = "AWS FinOps Control Tower cost impact estimation engine. Non-destructive EC2/EBS/EIP scanner."

  role    = aws_iam_role.finops_execution_role.arn
  handler = "finops_runner.lambda_handler"
  runtime = var.lambda_runtime

  filename         = data.archive_file.finops_lambda_package.output_path
  source_code_hash = data.archive_file.finops_lambda_package.output_base64sha256

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      FINOPS_REPORT_BUCKET    = aws_s3_bucket.finops_reports.bucket
      FINOPS_SNS_TOPIC_ARN    = aws_sns_topic.finops_alerts.arn
      PROJECT_NAME            = var.project_name
      ENVIRONMENT             = var.environment
      CPU_IDLE_THRESHOLD      = tostring(var.cpu_idle_threshold)
      CPU_RIGHTSIZE_THRESHOLD = tostring(var.cpu_rightsize_threshold)
      METRIC_LOOKBACK_DAYS    = tostring(var.metric_lookback_days)

      MONTHLY_HOURS            = tostring(var.monthly_hours)
      DEFAULT_EC2_HOURLY_RATE  = tostring(var.default_ec2_hourly_rate)
      RIGHTSIZE_SAVINGS_FACTOR = tostring(var.rightsize_savings_factor)
      EBS_GP2_GB_MONTH_RATE    = tostring(var.ebs_gp2_gb_month_rate)
      EBS_GP3_GB_MONTH_RATE    = tostring(var.ebs_gp3_gb_month_rate)
      PUBLIC_IPV4_HOURLY_RATE  = tostring(var.public_ipv4_hourly_rate)
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.finops_read_policy_attachment,
    aws_cloudwatch_log_group.finops_lambda_logs
  ]
}
