import sys
import time
import boto3
from awsglue.utils import getResolvedOptions
from ddb_helper_functions import submit_aws_batch_job
from dynamodb_util import TrainInputDataModel, TrainStateDataModel, TrainingMetaDataModel \
    , Timelaps


######################## This is for local development ###################
# import time
# import boto3
# from awsglue.utils import getResolvedOptions
#
# from model.utils.dynamodb_util import TrainInputDataModel, TrainStateDataModel, TrainingMetaDataModel \
#     , TrainingAlgorithmStatus, Timelaps
# from model.utils.ddb_helper_functions import submit_aws_batch_job, delete_table_record, get_job_logstream
# import json
# import logging
##########################################################################


def read_train_input_table():
    """
    :return: Returns iterator for the records from TrainInput DDB Table
    """
    items = TrainInputDataModel.scan()
    return items


def insert_train_job_state_table(batchjob_id,
                                 step_job_id,
                                 pk,
                                 mapping_id,
                                 mapping_json_s3_path, usecase_name,
                                 algo_execution_status,
                                 algo_names,
                                 s3_pk_mappingid_data_input_path,
                                 algo_final_run_s3outputpaths,
                                 batch_job_definition,
                                 s3_training_output_path,
                                 s3_pred_or_eval_output_path,
                                 cur_batchjob_id,
                                 first_run_awsbatchjob_cw_log_url,
                                 batch_job_status_overall, input_data_set, **kwargs) -> int:
    """
    Takes input all columns and saves data in TrainState DDB Table

    :param batch_triggered_num_runs:
    :param batchjob_id:
    :param batchjob_id:
    :param step_job_id:
    :param skuid:
    :param mapping_id:
    :param algo_execution_status:
    :param algo_names: list of algorithms
    :param s3_pk_mappingid_data_input_path:
    :param algo_final_run_s3outputpaths:
    :param batch_job_definition:
    :param s3_training_output_path:
    :param s3_pred_or_eval_output_path:
    :param cur_batchjob_id:
    :param batch_job_status_overall:
     **kwargs
    :return: exit code
    """
    # try:

    TrainStateDataModel(batchjob_id=batchjob_id,
                        step_job_id=step_job_id,
                        pk=pk,
                        mapping_id=mapping_id,
                        mapping_json_s3_path=mapping_json_s3_path,
                        usecase_name=usecase_name,
                        algo_execution_status=algo_execution_status,
                        algo_names=algo_names,
                        s3_pk_mappingid_data_input_path=s3_pk_mappingid_data_input_path,
                        algo_final_run_s3outputpaths=algo_final_run_s3outputpaths,
                        batch_job_definition=batch_job_definition,
                        s3_training_prefix_output_path=s3_training_output_path,
                        s3_pred_or_eval_prefix_output_path=s3_pred_or_eval_output_path,
                        cur_awsbatchjob_id=batchjob_id,
                        first_run_awsbatchjob_cw_log_url=first_run_awsbatchjob_cw_log_url,
                        awsbatch_job_status_overall=batch_job_status_overall,
                        input_data_set=input_data_set
                        ).save()
    # StateDataModel(querystring).save()

    # except Exception as error:
    #     logging.log(error)
    #     print("Error- {}".format(error))
    #     return False
    return True


