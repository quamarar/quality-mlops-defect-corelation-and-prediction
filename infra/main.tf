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

module "shared-s3-bucket" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-s3-bucket?ref=master"

  bucket                                = "${local.name_prefix}-${var.shared-s3-config.name}"
  force_destroy                         = true
  attach_policy                         = var.shared-s3-config.attach_policy
  policy                                = null
  attach_deny_insecure_transport_policy = var.shared-s3-config.attach_deny_insecure_transport_policy
  attach_require_latest_tls_policy      = var.shared-s3-config.attach_require_latest_tls_policy
  control_object_ownership              = var.shared-s3-config.control_object_ownership
  object_ownership                      = var.shared-s3-config.object_ownership 
  expected_bucket_owner                 = data.aws_caller_identity.current.account_id
  acl                                   = var.shared-s3-config.acl  
  versioning  = {
    status                    = var.shared-s3-config.enable_versioning
    mfa_delete                = var.shared-s3-config.enable_mfa_delete
  }
  server_side_encryption_configuration = {
    rule      = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id     =  module.kms_default.key_arn
        sse_algorithm         =  "aws:kms"
      }
    }
  }
}
