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
${app/lambda_function.py}
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

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem17.png" height='80'/>
 
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

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem20.png" height='150'/>


    5.3.	Clique em <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem21.png" height='25'/>

    5.4.	Espera a função terminar de executar

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem22.png" height='80'/>
 
    5.5.	Expanda <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem23.png" height='25'/> para ver os resultados. Você deve ver a mensagem true na área branca. Se não vir, verifique o log mais abaixo e verifique o nome do bucket

    <img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem24.png" height='50'/>
 
    5.6.	Abra o seu bucket de dados (`dataops-impacta-dados-nomesobrenome`, ou o nome criado no  <a href="https://github.com/fesousa/dataops-lab4/blob/master/app/lambda_function.py" target="_blank">`lambda_function.py` </a>) e verifique o arquivo baixado



<div class="footer">
    &copy; 2022 Fernando Sousa
    <br/>
    {{update}}
</div>