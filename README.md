# DataOps - Laboratório 3

Coleta de Dados com Lambda, Eventos e implantação com CodePipelne e Jenkins

As instruções do laboratório estão em português. Para alterar o idioma, procure a opção na barra inferior do console AWS.


## Objetivos

* Configurar Jenkins para construir a aplicação e implantar na AWS
*	Utilizar CodePipeline para integrar e implantar com Jenkins
*	Criar uma função Lambda para coleta de dados, disparada por um evento agendado
*	Implantar uma Função Lambda utilizando AWS SAM, Jenkins e CodePipeline



## Arquitetura da solução

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem1.png" width='100%'/>


## Função Lambda para coletar dados

1.	No VSCode, crie uma nova pasta `lab4` e dentro dela uma outra pasta `app`. Dentro da pasta `app` crie um arquivo `lambda_function.py`

2.	Coloque o seguinte código  no arquivo

  Este código faz o download do arquivo de vacinação no AC disponível <a href="https://dados.gov.br/dataset/covid-19-vacinacao/resource/ef3bd0b8-b605-474b-9ae5-c97390c197a8" target="_blank"> aqui </a> e copie para o bucket criado no <a href="https://github.com/fesousa/dataops-lab1" target="_blank"> Laboratório 1 </a> (nome sugerido foi `dataops-dados-nomesobrenome`, sendo que `nomesobrenome` deve ser seu nome e sobrenome; ou entáo coloque o nome do bucker que criou no  <a href="https://github.com/fesousa/dataops-lab1" target="_blank"> Laboratório 1 </a>, se for diferente)


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
      "url":"https://s3-sa-east-1.amazonaws.com/ckan.saude.gov.br/PNI/vacina/uf/2021-09-03/uf%3DAC/part-00000-55f3db2e-ec9a-4125-9044-11b088159962.c000.csv", 
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
 
    5.6.	Abra o seu bucket de dados (`dataops-impacta-dados-nomesobrenome`, ou o nome criado no  <a href="https://github.com/fesousa/dataops-lab4/blob/master/app/lambda_function.py" target="_blank">`lambda_function.py` </a>) e verifique o arquivo baixado


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



<div class="footer">
    &copy; 2022 Fernando Sousa
    <br/>
    
Last update: 2022-03-07 00:05:34
</div>