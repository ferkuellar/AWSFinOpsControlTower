resource "aws_cloudwatch_event_rule" "finops_schedule" {
  name                = "${var.project_name}-${var.environment}-schedule"
  description         = "Scheduled execution for AWS FinOps Control Tower."
  schedule_expression = var.finops_schedule_expression
}

resource "aws_cloudwatch_event_target" "finops_lambda_target" {
  rule      = aws_cloudwatch_event_rule.finops_schedule.name
  target_id = "finops-runner-lambda"
  arn       = aws_lambda_function.finops_runner.arn

  input = jsonencode({
    source      = "eventbridge"
    execution   = "scheduled"
    project     = var.project_name
    environment = var.environment
  })
}

resource "aws_lambda_permission" "allow_eventbridge_to_invoke_finops_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.finops_runner.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.finops_schedule.arn
}
