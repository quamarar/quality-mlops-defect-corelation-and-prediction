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
