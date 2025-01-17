pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'make REPOSITORY=$REPOSITORY build'
            }
        }
        stage('Push') {
            steps {
                sh 'make REPOSITORY=$REPOSITORY push'
            }
        }
        stage('Install') {
            steps {
                sh 'KUBECONFIG=$KUBECONFIG_FILE make REPOSITORY=$REPOSITORY install'
            }
        }        
    }
}
