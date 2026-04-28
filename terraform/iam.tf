data "aws_caller_identity" "current" {}

resource "aws_iam_role" "finops_execution_role" {
  name = "${var.project_name}-${var.environment}-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = [
            "lambda.amazonaws.com",
            "ec2.amazonaws.com"
          ]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "finops_read_policy" {
  name        = "${var.project_name}-${var.environment}-read-policy"
  description = "Read-only permissions required by the FinOps scanner."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CostExplorerRead"
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast",
          "ce:GetDimensionValues",
          "ce:GetReservationUtilization",
          "ce:GetSavingsPlansUtilization",
          "ce:GetRightsizingRecommendation"
        ]
        Resource = "*"
      },
      {
        Sid    = "InventoryRead"
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "elasticloadbalancing:Describe*",
          "autoscaling:Describe*",
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "rds:Describe*",
          "s3:ListAllMyBuckets",
          "s3:GetBucketLocation",
          "s3:GetBucketTagging",
          "s3:GetLifecycleConfiguration",
          "lambda:ListFunctions",
          "lambda:GetFunctionConfiguration",
          "tag:GetResources"
        ]
        Resource = "*"
      },
      {
        Sid    = "WriteReportsToS3"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.finops_reports.arn,
          "${aws_s3_bucket.finops_reports.arn}/*"
        ]
      },
      {
        Sid    = "PublishAlerts"
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.finops_alerts.arn
      },
      {
        Sid    = "WriteCloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "finops_read_policy_attachment" {
  role       = aws_iam_role.finops_execution_role.name
  policy_arn = aws_iam_policy.finops_read_policy.arn
}

resource "aws_iam_instance_profile" "finops_instance_profile" {
  name = "${var.project_name}-${var.environment}-instance-profile"
  role = aws_iam_role.finops_execution_role.name
}
