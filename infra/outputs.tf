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

output "shared-s3-bucket" {
  value       = module.shared-s3-bucket.s3_bucket_id
}
