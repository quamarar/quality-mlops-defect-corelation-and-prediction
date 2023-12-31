pipelineJob('seed-job/MSIL-Infra') {

  parameters {
    stringParam('AWS_REGION','ap-south-1','aws region')
    
    choiceParam('action', ['plan', 'apply', 'show', 'preview-destroy', 'destroy'], 'Terraform action to apply')
    choiceParam('ENVIRONMENT', ['dev', 'uat', 'prod'], 'deployment environment',)
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
