pipeline {
  agent any



    stages {
        stage('Initialise terraform directory') {
            steps{
                dir('infra') {
                    sh 'terraform init -no-color -backend-config="bucket=MSIL-DCP-dev-tfstate" -backend-config="key=MSIL-DCP-dev/terraform.tfstate" -backend-config=region=us-east1'
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
                     sh 'terraform plan -no-color  -input=false -out=tfplan -var aws_region=us-east1 --var-file=environments/dev.tfvars'
                }
            }
        }

 }
} 
