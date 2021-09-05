import requests
import boto3
import asyncio
import math

async def upload_s3_async(init, end, i, url, bucket, key, s3_client, mpu):
    print(f'Upload {i}')
    # download do pedaço do arquivo
    resume_header = {'Range':f'bytes={init}-{end}'}
    r = requests.get(url,  headers=resume_header)
    
    #upload para o S3
    return s3_client.upload_part(Bucket=bucket, Key=key, PartNumber=i, UploadId=mpu['UploadId'], Body=r.content)

async def upload_s3(url, bucket, key, s3_client, mpu):
    # separar arquivo em pedaços de 50 MB
    b = 52428800
    h = requests.head(url)
    t = int(h.headers['Content-Length'])
    n = math.ceil(t/b)
    parts = []
    tasks = []
    for i in range(n):
        init = i*b
        if init != 0:
            init += 1
        end = min((i+1)*b, t)
        print(end - init)
        if t-end < 6291456:
            end = t
        
        task = asyncio.ensure_future(upload_s3_async(init, end, i+1, url, bucket, key, s3_client, mpu) )
        tasks.append(task)
        
        
    # executar coleta dos pedaços do arquivo
    parts = await asyncio.gather(*tasks)
        
    return parts


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


    #fazer download do arquivo por partes    
    parts = asyncio.get_event_loop().run_until_complete(upload_s3(url, bucket, key, s3_client, mpu))
            
    # finalizar upload
    print(parts)
    part_info = {
        'Parts': [
            {
                'PartNumber': i+1,
                'ETag': p['ETag']
            } for i, p in enumerate(parts)
        ]
    
    }
    print(part_info)
    s3_client.complete_multipart_upload(Bucket=bucket
                         , Key=key
                         , UploadId=mpu['UploadId']
                         , MultipartUpload=part_info)
