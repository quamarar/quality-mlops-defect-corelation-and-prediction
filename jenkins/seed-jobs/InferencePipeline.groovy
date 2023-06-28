pipelineJob('seed-jobs-MSIL-Inference') {
    parameters {
         stringParam('Folder', 'Inference','name of the folder')
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
            scriptPath('jenkins/pipelines/Inference.Jenkinsfile')
        }
    }
}

