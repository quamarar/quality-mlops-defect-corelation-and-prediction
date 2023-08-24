"""
Prerequisites:
1. Create identity in SES service
2. Create an Amazon SNS Topic "model_start_dq_notification"
3. Create Email subscription to the Amazon SNS Topic
"""

import logging
import os
import sys
import time
import boto3
from awsglue.utils import getResolvedOptions
import pythena
from datetime import datetime

from ddb_helper_functions import copy_mapping_json, get_mapping_column_of_training_and_inferencing, \
    read_json_from_s3, get_algo_set_of_training_and_inferencing, email_sns
from dynamodb_util import TrainingMetaDataModel, Timelaps


# from model.utils.ddb_helper_functions import copy_mapping_json
# from model.utils.dynamodb_util import TrainingMetaDataModel, Timelaps


job_name = "training_gatekeeper"
log = logging.getLogger(__name__)
logging.basicConfig(format=' %(job_name)s - %(asctime)s - %(message)s ')


def populate_training_meta_table(args):
    try:
        step_job_id_post_split = "-".join(args['execution_id'].split(":")[-2:])
        TrainingMetaDataModel(hash_key="fixedlookupkey",
                              usecase_name=args['use_case_name'],
                              execution_year=args['year'],
                              execution_month=args['month'],
                              execution_day=args['day'],
                              aws_batch_job_definition=args['aws_batch_job_definition_arn'],
                              aws_batch_job_queue=args['aws_batch_job_queue'],
                              aws_batch_job_prefixname=args['aws_batch_job_name'],
                              s3_bucket_name_shared=args['s3_bucket_name_shared'],
                              s3_bucket_name_internal=args['s3_bucket_name_internal'],
                              train_inputtable_name=args['train_inputtable_name'],
                              train_metatable_name=args['train_metatable_name'],
                              train_statetable_name=args['train_statetable_name'],
                              athenadb_name=args['athenadb_name'],
                              athena_pred_or_eval_table_name=args['athena_pred_or_eval_table_name'],
                              athenadb_debug_table_name=args['athenadb_debug_table_name'],
                              athenadb_evaluation_summary_table=args['athenadb_evaluation_summary_table_name'],
                              athenadb_metadata_table_name=args['athenadb_metadata_table_name'],
                              region=args['region'],
                              step_job_id=step_job_id_post_split,
                              model_package_group_arn=args['model_package_group_arn'],
                              training_event_bus_name=args['training_event_bus_name'],
                              repository=args['repository'],
                              email_topic_arn=args['email_topic_arn']
                              ).save()
    except Exception as error:
        logging.error(error)
        raise Exception("populate_training_meta_table failed")


def update_ssm_store(args) -> None:
    ssm_client = boto3.client('ssm', region_name=args['region'])

    ssm_client.put_parameter(
        Name=args['ssm_training_complete_status'],
        Description='status complete',
        Value='False',
        Overwrite=True
    )


def query_execution_status(execution_id, athena_client):
    """
    Purpose: Check the athena execution status of athena query and keep on trying if the query is in pending or running state
    param : execution_id: execution id of the executed athena query
    param : athena_client: athena client object
    return: query_status: query status of the query
    """
    query_status = athena_client.get_query_status(execution_id)
    if query_status == 'QUEUED' or query_status == 'RUNNING':
        print(f"Sleep for 10 seconds ")
        time.sleep(10)
        query_execution_status(execution_id, athena_client)
    elif query_status == 'SUCCEEDED':
        print(f"Completed ")
        return query_status
    elif query_status == 'FAILED' or query_status == 'CANCELLED':
        print(f"Failed ")
        return query_status



def check_mapping_json_logical_integrity(sns_client,mapping_json_path, usecase_name, step_job_id, email_topic_arn):

    # checking train algos superset of Inference algos
    email_message = f'{datetime.now()}-> Alert!  mapping json integrity checks for {usecase_name} and stepjobid {step_job_id} failed, unable to proceed with ML processing'
    email_subject = f'{usecase_name} ML Model : Mapping Json Integrity check Failure at Training'
    failed = False
    mapping_json = read_json_from_s3(mapping_json_path)
    train_algo_inference, infer_algos_inference = get_algo_set_of_training_and_inferencing(mapping_json)
    if not train_algo_inference.issuperset(infer_algos_inference):
        log.error("inference algo are not subset of training algo..Kindly use same set of algo")
        failed = True

    (train_mapping_column, inference_mapping_column) = get_mapping_column_of_training_and_inferencing(mapping_json)

    if not train_mapping_column in [inference_mapping_column, 'default']:
        failed = True

    if failed is True:
        email_sns(sns_client,email_topic_arn, email_message, email_subject)
        raise Exception("inference algo are not subset of training algo")
        sys.exit(0)


