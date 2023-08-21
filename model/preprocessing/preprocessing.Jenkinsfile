pipeline {
  agent any


  environment {
    GIT_COMMIT_HASH = sh (script: "git rev-parse --short HEAD", returnStdout: true)   
  }
  
 stages {
       stage('checkout') {
         steps {
            git 'https://github.com/quamarar/quality-mlops-defect-corelation-and-prediction.git'

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
          sh 'aws ecr get-login-password --region ap-south-1 | sudo docker login --username AWS --password-stdin 731580992380.dkr.ecr.ap-south-1.amazonaws.com'
          sh 'sudo docker push 731580992380.dkr.ecr.ap-south-1.amazonaws.com/msil-mvp-poc-apsouth1-preprocessing:latest:${GIT_COMMIT_HASH}'
       }
    }
  }
}
