# 세팅
    - pip install -r requirements.txt

# 디비 구동
    - 도커 컨테이너 생성
        - docker run -d -p 3306:3306 --name dev_db --env MARIADB_ROOT_PASSWORD=1234 mariadb
    - 도커 컨테이너 접속
        - docker exec -it dev_db bash
    - mysql -u root -p
        - 1234
    - create database predict_db;
    - use predict_db;
    - 테이블 생성
        ```
            CREATE TABLE `predicts` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `uid` varchar(32) NOT NULL,
            `pred` varchar(32) NOT NULL,
            `ori` varchar(256) NOT NULL,
            `check` varchar(2) NOT NULL DEFAULT 0,
            `reg_date` timestamp NULL DEFAULT NULL,
            PRIMARY KEY (`id`) USING BTREE
            ) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
        ```

# 구동
    - Rookies076:~/environment/ $ cd was_service
    - Rookies076:~/environment/was_service $ flask --debug -e production.env run

