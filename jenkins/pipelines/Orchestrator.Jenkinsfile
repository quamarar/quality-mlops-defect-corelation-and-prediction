
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
  }
}
