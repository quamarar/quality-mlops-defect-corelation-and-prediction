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


/*===============================
#       SSM Parameters
===============================*/

module "ssm-parameters-training-ecr-preprocessing" {
  source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ssm-parameter?ref=master"

  
      
  name                    = "${var.ssm-parameter-training-ecr-preprocessing.name}"
  description             = var.ssm-parameter-training-ecr-preprocessing.description
  type                    = var.ssm-parameter-training-ecr-preprocessing.type
  value                   = var.ssm-parameter-training-ecr-preprocessing.value
  overwrite               = var.ssm-parameter-training-ecr-preprocessing.overwrite
}


module "ssm-parameter-training-ecr-training" {
  source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ssm-parameter?ref=master"

  
      
  name                    = "${var.ssm-parameter-training-ecr-training.name}"
  description             = var.ssm-parameter-training-ecr-training.description
  type                    = var.ssm-parameter-training-ecr-training.type
  value                   = var.ssm-parameter-training-ecr-training.value
  overwrite               = var.ssm-parameter-training-ecr-training.overwrite
}

module "ssm-parameters-glue-job" {
  source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ssm-parameter?ref=master"

  name                    = "${var.ssm-parameters-glue-job-config.name}"
  description             = var.ssm-parameters-glue-job-config.description
  type                    = var.ssm-parameters-glue-job-config.type
  value                   = var.ssm-parameters-glue-job-config.value

}