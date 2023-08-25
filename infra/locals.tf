locals {
    region-short    =  join("", split("-", data.aws_region.current.name))
}

locals {
  name_prefix = "${var.application-name}-${var.stage-name}-${var.env}-${local.region-short}"

  common_instance_user_data = <<-EOT
    #!/bin/bash
    echo "Append userdata commands underneath."
  EOT

}


locals {
  definition_template1 = <<EOF
{
  "Comment": "An example Step Functions state machine to run and check Glue job status",
  "StartAt": "Glue python(data gatekeeper)",
  "States": {
    "Glue python(data gatekeeper)": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${module.glue-job-gatekeeper.name}",
        "Arguments": {
          "--execution_id.$": "$$.Execution.Id",
          "--use_case_name.$": "$.use_case_name",
          "--athena_pred_or_eval_table_name.$": "$.athena_pred_or_eval_table_name",
          "--athenadb_name.$": "$.athenadb_name",
          "--athenadb_debug_table_name.$": "$.athenadb_debug_table_name",
          "--athenadb_evaluation_summary_table_name.$": "$.athenadb_evaluation_summary_table_name",
          "--train_statetable_name.$": "$.train_statetable_name",
          "--train_inputtable_name.$": "$.train_inputtable_name",
          "--train_metatable_name.$": "$.train_metatable_name",
          "--s3_bucket_name_internal.$": "$.s3_bucket_name_internal",
          "--s3_bucket_name_shared.$": "$.s3_bucket_name_shared",
          "--mapping_json_S3_path.$": "$.mapping_json_S3_path",
          "--aws_batch_job_definition_arn.$": "$.aws_batch_job_definition_arn",
          "--region.$": "$.region",
          "--year.$": "$.year",
          "--month.$": "$.month",
          "--day.$": "$.day",
          "--aws_batch_job_queue.$": "$.aws_batch_job_queue",
          "--aws_batch_job_name.$": "$.aws_batch_job_name",
          "--athenadb_metadata_table_name.$": "$.athenadb_metadata_table_name",
          "--ssm_training_complete_status.$": "$.ssm_training_complete_status",
          "--dq_athena_db.$": "$.dq_athena_db",
          "--dq_table.$": "$.dq_table",
          "--email_topic_arn.$": "$.email_topic_arn",
          "--model_package_group_arn.$": "$.model_package_group_arn",
          "--training_event_bus_name.$": "$.training_event_bus_name",
          "--repository.$": "$.repository"  
        }
      },
      "Next": "get ecr repo url",
      "Catch": [
        {
          "ErrorEquals": [
            "States.TaskFailed"
          ],
          "Comment": "Failed state handling",
          "Next": "Glue Python (Cleanup)"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.Timeout"
          ],
          "BackoffRate": 2,
          "MaxAttempts": 2,
          "Comment": "Time out retry",
          "IntervalSeconds": 30
        }
      ]
    },
    "get ecr repo url": {
      "Type": "Task",
      "Next": "SageMaker CreateProcessingJob-Sync",
      "Parameters": {
        "Name": "/mvp/development/training-job/ecr_preprocessing"
      },
      "Resource": "arn:aws:states:::aws-sdk:ssm:getParameter",
      "ResultPath": "$.Preprocessing_url"
    },
    "SageMaker CreateProcessingJob-Sync": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sagemaker:createProcessingJob.sync",
      "Parameters": {
        "ProcessingJobName.$": "$$.Execution.Name",
        "AppSpecification": {
          "ImageUri.$": "$.Preprocessing_url.Parameter.Value",
          "ContainerArguments.$": "States.StringSplit(States.Format('--train_metatable_name,{},--region,{}',$.Arguments['--train_metatable_name'],$.Arguments['--region']),',')"
        },
        "ProcessingResources": {
          "ClusterConfig": {
            "InstanceCount": 1,
            "InstanceType": "ml.c5.2xlarge",
            "VolumeSizeInGB": 10
          }
        },
        "RoleArn": "arn:aws:iam::731580992380:role/SagemakerProcessingJobAPIExecutionRole"
      },
      "Next": "Glue pyhton (Training submit AWS Batch)",
      "Catch": [
        {
          "ErrorEquals": [
            "States.TaskFailed"
          ],
          "Comment": "Failed stated handling",
          "Next": "Glue Python (Cleanup)"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.Timeout"
          ],
          "BackoffRate": 2,
          "MaxAttempts": 2,
          "Comment": "timeout retry",
          "IntervalSeconds": 30
        }
      ]
    },
    "Glue pyhton (Training submit AWS Batch)": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${module.glue-job-submit_training_job_awsbatch_statetable.name}"
      },
      "Next": "Wait",
      "Catch": [
        {
          "ErrorEquals": [
            "States.TaskFailed"
          ],
          "Comment": "failed state handling",
          "Next": "Glue Python (Cleanup)"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.Timeout"
          ],
          "BackoffRate": 2,
          "MaxAttempts": 2,
          "Comment": "timeout retry",
          "IntervalSeconds": 30
        }
      ]
    },
    "Glue python(status check AWS Batch)": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${module.glue-job-training_job_awsbatch_status_check.name}"
      },
      "Next": "GetParameter",
      "Catch": [
        {
          "ErrorEquals": [
            "States.TaskFailed"
          ],
          "Comment": "failed state handling",
          "Next": "Glue Python (Cleanup)"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.Timeout"
          ],
          "BackoffRate": 2,
          "MaxAttempts": 2,
          "Comment": "timeout retry",
          "IntervalSeconds": 30
        }
      ]
    },
    "GetParameter": {
      "Type": "Task",
      "Next": "Parameter-Check",
      "Parameters": {
        "Name": "${module.ssm-parameters-glue-job.ssm_parameter_name}"
      },
      "Resource": "arn:aws:states:::aws-sdk:ssm:getParameter"
    },
    "Parameter-Check": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.Parameter.Value",
          "StringEquals": "True",
          "Next": "Glue Python(Evalution)"
        },
        {
          "Variable": "$.Parameter.Value",
          "StringEquals": "False",
          "Next": "Wait"
        }
      ],
      "Default": "Glue Python(Evalution)"
    },
    "Glue Python(Evalution)": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${module.glue-job-evaluation_summary.name}"
      },
      "Next": "Glue Python (Cleanup)",
      "ResultPath": "$.jobRun",
      "Catch": [
        {
          "ErrorEquals": [
            "States.TaskFailed"
          ],
          "Comment": "failed state handling",
          "Next": "Glue Python (Cleanup)"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.Timeout"
          ],
          "BackoffRate": 2,
          "MaxAttempts": 2,
          "Comment": "timeout retry",
          "IntervalSeconds": 30
        }
      ]
    },
    "Glue Python (Cleanup)": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${module.glue-job-clean_up_job.name}"
      },
      "End": true,
      "ResultPath": "$.jobRun"
    },
    "Wait": {
      "Type": "Wait",
      "Seconds": 30,
      "Next": "Glue python(status check AWS Batch)"
    }
  }
}
EOF
}
