/*===============================
#       Common Details
===============================*/

variable "application-name" {
  type        = string
  description = "Application identifier"
}

variable "stage-name" {
  type        = string
  description = "Stage / Environment identifier"
}

variable "env" {
  type        = string
  description = "Stage / Environment identifier"
}
/*===============================
#         S3 Variables
===============================*/

variable "internal-s3-config" {
  type        = any
  description = "S3 bucket configurations"
  default     = null
}


/*===============================
#   SSM Parameters Variables
===============================*/

variable "ssm-parameter-training-ecr-preprocessing" {
  type        = map(any)
}

variable "ssm-parameter-training-ecr-training" {
  type        = map(any)
}

variable "ssm-parameters-glue-job-config" {
  type = map(any)
}

/*===============================
#   Glue-job
===============================*/

variable "glue-job-gatekeeper-config" {
   type = map(any) 
}

variable "glue-job-submit_training_job_awsbatch_statetable-config" {
     type = map(any) 
}

variable "glue-job-training_job_awsbatch_status_check-config" {
     type = map(any) 
}

variable "glue-job-evaluation_summary-config" {
     type = map(any) 
}

variable "glue-job-clean_up_job-config" {
     type = map(any) 
}

/*===============================
#    ECR
===============================*/

variable "processing-private-ecr-config" {
   type = map(any)
}

variable "training-private-ecr-config" {
   type = map(any)
}

variable "processing_ecr-registry-config" {
    type = map(any)
}

variable "training_ecr-registry-config" {
    type = map(any)
}

/*===============================
#    step-function
===============================*/


variable "step_function_name" {
  type = string
}