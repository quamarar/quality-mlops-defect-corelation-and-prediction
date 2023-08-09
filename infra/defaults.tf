# defaults.tf sets defaults for complex object types
# https://github.com/aws-ia/standards-terraform/issues/13

locals {
    region-short    =  join("", split("-", data.aws_region.current.name))
}

locals {
  name_prefix = "${var.application-name}-${var.stage-name}-${local.region-short}"

  common_instance_user_data = <<-EOT
    #!/bin/bash
    echo "Append userdata commands underneath."
  EOT

}

locals {
  bucket_ids  = {
    logging-bucket      = module.logging-s3-bucket.s3_bucket_id
    training-bucket     = module.training-s3-bucket.s3_bucket_id
    inference-bucket    = module.inference-s3-bucket.s3_bucket_id
    monitoring-bucket   = module.monitoring-s3-bucket.s3_bucket_id
  }
  

}
