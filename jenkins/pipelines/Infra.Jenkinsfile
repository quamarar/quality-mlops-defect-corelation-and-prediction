pipeline {
  agent any

  parameters {
    string(defaultValue: "ap-south-1", description: 'aws region', name: 'AWS_REGION')


    
    choice(
            choices: ['plan', 'apply', 'show', 'preview-destroy', 'destroy'],
            description: 'Terraform action to apply',
            name: 'action')
    choice(
            choices: ['dev', 'uat', 'prod'],
            description: 'deployment environment',
            name: 'ENVIRONMENT')
     }


    stages {
        stage('Initialise terraform directory') {
            steps{
                dir('infra') {
                 withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
                     {
                    sh 'terraform init --upgrade -reconfigure -no-color -backend-config="key=msil-mvp-tfstate/terraform.tfstate"'
                }
            }
        }
     }
        stage('TerraformValidate') {
            steps{
                dir('infra') {
                  withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
                   {
                    sh "terraform validate"
                }
            }
        } 
   }
        stage('Terraformplan') {
            when {
                expression { params.action == 'plan' || params.action == 'apply'  }
            }
            steps{
                dir('infra') {
                     withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
                     {
                     sh 'terraform plan -no-color  -input=false -out=tfplan  --var-file=../env/dev.tfvars.json'
                }
            }
          }
        }
        stage('approval') {
            when {
                expression { params.action == 'apply' }
            }
            steps {
              
                dir('infra') {
                  withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
                  {
                  sh 'terraform show -no-color tfplan > tfplan.txt'
                  script {
                    def plan = readFile 'tfplan.txt'
                    input message: "Apply the plan?",
                    parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                    }
                }
             }
            }
        }
        stage('apply') {
            when {
                expression { params.action == 'apply'}
            }
            steps {
                dir('infra') {
                  withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
                 {
                sh 'terraform apply -no-color -input=false tfplan'
            }
          }
         }
        } 
        stage('show') {
            when {
                expression { params.action == 'show'}
            }
            steps {
                dir('infra') {
                 withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
               {
                sh 'terraform show -no-color'
            }
          }
        }
     }
        stage('preview-destroy') {
            when {
                expression { params.action == 'preview-destroy' || params.action == 'destroy'}
            }
            steps {
               
                dir('infra') {
                withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
              {
                sh 'terraform plan -no-color -destroy -out=tfplan  --var-file=../env/dev.tfvars.json'
                sh 'terraform show -no-color tfplan > tfplan.txt'
            }
          }
       }
     }
        stage('destroy') {
            when {
                expression { params.action == 'destroy'}
            }
            steps {
              
                dir('infra') {
                withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
                {
                script {
                    def plan = readFile 'tfplan.txt'
                    input message: "Delete the stack?",
                    parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                }
                sh 'terraform destroy -no-color -auto-approve  --var-file=../env/dev.tfvars.json'
            }
         }
        }
    }
 }
} 
