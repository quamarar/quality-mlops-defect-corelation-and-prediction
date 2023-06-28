pipelineJob('seed-jobs-MSIL-Infra') {

    parameters {
         stringParam('Folder', 'Infra','name of the folder')
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
