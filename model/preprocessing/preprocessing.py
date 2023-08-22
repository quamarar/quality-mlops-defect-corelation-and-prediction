import argparse
import logging
import os
import time
import boto3
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from model.utils.ddb_helper_functions import upload_file,read_json_from_s3
from model.utils.dynamodb_util import TrainInputDataModel, TrainingMetaDataModel, Timelaps


######################
# import argparse
# import logging
# import time
# import boto3
# import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
# from model.utils.ddb_helper_functions import  upload_file, read_json_from_s3
# from model.utils.dynamodb_util import TrainInputDataModel, TrainingMetaDataModel, Timelaps
##################

def args_parse():
    """

    :param file_path:
    :return: arguments
    """
    constants = {
        'mapping_json_data': {
            'primaryKey': 'part_name',
            'mappingColumn': "region",
            'InferenceMapping': {
                "rajasthan": ["XGB", 'LR'],
                "haryana": ['LR', 'RF']
            },
            'TrainingMapping': {
                "rajasthan": ['XGB', 'LR'],
                "haryana": ['LR', 'RF']
            }
        }
    }
    # Create the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_metatable_name', type=str, required=True)
    parser.add_argument('--region', type=str, required=True)
    return constants, parser.parse_args()


def combine_harmonize_data(file_path) -> pd.DataFrame:
    """
    :param file_path:
    :return: DataFrame
    """
    path = "s3://"
    combined_df = pd.read_csv(file_path)
    return combined_df


def ml_preprocessing(combined_dataframe) -> pd.DataFrame:
    """
    :param combined_dataframe:
    :return: DataFrame
    """
    df = combined_dataframe
    df = df[['part_name', 'base_model', 'engine_type', 'vdtl_tm_type',
             'vdtl_fuel', 'platform', 'part_probability', 'region']]
    df = pd.get_dummies(df, columns=['base_model', 'engine_type', 'vdtl_tm_type', 'vdtl_fuel', 'platform'])
    scaler = MinMaxScaler()
    df[['part_probability']] = scaler.fit_transform(df[['part_probability']])
    return df


def insert_train_job_def_input_table(pk_mappingid, step_job_id, usecase_name,
                                     execution_year, execution_month, execution_day, pkid,
                                     mapping_id, mapping_json_s3_path, algo_execution_status, algo_names,
                                     s3_pk_mappingid_data_input_path, s3_output_bucket_name,
                                     batch_job_definition, batch_job_status_overall, input_data_set, recursive_run=0,
                                     **kwargs) -> int:
    """
    Takes input all columns and saves data in TrainInput DDB Table
    :param pk_mappingid: pk|mapping_id( primary key)
    :param step_job_id:
    :param usecase_name:
    :param execution_year: yyyy
    :param execution_month: mm
    :param execution_day: dd
    :param pkid: unique string
    :param mapping_id:
    :param algo_execution_status:
    :param s3_pk_mappingid_data_input_path:
    :param s3_output_bucket_name:
    :param batch_job_definition: algo_names:
    :param batch_job_status_overall:
    **kwargs
    :return: exit code
    """
    print(
        " About to insert into Input DynamoDB table for partition key {} and reursive num runs {}".format(pk_mappingid,
                                                                                                          recursive_run))
    try:
        TrainInputDataModel(pk_mappingid=pk_mappingid,
                            step_job_id=step_job_id,
                            usecase_name=usecase_name,
                            execution_year=execution_year,
                            execution_month=execution_month,
                            execution_day=execution_day,
                            pk=pkid,
                            mapping_id=mapping_id,
                            mapping_json_s3_path=mapping_json_s3_path,
                            input_data_set=input_data_set,
                            algo_execution_status=algo_execution_status,
                            algo_names=algo_names,
                            s3_pk_mappingid_data_input_path=s3_pk_mappingid_data_input_path,
                            s3_output_bucket_name=s3_output_bucket_name,
                            batch_job_definition=batch_job_definition,
                            batch_job_status_overall=batch_job_status_overall,
                            ).save()

    except Exception as error:
        logging.error(error)
        if recursive_run == 3:
            return False
        time.sleep(1)
        insert_train_job_def_input_table(pk_mappingid, step_job_id, usecase_name,
                                         execution_year, execution_month, execution_day, pkid,
                                         mapping_id, mapping_json_s3_path, algo_execution_status, algo_names,
                                         s3_pk_mappingid_data_input_path, s3_output_bucket_name,
                                         batch_job_definition, batch_job_status_overall, input_data_set,
                                         recursive_run + 1)

    return True


