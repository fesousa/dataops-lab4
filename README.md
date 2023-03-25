# DataOps - Laboratório 4

Coleta de Dados com Lambda, Eventos e implantação com Github e Jenkins

As instruções do laboratório estão em português. Para alterar o idioma, procure a opção na barra inferior do console AWS.


## Objetivos

* Configurar Jenkins para construir a aplicação e implantar na AWS
*	Utilizar Github para integrar e implantar com Jenkins
*	Criar uma função Lambda para coleta de dados, disparada por um evento agendado
*	Implantar uma Função Lambda utilizando AWS SAM, Jenkins e Github



## Arquitetura da solução

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem1.png" width='100%'/>


## Função Lambda para coletar dados

1.	No VSCode, crie uma nova pasta `lab4` e dentro dela uma outra pasta `app`. Dentro da pasta `app` crie um arquivo `lambda_function.py`

2.	Coloque o seguinte código  no arquivo

  Este código faz o download do arquivo de vacinação no AC disponível <a href="https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIPNI/COVID/uf/uf%3DAC/part-00000-0e081da1-2126-45b3-8bfd-78667a8589af.c000.csv" target="_blank"> aqui </a> e copie para o bucket criado no <a href="https://github.com/fesousa/dataops-lab1" target="_blank"> Laboratório 1 </a> (nome sugerido foi `dataops-dados-nomesobrenome`, sendo que `nomesobrenome` deve ser seu nome e sobrenome; ou entáo coloque o nome do bucker que criou no  <a href="https://github.com/fesousa/dataops-lab1" target="_blank"> Laboratório 1 </a>, se for diferente)


```python
import requests, boto3, asyncio, math

async def upload_s3_async(init, end, i, url, bucket, key, s3, mpu):
    print(f'Upload {i}')
    # download do pedaço do arquivo
    r = requests.get(url,  headers={'Range':f'bytes={init}-{end}'})    
    #upload para o S3
    return s3.upload_part(Bucket=bucket, Key=key, PartNumber=i, UploadId=mpu['UploadId'], Body=r.content)

async def upload_s3(url, bucket, key, s3, mpu):
    # separar arquivo em pedaços de 50 MB
    b = 52428800
    t = int(requests.head(url).headers['Content-Length'])
    parts, tasks = [], []
    for i in range(math.ceil(t/b)):
        init = i*b if i == 0 else i*b + 1
        end = min((i+1)*b, t)
        if t-end < 6291456: end = t        
        tasks.append(asyncio.ensure_future(upload_s3_async(init, end, i+1, url, bucket, key, s3, mpu)))

    # executar coleta dos pedaços do arquivo
    return await asyncio.gather(*tasks)

def lambda_handler(event, context):
    # url que virá pelo parâmetro
    url = event['url']
    # nome do bucket para upload
    bucket = 'dataops-impacta-dados-profernandosousa'
    #nome do arquivo que será salvo no bucket
    key = f'input/vacinas_{event["uf"]}.csv'
    #Concexão com s3
    s3 = boto3.client('s3')
    # iniciar upload multipart
    mpu = s3.create_multipart_upload(Bucket=bucket, Key=key)

    #fazer download do arquivo por partes    
    parts = asyncio.get_event_loop().run_until_complete(upload_s3(url, bucket, key, s3, mpu))
            
    # finalizar upload
    part_info = {'Parts': 
        [{'PartNumber': i+1, 'ETag': p['ETag']} for i, p in enumerate(parts)]    
    }
    s3.complete_multipart_upload(Bucket=bucket, Key=key, UploadId=mpu['UploadId'], MultipartUpload=part_info)

    return True

```

3.	Criar função Lambda no Console AWS

    3.1.	No console da AWS procure pelo serviço `Lambda`

    3.2.	Na tela do serviço, clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem2.png" height='25'/>

    3.3.	Na próxima tela, preencha os seguintes campos:

    &nbsp;&nbsp;&nbsp;&nbsp;a.	Nome da função: `dataops-coleta-vacinas`
    
    &nbsp;&nbsp;&nbsp;&nbsp;b.	Tempo de execução: `Python 3.7`

    &nbsp;&nbsp;&nbsp;&nbsp;c.	Abra a seção  <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem3.png" height='25'/>

    &nbsp;&nbsp;&nbsp;&nbsp;d.	Selecione <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem4.png" height='25'/>

    &nbsp;&nbsp;&nbsp;&nbsp;e.	Em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem5.png" height='25'/> selecione <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem6.png" height='25'/>

    &nbsp;&nbsp;&nbsp;&nbsp;O lambda precisa de permissão para usar o S3. A função (IAM Role) selecionado da essa permissão

    &nbsp;&nbsp;&nbsp;&nbsp;f.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem7.png" height='25'/>

