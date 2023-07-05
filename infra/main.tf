terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = var.aws_region
}


variable "instance_type" {
 }

variable "aws_region" {
}
 
resource "aws_instance" "app_server" {
  ami           = "ami-04a0ae173da5807d3"
  instance_type = var.instance_type

  tags = {
    Name = "ExampleAppServerInstance"
  }
}
