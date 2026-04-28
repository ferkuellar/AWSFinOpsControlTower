terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }

    random = {
      source  = "hashicorp/random"
      version = ">= 3.6.0, < 4.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4.0, < 3.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner
      CostCenter  = var.cost_center
      Purpose     = "FinOps-Control-Tower"
    }
  }
}
