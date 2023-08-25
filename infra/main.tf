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
  source = "git::https://github.com/quamarar/terraform-common-module.git//s3-bucket/?ref=master"

  bucket_name                             = "${local.name_prefix}-${var.internal-s3-config.name}"
  expected_bucket_owner                 =   data.aws_caller_identity.current.account_id
}

module "shared-s3-bucket" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-s3-bucket/?ref=master"

  bucket                                = "${local.name_prefix}-${var.shared-s3-config.name}"
  expected_bucket_owner                 =   data.aws_caller_identity.current.account_id
  attach_policy = true
  force_destroy                         = true
  policy                                = null
  attach_deny_insecure_transport_policy = true
  attach_require_latest_tls_policy      = true
  control_object_ownership              = true
}





/*===============================
#       SSM Parameters
===============================*/

module "ssm-parameters-training-ecr-preprocessing" {
  source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ssm-parameter?ref=master"

  
      
  name                    = "${var.ssm-parameter-training-ecr-preprocessing.name}"
  description             = var.ssm-parameter-training-ecr-preprocessing.description
  type                    = var.ssm-parameter-training-ecr-preprocessing.type
  overwrite               = var.ssm-parameter-training-ecr-preprocessing.overwrite
  value                   = var.ssm-parameter-training-ecr-preprocessing.value
}


module "ssm-parameter-training-ecr-training" {
  source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ssm-parameter?ref=master"

  
      
  name                    = "${var.ssm-parameter-training-ecr-training.name}"
  description             = var.ssm-parameter-training-ecr-training.description
  type                    = var.ssm-parameter-training-ecr-training.type
  overwrite               = var.ssm-parameter-training-ecr-training.overwrite
  value                   = var.ssm-parameter-training-ecr-training.value
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
  source = "git::https://github.com/quamarar/terraform-common-module.git//iam-policy?ref=master"

  create_policy            = true
  name                     = "${local.name_prefix}-glue-job-policy"
  path                     = "/"
  description              = "Policy for Glue job"
  policy                   = data.aws_iam_policy_document.glue-job-policy.json
}

module "glue-job-role" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//iam-role?ref=master"

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

/*===============================
#           Glue Job
===============================*/


module "glue-job-gatekeeper" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//glue-job?ref=master"

  job_name          = "${local.name_prefix}-${var.glue-job-gatekeeper-config.name}"
  job_description   = "Glue Job for-${var.glue-job-gatekeeper-config.name}"
  role_arn          = module.glue-job-role.iam_role_arn
  max_capacity      =  var.glue-job-gatekeeper-config.max_capacity 
  max_retries       = var.glue-job-gatekeeper-config.max_retries 
  timeout           =  var.glue-job-gatekeeper-config.timeout

  command = {
    name            = "pythonshell"
    script_location = format("s3://%s/src/master/model/gatekeeper/${var.glue-job-gatekeeper-config.file_name}", module.internal-s3-bucket.s3_bucket_id)
    python_version  = 3.9
  }

    default_arguments = {
    "--additional-python-modules" = "ndjson==0.3.1,pynamodb==5.5.0,scikit-learn==1.3.0,pandas==1.5.3,pythena==1.6.0"
    "--athenadb_name" = "default"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--region"                    = "ap-south-1"
    "--train_inputtable_name"     = "dcp-auto-dev-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "dcp-auto-dev-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "dcp-auto-dev-apsouth1-TrainStateTable"
    "--model_package_group_arn" = "demo-997"
    
  }
}

module "glue-job-submit_training_job_awsbatch_statetable" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//glue-job?ref=master"

  job_name          = "${local.name_prefix}-${var.glue-job-submit_training_job_awsbatch_statetable-config.name}"
  job_description   = "Glue Job for-${var.glue-job-submit_training_job_awsbatch_statetable-config.name}"
  role_arn          = module.glue-job-role.iam_role_arn
  max_capacity      =  var.glue-job-submit_training_job_awsbatch_statetable-config.max_capacity 
  max_retries       = var.glue-job-submit_training_job_awsbatch_statetable-config.max_retries 
  timeout           =  var.glue-job-submit_training_job_awsbatch_statetable-config.timeout

  command = {
    name            = "pythonshell"
    script_location = format("s3://%s/${var.glue-job-submit_training_job_awsbatch_statetable-config.file_name}", module.internal-s3-bucket.s3_bucket_id)
    python_version  = 3.9
  }

    default_arguments = {
    "--additional-python-modules" = "pythena,ndjson==0.3.1,pynamodb==5.5.0,scikit-learn==1.3.0,pandas==1.5.3"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--region"                    = "${local.region-short}"
    "--train_inputtable_name"     = "dcp-auto-dev-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "dcp-auto-dev-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "dcp-auto-dev-apsouth1-TrainStateTable"
  }
}

