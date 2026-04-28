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