4.	Você será redirecionado para a tela da função criada. Agora é preciso configurá-la

    4.1.	Na seção <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem8.png" height='25'/> remova o conteúdo do arquivo que está aberto e cole o código do arquivo <a href="https://github.com/fesousa/dataops-lab4/blob/master/app/lambda_function.py" target="_blank">`lambda_function.py` </a> criado no VSCode.


    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem9.png" width='100%'/>


    4.2.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem10.png" height='25'/>

    4.3.	Selecione a aba <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem11.png" height='25'/>

    4.4.	Nas opções da esquerda, selecione <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem12.png" height='25'/>

    4.5.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem13.png" height='25'/> para alterar o tempo máximo de execução da função e a quantidade de memória

    4.6.	Em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem14.png" height='25'/>  coloque 512 MB

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem15.png" height='80'/>
 
    4.7.	Em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem16.png" height='25'/> coloque 15 minutos

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem17.png" height='70'/>
 
    4.8.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem18.png" height='25'/>

5.	Testar a função

    5.1.	Selecione a aba <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem19.png" height='25'/>

    5.2.	Na caixa de texto onde está a string JSON, troque pelo seguinte, para coletar os dados de vacina do Acre:

    ```json
    {
      "url":"https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIPNI/COVID/uf/uf%3DAC/part-00000-0e081da1-2126-45b3-8bfd-78667a8589af.c000.csv", 
      "uf":"ac"
    }
    ```

    O evento de teste ficará assim:

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem20.png" height='200'/>


    5.3.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem21.png" height='25'/>

    5.4.	Espera a função terminar de executar

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem22.png" height='75'/>
 
    5.5.	Expanda <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem23.png" height='25'/> para ver os resultados. Você deve ver a mensagem true na área branca. Se não vir, verifique o log mais abaixo e verifique o nome do bucket

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem24.png" height='400'/>
 
    5.6.	Abra o seu bucket de dados (`dataops-dados-nomesobrenome`, ou o nome criado no  <a href="https://github.com/fesousa/dataops-lab4/blob/master/app/lambda_function.py" target="_blank">`lambda_function.py` </a>) e verifique o arquivo baixado


# Template SAM para a função lambda

1.	No VSCode crie um novo arquivo `template.yaml` na pasta `lab4`

2.	Coloque o seguinte código no arquivo. Veja os comentários para entender o que cada declaração faz

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: 'AWS::Serverless-2016-10-31'
Description: A starter AWS Lambda function.
Resources:
  # Criar função lambda agendada
  lambdafunction:
    Type: 'AWS::Serverless::Function'
    Properties:
      FunctionName: dataops-coleta-vacinas-ci-cd # nome da função
      Handler: lambda_function.lambda_handler # nome do arquivo e método de onde está a função
      Runtime: python3.7 # ambiente de execução
      CodeUri: ./app # local onde estarão os arquivos da função
      Description: Coletar dados de vacinas.
      MemorySize: 512 # memória utilizada pela funçãop
      Timeout: 900 # tempo máximo de execução, em segundos
      Role: !Sub arn:aws:iam::${AWS::AccountId}:role/LabRole # IAM role da função para permissões a outros recursos da AWS
      Events: # Evento agendado para execução
        ScheduledFunction:
          Type: Schedule
          Properties:
            Schedule: cron(15 00 * * ? *) # executa todo dia às 10:15
            Name: dataops-agenda-coleta-vacina
            Input: '{
              "url":"https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIPNI/COVID/uf/uf%3DAC/part-00000-ebb720ff-cda9-42f4-90a0-e4c8a15c22aa.c000.csv", 
              "uf":"ac"
            }' # evento com parâmetros que serão enviados para a função lambda
