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
