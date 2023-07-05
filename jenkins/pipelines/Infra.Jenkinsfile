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
                    sh 'terraform init -no-color -backend-config="bucket=MSIL-DCP-${ENVIRONMENT}-tfstate" -backend-config="key=MSIL-DCP-${ENVIRONMENT}/terraform.tfstate" -backend-config="region=${AWS_REGION}"'
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
            when {
                expression { params.action == 'plan' || params.action == 'apply' }
            }
            steps{
                dir('infra') {
                     sh 'terraform plan -no-color  -input=false -out=tfplan -var "aws_region=${AWS_REGION}" --var-file=environments/${ENVIRONMENT}.tfvars'
                }
            }
        }
        stage('approval') {
            when {
                expression { params.action == 'apply'}
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
 }
} 
