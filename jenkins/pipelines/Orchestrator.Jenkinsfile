def boolean test_results = false
 pipeline {
   agent any
 
     stage("triggerinfra pipeline") {
         steps {
           script {
           echo "Trigger Infra Pipeline"
  
            ret = build(job: " seed-job/MSIL-Infra" ,
                                parameters: [string(defaultValue: "ap-south-1", description: 'aws region', name: 'AWS_REGION'),             
                                             choice(
                                             choices: ['plan', 'apply', 'show', 'preview-destroy', 'destroy'],
                                             description: 'Terraform action to apply',
                                              name: 'action'),
                                              choice(
                                              choices: ['dev', 'uat', 'prod'],
                                              description: 'deployment environment',
                                               name: 'ENVIRONMENT')],
                                               propagate: true, wait: true )

                                              echo ret.result
                                              currentBuild.result = ret.result
                
               
    
          }
       } 
     }
   }
  




