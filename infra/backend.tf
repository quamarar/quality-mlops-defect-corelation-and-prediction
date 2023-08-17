terraform {
  backend "s3" {
    bucket         = "MSIL-MVP-tfstate"
    region         = "ap-south-1"
    encrypt        = true
  }
}
