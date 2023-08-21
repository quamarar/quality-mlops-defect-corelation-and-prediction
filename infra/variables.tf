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

variable "shared-s3-config" {
  type        = any
  description = "S3 bucket configurations"
  default     = null
}

