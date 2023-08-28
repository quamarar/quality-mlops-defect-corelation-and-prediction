from awsgluedq.transforms import EvaluateDataQuality
from awsglue.dynamicframe import DynamicFrame
from awsglue.transforms import SelectFromCollection

def gluedf_s3_loading(glueContext,dataframe_to_write, s3_path, athena_db,
                      athena_table):

    list_partition_key = ["year", "month", "day"]
    compression = "snappy"
    fileformat = "glueparquet"

    outcome = glueContext.getSink(
        path=s3_path,
        connection_type="s3",
        updateBehavior="UPDATE_IN_DATABASE",
        partitionKeys=list_partition_key,
        compression=compression,
        enableUpdateCatalog=True
    )
    outcome.setCatalogInfo(
        catalogDatabase=athena_db, catalogTableName=athena_table
    )
    outcome.setFormat(fileformat)
    outcome.writeFrame(dataframe_to_write)
    print(f"{dataframe_to_write} loaded in {s3_path} with catalog update of {athena_db}.{athena_table}")


def evaluate_dq_rules(glueContext,spark,dynamic_dataframe,dataquality_ruleset,workflow_id,source,target):

    evaluate_dataquality_multiframe = EvaluateDataQuality().process_rows(
        frame=dynamic_dataframe,
        ruleset=dataquality_ruleset,
        publishing_options={
            "dataQualityEvaluationContext": "EvaluateDataQualityMultiframe",
            "enableDataQualityCloudWatchMetrics": False,
            "enableDataQualityResultsPublishing": False,
        },
        additional_options={"performanceTuning.caching": "CACHE_NOTHING"},
    )

    ########################################################################
    #### Get the consolidated rule outcomes against rule set
    print("Get the consolidated rule outcomes against rule set ")
    rule_outcomes = SelectFromCollection.apply(
        dfc=evaluate_dataquality_multiframe,
        key="ruleOutcomes"
    )

    rule_outcomes_df = rule_outcomes.toDF()
    rule_outcomes_df.createOrReplaceTempView("rule_outcomes_df")
    # rule_outcomes_df.show(truncate=False)

    ########################################################################
    #### Get the rowlevel outcomes against rule set
    print("Get the rowlevel outcomes ")
    rowlevel_outcomes = SelectFromCollection.apply(
        dfc=evaluate_dataquality_multiframe,
        key="rowLevelOutcomes"
    )

    rowlevel_outcomes_df = rowlevel_outcomes.toDF()
    rowlevel_outcomes_df.createOrReplaceTempView("rowlevel_outcomes_df")

    ########################################################################
    #### Update the  rowlevel outcomes in specific structure
    print("Update the  rowlevel outcomes in specific structure ")
    sql_detailed_result_query = f"""
    select '{workflow_id}' as corelation_id ,* , year(current_date()) as year, month(current_date()) as month , day(current_date()) as day , current_timestamp() as AuditTimestamp
    from rowlevel_outcomes_df 
    """

    detailed_result_df = spark.sql(sql_detailed_result_query)
    detailed_result_df.show(truncate=False)

    detailed_result_dyf = DynamicFrame.fromDF(detailed_result_df, glueContext, "detailed_result_dyf")

    ########################################################################
    #### Update the  rowlevel outcomes in specific structure
    print("Consolidated result of all the DQ checks")

    sql_consolidated_result_query = f"""
        select  '{workflow_id}' as corelation_id ,
        '{source}' as  source, '{target}' as target , 
        t1.Rule , t1.Outcome, t1.FailureReason,cast (t1.EvaluatedMetrics as string) EvaluatedMetrics,
        PassCnt, FailCnt , year(current_date()) as year, month(current_date()) as month , day(current_date()) as day , current_timestamp() as AuditTimestamp
        from 
        rule_outcomes_df t1
        left join 
        (select pass_header as Rule,nvl(pass_cnt,0) as PassCnt,nvl(fail_cnt,0) as FailCnt from
            (select count(*) pass_cnt, pass_header from 
            ( select  explode(dataqualityrulespass) as pass_header from rowlevel_outcomes_df )
            group by pass_header) p 
        full outer join 
            (select count(*) fail_cnt , fail_header from 
            ( select  explode(dataqualityrulesfail) as fail_header from rowlevel_outcomes_df )
            group by fail_header) f 
        on p.pass_header  = f.fail_header) t2
        on t1.Rule = t2.Rule
    """

    consolidated_dq_result_df = spark.sql(sql_consolidated_result_query)
    consolidated_dq_result_df.show(truncate=False)

    consolidated_dq_result_dyf = DynamicFrame.fromDF(consolidated_dq_result_df, glueContext, "consolidated_dq_result_dyf")

    return detailed_result_dyf , consolidated_dq_result_dyf
