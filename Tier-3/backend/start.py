from flask import Flask
import pymysql 

app = Flask(__name__)

# DB Root 비밀번호 로드
root_password = None
with open('/run/secrets/db-password') as f:
    root_password = f.read()

print(root_password)

# DB 연동 코드를 추가해서, 도커 컴포즈로 구성된 컨테이너 간 DB 연동이 잘 되는 지 체크
def db_init():

    connection = None
    try:
        # 1. 접속 (mysql -u root -p > password : )
        connection = pymysql.connect(
            host="mysql_db",  # 127.0.0.1 (서버측)
            port = 3306, # 포트
            user="root",  # 사용자 계정, root 계정 외 사용 권장
            password=root_password,  # 비밀번호
            charset='utf8'
        )
        # mysql[None]:>
        print("접속 성공")
        
        with connection: # 커넥션이 with문을 나가면 자동으로 닫힌다
            with connection.cursor() as cur: # 커서는 with문을 나가면 자동으로 닫힌다
                # 1. DB 생성
                cur.execute('create database if not EXISTS db_mysql;')

                # 2. 커밋 -> DB에 변동을 가하면 (db 생성, table 생성, 데이터 입력/수정/삭제)
                connection.commit()
                
                # 3. DB 사용 지정
                cur.execute('use db_mysql;')

                # 4. 테이블 생성
                cur.execute('''
                    create table dummy (
                        id INT(32) AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(256)
                    );
                ''')

                # 5. 커밋
                connection.commit()

    except Exception as e:
        print("접속 오류", e)

    else:
        print("접속시 문제 없었음")

    finally:
        print("접속 종료 성공")

db_init()

# 더미 데이터 삽입 및 조회
def db_insert_select():
    rows = []
    try:
        # 커넥션
            connection = pymysql.connect(
            host="mysql_db",  # 127.0.0.1 (서버측)
            port = 3306, # 포트
            user="root",  # 사용자 계정, root 계정 외 사용 권장
            password=root_password,  # 비밀번호
            database='db_mysql',
            charset='utf8',
            cursorclass = pymysql.cursors.DictCursor
        )
            with connection:
                with connection.cursor() as cur:
                    # 더미 데이터 삽입 -> row 변화 -> 커밋행위 확정
                    cur.execute("insert into dummy (title) values ('test'); ")
                    # 커밋
                    connection.commit()
                    # 모든 데이터 조회
                    cur.execute('select title from dummy')
                    # 조회 데이터 획득
                    rows = cur.fetchall()
    
            
    except Exception as e:
        print("접속 오류", e)
    
    else:
        print("접속시 문제 없었음")

    finally:
        # 응답
        return rows

@app.route('/')
def home():
    rows = db_insert_select()
    return f"hello Container - 데이터 수 : {len(rows)}"

if __name__ == "__main__":
    app.run(debug=True)
