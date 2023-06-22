

pipeline {
  agent any
  parameters {
  string defaultValue: 'Orchestrator', name: 'Folder'
}


  stages {
    stage("local") {
      steps {
        sh 'echo "This is ${Folder}  and its automated pipeline"'
      }
    }
  }
}
