pipeline {
  agent any


  environment {
    GIT_COMMIT_HASH = sh (script: "git rev-parse --short HEAD", returnStdout: true)  
    GIT_file_change =  sh (script: "git diff --name-only HEAD^ HEAD", returnStdout: true)
  }
  
 stages {
       stage('checkout') {
         steps {
            git 'https://github.com/quamarar/quality-mlops-defect-corelation-and-prediction.git'

           }
         }

        stage('detect file change in folder model') {
          steps {
            dir ('model') {
              echo "${GIT_file_change}"
          }
        }
        }

        stage ('do s3 sync') {
          steps {
            dir ('model') {
            script{
              def file_change = sh (script: "git diff --name-only HEAD^ HEAD", returnStdout: true)
              if(file_change == 'model/preprocessing/preprocessing.py') 
              {
                sh "echo sync done"
              }
              else {
                sh "echo no change"
              }
            }
          }
          }
        }
        
        stage('build docker image') {
            steps {
                dir ('model/preprocessing') {
                     sh 'sudo docker build -f Dockerfile . -t msil-preprocessing:${GIT_COMMIT_HASH}'
                     sh 'sudo docker tag msil-preprocessing:${GIT_COMMIT_HASH} 731580992380.dkr.ecr.ap-south-1.amazonaws.com/msil-mvp-poc-apsouth1-preprocessing:${GIT_COMMIT_HASH} '  
                }
            }
        }

        stage('login to ecr') {
        steps {
          dir ('model/preprocessing') {
            withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
            {
            sh 'aws ecr get-login-password --region ap-south-1 | sudo docker login --username AWS --password-stdin 731580992380.dkr.ecr.ap-south-1.amazonaws.com'
            sh 'sudo docker push 731580992380.dkr.ecr.ap-south-1.amazonaws.com/msil-mvp-poc-apsouth1-preprocessing:${GIT_COMMIT_HASH}'
           }
        }
      }
    }
         stage ('push commitid to pm') {
          steps {
            dir ('model/preprocessing') {
            withAWS(roleAccount:'731580992380', role:'Cross-Account-role', region:'ap-south-1')
            {
            sh 'aws ssm put-parameter --name "/mvp/development/training-job/ecr_preprocessing" --type "String"  --value "${GIT_COMMIT_HASH}" --overwrite'
            sh 'aws ssm get-parameters --names "/mvp/development/training-job/ecr_preprocessing"'

         }

      }
    }
  }
 }
}
