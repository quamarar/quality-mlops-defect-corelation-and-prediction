pipelineJob('seed-job/MSIL-Orchestrator') {


    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        github('quamarar/quality-mlops-defect-corelation-and-prediction')
                    }
                }
            }
            scriptPath('jenkins/pipelines/Orchestrator.Jenkinsfile')
        }
    }
}
