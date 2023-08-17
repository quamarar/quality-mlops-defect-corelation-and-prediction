pipeline {
    agent any

    stages {
        stage('List S3 buckets') {
            steps {
                withAWS(roleAccount:'731580992380', role:'Cross-Account-role') {
                    sh 'aws s3 ls'
                }
            }
        }
    }
}
