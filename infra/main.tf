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
  overwrite               = var.ssm-parameter-training-ecr-preprocessing.overwrite
}


module "ssm-parameter-training-ecr-training" {
  source  = "git::https://github.com/quamarar/terraform-common-module.git//terraform-aws-ssm-parameter?ref=master"

  
      
  name                    = "${var.ssm-parameter-training-ecr-training.name}"
  description             = var.ssm-parameter-training-ecr-training.description
  type                    = var.ssm-parameter-training-ecr-training.type
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
    "--enable-glue-datacatalog"   = "true"
    "--enable-job-insights"       = "false"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--job-language"              = "python"
    "--region"                    = "ap-south-1"
    "--train_inputtable_name"     = "msil-mvp-poc-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "msil-mvp-poc-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "msil-mvp-poc-apsouth1-TrainStateTable"
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
    "--additional-python-modules" = "ndjson==0.3.1,pynamodb==5.5.0,scikit-learn==1.3.0,pandas==1.5.3,pythena==1.6.0"
    "--enable-glue-datacatalog"   = "true"
    "--enable-job-insights"       = "false"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--job-language"              = "python"
    "--region"                    = "${local.region-short}"
    "--train_inputtable_name"     = "msil-mvp-poc-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "msil-mvp-poc-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "msil-mvp-poc-apsouth1-TrainStateTable"
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
    "--additional-python-modules" = "ndjson==0.3.1,pynamodb==5.5.0,scikit-learn==1.3.0,pandas==1.5.3,pythena==1.6.0"
    "--enable-glue-datacatalog"   = "true"
    "--enable-job-insights"       = "false"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--job-language"              = "python"
    "--region"                    = "ap-south-1"
    "--train_inputtable_name"     = "msil-mvp-poc-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "msil-mvp-poc-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "msil-mvp-poc-apsouth1-TrainStateTable"
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
    "--enable-glue-datacatalog"   = "true"
    "--enable-job-insights"       = "false"
    "--enable-metrics"            = "true"
    "--enable-spark-ui"           = "true"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--job-language"              = "python"
    "--region"                    = "ap-south-1"
    "--train_inputtable_name"     = "msil-mvp-poc-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "msil-mvp-poc-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "msil-mvp-poc-apsouth1-TrainStateTable"
    "--job-bookmark-option"       = "job-bookmark-disable"
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
    "--additional-python-modules" = "ndjson==0.3.1,pynamodb==5.5.0,scikit-learn==1.3.0,pandas==1.5.3,pythena==1.6.0"
    "--enable-glue-datacatalog"   = "true"
    "--enable-job-insights"       = "false"
    "--extra-files"               = "s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/ddb_helper_functions.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/dynamodb_util.py,s3://msil-mvp-poc-apsouth1-internal/src/master/model/utils/constants.py"
    "--job-language"              = "python"
    "--region"                    = "ap-south-1"
    "--train_inputtable_name"     = "msil-mvp-poc-apsouth1-TrainInputTable"
    "--train_metatable_name"      = "msil-mvp-poc-apsouth1-TrainMetaTable"
    "--train_statetable_name"     = "msil-mvp-poc-apsouth1-TrainStateTable"
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

/*===============================
#           AWS Batch
===============================*/

module "training_batch" {
  source = "../Modules/terraform-aws-batch-master"

  instance_iam_role_name        = ${local.name_prefix}-${var.training-batch-config.instance_iam_role_name}"
  instance_iam_role_path        = "/batch/"
  instance_iam_role_description = "IAM instance role/profile for AWS Batch ECS instance(s)"
  instance_iam_role_additional_policies = [
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  ]

  service_iam_role_name        = "test-batch-msil"
  service_iam_role_path        = "/batch/"
  service_iam_role_description = "IAM service role for AWS Batch"


