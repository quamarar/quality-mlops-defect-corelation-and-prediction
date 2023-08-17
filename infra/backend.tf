terraform {
  backend "s3" {
    bucket         = "tfstate"
    region         = "ap-south-1"
    encrypt        = true
  }
}
