pipeline {
  agent any
 
  stages {
    stage('instalar sam-cli') {
      steps {
        sh 'python3 -m venv venv && venv/bin/pip install aws-sam-cli'
        stash includes: '**/venv/**/*', name: 'venv'
      }
    }
    stage('deploy') {
      environment {
        STACK_NAME = 'dataops-coleta-vacinas-stack'
        S3_BUCKET = 'dataops-deploy-nomesobrenome-accountID-regiao'
      }
      steps {
        unstash 'venv'        
        sh 'venv/bin/sam build'
        stash includes: '**/.aws-sam/**/*', name: 'aws-sam'
        unstash 'aws-sam'
        sh 'venv/bin/sam package --region us-east-1 --s3-bucket $S3_BUCKET'
        stash includes: '**/.aws-sam/**/*', name: 'aws-sam'
        sh 'venv/bin/sam deploy --stack-name $STACK_NAME --region us-east-1 --capabilities CAPABILITY_IAM --s3-bucket $S3_BUCKET'
      }
    }   
  }
}