  compute_environments = {
    a_ec2 = {
      name = "msil-batch-poc-compute-env"


      compute_resources = {
        type           = "EC2"
        min_vcpus      = 0
        max_vcpus      = 256
        desired_vcpus  = 0
        instance_types = ["m5.large", "r5.large"]

        security_group_ids = [module.vpc_endpoint_security_group.security_group_id]
        subnets            = module.vpc.private_subnets

        # Note - any tag changes here will force compute environment replacement
        # which can lead to job queue conflicts. Only specify tags that will be static
        # for the lifetime of the compute environment
        tags = {
          # This will set the name on the Ec2 instances launched by this compute environment
          Name = "msil-batch-test"
          Type = "Ec2"
        }
      }
    }

    c_unmanaged = {
      name_prefix = "ec2_unmanaged"
      type        = "UNMANAGED"
    }
  }

  # Job queus and scheduling policies
  job_queues = {
    low_priority = {
      name     = "msil-poc-batch-job-queue"
      state    = "ENABLED"
      priority = 1
      order = 1

      compute_environments = ["a_ec2"]

      tags = {
        JobQueue = "msil-poc-batch-job-queue"
      }
    }

  }

  job_definitions = {
    example = {
      name           = "msil-poc-batch-job-def"
      propagate_tags = true

      container_properties = jsonencode({
        command = ["python3","/opt/ml/training.py"]
        image   = module.ssm-parameter-training-ecr-training.value
        privileged = true
        resourceRequirements = [
          { type = "VCPU", value = "1" },
          { type = "MEMORY", value = "1024" }
        ]
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = aws_cloudwatch_log_group.this.id
            awslogs-region        = "ap-south-1"
            awslogs-stream-prefix = "msil"
          }
        }
      })

      attempt_duration_seconds = 60
      retry_strategy = {
        attempts = 3
        evaluate_on_exit = {
          retry_error = {
            action       = "RETRY"
            on_exit_code = 1
          }
          exit_success = {
            action       = "EXIT"
            on_exit_code = 0
          }
        }
      }

      tags = {
        JobDefinition = "msil-poc-job-def"
      }
    }
  }

  tags = local.tags
}

################################################################################
# Supporting Resources
################################################################################


module "vpc" {
  source  = "../Modules/terraform-aws-vpc"

  name = local.name
  cidr = "172.30.0.0/16"

  azs             = ["${local.region}a", "${local.region}b"]
  private_subnets  = ["172.30.0.0/18", "172.30.64.0/18", "172.30.128.0/19", "172.30.160.0/19", "172.30.192.0/19", "172.30.224.0/19"]


  private_route_table_tags = { Name = "${local.name}-private" }
  private_subnet_tags      = { Name = "${local.name}-private" }


  tags = local.tags
}

module "vpc_endpoints" {
  source  = "../Modules/terraform-aws-vpc/modules/vpc-endpoints"

  vpc_id             = module.vpc.vpc_id
  security_group_ids = [module.vpc_endpoint_security_group.security_group_id]

  endpoints = {
    ecr_api = {
      service             = "ecr.api"
      private_dns_enabled = true
      subnet_ids          = var.public_subnet_ids
    }
    ecr_dkr = {
      service             = "ecr.dkr"
      private_dns_enabled = true
      subnet_ids          = var.public_subnet_ids_dkr
    }
    s3 = {
      service         = "s3"
      service_type    = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
    }
    dynamodb = {
      service         = "dynamodb"
      service_type    = "Gateway"
      route_table_ids = flatten([module.vpc.private_route_table_ids])
      tags            = { Name = "dynamodb-vpc-endpoint" }
    }
  }

  tags = local.tags
}

module "vpc_endpoint_security_group" {
  source  = "../Modules/terraform-aws-security-group"

  name        = "${local.name}-vpc-endpoint"
  description = "Security group for VPC endpoints"
  vpc_id      = module.vpc.vpc_id

  ingress_with_self = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "Container to VPC endpoint service"
      self        = true
    },
  ]

  egress_cidr_blocks = ["0.0.0.0/0"]
  egress_rules       = ["https-443-tcp"]

  tags = local.tags
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/batch/${local.name}"
  retention_in_days = 1

  tags = local.tags
}
