def boolean test_results = false
@Library("shared-library") _
pipeline {
  agent any

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
            build job: "seed-jobs-MSIL-Infra" ,
                propagate: true, wait: true }
             else
               { This job is failed}
         }
      } 
    }
   
  

    stage("triggerinference pipeline") {
        steps {
           build job: "seed-jobs-MSIL-Inference" ,

                propagate: true, wait: true }   

    }
  
}
}
