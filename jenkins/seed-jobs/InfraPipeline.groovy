pipelineJob('seed-jobs-MSIL-Infra') {

  parameters {
    stringParam(defaultValue: "us-east-1", description: 'aws region', name: 'AWS_REGION')
    
    choiceParam(
            choices: ['plan', 'apply', 'show', 'preview-destroy', 'destroy'],
            description: 'Terraform action to apply',
            name: 'action')
    choiceParam(
            choices: ['dev', 'uat', 'prod'],
            description: 'deployment environment',
            name: 'ENVIRONMENT')
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
