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
                sh 'python --version'
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate'
                sh 'pip install python-jenkins'
                sh 'pip install -r requirements.txt'
                sh 'python3 jenkins_automation.py' 
            }
        }
    }
}
