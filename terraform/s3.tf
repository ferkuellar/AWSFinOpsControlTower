resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "finops_reports" {
  bucket = "${var.project_name}-${var.environment}-reports-${random_id.bucket_suffix.hex}"

  force_destroy = false
}

resource "aws_s3_bucket_versioning" "finops_reports_versioning" {
  bucket = aws_s3_bucket.finops_reports.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "finops_reports_encryption" {
  bucket = aws_s3_bucket.finops_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "finops_reports_public_access" {
  bucket = aws_s3_bucket.finops_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "finops_reports_lifecycle" {
  bucket = aws_s3_bucket.finops_reports.id

  rule {
    id     = "transition-old-reports"
    status = "Enabled"

    filter {
      prefix = "reports/"
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
