import json
import urllib.parse
import boto3
import time

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

def send_sqs_msg(key):
    sqs.send_message(
            QueueUrl        = "ai-request-queue",
            MessageBody     = json.dumps({ "cmd":"predict", "data":key})
    )

def lambda_handler(event, context):
    # 버킷 정보
    bucket      = event['Records'][0]['s3']['bucket']['name']
    # 키 정보
    key         = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    # 업로드 파일 정보
    print( bucket, key )
    send_sqs_msg( key )
    # #print("Received event: " + json.dumps(event, indent=2))
    
    # # 업로드된 데이터 획득
    # # Get the object from the event and show its content type
    # try:
    #     response = s3.get_object(Bucket=bucket, Key=key)
    #     print("CONTENT TYPE: " + response['ContentType'])
    #     return response['ContentType']
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e