if __name__ == '__main__':

    # https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-extensions-get-resolved-options.html
    args = getResolvedOptions(sys.argv,
                              [
                                  'train_inputtable_name',
                                  'train_statetable_name',
                                  'train_metatable_name',
                                  'region'])

    submit_start_epoch = int(time.time())

    # dynamically set the table names for input, state and meta dynamoDB tables
    TrainInputDataModel.setup_model(TrainInputDataModel,
                                    args['train_inputtable_name'],
                                    args['region'])
    TrainStateDataModel.setup_model(TrainStateDataModel,
                                    args['train_statetable_name'],
                                    args['region'])
    TrainingMetaDataModel.setup_model(TrainingMetaDataModel,
                                      args['train_metatable_name'],
                                      args['region'])

    if not TrainStateDataModel.exists():
        TrainStateDataModel.create_table(read_capacity_units=100, write_capacity_units=100)
        time.sleep(20)

    metaitemtemp = TrainingMetaDataModel.get("fixedlookupkey")

    # fetch batch job params from Meta Data Table
    aws_batch_job_name = metaitemtemp.aws_batch_job_prefixname
    aws_batch_job_queue = metaitemtemp.aws_batch_job_queue
    aws_batch_job_def = metaitemtemp.aws_batch_job_definition

    pk_items_data_iterator = read_train_input_table()
    total_skus = pk_items_data_iterator.total_count

    batch_client = boto3.client('batch')
    num_entry_in_state_table=0
    for job in pk_items_data_iterator:
        num_entry_in_state_table = num_entry_in_state_table +1
        print("I am inside loop", job.to_json())
        # item = json.loads(item.to_json())
        # TODO- custom create s3 path training and evaluation
        # TODO- few parameters are coming from inputTable and few needs to be created

        training_output_path = """s3://{}/training/year={}/month={}/day={}/stepjobid={}/pk={}/mapping={}/""".format(
            job.s3_output_bucket_name, job.execution_year, job.execution_month,
            job.execution_day, job.step_job_id, job.pk, job.mapping_id)

        pred_or_eval_output_path = """s3://{}/pred_or_eval/year={}/month={}/day={}/stepjobid={}/pk={}/mapping={}/""".format(
            job.s3_output_bucket_name, job.execution_year, job.execution_month,
            job.execution_day, job.step_job_id, job.pk, job.mapping_id)

        status, job_id, aws_batch_job_definition = submit_aws_batch_job(
            boto3_client=batch_client,
            algo_names_list=job.algo_names,
            s3_pk_mappingid_data_input_path=job.s3_pk_mappingid_data_input_path,
            s3_training_prefix_output_path=training_output_path,
            s3_pred_or_eval_prefix_output_path=pred_or_eval_output_path,
            train_metatable_name=args['train_metatable_name'],
            pk=job.pk,
            mapping_id=job.mapping_id,
            aws_batch_job_name=aws_batch_job_name,
            aws_batch_job_queue=aws_batch_job_queue,
            aws_batch_job_definition=aws_batch_job_def,
            region=args['region']
        )

        s3_training_output_path = """s3://{}/training/year={}/month={}/day={}/stepjobid={}/pk={}/mapping={}/batchjobid={}/""".format(
            job.s3_output_bucket_name, job.execution_year, job.execution_month,
            job.execution_day, job.step_job_id, job.pk, job.mapping_id, job_id)

        s3_pred_or_eval_output_path = """s3://{}/evaluation/year={}/month={}/day={}/stepjobid={}/pk={}/mapping={}/batchjobid={}""".format(
            job.s3_output_bucket_name, job.execution_year, job.execution_month,
            job.execution_day, job.step_job_id, job.pk, job.mapping_id, job_id)

        # TODO- Thi needs to be moved into Complete Script
        # first_run_awsbatchjob_cw_log_url = get_job_logstream(batchjob_id=job_id,
        #                                                     boto3_client=batch_client)
        first_run_awsbatchjob_cw_log_url = ""

        print("AWS batch details ", status, job_id, total_skus)
        batch_job_status_overall = "SUBMITTED"
        runid = 0

        if status:
            # s3_training_outpath = os.path.join(job.s3_output_bucket_name, "training")
            # s3_evaluation_outpath = os.path.join(job.s3_output_bucket_name, "evaluation")

            # Insert record into TrainStateTable

            insert_train_job_state_table(batchjob_id=job_id,
                                         step_job_id=job.step_job_id,
                                         pk=job.pk,
                                         mapping_id=job.mapping_id,
                                         algo_execution_status=[],
                                         algo_names=job.algo_names,
                                         algo_final_run_s3outputpaths=[],
                                         batch_job_definition=aws_batch_job_definition,
                                         s3_training_output_path=s3_training_output_path,
                                         s3_pred_or_eval_output_path=s3_pred_or_eval_output_path,
                                         cur_batchjob_id=job_id,
                                         first_run_awsbatchjob_cw_log_url=first_run_awsbatchjob_cw_log_url,
                                         batch_job_status_overall=batch_job_status_overall,
                                         mapping_json_s3_path=job.mapping_json_s3_path,
                                         usecase_name=job.usecase_name,
                                         s3_pk_mappingid_data_input_path=job.s3_pk_mappingid_data_input_path,
                                         input_data_set=job.input_data_set
                                         )
            # Deleting at cleanup stage - required for debugging and rerunning and manually
            # delete_table_record(TrainInputDataModel, TrainInputDataModel.pk_mappingid,
            #                    job.pk_mappingid)
        else:
            raise Exception("Job submission process steps failed")

    # Crate entries to save into Meta
    training_step_prefix_path = """s3://{}/training/year={}/month={}/day={}/stepjobid={}/""".format(
        metaitemtemp.s3_bucket_name_shared, metaitemtemp.execution_year, metaitemtemp.execution_month,
        metaitemtemp.execution_day, metaitemtemp.step_job_id)

    pred_or_eval_step_prefix_path = """s3://{}/pred_or_eval/year={}/month={}/day={}/stepjobid={}/""".format(
        metaitemtemp.s3_bucket_name_shared, metaitemtemp.execution_year, metaitemtemp.execution_month,
        metaitemtemp.execution_day, metaitemtemp.step_job_id)

    count_train_state_model = TrainStateDataModel.count()
    submit_end_epoch = int(time.time())
    metaitemtemp.s3_pred_or_eval_prefix_output_path = pred_or_eval_step_prefix_path
    metaitemtemp.s3_eval_summary_prefix_output_path = training_step_prefix_path
    metaitemtemp.aws_batch_submission_timelaps = Timelaps(start_time=submit_start_epoch, end_time=submit_end_epoch)
    metaitemtemp.model_creation_pred_or_eval_timelaps = Timelaps(start_time=submit_end_epoch, end_time=submit_end_epoch)
    metaitemtemp.state_table_total_num_batch_jobs = num_entry_in_state_table
    metaitemtemp.save()

    # check number of records
    # assert (TrainInputDataModel.count() == 0), "Failed to submit all jobs"
    assert (int(count_train_state_model) == int(total_skus)), "Failed to submit all jobs"
    print(count_train_state_model)
