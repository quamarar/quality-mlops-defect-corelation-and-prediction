terraform {
  backend "s3" {
    bucket         = "msil-mvp-tfstate"
    region         = "ap-south-1"
    encrypt        = true
  }
}
