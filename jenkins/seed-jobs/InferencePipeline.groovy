pipelineJob('seed-job/MSIL-Inference') {

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

