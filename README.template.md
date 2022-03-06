# DataOps - Laboratório 3

Coleta de Dados com Lambda, Eventos e implantação com CodePipelne e Jenkins

As instruções do laboratório estão em português. Para alterar o idioma, procure a opção na barra inferior do console AWS.


## Objetivos

* Configurar Jenkins para construir a aplicação e implantar na AWS
*	Utilizar CodePipeline para integrar e implantar com Jenkins
*	Criar uma função Lambda para coleta de dados, disparada por um evento agendado
*	Implantar uma Função Lambda utilizando AWS SAM, Jenkins e CodePipeline



## Arquitetura da solução

<img src="https://raw.github.com/fesousa/dataops-lab4/master/images/Imagem1.png" height='330'/>


## Função Lambda para coletar dados

1.	No VSCode, crie uma nova pasta `lab4` e dentro dela uma outra pasta `app`. Dentro da pasta `app` crie um arquivo `lambda_function.py`

2.	Coloque o seguinte código  no arquivo

  Este código faz o download do arquivo de vacinação no AC disponível em [aqui](https://dados.gov.br/dataset/covid-19-vacinacao/resource/ef3bd0b8-b605-474b-9ae5-c97390c197a8) e copie para o bucket criado no [Laboratório 1](https://github.com/fesousa/dataops-lab1) (nome sugerido foi `dataops-dados-nomesobrenome`, sendo que `nomesobrenome` deve ser seu nome e sobrenome; ou entáo coloque o nome do bucker que criou no  [Laboratório 1](https://github.com/fesousa/dataops-lab1), se for diferente)


```python
${app/lambda_function.py}
```





<div class="footer">
    &copy; 2022 Fernando Sousa
    <br/>
    {{update}}
</div>