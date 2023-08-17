terraform {
  required_version = ">= 0.15, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.61.0"
    }
    awscc = {
      source  = "hashicorp/awscc"
      version = ">= 0.49.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}
