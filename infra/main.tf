/*===============================
#            KMS
===============================*/

module "kms_default" {
  source        = "git::https://github.com/quamarar/terraform-common-module.git?ref=master"

  aliases       = [
    "${local.name_prefix}-default-key"
  ]

}