if __name__ == "__main__":
    pre_processing_start_epoch = int(time.time())
    s3_client = boto3.client('s3')

    _,args = args_parse()

    # Meta Table name and Region required to instantiate TrainingMetaDataModel
    TrainingMetaDataModel.setup_model(TrainingMetaDataModel, args.train_metatable_name, args.region)
    meta_item = TrainingMetaDataModel.get("fixedlookupkey")
    TrainInputDataModel.setup_model(TrainInputDataModel, meta_item.train_inputtable_name, meta_item.region)

    # DynamoDB Table Creation
    if not TrainInputDataModel.exists():
        TrainInputDataModel.create_table(read_capacity_units=100, write_capacity_units=100)
        time.sleep(10)


    # Input Path for Preprocessing Job
    analytical_data_path = "s3://{}/{}".format(meta_item.s3_bucket_name_internal, "analytical_data/sample_data.csv")

    combined_df = combine_harmonize_data(analytical_data_path)
    ml_dataset = ml_preprocessing(combined_df)

    # "bucket/trigger_eval_summary/year={year}/month={}/day={}/stepjobid={}"
    # s3_output_path = """s3:///framework-msil-poc-apsouth1-shared/preprocessing/year=execution_year
    #                                        /month=execution_month/day=execution_day/stepjobid=step_execution_id/
    #                                        sm_id=step_execution_id/""".format()

    # preprocess_output_path = "s3://{}/{}".format(shared_s3_bucket,"preprocessing")
    # "this will be used in in_path"
    preprocess_output_path = "s3://{}/preprocessing/year={}/month={}/day={}/stepjobid={}/smid={}/".format(meta_item.s3_bucket_name_shared,
                                         meta_item.execution_year,
                                         meta_item.execution_month,
                                         meta_item.execution_day,
                                         meta_item.step_job_id,
                                         meta_item.step_job_id)

    # Read mapping json from Amazon S3
    mapping_json_constants = read_json_from_s3(meta_item.mapping_json_s3_path, s3_client)
    primaryKey = mapping_json_constants["mapping_json_data"]["primary_key"]
    mapping_id = mapping_json_constants["mapping_json_data"]['Training']["mappingColumn"]

    ml_dataset["pk"] = ml_dataset[primaryKey]
    if mapping_id == "default":
        ml_dataset["mapping"] = 'default'
    else:
        ml_dataset["mapping"] = ml_dataset[mapping_id]
    ml_dataset.to_parquet(preprocess_output_path, partition_cols=["pk", "mapping"])
    filtered_data = ml_dataset.drop_duplicates(subset=[primaryKey, mapping_id], keep="last")
    succes_file_key = "trigger_preprocessing/year={}/month={}/day={}/stepjobid={}/_success.txt".format(meta_item.execution_year,
                                                                                                       meta_item.execution_month,
                                                                                                       meta_item.execution_day,
                                                                                                       meta_item.step_job_id)
    upload_file("", bucket_name=meta_item.s3_bucket_name_shared,
                object_name=succes_file_key)

    ################### Ciustom Business Logic from below #######################################
    s3_preprocessing_prefix_output_path = (
        "s3://{}/preprocessing/year={}/month={}/day={}/stepjobid={}/smid={}/").format(
        meta_item.s3_bucket_name_shared,
        meta_item.execution_year,
        meta_item.execution_month,
        meta_item.execution_day,
        meta_item.step_job_id,
        meta_item.step_job_id)

    total_num_training_jobs = 0
    for index, row in filtered_data.iterrows():
        total_num_training_jobs = total_num_training_jobs + 1
        algo_names = mapping_json_constants["mapping_json_data"]["TrainingMapping"][row.region]

        # "smid is same as step function id"


        s3_pk_mappingid_data_input_path = ("s3://{}/preprocessing/year={}/month={}/day={}/stepjobid={}/smid={}/pk={}/mapping={}/").format(
                 meta_item.s3_bucket_name_shared,
                       meta_item.execution_year,
                       meta_item.execution_month,
                       meta_item.execution_day,
                       meta_item.step_job_id,
                       meta_item.step_job_id,
                       row.part_name,
                       row.region)

        preprocess_output_bucket_name = "s3://{}".format(meta_item.s3_bucket_name_shared)
        aws_batch_job_definition = meta_item.aws_batch_job_definition

        status_input_job = insert_train_job_def_input_table(pk_mappingid=row.pk + "|" + row.mapping,
                                                            step_job_id= meta_item.step_job_id,
                                                            usecase_name=meta_item.usecase_name,
                                                            execution_year=meta_item.execution_year,
                                                            execution_month=meta_item.execution_month,
                                                            execution_day=meta_item.execution_day,
                                                            pkid=row.pk,
                                                            mapping_id=row.mapping,
                                                            mapping_json_s3_path=meta_item.mapping_json_s3_path,
                                                            algo_execution_status=[],
                                                            algo_names=list(algo_names),
                                                            s3_pk_mappingid_data_input_path=s3_pk_mappingid_data_input_path,
                                                            s3_output_bucket_name=preprocess_output_bucket_name,
                                                            batch_job_definition=aws_batch_job_definition,
                                                            batch_job_status_overall="TO_BE_CREATED",
                                                            input_data_set=[analytical_data_path]
                                                            )
        if not status_input_job:
            raise Exception("Preprocessing failed!")

    pre_processing_end_epoch = int(time.time())


    meta_item.preprocessing_timelaps = Timelaps(start_time=pre_processing_start_epoch,
                                                end_time=pre_processing_end_epoch)
    meta_item.input_data_set = [analytical_data_path]
    # TODO for NIKHIL - This needs to be fixed
    meta_item.algo_names=list(algo_names)
    meta_item.preprocessing_total_batch_jobs = total_num_training_jobs
    meta_item.s3_preprocessing_prefix_output_path = s3_preprocessing_prefix_output_path
    meta_item.save()
print("Preprocessing Complete!")

# docker run -v ~/.aws:/root/.aws 731580992380.dkr.ecr.ap-south-1.amazonaws.com/msil-preprocessing:latest  --region ap-south-1 --train_metatable_name trainmetatable
