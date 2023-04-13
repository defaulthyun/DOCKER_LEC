################
# 모델 에이전트 => 예측수행 => sqs 생성(예측결과만 담은큐) => 트리거 발동 => 람다 함수 호출 => 디비입력
# lambda_function.py
# 람다 환경에 별도 패키지 설치
# 로컬 pc상 특정 폴더 예를 들면 pack 밑에서 아래 명령 수행
# ~pack>pip install pymysql -t .
# pack 파일 압축 => pack.zip
# 람다 함수를 기본형으로 생성
# 에서 업로드 버튼 클릭 > .zip파일 > pack.zip 선택
# 이후 아래 코드 붙이면됨
################
import json
import pack.pymysql as my


def lambda_handler(event, context):
    try:
        print(event["Records"][0]["body"])
        print(1)
        # {"cmd": "response", "data": "0.6121106"}
        res = json.loads(event["Records"][0]["body"])
        print(2)
        insert_data(res)
    except Exception as e:
        print(e)


def insert_data(res):
    pred = res["pred"]
    uid = res["uid"]
    file_name = res["file_name"]
    print(" DB 등록 1 ")
    connection = None
    print(" DB 등록 2 ")
    try:
        # host ip는 cloud9 아이피로 도커 컨테이너로 DB가 가동중임 (인바운드 3306 오픈 상태)
        connection = my.connect(
            host="ip_address",  # ip주소 설정 필요
            user="root",
            password="1234",
            database="predict_db",
            cursorclass=my.cursors.DictCursor,
        )
        print(" DB 등록 3 ")
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO `predicts` (`uid`, `pred`, `ori`, `reg_date`) VALUES (%s, %s, %s, now());
            """
            print(" DB 등록 4 ", sql, uid, pred, file_name)
            cursor.execute(sql, (uid, pred, file_name))
        connection.commit()
        print(" DB 등록 완료 ")
    except Exception as e:
        print("에러 => ", e)
    finally:
        if connection:
            connection.close()
