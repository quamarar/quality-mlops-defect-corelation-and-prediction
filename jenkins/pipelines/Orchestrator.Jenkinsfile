
@Library("shared-library") _
pipeline {
  agent any
  parameters {
  string defaultValue: 'Orchestrator', name: 'Folder'
}

  stages {
    stage("local") {
      steps {
        Pipeline()
        }
      }

    stage("triggerinfra pipeline") {
        steps {
         build : 'seed-jobs-MSIL-Infra' 
          parameters [
              string defaultValue: 'Infra', name: 'Folder'
               ]
      } 
    }
   }
  }

