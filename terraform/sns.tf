resource "aws_sns_topic" "finops_alerts" {
  name = "${var.project_name}-${var.environment}-alerts"
}

resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.finops_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
