import argparse
import awswrangler as wr
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib
import os
import boto3
import json
import time
import logging
import sys
import s3fs
import pandas as pd
import traceback
from pynamodb.attributes import UnicodeSetAttribute, NumberAttribute, ListAttribute
from utils.dynamodb_util import TrainStateDataModel, TrainingAlgorithmStatus, TrainingMetaDataModel, \
    TrainingAlgorithmS3OutputPath

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

# os.environ["AWS_BATCH_JOB_ID"] = "20d3a773-3d6f-42e1-b201-7312b716fcbb"
# os.environ["AWS_BATCH_JOB_ATTEMPT"] = "0"
###

AWS_BATCH_JOB_ID = os.environ['AWS_BATCH_JOB_ID']
# AWS_BATCH_JOB_ID = 111222
AWS_BATCH_JOB_ATTEMPT = int(os.environ["AWS_BATCH_JOB_ATTEMPT"])

algo_execution_status = []
algo_final_run_s3outputpaths = []
awsbatch_triggered_num_runs = 0
algo_names_global = []
overall_fail_count = 0
args = None


def clean_out_path(s3_path):
    bucket, key = get_s3_bucket_key(s3_path)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    bucket.objects.filter(Prefix=key).delete()


def setup():
    if args.prev_batch_job_id == 'empty':
        clean_out_path(args.s3_training_prefix_output_path)
        clean_out_path(args.s3_pred_or_eval_prefix_output_path)
    # TODO directory cleanup in case of RERUN neeeds to be handled

    TrainingMetaDataModel.setup_model(TrainingMetaDataModel,
                                      args.train_metatable_name,
                                      args.region)

    train_statetable_name = TrainingMetaDataModel.get('fixedlookupkey').train_statetable_name

    TrainStateDataModel.setup_model(TrainStateDataModel, train_statetable_name, args.region)
    item = TrainStateDataModel.get(hash_key=f"{AWS_BATCH_JOB_ID}")

    for algo_name in item.algo_names:
        global algo_names_global
        algo_names_global.append(algo_name)

    global awsbatch_triggered_num_runs
    awsbatch_triggered_num_runs = item.awsbatch_triggered_num_runs + 1


def insert_train_job_state_table(train_start_exec_epoc, recursive_runs=0):
    # try:

    # The purpose of below sleep is to avoid contention between Glue job and Container while writing same row to Dynamo
    try:

        logging.info(f"args.train_metatable_name:{args.train_metatable_name}")

        state_table_item = TrainStateDataModel.get(hash_key=AWS_BATCH_JOB_ID)
        print("Updating JOBID- {} status in StateTable".format(AWS_BATCH_JOB_ID))

        for algo_execution_status_item in algo_execution_status:
            state_table_item.algo_execution_status.append(algo_execution_status_item)

        state_table_item.algo_final_run_s3outputpaths = algo_final_run_s3outputpaths
        state_table_item.awsbatch_triggered_num_runs = awsbatch_triggered_num_runs
        state_table_item.last_batch_run_time = int(time.time()) - train_start_exec_epoc
        state_table_item.save()


    except Exception as error:
        if recursive_runs == 3:
            raise Exception("Exception inside insert_train_job_state_table")
        logging.info("Retrying insert_train_job_state_table recursive_runs {}".format(recursive_runs))
        time.sleep(1)
        insert_train_job_state_table(recursive_runs + 1)


def get_s3_bucket_key(s3_path):
    path_parts = s3_path.replace("s3://", "").split("/")
    bucket = path_parts.pop(0)
    key = "/".join(path_parts)
    return bucket, key


def append_status_path(algo, algorithm_execution_status, run_id, s3_training_output_key, s3_evaluation_output_path):
    global algo_execution_status
    algo_execution_status.append(TrainingAlgorithmStatus(algorithm_name=algo,
                                                         algorithm_execution_status=algorithm_execution_status,
                                                         runid=run_id))

    global algo_final_run_s3outputpaths
    algo_final_run_s3outputpaths.append(TrainingAlgorithmS3OutputPath(algorithm_name=algo,
                                                                      model_s3_output_path=s3_training_output_key,
                                                                      pred_or_eval_s3_output_path=
                                                                      s3_evaluation_output_path))


