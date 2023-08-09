terraform {
  backend "s3" {
    bucket         = "shared-298320596430"
    region         = "us-east-1"
    encrypt        = true
  }
}
