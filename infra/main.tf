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

/*===============================
#            IAM
===============================*/

module "glue-job-policy" {
  source = "../Modules/iam-policy"

  create_policy            = true
  name                     = "${local.name_prefix}-glue-job-policy"
  path                     = "/"
  description              = "Policy for Glue job"
  policy                   = data.aws_iam_policy_document.glue-job-policy.json
}

module "glue-job-role" {
  source = "../Modules/iam-role"

  create_role             = true
  role_name               = "${local.name_prefix}-glue-job-role"
  role_description        = "Role for Glue job"
  trusted_role_actions    = ["sts:AssumeRole"]
  trusted_role_services   = ["glue.amazonaws.com"]
  max_session_duration    = 3600
  custom_role_policy_arns = [
    module.glue-job-policy.arn,
    "arn:aws:iam::aws:policy/CloudWatchFullAccess",
    "arn:aws:iam::aws:policy/AmazonKinesisFullAccess",
    "arn:aws:iam::aws:policy/IAMFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
  ]
}

