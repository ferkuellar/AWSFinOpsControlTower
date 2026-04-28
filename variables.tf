
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
