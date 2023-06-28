@Library("shared-library") _
pipeline {
  agent any
    parameters {
      string (defaultValue: 'Infra', name: 'Folder')
      }



  stages {
    stage("local") {
      steps {
        Pipeline()
      }
    }
  }
}
