
pipeline {
  agent any

  environment {
    // FOO will be available in entire pipeline
    This = "Inference"
  }

  stages {
    stage("local") {
      environment {
        // BAR will only be available in this stage
        automated = "Pipeline"
      }
      steps {
        sh 'echo "This is $This and its automated  $automated"'
      }
    }
    stage("global") {
      steps {
        sh 'echo "FOO is $FOO and BAR is $BAR"'
      }
    }
  }
}
