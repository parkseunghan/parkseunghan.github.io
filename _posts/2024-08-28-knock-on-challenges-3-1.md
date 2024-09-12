---
title: "[Writeup] Knockon Bootcamp - 3.1 SQLi_WAF_1"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - SQL Injection
  - Filter Bypass
last_modified_at: 2024-08-28T23:00:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10030/>

![3.1 SQLi WAF 1 1](/assets/images/writeup/web-hacking/knock-on/3-1_SQLi_WAF_1_1.png)

![3.1 SQLi WAF 1 2](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png)

![3.1 SQLi WAF 1 3](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png)

|

|

|

### 목표

---

필터링 로직을 우회하여 admin 계정으로 로그인하기

|

### 공격 기법

---

SQL Injection

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
import string

app = Flask(__name__)

MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
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
        filtering_list = ['or', 'and']
        username = request.form["username"].lower()
        password = request.form["password"].lower()

        for filter in filtering_list :
            if (filter in username) or (filter in password):
                return render_template("login.html", error='no Hack!')

        query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
        
        with db.engine.connect() as connection:
            result = connection.execute(query)
            user = result.fetchone()
        if user and user[1] == "admin":
            return redirect(url_for("success", username=user[1], flag=LOGIN_FLAG))
        elif user:
            return redirect(url_for("success", username=user[1]))
        else:
            error = "Invalid Credentials"
        return render_template("login.html", error=error, query=str(query))
    else :
        return render_template("login.html")


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

### login()

---

```python
filtering_list = ['or', 'and']
username = request.form["username"].lower()
password = request.form["password"].lower()

for filter in filtering_list :
    if (filter in username) or (filter in password):
        return render_template("login.html", error='no Hack!')
```

`username`과 `password`에 `filtering_list`에 있는 키워드들을 사용하면 로그인 시도가 차단됨 

또한 `OR`과 `AND`와 같이 대문자로 입력을 해도 모두 소문자로 바뀌어 필터링됨

`WAF(Web Application Firewall) Bypass`기법과 같이 보안 시스템을 우회하는 것처럼, 서버에서 정해놓은 `filtering_list`의 키워드들을 우회하여 SQL Injection을 시도해야 함

|

```python
if user and user[1] == "admin":
    return redirect(url_for("success", username=user[1], flag=LOGIN_FLAG))
```

쿼리가 유효하고 admin으로 로그인 성공 시 화면에 flag가 출력됨

|

|

|

## Exploit

1. `‘`를 입력하면 에러가 뜸 → SQL Injection 가능

2. admin으로 로그인 시도

    ```python
    admin' -- 1
    ```

`or`과 `and`를 사용할 필요도 없이 로그인 성공

|

|

|

## Payload

```
username: admin' -- 1 

password: 1
```

|

|

### FLAG

---

```
K0{and_and_or_bypass!}
```

|

---