/*===============================
#         S3 Variables
===============================*/

variable "logging-s3-config" {
  type        = any
  description = "S3 bucket configurations"
  default     = null
}

variable "training-s3-config" {
  type        = any
  description = "S3 bucket configurations"
  default     = null
}

variable "inference-s3-config" {
  type        = any
  description = "S3 bucket configurations"
  default     = null
}

variable "monitoring-s3-config" {
  type        = any
  description = "S3 bucket configurations"
  default     = null
}
