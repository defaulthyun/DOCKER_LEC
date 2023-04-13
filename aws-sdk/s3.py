'''
    s3 서비스를 파이썬으로 엑세스 및 처리 테스트 코드
        - 버컷리스트
        - 파일 업로드
            - 클라이언트가 예측을 위해서 데이터를 업로드 할 때 사용 할 코드
        - 파일 다운로드
            - 딥러닝 모델 Agent가 예측 수행하기 위해서 s3->cdn->다운로드 할 때 사용 할 코드
            - boto3 패키지가 AWS SDK의 핵심 패키지 (아마존 생태계에서 사용)
                - pip install boto3        
'''

'''
    aws 바깥쪽 생테계에서 pwd을 엑세스 할 때에는 권한을 증명 할 수 있는 엑세스 키 필요
        - AWS IAM 이용
            - 단, key.json은 노출 시 보안에 크게 문제가 발생
            - 키는 IAM을 통해 발급 -> 누출ㅊㅇ  주의
'''
import boto3
import time
import json

from pp import ProgressPercentage as PP
from botocore.client import Config
# 아마존 생태꼐 바깥쪽에서 아마존 엑세스 처리 사용 할 코드
with open('./aws-sdk/key.json') as f:
    keys = json.load(f)

# s3 서비스 객체 생성
s3 = boto3.resource('s3',
                    aws_access_key_id=keys['ACCESS_KEY_ID'],
                    aws_secret_access_key=keys['ACCESS_SECRET_KEY'],
                    config=Config(signature_version='s3v4')
                    )
s3_client = boto3.client('s3',
                         aws_access_key_id=keys['ACCESS_KEY_ID'],
                         aws_secret_access_key=keys['ACCESS_SECRET_KEY'],
                         config=Config(signature_version='s3v4'),
                         )

# 버킷 리스트 획득
def test():
    bks = [bk.name for bk in s3.buckets.all() ]
    print(bks)
    return bks

# 파일 업로드, 단 s3을 boto3.resource()로 생성 시 
def test2(bks):
    # 파일 읽기 (텍스트 파일, 바이너리 파일?)
    with open('./aws-sdk/docker-compose---.txt', 'r', encoding='utf8') as f:
        data = f.read()
    
    # 업로드 -> 버킷 선택
    for bk in bks:
        # 각자 버킷명으로 사용, 편의상 표현
        if bk == 'ai-public-bk-20230405':
            # 업로드 시 충돌되지 않게 해싱사용, 여기서는 그냥 이름
            s3.Bucket(bk).put_object(Key='docker-compose2.txt', Body=data)

def test3(bks):
    with open('./aws-sdk/docker-compose---.txt', 'r', encoding='utf8') as f:
        data = f.read()
    
    for bk in bks:
        if bk == 'ai-public-bk-20230405':
            s3_client.upload_file('./aws-sdk/docker-compose---.txt',bk,
            'docker-compose_bucket.txt',Callback=PP('./aws-sdk/docker-compose---.txt'))

# 파일 다운로드(Direct)
def test4():
    # 버킷 이름, s3상 존재하는 다운로드 받은 객체명 다운로드 시 파일명
    # 딥러닝 모델이 예측해야 할 데이터
    s3_client.download_file('ai-public-bk-20230405', 'docker-compose_bucket.txt', 'docker-compose_download.txt')
    # 현재는 s3에서 직접 받는 코드, 향후 CDN에서 직접 내려받겠다 (속도차이)
    
    
# 실행
if __name__ == "__main__":
    bks = test()
    
    # 파일 업로드
    #test2(bks)
    #test3(bks)
    
    # 파일 다운로드
    test4()