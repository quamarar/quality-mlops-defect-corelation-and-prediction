"""
Prerequisites:
1. Model registry group should be already created
2. DDB metadata table to be populated with required parameters

Code Logic:
1. Read input from the trainDataModel dynamoDB table
2. Read the parquet using spark dataframe
3. calculate the evaluation metric and write parquet in s3
4. Get the Image ARN for model registry
5. Publish the entry in model registry
6. Dump the dynamodb meta table in to s3 

"""

import time
import boto3
from dynamodb_util import TrainStateDataModel, TrainingMetaDataModel, Timelaps
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from ddb_helper_functions import dump_data_to_s3

# ## @params: [JOB_NAME]
# args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
# job.init(args['JOB_NAME'], args)

######################################################################################################


def get_image_from_job_definition(job_definition_name):
    """
    Purpose: get the image id from batch_job_definition
    param : string value of job_definition_name
    return: String value containing the image uri 
    """
    batch_client = boto3.client('batch')
    describe_job_id = "{}".format(job_definition_name)
    response = batch_client.describe_job_definitions(jobDefinitions =[describe_job_id])
    return response["jobDefinitions"][0]["containerProperties"]["image"]

if __name__ == "__main__":
    print("Eneted the mail function")
    args = getResolvedOptions(sys.argv,
                              [
                                  'train_inputtable_name',
                                  'train_statetable_name',
                                  'train_metatable_name',
                                  'region'])

    ###Captured the parameters from the passed arguments
    eval_summary_start_epoch = int(time.time())
    print(f"Returning the epoch time :{eval_summary_start_epoch}")

    # dynamically set the table names for input, state and meta dynamoDB tables
    TrainingMetaDataModel.setup_model(TrainingMetaDataModel, args['train_metatable_name'], args['region'])
    print("Instantiating dynamo table")
    metaitemtemp = TrainingMetaDataModel.get("fixedlookupkey")
    TrainStateDataModel.setup_model(TrainStateDataModel, metaitemtemp.train_statetable_name, metaitemtemp.region)

    year = metaitemtemp.execution_year
    month = metaitemtemp.execution_month
    day = metaitemtemp.execution_day
    stepjobid = metaitemtemp.step_job_id
    athena_db = metaitemtemp.athenadb_name
    eval_summary_bucket = metaitemtemp.s3_bucket_name_shared
    region = metaitemtemp.region
    # evaluation_table = metaitemtemp.athena_pred_or_eval_table_name
    # evaluation_summary_table_name = metaitemtemp.athenadb_evaluation_summary_table
    usecase_name=metaitemtemp.usecase_name
    job_definition_name=metaitemtemp.aws_batch_job_definition
    
    # Parameters which are derived in this job statically
    training_read = f's3://{eval_summary_bucket}/pred_or_eval/year={year}/month={month}/day={day}/stepjobid={stepjobid}/'
    target_path = f"s3://{eval_summary_bucket}/model_eval_summary/"  # target S3 bucket
    eval_success_trigger_key = f'trigger_eval_summary/year={year}/month={month}/day={day}/stepjobid={stepjobid}'
    modeldataurlkey = "dummy_model/model.tar.gz"  # dummymodelpath on root bucket
    object_name = """meta/year={}/month={}/day={}/stepjobid=step_job_id/meta_ddb_table.json""".format(
        year, month, day, stepjobid)
    
    
    #fNeed to be added in  dynamo db meta table 
    model_package_group_arn = "demo-997"
    commitid = "521747298a3790fde1710f3aa2d03b55020575aa"
    repository = "https://gitlab.aws.dev/proserve-india/projects/etip/maruti-modelops"
    
    
    # print(f"Retuning all the values : {year}, {month},{day},{stepjobid},{athena_db},{eval_summary_bucket}, {region},{evaluation_table},{evaluation_summary_table_name}")



    session = boto3.session.Session()
    # athena_client = pythena.Athena(database=athena_db, session=session, region=region)
    s3 = boto3.client('s3')
    print("Instantiating the boto3 session")

    ######################################################################################################
    #### Reading the preprocesing file 
    
    training_df = spark.read.format("parquet").option("header", "true").option("inferSchema", "true").load(training_read)
    training_df.createOrReplaceTempView("training_df")
    
    actual_data_df = spark.sql(""" select distinct pk,mapping,batch,algo from 
                                (select * , rank()over ( partition by pk, mapping,batch,algo order by part_probability desc) rnk 
                                from training_df ) where rnk <= 200 """)
    
    actual_data_df.createOrReplaceTempView("actual_data_df")
    
    pred_data_df = spark.sql(""" select distinct pk,mapping,batch,algo from 
                                (select * , rank()over ( partition by pk, mapping,batch,algo order by pred desc) rnk 
                                from training_df ) where rnk <= 200 """)
    pred_data_df.createOrReplaceTempView("pred_data_df")
    
    final_df = spark.sql(f""" select 'Intersection' metric_name ,count(1) metric_value ,prd.algo ,cast(current_timestamp as timestamp ) as audit_timestamp
                                ,'{year}' as year , '{month}' as month , '{day}' as day , '{stepjobid}' as stepjobid
                                from pred_data_df prd
                                inner join actual_data_df acd
                                on prd.pk = prd.pk and prd.mapping = acd.mapping
                                group by prd.algo""")
    final_df.createOrReplaceTempView("final_df")
    final_df.show(truncate=False)
    
    #########################################################################################################################################
    #Output data is written in parquet in eval summary bucket
    final_df.write.partitionBy("year","month","day","stepjobid","algo").mode('append').parquet(target_path)
    print("Output data is written in parquet in eval summary bucket")
    

    #########################################################################################################################################
    # Write the success file
    s3.put_object(
        Bucket=eval_summary_bucket,
        Key=eval_success_trigger_key
    )

    # Write the dummy model file for the model registry to enter the value
    s3.put_object(
        Bucket=eval_summary_bucket,
        Key=modeldataurlkey
    )
    #########################################################################################################################################
    # Comment: Placeholder for additional columns for model registry
    
    winning_model_df = spark.sql(""" select cast (max(metric_value) as string) as winningalgometric, algo as winningalgo from final_df group by algo """)
    
    winning_algo_metric= winning_model_df.head()['winningalgometric']
    winning_algo= winning_model_df.head()['winningalgo']
    winningalgos3uri=training_read
    
    imageurl= get_image_from_job_definition(job_definition_name)
    
    # need to get them image arn 
    print(f"Starting the model registry insertion")
    modelpackage_inference_specification = {
        "InferenceSpecification": {
            "Containers": [
                {
                    # Pass Image ARN returned from the function - get_image_from_job_definition
                    "Image": imageurl,
                    "ModelDataUrl": f"s3://{eval_summary_bucket}/{modeldataurlkey}"
                }
            ],
            "SupportedContentTypes": ["text/csv"],
            "SupportedResponseMIMETypes": ["text/csv"],
        }
    }

    create_model_package_input_dict = {
    "ModelPackageGroupName" : model_package_group_arn,
    "ModelPackageDescription": f""" {{ "winning_algo":"{winning_algo}","winning_algo_metric":"{winning_algo_metric}","winningalgos3uri":"{winningalgos3uri}" }} """,
    
    "ModelApprovalStatus" : "PendingManualApproval",
    
    "CustomerMetadataProperties": { 
      "winning_algo" : winning_algo,
      "winning_algo_metric":winning_algo_metric,
      "winningalgos3uri":winningalgos3uri},
    "MetadataProperties": { 
      "CommitId": commitid,
      "GeneratedBy": "framework_evaluation",
      "ProjectId": usecase_name,
      "Repository": repository
        }
    }
    
    
    create_model_package_input_dict.update(modelpackage_inference_specification)
    print(create_model_package_input_dict)

    sm_client = boto3.client('sagemaker', region_name=region)

    # sm_client.create_model_package_group(ModelPackageGroupName="demo-999")

    create_model_package_response = sm_client.create_model_package(**create_model_package_input_dict)
    model_package_arn = create_model_package_response["ModelPackageArn"]
    print('ModelPackage Version ARN : {}'.format(model_package_arn))

    # Update MetaData Table
    eval_summary_prefix_path = """{}year={} /month={}/day={}/stepjobid={}/""".format(
        target_path, metaitemtemp.execution_year, metaitemtemp.execution_month, metaitemtemp.execution_day,
        metaitemtemp.step_job_id)

    metaitemtemp.s3_eval_summary_prefix_output_path = eval_summary_prefix_path
    eval_summary_end_epoch = int(time.time())
    metaitemtemp.eval_summary_timelaps = Timelaps(start_time=eval_summary_start_epoch, end_time=eval_summary_end_epoch)
    metaitemtemp.step_function_end_time = eval_summary_end_epoch
    metaitemtemp.e2e_execution_time = eval_summary_end_epoch - metaitemtemp.step_function_start_time
    metaitemtemp.save()
    
    #########################################################################################################################################
    #Dump data to s3
    
    dump_data_to_s3(s3_ouput_bucket=eval_summary_bucket,
                        s3_output_object_name=object_name, ddb_model=TrainStateDataModel)


# job.commit()
