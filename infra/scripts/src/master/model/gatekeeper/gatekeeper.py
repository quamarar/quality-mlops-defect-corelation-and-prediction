import logging
import os
import sys
import time
import boto3
from awsglue.utils import getResolvedOptions

from ddb_helper_functions import copy_mapping_json
from dynamodb_util import TrainingMetaDataModel, Timelaps

# from model.utils.ddb_helper_functions import copy_mapping_json
# from model.utils.dynamodb_util import TrainingMetaDataModel, Timelaps
# TODO - sns
# TODO - git url needs to saved

def populate_training_meta_table(args):
    try:
        step_job_id_post_split = ":".join(args['execution_id'].split(":")[-2:])
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
                              step_job_id= step_job_id_post_split
                              ).save()
    except Exception as error:
        logging.error(error)
        raise Exception("populate_training_meta_table failed")

def update_ssm_store(args)->None:
    ssm_client = boto3.client('ssm',region_name=args['region'])

    ssm_client.put_parameter(
        Name=args['ssm_training_complete_status'],
        Description='status complete',
        Value='False',
        Overwrite=True
        )


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
                                  'region'])
    print (args)
    print("##################################################################")
    gatekeeper_start_epoch = int(time.time())
    s3_client = boto3.client('s3')


    TrainingMetaDataModel.setup_model(TrainingMetaDataModel,args['train_metatable_name'],args['region'])
    if not TrainingMetaDataModel.exists():
        TrainingMetaDataModel.create_table(read_capacity_units=100, write_capacity_units=100)
        time.sleep(10)

    #################### Gatekeeper Logic goes in #########################


    # TODO manan needs to write his code here

    # TODO- checking train algos superset of Inference algos


    #######################################################################

    update_ssm_store(args)
    populate_training_meta_table(args)

    # execution_id example is ARN  - arn:aws:states:ap-south-1:ACCNO:execution:MSILStateMachine:0a260727-cfea-407d-adfa-dc5add684217
    step_job_id = ":".join(args['execution_id'].split(":")[-2:])
    internal_s3_mapping_json_path = args['mapping_json_S3_path']
    print("Shared and interal  S3 bucket, incoming mapping_json_s3_path : ", args['s3_bucket_name_shared'], args['s3_bucket_name_internal'],internal_s3_mapping_json_path)

    shared_s3_mapping_json_key = "mappingjson/year={}/month={}/day={}/stepjobid={}/mapping.json".format(args['year'], args['month'], args['day'], step_job_id)

    mapping_json_constants = copy_mapping_json(
                                               source_path=internal_s3_mapping_json_path,
                                               destination_s3_bucket=args['s3_bucket_name_shared'],
                                               destination_s3_key=shared_s3_mapping_json_key)
    print(mapping_json_constants)
    print("*********** Loading mapping json from S3: Complete ! ************")

    mapping_json_s3_path = args['s3_bucket_name_shared'] + shared_s3_mapping_json_key
    print("Mapping Json S3 path private copy is : ", mapping_json_s3_path)

    primaryKey = mapping_json_constants["mapping_json_data"]["primary_key"]
    mapping_id = mapping_json_constants["mapping_json_data"]["mappingColumn"]


    #Populate other elements of the Meta Table
    meta_item = TrainingMetaDataModel.get(hash_key="fixedlookupkey")
    meta_item.step_function_start_time=gatekeeper_start_epoch
    meta_item.pk_column_name = primaryKey
    meta_item.mapping_id_column_name = mapping_id
    gatekeeper_end_epoch = int(time.time())
    meta_item.step_function_start_time = gatekeeper_start_epoch
    meta_item.gatekeeper_timelaps = Timelaps(start_time=gatekeeper_start_epoch,
                                                end_time=gatekeeper_end_epoch)
    #TODO  Needs to be fixed
    meta_item.mapping_json_s3_path = internal_s3_mapping_json_path
    meta_item.save()

    # Revalidate deserialization of Model is happening as expected
    test_item = TrainingMetaDataModel.get(hash_key="fixedlookupkey")
    print( "Dumped metadata table entryu is ======  " , test_item.to_json())