```

3.	Crie um  repositório `dataops-lab4` no seu GitHub e adicione a pasta lab4 nesse repositório.


## Configurar Jenkins para fazer CI/CD da função lambda

1. Inicie seu ambiente da AWS como fez nos laboratórios anteriores

2. Ainda na tela do laboratório no AWS Academy, clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem105.png" height='25'/>

3.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem25.png" height='25'/> para baixar a chave SSH para acessar as instâncias EC2

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem26.png" height='300'/>

4.	Acesse o console da AWS

5.	Verifique se a instância EC2 criada na no [Laboratório 3](https://github.com/fesousa/dataops-lab3) está ligada. Se não, inicie a instância. A instância deve ficar parecida com a imagem abaixo:

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem27.png" height='120'/>

6.	Na barra superior, clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem28.png" height='25'/>  para abrir um console de linha de comando do AWS CloudShell e espere iniciar

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem29.png" height='350'/> 

7.	Faça o upload da chave SSH que acabou de baixar (`labsuser.pem`) para o CloudShell

    7.1.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem30.png" height='25'/>

    7.2.	Selecione a opção <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem31.png" height='25'/>

    7.3.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem32.png" height='25'/>

    7.4.	Procure o arquivo `labsuser.pem` que baixou

    7.5.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem33.png" height='25'/>

    7.6.	Espere o arquivo ser carregado. Aparecerá a seguinte mensagem no canto superior direito

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem34.png" height='150'/>

    7.7.	No terminal do CloudShell digite `ls` e verifique a presença do arquivo

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem35.png" height='300'/>
 
8.	Ainda no terminal, digite o seguinte comando para mudar a permissão de acesso à chave SSH:

```bash
chmod 400 labsuser.pem
```

9.	Acesse a instância EC2 do Jenkins pela linha de comando

    9.1.	Volte ao console da AWS, no serviço do EC2

    9.2.	Selecione a instância ec2-jenkins criada na aula anterior

    9.3.	No painel inferior, em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem36.png" height='25'/> copie o <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem37.png" height='25'/> clicando em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem38.png" height='25'/>

    9.4.	Volte à tela do AWS CloudShell e digite o seguinte comando para acessar a instância EC2. Troque `<IP-INSTANCIA>` pelo IP copiado no passo anterior

    ```bash
    ssh -i labsuser.pem ec2-user@<IP-INSTANCIA>
    ```

    9.5.	 Confirme a conexão digitando `yes`

    9.6.	Se a conexão deu certo, você verá a linha de comando iniciando com `ec2-user`

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem39.png" height='300'/>

10.	Conectado na instância, precisamos recuperar a senha de administrador do Jenkins

    10.1.	Na linha de comando digite:
    
    ```bash
    sudo cat /var/lib/jenkins/secrets/initialAdminPassword
    ```

    10.2.	Copie e guarde o valor alfanumérico que aparecer no terminal

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem40.png" height='300'/>

11.	Em uma nova aba do navegador, acesse o Jenkins escrevendo `<IP-INSTANCIA>:8080`. Por exemplo: `12.345.6.789:800`. O IP é o mesmo utilizado para conectar na instância pelo terminal

12.	Coloque a senha do administrador no campo de texto e clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem41.png" height='25'/>

Essa é a senha do administrador. Quando acessar o Jenkins novamente, será solicitado o usuário e senha. Utilize o usuário “admin” e a senha que acabou de copiar

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem42.png" width='100%'/>

14. Na tela de customização, clique em  `Instalar as extensões sugeridas` e aguarde a instalação ser finalizada

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem106.png" width='100%'/>

15. Assim que instalação terminar, na nova tela clique em `Pular e continuar como administrador` 

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem107.png" width='100%'/>

15. Na próxima tela clique em `Gravar e concluir` 

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem108.png" width='100%'/>

16. Por fim, clique em `Começar a o Jenkins`

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem44.png" height='350'/>

# Configurar credenciais do Github

1. No seu repositório, clique no seu perfil no canto superior direito e depois em `Settings`

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem112.png" height='500'/> 

2. No menu lateral procure por <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem113.png" height='25'/> (última opção)

3. No novo menu lateral clique abra `Personal access tokens` e clique em `Token (classic)` 

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem115.png" height='150'/> 

4. Clique na opção `Generate new token` e depois em `Generate new token (classic)`

5. Preencha um nome no campo `Note`

6. Defina a data de expiração (`Expiration`) para 90 dias 

7. Em `Select scopes` selecione as opções conforme imagem abaixo:

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem126.png" width='100%'/> 

8. Clique em `Generate token`

9. Na página seguinte será mostrado o personal access token gerado, no campo com fundo verde. Ele funciona como uma senha para acessar o github a partir de aplicações. **Guarde esse token**, o github não mostra mais ele. Se perder, terá que gerar outro e reconfigurar tudo que usa o token.

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem127.png" width='100%'/> 

## Criar pipeline no Jenkins

1. Volte ao Jenkins. Na página inicial do Jenkins clique em `Gerenciar Jenkins` no menu lateral

2. Clique em `Ferramentas de configuração global`

3. Procure pela seção `Git` e clique no botão `Add Git` e depois em `JGit`

4. Clique em `Save`

5. Volte à pagina inicial do jenkins e clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem45.png" height='25'/> no menu lateral

6. Clique em `Manage credentials` 

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem109.png" height='75'/> 

7. Clique em `(global)`

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem110.png" width='100%'/> 

8. Clique no botão <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem111.png" height='25'/>

9. Na próxima tela coloque seu usuário do github no campo `Username`, o token gerado anteriormente no campo `Password` e clique em `Create`

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem117.png" width='100%'/> 

10. Volte a tela inicial do Jenkins e clique em `Novo tarefa`

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem118.png" width='100%'/> 

11. Configure o nome da tarefa para `DataOpsDeployColeta`

12. Selecione a opção `Pipeline`

13. Clique em `Tudo certo`

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem119.png" width='100%'/> 

14. Na tela de configuração do pipeline, procure pela seção `Build Triggers` e selecione <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem120.png" height='25'/>

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem121.png" width='100%'/> 

15. Aida na mesma tela, procure pela seção `Pipeline` e configure conforme a imagem abaixo. Troque os seguintes valores pelas suas configurações:

    * `Repository URL`: URL do seu repositório do lab 4

    * `Credentials`: selecione a credencial criada anteriormente

    * `Branch Specifier (blank for 'any')`: Coloque a sua branch principal (provavelmente `main`) 

16. Clique em `Aplicar` e depois em `Salvar`

## Configurar webhook no Github

1. Volte ao Github e abra seu repositório do Lab4

2. Clique em `Settings > Webhooks`

3. Clique em `Add webhook` E CONFIGURE O SEGUINTE:

    * `Payload URL`: `http://{IP_JENKINS_EC2}:8080/github-webhook/`  Troque `{IP_JENKINS_EC2}` pelo IP da sua instância EC2. Repare na barra no final da URL

    * `Content type`: `application/json`

