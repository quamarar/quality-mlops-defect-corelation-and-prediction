pipelineJob('seed-jobs-MSIL-Infra') {

  parameters {
    stringParam('us-east-1', 'aws region', 'AWS_REGION')
    

  }

    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        github('quamarar/quality-mlops-defect-corelation-and-prediction')
                    }
                }
            }
            scriptPath('jenkins/pipelines/Infra.Jenkinsfile')
        }
    }
}
