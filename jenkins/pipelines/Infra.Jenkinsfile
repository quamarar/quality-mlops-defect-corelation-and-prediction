
pipeline {
  agent any

  environment {
    This = "Infra"
  }

  stages {
    stage("local") {
      environment {
        automated = "Pipeline"
      }
      steps {
        sh 'echo "This is $This and its automated  $automated"'
      }
    }
    stage("global") {
      steps {
        sh 'echo "This is $This and its automated  $automated"'
      }
    }
  }
}
