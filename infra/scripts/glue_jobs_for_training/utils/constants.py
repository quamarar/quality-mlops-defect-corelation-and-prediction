AWS_BATCH_JOB_NAME = "batch_job_name"
AWS_BATCH_JOB_QUEUE = "arn:aws:batch:ap-south-1:731580992380:job-queue/mlops-batch_queue_ec2-poc"
AWS_BATCH_JOB_DEFINITION = "arn:aws:batch:ap-south-1:731580992380:job-definition/mlops-batch_job_ec2-poc:1"

SSM_TRAINING_COMPLETE_STATUS = 'ssm_training_complete_status'
SSM_INFERENCING_COMPLETE_STATUS = 'ssm_inferencing_complete_status'
SSM_WINNER_ALGORITHM = 'ssm_winner_algorithm'
SSM_APPROVED_MODEL_PREFIX_PATH = 'ssm_approved_model_prefix_path'

JOB_STATUS_DICT = {'submitted':'SUBMITTED', 'pending': 'PENDING',
                   'runnable': 'RUNNABLE', 'starting': 'STARTING',
                   'running': 'RUNNING',
                   'succeeded': 'SUCCEEDED', 'failed': 'FAILED'}
