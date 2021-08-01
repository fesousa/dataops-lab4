import requests
import boto3


def lambda_handler(event, context):

    #download do arquivo
    local_filename = '/tmp/vacinas.csv'
    url = "https://s3-sa-east-1.amazonaws.com/ckan.saude.gov.br/PNI/vacina/uf/2021-07-22/uf%3DAC/part-00000-02e8fcac-58d6-488c-abda-dc607278e619.c000.csv"

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):                
                f.write(chunk)

    # copiar para S3
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(local_filename, "dataops-impacta-dados-fernandosousa", "vacinas.csv")
    except Exception as e:
        print(e)
        return False
    
    return True

#lambda_handler(None, None)