module "glue-job-training_job_awsbatch_status_check" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//glue-job?ref=master"

  job_name          = "${local.name_prefix}-${var.glue-job-training_job_awsbatch_status_check-config.name}"
  job_description   = "Glue Job for-${var.glue-job-training_job_awsbatch_status_check-config.name}"
  role_arn          = module.glue-job-role.iam_role_arn
  max_capacity      =  var.glue-job-training_job_awsbatch_status_check-config.max_capacity 
  max_retries       = var.glue-job-training_job_awsbatch_status_check-config.max_retries 
  timeout           =  var.glue-job-training_job_awsbatch_status_check-config.timeout

  command = {
    name            = "pythonshell"
    script_location = format("s3://%s/${var.glue-job-training_job_awsbatch_status_check-config.file_name}", module.internal-s3-bucket.s3_bucket_id)
    python_version  = 3.9
  }

    default_arguments = {
    "--additional-python-modules" = "pythena,ndjson==0.3.1,pynamodb==5.5.0,scikit-learn==1.3.0,pandas==1.5.3"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--ssm_training_complete_status" = "training_complete_status"
    "--region"                    = "ap-south-1"
     "--train_inputtable_name"     = "dcp-auto-dev-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "dcp-auto-dev-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "dcp-auto-dev-apsouth1-TrainStateTable"
    "--athenadb_name" =  "default"
  }
}

module "glue-job-evaluation_summary" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//glue-job?ref=master"

  job_name          = "${local.name_prefix}-${var.glue-job-evaluation_summary-config.name}"
  job_description   = "Glue Job for-${var.glue-job-evaluation_summary-config.name}"
  role_arn          = module.glue-job-role.iam_role_arn
  number_of_workers      =  var.glue-job-evaluation_summary-config.number_of_workers
  max_retries       = var.glue-job-evaluation_summary-config.max_retries 
  timeout           =  var.glue-job-evaluation_summary-config.timeout
  worker_type       = var.glue-job-evaluation_summary-config.worker_type
  glue_version      = var.glue-job-evaluation_summary-config.glue_version

  command = {
    name            = "glueetl"
    script_location = format("s3://%s/src/master/model/evaluation/${var.glue-job-evaluation_summary-config.file_name}", module.internal-s3-bucket.s3_bucket_id)
    python_version  = 3
  }

    default_arguments = {
    "--additional-python-modules" = "pythena==1.6.0,pynamodb==5.5.0,boto3==1.28.27,ndjson~=0.3.1"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--region"                    = "ap-south-1"
    "--train_inputtable_name"     = "dcp-auto-dev-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "dcp-auto-dev-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "dcp-auto-dev-apsouth1-TrainStateTable"
  }
}


module "glue-job-clean_up_job" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//glue-job?ref=master"

  job_name          = "${local.name_prefix}-${var.glue-job-clean_up_job-config.name}"
  job_description   = "Glue Job for-${var.glue-job-clean_up_job-config.name}"
  role_arn          = module.glue-job-role.iam_role_arn
  max_capacity      =  var.glue-job-clean_up_job-config.max_capacity 
  max_retries       = var.glue-job-clean_up_job-config.max_retries 
  timeout           =  var.glue-job-clean_up_job-config.timeout

  command = {
    name            = "pythonshell"
    script_location = format("s3://%s/${var.glue-job-clean_up_job-config.file_name}", module.internal-s3-bucket.s3_bucket_id)
    python_version  = 3.9
  }

    default_arguments = {
    "--additional-python-modules" = "pythena,ndjson==0.3.1,pynamodb==5.5.0,scikit-learn==1.3.0,pandas==1.5.3"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--ssm_training_complete_status"              = "training_complete_status"
    "--region"                    = "ap-south-1"
    "--train_inputtable_name"     = "dcp-auto-dev-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "dcp-auto-dev-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "dcp-auto-dev-apsouth1-TrainStateTable"
  }
}
/*===============================
#           ECR
===============================*/


module "ecr_preprocessing" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ecr?ref=master"

  repository_name = "${local.name_prefix}-${var.processing-private-ecr-config.repository_name}"

  repository_read_write_access_arns = [data.aws_caller_identity.current.arn]
  create_lifecycle_policy           = true
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep last 30 images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["v"],
          countType     = var.processing-private-ecr-config.countType,
          countNumber   = 30
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
  repository_force_delete = true
}


/*===============================
#     ECR Registry Management
===============================*/

