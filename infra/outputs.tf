/*===============================
#              KMS
===============================*/

output "kms_default" {
  value       = module.kms_default.key_arn
}



/*===============================
#              S3
===============================*/

output "internal-s3-bucket" {
  value       = module.internal-s3-bucket.s3_bucket_id
}

/*===============================
#       SSM Parameters
===============================*/

output "ssm-parameters-training-ecr-preprocessing" {
 value = module.ssm-parameters-training-ecr-preprocessing.ssm_parameter_name
}

output "ssm-parameter-training-ecr-training" {
 value = module.ssm-parameter-training-ecr-training.ssm_parameter_name
}

output "ssm_parameter_name_glue_job" {
 value = module.ssm-parameters-glue-job.ssm_parameter_name
}

/*===============================
#            IAM
===============================*/

output "glue-job-role-arn" {
  description = "ARN of IAM role"
  value       = module.glue-job-role.iam_role_arn
}

/*===============================
#            glue-job
===============================*/

output "glue-job-gatekeeper" {
  description = "Glue job gatekeeper name"
   value = module.glue-job-gatekeeper.name
}

output "glue-job-submit_training_job_awsbatch_statetable" {
  description = "Glue job submit training job awsbatch statetable name"
  value = module.glue-job-submit_training_job_awsbatch_statetable.name
}

output "glue-job-training_job_awsbatch_status_check" {
  description = "Glue job submit training job status check name"
  value = module.glue-job-training_job_awsbatch_status_check.name
}

output "glue-job-evaluation_summary" {
  description = "Glue job evaluation summary name"
  value = module.glue-job-evaluation_summary.name
}

output "glue-job-clean_up_job" {
  description = "Glue job clean up job name"
  value = module.glue-job-clean_up_job.name
}

/*===============================
#           ECR
===============================*/

output "repository_arn_processing" {
  description = "Full ARN of the repository"
  value       = module.ecr_registry_processing.repository_arn
}

output "repository_arn_training" {
  description = "Full ARN of the repository"
  value       = module.ecr_registry_training.repository_arn
}


output "repository_url_processing" {
  description = "The URL of the repository (in the form `aws_account_id.dkr.ecr.region.amazonaws.com/repositoryName`)"
  value       = module.ecr_registry_processing.repository_url
}

output "repository_url_training" {
  description = "The URL of the repository (in the form `aws_account_id.dkr.ecr.region.amazonaws.com/repositoryName`)"
  value       = module.ecr_registry_training.repository_url
}

/*===============================
#    DynamoDb Table
===============================*/

output "traininput-dynamodb-table_arn" {
  description = "ARN of the DynamoDB table"
  value       = module.traininput-dynamodb-table.dynamodb_table_arn
}

output "trainstate-dynamodb-table_arn" {
  description = "ARN of the DynamoDB table"
  value       = module.trainstate-dynamodb-table.dynamodb_table_arn
}

output "trainmeta-dynamodb-table_arn" {
  description = "ARN of the DynamoDB table"
  value       = module.trainmeta-dynamodb-table.dynamodb_table_arn
}