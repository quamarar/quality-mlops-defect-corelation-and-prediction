/*===============================
#            S3
===============================*/

module "logging-s3-bucket" {
  source = "git::https://github.com/quamarar/terraform-common-module.git"

  bucket                                = "${local.name_prefix}-${var.logging-s3-config.name}"
  force_destroy                         = true
  tags                                  = var.common-tags
  attach_policy                         = var.logging-s3-config.attach_policy
  policy                                = null
  attach_deny_insecure_transport_policy = var.logging-s3-config.attach_deny_insecure_transport_policy
  attach_require_latest_tls_policy      = var.logging-s3-config.attach_require_latest_tls_policy
  control_object_ownership              = var.logging-s3-config.control_object_ownership
  object_ownership                      = var.logging-s3-config.object_ownership 
  expected_bucket_owner                 = data.aws_caller_identity.current.account_id
  acl                                   = var.logging-s3-config.acl  
  versioning  = {
    status                    = var.logging-s3-config.enable_versioning
    mfa_delete                = var.logging-s3-config.enable_mfa_delete
  }
  server_side_encryption_configuration = {
    rule      = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id     = var.logging-s3-config.kms_encryption ? module.kms_default.key_arn : null
        sse_algorithm         = var.logging-s3-config.kms_encryption ? "aws:kms" : "AES256"
      }
    }
  }
}
