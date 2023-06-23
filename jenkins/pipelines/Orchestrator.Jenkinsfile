def boolean test_results = false
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
        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
        script { test_results = true }
        }
      }
    }
 
    stage("triggerinfra pipeline") {
        steps {
          script {
           if( test_results == true ) {
            build job: "MSIL Demo/seed-jobs-MSIL-Infra" ,
             parameters: [
              string (defaultValue: 'Infra', name: 'Folder')
               ],
                propagate: true, wait: true }
             else
               { This job is failed}
         }
      } 
    }
   
  

    stage("triggerinference pipeline") {
        steps {
           build job: "MSIL Demo/seed-jobs-MSIL-Inference" ,
            parameters: [
              string (defaultValue: 'Inference', name: 'Folder')
               ],
                propagate: true, wait: true }   

    }
  
}
}
