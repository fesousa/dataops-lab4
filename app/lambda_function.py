import requests
import boto3
import asyncio

async def upload_s3_async(i, bucket, key, chunk, s3_client, mpu):
    print(f'Upload {i}')
    return s3_client.upload_part(Bucket=bucket, Key=key, PartNumber=i, UploadId=mpu['UploadId'], Body=chunk)

async def upload_s3(i, bucket, key, chunk, s3_client, mpu):
    return await upload_s3_async(i, bucket, key, chunk, s3_client, mpu)  


def lambda_handler(event, context):
    
    #download do arquivo
    #local_filename = f'/tmp/vacinas_{event["uf"]}.csv'
    # url que verá pelo parâmetro
    url = event['url']
    #lista com as partes para upload
    parts = []
    
    # nome do bucket paa upload
    bucket = 'dataops-impacta-dados-fernandosousa'
    #nome do arquivo que será salvo no bucket
    key = f'vacinas_{event["uf"]}.csv'
    #Concexão com s3
    s3_client = boto3.client('s3')
    # iniciar upload multipart
    mpu = s3_client.create_multipart_upload(Bucket=bucket, Key=key)

    #fazer download do arquivo por stream
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        #with open(local_filename, 'wb') as f:
        i = 1
        for chunk in r.iter_content(chunk_size=104857600):
            # upload de parte do arquivo
            
            parts.append(asyncio.run(upload_s3(i, bucket, key, chunk, s3_client, mpu)))
            i+=1
            #f.write(chunk)
            
    # finalizar upload
    part_info = {
        'Parts': [
            {
                'PartNumber': i+1,
                'ETag': p['ETag']
            } for i, p in enumerate(parts)
        ]
    
    }
    s3_client.complete_multipart_upload(Bucket=bucket
                         , Key=key
                         , UploadId=mpu['UploadId']
                         , MultipartUpload=part_info)

    # copiar para S3
    
    # try:
    #     response = s3_client.upload_file(local_filename, 'dataops-impacta-dados-fernandosousa', f'vacinas_{event["uf"]}.csv')
    # except Exception as e:
    #     print(e)
    #     return False
    
    # return True

#lambda_handler(None, None)