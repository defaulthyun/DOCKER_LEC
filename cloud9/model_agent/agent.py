"""
    usage:
        - insatll
            - pip install -r requirements.txt
"""
import boto3
import os
import tensorflow as tf
import urllib
from PIL import Image
import numpy as np
import time
import json
import datetime

model = None
down_wei_name = "08-0.57376.h5"


def init_weight():
    if not os.path.exists("./" + down_wei_name):  # 파일이 없다면
        # step 1. 최초 로드시 s3로부터 가중치 혹은 모델덤프 파일 다운로드(1회만)
        #         차후, 버전 관리(1.0버전(90% 적용), 1.1버전(10%적용) -> 테스팅 -> 확대 및 교체)
        s3_client = boto3.client("s3")
        s3_client.download_file(
            "ai-000000-bk-2023", "models/" + down_wei_name, down_wei_name
        )
        print(f"{down_wei_name} 다운로드 완료")
    else:
        print(f"{down_wei_name} 이미 존재함")


# step 2. 모델로드
def load_model():
    global model
    model = tf.keras.models.load_model("./" + down_wei_name)


# step 3. 예측 및 결과 송신
#         3-1. case 1 : 로그저장, db에 저장->푸시,
#         3-2. case 2 : 로그저장, sqs, ai-response-queue 큐 -> was에서 큐를 체크하면서 응답처리)
def get_predict(url, uid, file_name):
    """
    url : https://xxxx.cloudfront.net//data/xxxx.xxx
        - CDN + 버킷상의 주소로 전달된다 -> sqs를 통해서
    """
    # 1. 다운로드
    print(url)
    down_file_name = url.split("/")[-1]
    urllib.request.urlretrieve(url, down_file_name)
    # 2. 이미지 => ndarray , shape: NHWC -> 4D
    img = Image.open("./" + down_file_name)
    img_arr = np.array(img).reshape((-1, 150, 150, 3))
    # 3. 예측
    result = model.predict(img_arr / 255)
    # 4. 응답큐에 메시지를 입력 => 트리거 발생 => 람다 호출 => 디비 결과 입력
    # result => [[0.6121106]]
    # print( result )
    send_sqs_message(result[0][0], uid, file_name)


def send_sqs_message(y_pred, uid, file_name):
    try:
        sqs = boto3.client("sqs")
        sqs.send_message(
            QueueUrl="ai-response-queue",  # 응답큐
            MessageBody=json.dumps(
                {
                    "cmd": "response",
                    "pred": str(y_pred),
                    "uid": uid,
                    "file_name": file_name,
                }
            ),
        )
        print("응답큐에 결과 전송")
    except Exception as e:
        print("메세지 전송 오류", e)


def test_004():
    # 대기열 큐를 특정 주기로 계속해서 체크, 모니터링, 감지한다
    q_name = "ai-request-queue"
    sqs = boto3.client("sqs")
    res = sqs.receive_message(
        QueueUrl=q_name,
        AttributeNames=["SentTimestamp"],
        MessageAttributeNames=[
            "All",
        ],
        MaxNumberOfMessages=1,  # 1개씩 가져오는것으로
        VisibilityTimeout=0,
        WaitTimeSeconds=0,
    )
    if res and ("Messages" in res):  # 해당 키가 존재하면 메시지가 존재하는것
        # 수신한 값을 기준 => 메시지가 존재하는 여부 체크 -> 메시지 삭제(큐에서) -> 예측 처리 요청 진행
        receipt_handle = res["Messages"][0]["ReceiptHandle"]  # 메시지 고유값
        body = res["Messages"][0]["Body"]
        body = json.loads(body)
        print(body["data"])
        standby_predict(body["data"])

        # 메세지 삭제 -> 큐에서 제거
        sqs.delete_message(QueueUrl=q_name, ReceiptHandle=receipt_handle)

        # 예측 수행을 지시(컨테이너) -> 예측 수행(딥러닝 에이전트(컨테이너) or 람다함수)
        # -> 결과를 받아서 응답 하는 큐에 메시지를 전송
    else:
        print("no message", datetime.datetime.now())


def standby_predict(key):
    # sqs => 메시지 획득 => key 획득 => 예측수행
    # key = 'normal_test_7.jpg'
    cdn = "cdn 주소"
    # url = f'{cdn}/data/{key}'
    url = f"{cdn}/{key}"
    get_predict(url, key.split("/")[1].split("_")[0], key)


if __name__ == "__main__":
    # step 1. 최초 로드시 s3로부터 가중치 혹은 모델덤프 파일 다운로드(1회만)
    init_weight()
    # step 2. 모델로드
    load_model()
    # step 3. 대기열 큐를 특정 주기로 계속해서 체크, 모니터링, 감지한다
    while True:
        try:
            test_004()
        except Exception as e:
            print(e)
        time.sleep(1)
