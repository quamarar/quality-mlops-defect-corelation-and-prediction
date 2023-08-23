pipelineJob('seed-job/MSIL-Model') {


    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        github('quamarar/quality-mlops-defect-corelation-and-prediction')
                    }
                }
            }
            scriptPath('jenkins/pipelines/Model.Jenkinsfile')
        }
    }
}