4. Clique em `Add webhook`

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem124.png" width='100%'/> 

5. Quando voltar a lista de webhooks você deve ver um check ao lado do webhook

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem125.png" height='75'/>


# Executar pipeline Jenkins

1. No VSCode, crie o arquivo `Jenkinsfile` na pasta `lab4` com o seguinte conteúdo. Troque `deploy-nomesobrenome-accountID-regiao` pelo bucket criado no Laboratório 2

```javascript
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
        S3_BUCKET = 'deploy-nomesobrenome-accountID-regiao'
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
```

2. Envie os arquivos para o github e acompanhe a execução no Jenkins. Se não executar automaticamente, abra a o pipeline criado no Jenkins e clique em `Construir agora`. As próximas alterações no repositório devem iniciar o pipeline automaticamente. Faça alguma alteração em algum arquivo do lab4, envie para o github e veja a execução automática do pipeline.


12.	Acompanhe a execução no Jenkins e espere completar com sucesso

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem98.png" height='400'/>
 
13.	Verifique se a função lambda foi criada

14.	Verifique no serviço EventBridge o evento criado e o horário de execução

    14.1. Esse evento irá executar automaticamente no horário definido no template e disparar a função AWS
    
    14.2. No EventBridge, acesse `Regras` no menu lateral esquerdo para abrir as regras de execução automática. 

    14.3. Clique na regra “dataops-agenda-coleta-vacina”

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem99.png" height='350'/>
 
    14.4. Nos detalhes da regra, clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem100.png" height='25'/>

    14.5. Vá até a seção <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem101.png" height='25'/> e na caixa de seleção ao lado de <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem102.png" height='25'/> selecione a opção <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem103.png" height='25'/> para ver qual a próxima execução no horário de Brasília
 
    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem104.png" height='350'/>

    14.6. Se o horário já passou ou ainda está longe (pode ser que seja só amanhã), altere no template do SAM na propriedade `Schedule` dentro de `Events` a hora da execução para daqui 10 minutos, envie para o repositório e espere a atualização da função pelo pipeline. O horário da AWS fica 3 horas adiantando ao horário atual. Então no agendamento coloque 3 horas a mais do horário atual. Por exemplo, se for 21:00 no seu relógio, coloque a execução para às 00:10 (`cron(10 00 * * ? *)` – o primeiro número são os minutos e o segundo são as horas). Assim o evento passa a executar todos os dias as 21:10.



<div class="footer">
    &copy; 2022 Fernando Sousa
    <br/>
    
Last update: 2023-03-25 20:14:11
</div>