pipeline {
  agent any


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
 }
} 
