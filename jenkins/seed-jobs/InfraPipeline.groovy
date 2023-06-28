pipelineJob('seed-jobs-MSIL-Infra') {

    parameters {
         stringParam(defaultValue: 'Infra', name: 'Folder')
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
