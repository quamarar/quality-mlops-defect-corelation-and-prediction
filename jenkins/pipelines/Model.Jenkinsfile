pipeline {
  agent any


  environment {
    GIT_COMMIT_HASH = sh(script: 'git rev-parse --short HEAD',returnStdout: true).trim()
    GIT_file_change =  sh(script:"git diff --name-only HEAD^ HEAD",returnStdout: true)
  }
  
 stages {
       stage('checkout') {
         steps {
            git 'https://github.com/quamarar/quality-mlops-defect-corelation-and-prediction.git'

           }
         }

        stage('detect file change in folder model')
         {
          steps {
            dir ('model') {
              echo "${GIT_file_change}"
              echo "${GIT_COMMIT_HASH}"
              sh 'aws s3 sync . s3://dcp-auto-dev-apsouth1-internal'

          }
        }
        }


        
        stage('build processing docker image and push to ecr') {
          when {
              changeset "model/training_job/preprocessing/*"
            }
            steps {
                dir ('model') {
                  withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
                  {
                     sh 'docker build -f ./training_job/preprocessing/Dockerfile . -t msil-preprocessing:${GIT_COMMIT_HASH}'
                     sh 'docker tag msil-preprocessing:${GIT_COMMIT_HASH} 731580992380.dkr.ecr.ap-south-1.amazonaws.com/dcp-auto-dev-apsouth1-preprocessing:${GIT_COMMIT_HASH} '  
                     sh 'aws ecr get-login-password --region ap-south-1 |docker login --username AWS --password-stdin 731580992380.dkr.ecr.ap-south-1.amazonaws.com'
                     sh 'docker push 731580992380.dkr.ecr.ap-south-1.amazonaws.com/dcp-auto-dev-apsouth1-preprocessing:${GIT_COMMIT_HASH}'
                     sh 'aws ssm put-parameter --name "/mvp/development/training-job/ecr_preprocessing" --type "String" --value "731580992380.dkr.ecr.ap-south-1.amazonaws.com/dcp-auto-dev-apsouth1-preprocessing:${GIT_COMMIT_HASH}" --region "ap-south-1" --overwrite'
                     sh 'docker run -v ~/.aws:/root/.aws 731580992380.dkr.ecr.ap-south-1.amazonaws.com/dcp-auto-dev-apsouth1-preprocessing:${GIT_COMMIT_HASH}   --train_metatable_name  dcp-auto-dev-apsouth1-TrainMetaTable  --region ap-south-1'
                }
            }
        }
        }
                
        stage('build training docker image and push to ecr') {
          when {
              changeset "model/training_job/training/*"
            }
            steps {
                dir ('model') {
                  withAWS(roleAccount:'731580992380', role:'Cross-Account-role') 
                  {

                     sh 'docker build -f ./tarining_job/training/Dockerfile . -t msil-training:${GIT_COMMIT_HASH}'
                     sh 'docker tag msil-training:${GIT_COMMIT_HASH} 731580992380.dkr.ecr.ap-south-1.amazonaws.com/dcp-auto-dev-apsouth1-training:${GIT_COMMIT_HASH} '  
                     sh 'aws ecr get-login-password --region ap-south-1 |docker login --username AWS --password-stdin 731580992380.dkr.ecr.ap-south-1.amazonaws.com'
                     sh 'docker push 731580992380.dkr.ecr.ap-south-1.amazonaws.com/dcp-auto-dev-apsouth1-training:${GIT_COMMIT_HASH}'
                     sh 'aws ssm put-parameter --name "/mvp/development/training-job/ecr_training" --type "String" --region "ap-south-1" --value "731580992380.dkr.ecr.ap-south-1.amazonaws.com/dcp-auto-dev-apsouth1-training:${GIT_COMMIT_HASH}" --overwrite'
                }
            }
        }
      }

 }
}

