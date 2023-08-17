/*===============================
#              KMS
===============================*/

output "kms_default" {
  value       = module.kms_default.key_arn
}

