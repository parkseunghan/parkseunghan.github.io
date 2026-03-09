---
title: "[1주차 TIL] KnockOn Bootcamp - 프록시 (Challenge)"
categories:
  - Web Architecture
tags:
  - Knockon Bootcamp 2nd
  - Proxy
last_modified_at: 2024-08-05T04:54:00-05:00
published: true
---

|

Burp Suite 사용

# 0. POST 요청으로 변경하세요!

```js
GET -> POST로 변경
```

|

---

|

# 1. POST 요청의 'request' 파라미터를 'get-flag'로 설정하세요!

```js
POST / HTTP/1.1
Host: war.knock-on.org:10001
Content-Type: application/x-www-form-urlencoded
Content-Length: 16

request=get-flag
```

> request=get-flag 추가

|

---

|

# 2. User-Agent 헤더를 'bot'으로 설정하세요!

```js
POST / HTTP/1.1 
Host: war.knock-on.org:10001
User-Agent: bot
Content-Type: application/x-www-form-urlencoded
Content-Length: 16

request=get-flag
```

> User-Agent: bot 추가

|

---

|

# 3. API_KEY가 'SUp3r_STr0000ng_k3y'인 Cookie 헤더를 가지고 있어야만 합니다!

```js
POST / HTTP/1.1
Host: war.knock-on.org:10001
User-Agent: bot
Content-Type: application/x-www-form-urlencoded
Content-Length: 20
Cookie: API_KEY=SUp3r_STr0000ng_k3y

request=get-flag
```

> Cookie: API_KEY=SUp3r_STr0000ng_k3y 추가

|

---

|

# Success!!!

```
K0{M4n1pul4t1ng_c00k13s_1s_qu1t3_3z!!}
```

|

---

|