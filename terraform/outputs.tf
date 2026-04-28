output "finops_reports_bucket_name" {
  description = "S3 bucket used to store FinOps reports."
  value       = aws_s3_bucket.finops_reports.bucket
}

output "finops_reports_bucket_arn" {
  description = "S3 bucket ARN."
  value       = aws_s3_bucket.finops_reports.arn
}

output "finops_alerts_topic_arn" {
  description = "SNS topic ARN for FinOps alerts."
  value       = aws_sns_topic.finops_alerts.arn
}

output "finops_execution_role_arn" {
  description = "IAM role ARN used by the FinOps execution layer."
  value       = aws_iam_role.finops_execution_role.arn
}

output "finops_instance_profile_name" {
  description = "Instance profile name for optional EC2 runner."
  value       = aws_iam_instance_profile.finops_instance_profile.name
}

output "finops_log_group_name" {
  description = "CloudWatch Log Group used for FinOps foundation logs."
  value       = aws_cloudwatch_log_group.finops_logs.name
}

output "finops_lambda_function_name" {
  description = "Lambda function name for the FinOps runner."
  value       = aws_lambda_function.finops_runner.function_name
}

output "finops_lambda_function_arn" {
  description = "Lambda function ARN for the FinOps runner."
  value       = aws_lambda_function.finops_runner.arn
}

output "finops_eventbridge_rule_name" {
  description = "EventBridge rule used to schedule FinOps execution."
  value       = aws_cloudwatch_event_rule.finops_schedule.name
}

output "finops_schedule_expression" {
  description = "Schedule expression used by EventBridge."
  value       = aws_cloudwatch_event_rule.finops_schedule.schedule_expression
}
