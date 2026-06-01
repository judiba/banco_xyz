################################
# TTYD — terraform/main.tf
# Provider + backend configurado por ambiente via tfvars
################################

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend remoto — descomente e configure para PROD
  # backend "s3" {
  #   bucket = "ttyd-terraform-state"
  #   key    = "ttyd/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
    }
  }
}
