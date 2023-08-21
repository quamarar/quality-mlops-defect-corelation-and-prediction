
from dynamodb_util import TrainStateDataModel, TrainInputDataModel,TrainingMetaDataModel
from awsglue.utils import getResolvedOptions
from constants import SSM_TRAINING_COMPLETE_STATUS
import ddb_helper_functions
import logging
import boto3
import sys


ssm_client = boto3.client('ssm')
args = getResolvedOptions(sys.argv,
                          [
                              'ssm_training_complete_status'
                          ]
                          )


def clean_up_framework(args):

    """
    @:param args: parameters sent from environment
    :return: True
    """
    # dynamically set the table names for input, state and meta dynamoDB tables
    TrainInputDataModel.setup_model(TrainInputDataModel, args['train_inputtable_name'], args['region'])
    TrainStateDataModel.setup_model(TrainStateDataModel, args['train_statetable_name'], args['region'])
    TrainingMetaDataModel.setup_model(TrainingMetaDataModel, args['train_metatable_name'], args['region'])
    input_records = ddb_helper_functions.delete_ddb_table(TrainInputDataModel)
    # if input_records.total_count > 0:
    #     for record in input_records:
    #         ddb_helper_functions.delete_ddb_table()
    #         ddb_helper_functions.delete_table_record(TrainInputDataModel, TrainInputDataModel.sku_mappingid,
    #                                                  record.sku_mappingid)

    all_jobs = ddb_helper_functions.fetch_all_records(TrainStateDataModel)
    batch_client = boto3.client('batch')
    for job in all_jobs:
        if job.awsbatch_job_status_overall != "SUCCEEDED" and job.awsbatch_job_status_overall != "FAILED":
            try:
                logging.log("Terminating AWS Btach JOBID- {}".format(job.cur_awsbatchjob_id))
                response = batch_client.terminate_job(
                    jobId=job.cur_awsbatchjob_id,
                    reason='cleanup'
                )
                ddb_helper_functions.delete_table_record(TrainStateDataModel, TrainStateDataModel.batchjob_id,
                                                         job.batchjob_id)
            except Exception as error:
                logging.error(f"Error to terminate job {job.cur_awsbatchjob_id} - {error}")

    ddb_helper_functions.delete_ddb_table(TrainStateDataModel)
    ddb_helper_functions.delete_ddb_table(TrainingMetaDataModel)
    # state_records = ddb_helper_functions.fetch_all_records(TrainStateDataModel)
    response = ssm_client.put_parameter(
        Name=args.ssm_training_complete_status,
        Description='status complete',
        Value='False',
        Overwrite=True,
    )

    # assert (0 == len(list(input_records))), "Error in deleting records from StateTable"
    # assert (0 == len(list(all_jobs.total_count))), "Error in deleting records from InputTable"
    logging.info("CleanUp job Completed")
    return True


if __name__ == '__main__':
    args = getResolvedOptions(sys.argv,
                              [
                                  'train_inputtable_name',
                                  'train_statetable_name',
                                  'train_metatable_name',
                                  SSM_TRAINING_COMPLETE_STATUS,
                                  'region'])
    clean_up_framework(args)