module "ecr_registry_processing" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ecr?ref=master"

  create_repository = var.processing_ecr-registry-config.create_repository
  repository_name = "${local.name_prefix}/${var.processing-private-ecr-config.repository_name}"

  # Registry Policy
  #create_registry_policy = var.processing_ecr-registry-config.create_registry_policy
  #registry_policy        = data.aws_iam_policy_document.registry_processing.json

  #Registry Pull Through Cache Rules
  #registry_pull_through_cache_rules = {
   # pub = {
     # ecr_repository_prefix = var.processing_ecr-registry-config.ecr_repository_prefix
      #upstream_registry_url = var.processing_ecr-registry-config.upstream_registry_url
    #}
  #}

    # Registry Scanning Configuration
  #manage_registry_scanning_configuration = var.processing_ecr-registry-config.manage_registry_scanning_configuration
  #registry_scan_type                     = var.processing_ecr-registry-config.registry_scan_type
  #registry_scan_rules = [
   # {
    #  scan_frequency = "SCAN_ON_PUSH"
     # filter         = "*"
      #filter_type    = "WILDCARD"
      #}
  #]
}

/*===============================
#           ECR
===============================*/
module "ecr_training" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ecr?ref=master"

  repository_name = "${local.name_prefix}-${var.training-private-ecr-config.repository_name}"

  repository_read_write_access_arns = [data.aws_caller_identity.current.arn]
  create_lifecycle_policy           = true
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep last 30 images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["v"],
          countType     = var.training-private-ecr-config.countType,
          countNumber   = 30
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
  repository_force_delete = true
}

/*===============================
#     ECR Registry Management
===============================*/

module "ecr_registry_training" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ecr?ref=master"

  create_repository = var.training_ecr-registry-config.create_repository
  repository_name = "${local.name_prefix}/${var.training-private-ecr-config.repository_name}"

  # Registry Policy
 # create_registry_policy = var.training_ecr-registry-config.create_registry_policy
  #registry_policy        = data.aws_iam_policy_document.registry_training.json

  #Registry Pull Through Cache Rules
  #registry_pull_through_cache_rules = {
   # pub = {
    #  ecr_repository_prefix = var.training_ecr-registry-config.ecr_repository_prefix
     # upstream_registry_url = var.training_ecr-registry-config.upstream_registry_url
    #}
  #}

    # Registry Scanning Configuration
  #manage_registry_scanning_configuration = var.training_ecr-registry-config.manage_registry_scanning_configuration
  #registry_scan_type                     = var.training_ecr-registry-config.registry_scan_type
  #registry_scan_rules = [
   # {
    #  scan_frequency = "SCAN_ON_PUSH"
     # filter         = "*"
      #filter_type    = "WILDCARD"
      #}
  #]
}
/*===============================
#    DynamoDb Table
===============================*/

module "traininput-dynamodb-table" {
  source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-dynamodb-table?ref=master"

  name = "${local.name_prefix}-${var.traininput-dynamodb-table-config.name}"
  hash_key = var.traininput-dynamodb-table-config.hash_key
  table_class = var.traininput-dynamodb-table-config.table_class
  deletion_protection_enabled = var.traininput-dynamodb-table-config.deletion_protection_enabled
  attributes = [
         {
          "name" : "sku_mappingid"
          "type" : "S"
         }
        ]
   }

module "trainstate-dynamodb-table" {
    source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-dynamodb-table?ref=master"

  name = "${local.name_prefix}-${var.trainstate-dynamodb-table-config.name}"
  hash_key = var.trainstate-dynamodb-table-config.hash_key
  table_class = var.trainstate-dynamodb-table-config.table_class
  deletion_protection_enabled = var.trainstate-dynamodb-table-config.deletion_protection_enabled
  attributes = [
         {
          "name" : "batchjob_id"
          "type" : "S"
         },

        ]
   }  

module "trainmeta-dynamodb-table" {
    source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-dynamodb-table?ref=master"

  name = "${local.name_prefix}-${var.trainmeta-dynamodb-table-config.name}"
  hash_key = var.trainmeta-dynamodb-table-config.hash_key
  table_class = var.trainmeta-dynamodb-table-config.table_class
  deletion_protection_enabled = var.trainmeta-dynamodb-table-config.deletion_protection_enabled
  attributes = [
         {
          "name" : "metaKey"
          "type" : "S"
         },

        ]
   }

/*===============================
#           Step Function
===============================*/

module "step_function" {
  source = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-step-functions?ref=master"

  name = "${local.name_prefix}-${var.step_function_name}"

  type = "standard"

  definition = local.definition_template1

  logging_configuration = {
    include_execution_data = true
    level                  = "ALL"
  }
  }

