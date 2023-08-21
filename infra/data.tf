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
          "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess" ,
          ""
         ]
    }
}
