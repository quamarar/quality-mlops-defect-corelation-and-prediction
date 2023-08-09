/*===============================
#              S3
===============================*/

output "logging-s3-bucket" {
  value       = module.logging-s3-bucket.s3_bucket_id
}

output "training-s3-bucket" {
  value       = module.training-s3-bucket.s3_bucket_id
}

output "inference-s3-bucket" {
  value       = module.inference-s3-bucket.s3_bucket_id
}

output "monitoring-s3-bucket" {
  value       = module.monitoring-s3-bucket.s3_bucket_id
}
