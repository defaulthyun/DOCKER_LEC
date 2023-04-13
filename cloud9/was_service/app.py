from flask import Flask, render_template, request, jsonify, make_response, Response
import boto3
import pymysql as my
import jwt
from datetime import datetime, timedelta
import time

app = Flask(__name__)
app.secret_key = "secretkey"
s3 = boto3.resource("s3")


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")
    else:
        uid = request.form.get("uid")
        upw = request.form.get("upw")
        if uid == "guest" and upw == "1234":
            payload = {
                "id": uid,
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(payload, app.secret_key, algorithm="HS256")
            # 응답을 직접 구성 + 쿠키 설정
            resp = make_response(render_template("auth.html"), 200)
            resp.set_cookie("token", token)
            return resp
        else:
            return "회원아님"


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("predict.html")
    else:
        try:
            token = request.cookies.get("token")
            payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            if payload["exp"] < time.mktime(
                datetime.utcnow().timetuple()
            ):  # 현재시간보다는 과거
                return Response(status=401)
        except jwt.InvalidTokenError:
            return Response(status=401)
        except jwt.ExpiredSignatureError:
            return Response(status=401)
        except jwt.exceptions.DecodeError:
            return Response(status=401)

        file = request.files["file"]
        # return f'{payload["id"]}_{token}_{file.filename}'
        name = f'{payload["id"]}_{file.filename}'
        file.save(name)
        s3_upload(name)
        return render_template("result.html")


def select_data(uid):
    connection = None
    row = None
    try:
        connection = my.connect(
            host="ip_address",
            user="root",
            password="1234",
            database="predict_db",
            cursorclass=my.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            sql = """
                select * from predicts where uid=%s and `check`=0 order by reg_date desc limit 1;
            """
            cursor.execute(sql, (uid))
            row = cursor.fetchone()
    except Exception as e:
        print("에러 => ", e)
    finally:
        if connection:
            connection.close()
    return row


def update_predict_check(uid):
    connection = None
    try:
        connection = my.connect(
            host="ip_address",
            user="root",
            password="1234",
            database="predict_db",
            cursorclass=my.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            sql = """
                update predicts set `check`=1 where uid=%s and `check`=0;
            """
            cursor.execute(sql, (uid))
        connection.commit()
    except Exception as e:
        print("에러 => ", e)
    finally:
        if connection:
            connection.close()


@app.route("/result")
def result():
    token = request.cookies.get("token")
    payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
    row = select_data(payload["id"])
    if not row:
        res = {"code": 0, "msg": "예측중"}
    else:
        update_predict_check(payload["id"])
        res = {"code": 1, "msg": "양성"}
    return jsonify(res)


def s3_upload(file):
    with open(file, "rb") as f:
        data = f.read()
    print("data/" + file)

    s3.Bucket("ai-000000-bk-2023").put_object(Key="data/" + file, Body=data)
