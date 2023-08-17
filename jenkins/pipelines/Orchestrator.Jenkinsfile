// def boolean test_results = false
// pipeline {
//   agent any

//   stages {
//     stage("local") {
//       steps {
//         Pipeline()
//         catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
//         script { test_results = true }
//         }
//       }
//     }
 
//     stage("triggerinfra pipeline") {
//         steps {
//           script {
//            if( test_results == true ) {
//             build job: "seed-jobs-MSIL-Infra" ,
//                 propagate: false, wait: true }
//              else
//                { This job is failed}
//          }
//       } 
//     }
   
  

//     stage("triggerinference pipeline") {
//         steps {
//            build job: "seed-jobs-MSIL-Inference" ,

//                 propagate: true, wait: true }   

//     }
  
// }
// }
 pipeline {
  agent any

   stages {
     stage("local") {
      steps {
          echo "hello-world"
          }
       }
    }

