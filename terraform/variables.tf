variable "aws_region" {
  description = "AWS region where the FinOps foundation will be deployed."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Local AWS CLI profile used by Terraform."
  type        = string
  default     = "ControlTower"
}

variable "project_name" {
  description = "Project name used for naming and tagging."
  type        = string
  default     = "aws-finops-control-tower"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Resource owner."
  type        = string
  default     = "Fernando-Cuellar"
}

variable "cost_center" {
  description = "Cost center or financial ownership identifier."
  type        = string
  default     = "finops-lab"
}

variable "alert_email" {
  description = "Email address that will receive FinOps SNS alerts."
  type        = string
}

variable "lambda_runtime" {
  description = "Python runtime used by the FinOps Lambda function."
  type        = string
  default     = "python3.13"
}

variable "lambda_timeout" {
  description = "Lambda execution timeout in seconds."
  type        = number
  default     = 120
}

variable "lambda_memory_size" {
  description = "Lambda memory size in MB."
  type        = number
  default     = 256
}

variable "finops_schedule_expression" {
  description = "EventBridge schedule expression for the FinOps scanner."
  type        = string
  default     = "cron(0 13 * * ? *)"
}

variable "cpu_idle_threshold" {
  description = "Average CPU percentage below which an EC2 instance is considered idle."
  type        = number
  default     = 5
}

variable "cpu_rightsize_threshold" {
  description = "Average CPU percentage below which an EC2 instance is considered a rightsizing candidate."
  type        = number
  default     = 20
}

variable "metric_lookback_days" {
  description = "Number of days used for CloudWatch CPU utilization analysis."
  type        = number
  default     = 7
}

variable "monthly_hours" {
  description = "Monthly hours used for cost impact estimation."
  type        = number
  default     = 730
}

variable "default_ec2_hourly_rate" {
  description = "Default EC2 hourly rate used until AWS Price List API integration is added."
  type        = number
  default     = 0.05
}

variable "rightsize_savings_factor" {
  description = "Estimated percentage of savings for rightsizing candidates."
  type        = number
  default     = 0.30
}

variable "ebs_gp2_gb_month_rate" {
  description = "Estimated gp2 EBS GB-month rate."
  type        = number
  default     = 0.10
}

variable "ebs_gp3_gb_month_rate" {
  description = "Estimated gp3 EBS GB-month rate."
  type        = number
  default     = 0.08
}

variable "public_ipv4_hourly_rate" {
  description = "Public IPv4 hourly rate used for Elastic IP cost estimation."
  type        = number
  default     = 0.005
}
