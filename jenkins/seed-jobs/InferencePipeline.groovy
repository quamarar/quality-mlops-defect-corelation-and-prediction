pipelineJob('quality-mlops-defect-corelation-and-prediction/seed-jobs') {
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