if __name__ == '__main__':
    args = getResolvedOptions(sys.argv,
                              [
                                  'execution_id',
                                  'use_case_name',
                                  'year',
                                  'month',
                                  'day',
                                  'aws_batch_job_definition_arn',
                                  'aws_batch_job_queue',
                                  'aws_batch_job_name',
                                  's3_bucket_name_shared',
                                  's3_bucket_name_internal',
                                  'train_inputtable_name',
                                  'train_statetable_name',
                                  'train_metatable_name',
                                  'athenadb_name',
                                  'athena_pred_or_eval_table_name',
                                  'athenadb_debug_table_name',
                                  'athenadb_metadata_table_name',
                                  'mapping_json_S3_path',
                                  'ssm_training_complete_status',
                                  'athenadb_evaluation_summary_table_name',
                                  'region',
                                  'dq_athena_db',
                                  'dq_table',
                                  'email_topic_arn',
                                  'model_package_group_arn',
                                  'training_event_bus_name',
                                  'repository'])
    print(args)
    print("##################################################################")

    # dq_athena_db = 'poc_monitoring'
    # dq_table = 'dqresults'
    # email_topic_arn = 'arn:aws:sns:ap-south-1:731580992380:model_start_dq_notification'
    dq_athena_db = args['dq_athena_db']
    dq_table = args['dq_table']
    region = args['region']
    usecase_name = args['use_case_name']
    email_topic_arn = args['email_topic_arn']

    gatekeeper_start_epoch = int(time.time())
    s3_client = boto3.client('s3')
    sns_client = boto3.client('sns')
    session = boto3.session.Session()
    athena_client = pythena.Athena(database=dq_athena_db, session=session, region=region)


    TrainingMetaDataModel.setup_model(TrainingMetaDataModel, args['train_metatable_name'], args['region'])
    if not TrainingMetaDataModel.exists():
        TrainingMetaDataModel.create_table(read_capacity_units=100, write_capacity_units=100)
        time.sleep(10)

    #################### Gatekeeper Logic goes in #########################

    # msck repair table
    dq_repair_query = f"MSCK REPAIR TABLE {dq_athena_db}.{dq_table}"
    print(dq_repair_query)
    execution_id = athena_client.execute(query=dq_repair_query, run_async='True')
    query_status = query_execution_status(execution_id, athena_client)

    # DQ failure status check
    athena_dq_failure_check = f"""select sum(status) failed_count from (
                            select case when outcome = 'Failed' then 1 else 0  end as status from (
                            select * , rank() over (partition by source , target , rule order by audittimestamp desc ) rnk 
                            from {dq_athena_db}.{dq_table}) where rnk = 1 )"""
    print(f"athena_dq_failure_check :{athena_dq_failure_check}")
    (validation_df, execution_id) = athena_client.execute(query=athena_dq_failure_check)
    fail_cnt = validation_df['failed_count'].tolist()[0]
    print(f"ETL DQ Failure count :  {fail_cnt}")

    if fail_cnt > 0:
        dq_email_message = f'{datetime.now()}-> Alert! {fail_cnt} DQ checks for {usecase_name} ETL failed, unable to proceed with ML processing'
        dq_email_subject = f'{usecase_name} ML Model : DQ Status Update'
        response = email_sns(sns_client, email_topic_arn, dq_email_message, dq_email_subject)
        print("Sent Email")
        raise Exception(
            f'{datetime.now()}-> Alert! {fail_cnt} DQ checks for {usecase_name} ETL failed, unable to proceed with ML processing')
        sys.exit(0)

    #######################################################################

    # execution_id example is ARN  - arn:aws:states:ap-south-1:ACCNO:execution:MSILStateMachine:0a260727-cfea-407d-adfa-dc5add684217
    step_job_id = "-".join(args['execution_id'].split(":")[-2:])
    internal_s3_mapping_json_path = args['mapping_json_S3_path']
    check_mapping_json_logical_integrity(sns_client,internal_s3_mapping_json_path, usecase_name, step_job_id, email_topic_arn)

    update_ssm_store(args)
    populate_training_meta_table(args)

    print("Shared and interal  S3 bucket, incoming mapping_json_s3_path : ", args['s3_bucket_name_shared'],
          args['s3_bucket_name_internal'], internal_s3_mapping_json_path)

    shared_s3_mapping_json_key = "mappingjson/year={}/month={}/day={}/stepjobid={}/mapping_json.json".format(
        args['year'], args['month'], args['day'], step_job_id)

    (mapping_json_constants, destination_path) = copy_mapping_json(
        source_path=internal_s3_mapping_json_path,
        destination_s3_bucket=args['s3_bucket_name_shared'],
        destination_s3_key=shared_s3_mapping_json_key)
    print(mapping_json_constants)
    print(f"*********** Loading mapping json from S3: Complete ! : {mapping_json_constants}************")


    mapping_json_s3_path = args['s3_bucket_name_shared'] + shared_s3_mapping_json_key
    print("Mapping Json S3 path private copy is : ", mapping_json_s3_path)

    print("Getting the primary key")
    primaryKey = mapping_json_constants["mapping_json_data"]["primary_key"]
    mapping_id = mapping_json_constants["mapping_json_data"]['Training']["mappingColumn"]
    print(f"primaryKey:{primaryKey} , mapping_id:{mapping_id}")

    # Populate other elements of the Meta Table
    meta_item = TrainingMetaDataModel.get(hash_key="fixedlookupkey")
    meta_item.step_function_start_time = gatekeeper_start_epoch
    meta_item.pk_column_name = primaryKey
    meta_item.mapping_id_column_name = mapping_id
    gatekeeper_end_epoch = int(time.time())
    meta_item.step_function_start_time = gatekeeper_start_epoch
    meta_item.gatekeeper_timelaps = Timelaps(start_time=gatekeeper_start_epoch,
                                             end_time=gatekeeper_end_epoch)

    meta_item.mapping_json_s3_path = destination_path
    meta_item.save()
    # Revalidate deserialization of Model is happening as expected
    test_item = TrainingMetaDataModel.get(hash_key="fixedlookupkey")
    print("Dumped metadata table entryu is ======  ", test_item.to_json())