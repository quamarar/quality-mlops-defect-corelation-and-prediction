pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scmGit(branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/quamarar/quality-mlops-defect-corelation-and-prediction.git']])
         }
        }        
        stage('build') {
            steps {
                python3 jenkins_automation.py
            }
        }
    }
}
