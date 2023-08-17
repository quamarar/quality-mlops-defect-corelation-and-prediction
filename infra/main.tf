/*===============================
#            KMS
===============================*/

module "kms_default" {
  source        = "../Modules/terraform-aws-kms-master"

  aliases       = [
    "${local.name_prefix}-default-key"
  ]

}
