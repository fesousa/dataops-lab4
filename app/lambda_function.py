import requests
import boto3


def lambda_handler(event, context):

    #download do arquivo
    local_filename = f'/tmp/vacinas_{event["uf"]}.csv'
    url = event['url']

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):                
                f.write(chunk)

    # copiar para S3
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(local_filename, 'dataops-impacta-dados-fernandosousa', 'vacinas_{event["uf"]}.csv')
    except Exception as e:
        print(e)
        return False
    
    return True

#lambda_handler(None, None)