import requests
import boto3


def lambda_handler(event, context):
    bucket = 'dataops-impacta-dados-fernandosousa'
    key = f'vacinas_{event["uf"]}.csv'
    #download do arquivo
    local_filename = f'/tmp/vacinas_{event["uf"]}.csv'
    url = event['url']
    parts = []

    s3_client = boto3.client('s3')
    mpu = s3_client.create_multipart_upload(Bucket=bucket, Key=key)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        #with open(local_filename, 'wb') as f:
        i = 1
        for chunk in r.iter_content(chunk_size=8192):                
            parts.append(s3_client.upload_part(Bucket=bucket
                       , Key=key
                       , PartNumber=1
                       , UploadId=mpu['UploadId']
                       , Body=chunk))
            i+=1
            #f.write(chunk)
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
    
    try:
        response = s3_client.upload_file(local_filename, 'dataops-impacta-dados-fernandosousa', f'vacinas_{event["uf"]}.csv')
    except Exception as e:
        print(e)
        return False
    
    return True

#lambda_handler(None, None)