pipeline{
    agent any

    stages{
        stage('Deploy Lambda'){
            steps {
                sh """ #!/bin/bash
                    #Define o caminho para o python
                PYENV_HOME=$WORKSPACE
                #Cria um venv na pasta
                python3 -m venv $PYENV_HOME
                #Ativa o venv
                . $PYENV_HOME/bin/activate
                #instala aws-sam-cli
                pip install Jinja2==2.10.1
                pip install aws-sam-cli==1.51.0
                #Construir pacote
                sam build
                #Cria o pacote para publicação da função lambda
                sam package --region us-east-1 --s3-bucket deploy-nomesobrenome-accountID-regiao
                #Publica a função lambda utilizando o bucket s3 e CloudFormation
                sam deploy --stack-name dataops-coleta-vacinas-stack --region us-east-1 --capabilities CAPABILITY_IAM --s3-bucket deploy-nomesobrenome-accountID-regiao
                """
            }
        }  
    }
}