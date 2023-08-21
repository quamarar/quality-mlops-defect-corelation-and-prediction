/*===============================
#            KMS
===============================*/

module "kms_default" {
  source        = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-kms?ref=master"

  aliases       = [
    "${local.name_prefix}-default-key"
  ]

}

/*===============================
#            S3
===============================*/

module "internal-s3-bucket" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//s3-bucket?ref=master"

  bucket_name                                = "${local.name_prefix}-${var.internal-s3-config.name}"
  expected_bucket_owner                 =   data.aws_caller_identity.current.account_id
}


