terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment for team use:
  # backend "s3" {
  #   bucket         = "network-monitoring-tfstate"
  #   key            = "platform/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "network-monitoring-tf-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "network-monitoring-platform"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
