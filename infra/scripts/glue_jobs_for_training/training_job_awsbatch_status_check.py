import logging
import sys
import time

import boto3
from awsglue.utils import getResolvedOptions
from ddb_helper_functions import submit_aws_batch_job, get_job_logstream, \
    delete_folder_from_s3, get_aws_job_status_and_compute_requirement,dump_data_to_s3
from dynamodb_util import TrainStateDataModel, TrainingMetaDataModel, TrainInputDataModel, Timelaps

from constants import SSM_TRAINING_COMPLETE_STATUS, JOB_STATUS_DICT

######################## This is for local development ###################
# import logging
# import sys
# import time
#
# import boto3
#
# from model.utils.constants import JOB_STATUS_DICT, SSM_TRAINING_COMPLETE_STATUS
# from model.utils.dynamodb_util import TrainStateDataModel, TrainingMetaDataModel, TrainInputDataModel, Timelaps
# from model.utils.ddb_helper_functions import submit_aws_batch_job, delete_table_record, get_job_logstream, \
#     delete_folder_from_s3, get_aws_job_status_and_compute_requirement, dump_data_to_s3
# from awsglue.utils import getResolvedOptions

######################## This is for local development ###################

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def reupdate_train_job_state_table_onjobsubmission(batchjob_id, cur_batchjob_id, rerun_batchjob_id,
                                                   batch_job_status_overall, num_runs, recursive_runs=0) -> int:
    """
    :param cur_batchjob_id: 
    :param batchjob_id: haskey for the record to update
    :param rerun_batchjob_id: on submitting job a jobid is returned and for second time re-run try
    :param batch_job_status_overall: status changes  SUBMITTED on re-run
    :param num_runs: default is 1 and auto increments by 1
    :return: exit code
    """

    try:
        item = TrainStateDataModel.get(hash_key=batchjob_id)
        print("Updating JOBID- {} record on resumission of failed job-".format(batchjob_id))
        item.cur_awsbatchjob_id = cur_batchjob_id
        item.rerun_awsbatchjob_id = rerun_batchjob_id
        item.num_runs = num_runs + 1
        item.awsbatch_job_status_overall = batch_job_status_overall
        item.save()

    except Exception as error:
        logging.error("Error: {}".format(error))
        print("Error-".format(error))
        if recursive_runs == 3:
            time.sleep(2)
            return False
        logging.error(
            " Retrying in reupdate_train_job_state_table_onjobsubmission recursive_runs {}".format(recursive_runs))
        reupdate_train_job_state_table_onjobsubmission(batchjob_id, cur_batchjob_id, rerun_batchjob_id,
                                                       batch_job_status_overall, num_runs, recursive_runs + 1)
    return True


def status_update_train_job_state_table(batchjob_id, batch_job_status_overall, num_recursive_calls=0) -> int:
    """
    :param batchjob_id: haskey for the record to update
    :param batch_job_status_overall
    :return: exit code
    """

    try:
        item = TrainStateDataModel.get(hash_key=batchjob_id)
        logging.info("Updating JOBID- {} status to {} in StateTable".
                     format(batchjob_id,batch_job_status_overall))

        item.awsbatch_job_status_overall = batch_job_status_overall
        item.save()

    except Exception as error:
        logging.error("Error: {}".format(error))

        logging.error(
            "Retrying in status_update_train_job_state_table with num_recursive_calls: {}".format(num_recursive_calls))
        if num_recursive_calls == 3:
            raise Exception("status_update_train_job_state_table dynamoDB threw an Exception")
        time.sleep(2)
        status_update_train_job_state_table(batchjob_id, batch_job_status_overall, num_recursive_calls + 1)

    return True


def submit_failed_job_train_state_table(job, batch_client, **kwargs) -> int:
    """
    Method submit to AWS Batch job queue for RE-RUN and update TrainState DDB Table
    @:param job:
    @:param batch_client:
    :return: Returns exit code otherwise exception
    """

    metaitemtemp = TrainingMetaDataModel.get("fixedlookupkey")
    aws_batch_job_name = metaitemtemp.aws_batch_job_prefixname
    aws_batch_job_queue = metaitemtemp.aws_batch_job_queue
    aws_batch_job_def = metaitemtemp.aws_batch_job_definition

    delete_folder_from_s3(boto_s3_resource=kwargs["s3_resource"],
                          bucket=kwargs["bucket"], marker=kwargs["marker"])

    status, batch_job_id, _ = submit_aws_batch_job(boto3_client=batch_client,
                                                   algo_names_list=job.algo_names,
                                                   s3_pk_mappingid_data_input_path=job.s3_pk_mappingid_data_input_path,
                                                   s3_training_prefix_output_path=job.s3_training_prefix_output_path,
                                                   s3_pred_or_eval_prefix_output_path=job.s3_pred_or_eval_prefix_output_path,
                                                   train_metatable_name=metaitemtemp.train_metatable_name,
                                                   pk=job.pk,
                                                   mapping_id=job.mapping_id,
                                                   job_id=job.batchjob_id,
                                                   aws_batch_job_name=aws_batch_job_name,
                                                   aws_batch_job_queue=aws_batch_job_queue,
                                                   aws_batch_job_definition=aws_batch_job_def,
                                                   region = job.Meta.region,
                                                   aws_batch_compute_scale_factor=2)

    reupdate_train_job_state_table_onjobsubmission(batchjob_id=job.batchjob_id, cur_batchjob_id=batch_job_id,
                                                   rerun_batchjob_id=batch_job_id, batch_job_status_overall="SUBMITTED",
                                                   num_runs=job.num_runs)


