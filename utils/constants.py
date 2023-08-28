AWS_BATCH_JOB_NAME_TRAINING = "batch_job_name"
AWS_BATCH_JOB_QUEUE_TRAINING = "arn:aws:batch:ap-south-1:731580992380:job-queue/mlops-batch_queue_ec2-poc"
AWS_BATCH_JOB_DEFINITION_TRAINING = "arn:aws:batch:ap-south-1:731580992380:job-definition/mlops-batch_job_ec2-poc:1"

AWS_BATCH_JOB_NAME_INFERENCE = "batch_job_inference"
AWS_BATCH_JOB_QUEUE_INFERENCE = "arn:aws:batch:ap-south-1:731580992380:job-queue/mlops-inferencing-batch-queue-ec2-poc"
AWS_BATCH_JOB_DEFINITION_INFERENCE = "arn:aws:batch:ap-south-1:731580992380:job-definition/mlops-inference-batch-job-def-ec2-poc:1"

SSM_TRAINING_COMPLETE_STATUS = 'ssm_training_complete_status'
SSM_INFERENCING_COMPLETE_STATUS = 'ssm_inferencing_complete_status'
SSM_WINNER_ALGORITHM = 'ssm_winner_algorithm'
SSM_APPROVED_MODEL_PREFIX_PATH = 'ssm_approved_model_prefix_path'

SSM_TRAINING_COMPLETE_STATUS_NAME = 'training_complete_status'
SSM_INFERENCING_COMPLETE_STATUS_NAME = 'inferencing_complete_status'
SSM_WINNER_ALGORITHM_NAME = 'winner_algorithm'
SSM_APPROVED_MODEL_PREFIX_PATH_NAME = 'approved_model_prefix_path'

TRAINING_ATHENA_DB = 'default'
TRAINING_STATETABLE_ATHENA_TABLE_NAME = 'debug'
TRAINING_METATABLE_ATHENA_TABLE_NAME = 'meta'

INFERENCE_DATASET_S3_KEY = 'inference_data/inference_data.csv'

JOB_STATUS_DICT = {'submitted': 'SUBMITTED', 'pending': 'PENDING',
                   'runnable': 'RUNNABLE', 'starting': 'STARTING',
                   'running': 'RUNNING',
                   'succeeded': 'SUCCEEDED', 'failed': 'FAILED'}
