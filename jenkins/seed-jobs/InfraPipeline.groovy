pipelineJob('seed-jobs-MSIL-Infra') {

  parameters {
    stringParam('us-east-1', 'aws region', 'AWS_REGION')
    
    choiceParam('action', ['plan', 'apply', 'show', 'preview-destroy', 'destroy'], 'Terraform action to apply')
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
