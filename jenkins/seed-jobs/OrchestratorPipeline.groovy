pipelineJob('seed-jobs-MSIL-Orchestrator') {

    parameters {
         stringParam('Folder','Orchestrator','name of the folder')
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
            scriptPath('jenkins/pipelines/Orchestrator.Jenkinsfile')
        }
    }
}
