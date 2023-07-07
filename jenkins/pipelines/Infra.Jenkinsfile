pipeline {
  agent any

  parameters {
    string(defaultValue: "us-east-1", description: 'aws region', name: 'AWS_REGION')
    
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
                    sh 'terraform init -no-color -backend-config="bucket=MSIL-DCP-${ENVIRONMENT}-tfstate" -backend-config="key=MSIL-DCP-dev/terraform.tfstate" -backend-config="region=${AWS_REGION}"'
                }
            }
        }
        stage('TerraformValidate') {
            steps{
                dir('infra') {
                    sh "terraform validate"
                }
            }
        }  
        stage('Terraformplan') {
            steps{
                dir('infra') {
                     sh 'terraform plan -no-color  -input=false -out=tfplan -var "aws_region=${AWS_REGION}" --var-file=environments/dev.tfvars'
                }
            }
        }

         stage('approval') {
            when {
                expression { params.action == 'apply' && env.BRANCH_NAME != 'master'}
            }
            steps {
                dir('infra') {
                sh 'terraform show -no-color tfplan > tfplan.txt'
                script {
                    def plan = readFile 'tfplan.txt'
                    input message: "Apply the plan?",
                    parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                    }
                }

            }
        }

          stage('apply') {
            when {
                expression { params.action == 'apply' && env.BRANCH_NAME != 'master' }
            }
            steps {
                dir('infra/terraform') {
                sh 'terraform apply -no-color -input=false tfplan'
            }
          }
        } 

         stage('show') {
            when {
                expression { params.action == 'show' }
            }
            steps {
                dir('infra/terraform') {
                sh 'terraform show -no-color'
            }
          }
        }

        stage('preview-destroy') {
            when {
                expression { params.action == 'preview-destroy' || params.action == 'destroy' && env.BRANCH_NAME != 'master'}
            }
            steps {
                dir('infra/terraform') {
                sh 'terraform plan -no-color -destroy -out=tfplan -var "aws_region=${AWS_REGION}" --var-file=environments/${ENVIRONMENT}.tfvars'
                sh 'terraform show -no-color tfplan > tfplan.txt'
            }
          }
       }
        stage('destroy') {
            when {
                expression { params.action == 'destroy' && env.BRANCH_NAME != 'master' }
            }
            steps {
                dir('infra/terraform') {
                script {
                    def plan = readFile 'tfplan.txt'
                    input message: "Delete the stack?",
                    parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                }
                sh 'terraform destroy -no-color -auto-approve -var "aws_region=${AWS_REGION}" --var-file=environments/${ENVIRONMENT}.tfvars'
            }
        }
    }



 }
} 
