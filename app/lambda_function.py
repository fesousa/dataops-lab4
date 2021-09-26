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
    bucket = 'dataops-impacta-dados-fernandosousa'
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
