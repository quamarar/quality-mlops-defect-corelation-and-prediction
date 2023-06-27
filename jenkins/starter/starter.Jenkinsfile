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
                sh 'python3 --version'
                sh 'pip install python-jenkins'
                sh 'pip install -r requirements.txt'
                sh 'python3 jenkins_automation.py' 
            }
        }
    }
}
