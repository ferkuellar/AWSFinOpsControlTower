resource "aws_cloudwatch_log_group" "finops_logs" {
  name              = "/aws/finops/${var.project_name}-${var.environment}"
  retention_in_days = 30
}
