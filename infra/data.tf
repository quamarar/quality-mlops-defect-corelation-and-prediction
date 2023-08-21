data "aws_region" "current" { }

data "aws_caller_identity"  "current"   {}
data "aws_partition" "current" {}

data "aws_iam_policy_document" "glue-job-policy" {
    statement {
        sid = "glue01"

        actions = [
            "*"
        ]

       resources = [ 
          "arn:aws:iam::aws:policy/IAMFullAccess",
          "arn:aws:iam::aws:policy/AmazonS3FullAccess",
          "arn:aws:iam::aws:policy/CloudWatchFullAccess",
          "arn:aws:iam::aws:policy/AmazonKinesisFullAccess",
          "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
          
         ]
    }
}


data "aws_iam_policy_document" "registry_processing" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions = [
      "ecr:ReplicateImage",
    ]

    resources = [
      module.ecr_registry_processing.repository_arn
    ]
  }
}

data "aws_iam_policy_document" "registry_training" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions = [
      "ecr:ReplicateImage",
    ]

    resources = [
      module.ecr_registry_training.repository_arn
    ]
  }
}