def lr(algo):
    try:

        preprocessed_df = wr.s3.read_parquet(path=args.s3_pk_mappingid_data_input_path)

        logging.info(f"Preprocessing:{preprocessed_df.columns}")

        features = preprocessed_df.drop(['part_probability', 'part_name'], axis=1)
        labels = preprocessed_df['part_probability']

        # Test
        features = features.drop(['region'], axis=1)

        x_train, x_test, y_train, y_test = train_test_split(features, labels, train_size=0.9, test_size=0.1,
                                                            random_state=0)

        lr_model = LinearRegression()
        lr_model.fit(x_train, y_train)

        s3_training_prefix_output_path_updated = os.path.join(args.s3_training_prefix_output_path,
                                                              f"batchjobid={AWS_BATCH_JOB_ID}", f"algoname={algo}")
        clean_out_path(s3_training_prefix_output_path_updated)
        logging.info("Saving model to {s3_training_prefix_output_path_updated}")
        s3_training_output_key = os.path.join(s3_training_prefix_output_path_updated, "model.tar.gz")

        fs = s3fs.S3FileSystem()

        with fs.open(s3_training_output_key, 'wb') as f:
            joblib.dump(lr_model, f)

        y_pred = lr_model.predict(x_test)

        y_pred_series = pd.Series(data=y_pred, name="pred")
        y_test_series = y_test.reset_index(drop=True)

        test_pred_df = pd.concat([y_test_series, y_pred_series], axis=1)

        clean_out_path(args.s3_pred_or_eval_prefix_output_path)
        # check slash
        s3_evaluation_output_path = os.path.join(args.s3_pred_or_eval_prefix_output_path,
                                                 f"batchjobid={AWS_BATCH_JOB_ID}",
                                                 f"algoname={algo}",
                                                 "test_pred.parquet"
                                                 )

        wr.s3.to_parquet(df=test_pred_df, path=s3_evaluation_output_path)

        append_status_path(algo=algo,
                           algorithm_execution_status='SUCCESS',
                           run_id=awsbatch_triggered_num_runs,
                           s3_training_output_key=s3_training_output_key,
                           s3_evaluation_output_path=s3_evaluation_output_path)
    except Exception:
        logging.info(traceback.format_exc())
        append_status_path(algo=algo,
                           algorithm_execution_status='FAILED',
                           run_id=awsbatch_triggered_num_runs,
                           s3_training_output_key='',
                           s3_evaluation_output_path='')
        global overall_fail_count
        overall_fail_count = overall_fail_count + 1


def parse_args():
    # print(sys_args)
    logging.info("inside parse_args")
    parser = argparse.ArgumentParser()

    parser.add_argument("--s3_pk_mappingid_data_input_path", type=str, required=True)
    parser.add_argument("--pk_id", type=str, required=True)
    parser.add_argument("--s3_training_prefix_output_path", type=str, required=True)
    parser.add_argument("--s3_pred_or_eval_prefix_output_path", type=str, required=True)
    parser.add_argument("--prev_batch_job_id", type=str, required=True)
    parser.add_argument("--train_metatable_name", type=str, required=True)
    parser.add_argument("--mapping_id", type=str, required=True)
    parser.add_argument("--region", type=str, required=True)
    logging.info("end parse_args")
    return parser.parse_args()


if __name__ == "__main__":
    train_job_start_time = int(time.time())

    args = parse_args()
    setup()

    print("Starting Training job")
    for algo_name in algo_names_global:
        print(algo_name.lower())

    if 'lr' in (algo_name.lower() for algo_name in algo_names_global):
        lr(algo="lr")

    insert_train_job_state_table(train_job_start_time)

    print("Training job ending")

    if overall_fail_count > 0:
        raise Exception("One of the algos has failed hence failing container")
