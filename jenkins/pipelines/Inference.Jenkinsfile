@Library("shared-library") _
pipeline {
  agent any
  parameters {
  string defaultValue: 'Inference', name: 'Folder'
}


  stages {
    stage("local") {
      steps {
        Pipeline()
      }
    }
  }
}