def update_batch_job_status() -> bool:
    batch_client = boto3.client('batch')
    s3_resource = boto3.resource('s3')

    all_batch_jobs = TrainStateDataModel.scan()

    logging.info('running update_batch_job_status method')
    for job in all_batch_jobs:
        if (job.awsbatch_job_status_overall == JOB_STATUS_DICT['succeeded']) or (
                (job.num_runs == 1) and (job.awsbatch_job_status_overall == JOB_STATUS_DICT['failed'])):
            pass

        cur_batch_job_status, _ = get_aws_job_status_and_compute_requirement(batchjob_id=job.cur_awsbatchjob_id,
                                                                             boto3_client=batch_client)

        # Update only if the status changes - else pass
        if cur_batch_job_status != job.awsbatch_job_status_overall:
            status_update_train_job_state_table(batchjob_id=job.batchjob_id,batch_job_status_overall=cur_batch_job_status)

        if (job.num_runs == 0) and (cur_batch_job_status == JOB_STATUS_DICT['failed']):
            delete_subfolder = str(job.s3_training_prefix_output_path).replace("s3://", "")
            bucket_name = delete_subfolder.split("/")[0]
            marker_path = "/".join(delete_subfolder.split('/')[1:-2])

            submit_failed_job_train_state_table(job=job, batch_client=batch_client, s3_resource=s3_resource,
                                                bucket=bucket_name, marker=marker_path)

    return True


def check_overall_batch_completion() -> bool:
    completed = True
    all_jobs = TrainStateDataModel.scan()

    logging.info('running check_overall_batch_completion method')
    for job in all_jobs:

        if (job.num_runs == 0) and (job.awsbatch_job_status_overall == JOB_STATUS_DICT['failed']):
            logging.info('Not all jobs completed, wait for completion...')
            return False
        if (job.awsbatch_job_status_overall != JOB_STATUS_DICT['failed']) and (
                job.awsbatch_job_status_overall != JOB_STATUS_DICT['succeeded']):
            logging.info('Not all jobs completed, wait for completion...')
            return False
    return completed


def update_cloudwatch_log_urls() -> tuple:
    batch_client = boto3.client('batch')
    scan_items = TrainStateDataModel.scan()
    total_batch_success = 0
    total_batch_failures = 0

    for item in scan_items:
        if item.awsbatch_job_status_overall == 'SUCCEEDED':
            total_batch_success = total_batch_success + 1
        else:
            total_batch_failures = total_batch_failures + 1
        first_run_cw_log = get_job_logstream(item.batchjob_id, batch_client)
        item.first_run_awsbatchjob_cw_log_url = first_run_cw_log
        rerun_cw_log = ""
        if item.rerun_awsbatchjob_id != TrainStateDataModel.rerun_awsbatchjob_cw_log_url.default:
            rerun_cw_log = get_job_logstream(item.rerun_awsbatchjob_id, batch_client)
        item.update(actions=[
            TrainStateDataModel.first_run_awsbatchjob_cw_log_url.set(first_run_cw_log),
            TrainStateDataModel.rerun_awsbatchjob_cw_log_url.set(rerun_cw_log)
        ])

    return total_batch_success, total_batch_failures


if __name__ == "__main__":
    args = getResolvedOptions(sys.argv,
                              [
                                  'train_inputtable_name',
                                  'train_statetable_name',
                                  'train_metatable_name',
                                  SSM_TRAINING_COMPLETE_STATUS,
                                  'region'])

    # dynamically set the table names for input, state and meta dynamoDB tables
    TrainInputDataModel.setup_model(TrainInputDataModel, args['train_inputtable_name'], args['region'])
    TrainStateDataModel.setup_model(TrainStateDataModel, args['train_statetable_name'], args['region'])
    TrainingMetaDataModel.setup_model(TrainingMetaDataModel, args['train_metatable_name'], args['region'])

    # UPDATE STATUS OF THE JOBS In STATE TABLE
    update_batch_job_status()

    """model_s3_output_path = s3://bucketname/debug/year=execution_year
                                       /month=execution_month/day=execution_day/stepjobid=step_job_id/"""

    metaitem = TrainingMetaDataModel.get("fixedlookupkey")
    year = metaitem.execution_year
    month = metaitem.execution_month
    day = metaitem.execution_day
    s3_bucket = metaitem.s3_bucket_name_shared
    sf_exec_id = metaitem.step_job_id
    all_job_completion_flag = check_overall_batch_completion()
    logging.info("Job completion flag {}".format(all_job_completion_flag))
    if all_job_completion_flag:
        print("All sumbitted AWS Batch Jobs Completed")

        object_name = """debug/year={}/month={}/day={}/stepjobid=step_job_id/step_job_overall_summary.json""".format(
            year, month, day, sf_exec_id)

        dump_data_to_s3(s3_ouput_bucket=s3_bucket,
                       s3_output_object_name=object_name, ddb_model=TrainStateDataModel)

        total_batch_success, total_batch_failures = update_cloudwatch_log_urls()

        metaitem.total_numb_batch_job_succeeded = total_batch_success
        metaitem.total_num_batch_job_failed = total_batch_failures

        temp_start = metaitem.model_creation_pred_or_eval_timelaps.start_time
        metaitem.model_creation_pred_or_eval_timelaps = Timelaps(start_time=temp_start,
                                                                 end_time=int(time.time()))
        metaitem.save()

        ssm_client = boto3.client('ssm')

        response = ssm_client.put_parameter(
            Name=args[SSM_TRAINING_COMPLETE_STATUS],
            Description='status complete',
            Value='True',
            Overwrite=True
        )
