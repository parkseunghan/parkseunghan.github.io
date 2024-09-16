---
title: "[Writeup] Knockon Bootcamp - 12.2 IDOR"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - Insecure Direct Object References
last_modified_at: 2024-09-16T16:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10017/>

![12.2 IDOR 1](/assets/images/writeup/web-hacking/knock-on/12-2_IDOR_1.png)

![12.2 IDOR 2](/assets/images/writeup/web-hacking/knock-on/12-2_IDOR_2.png)

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

## 분석

### /signup

---

![12.2 IDOR 3](/assets/images/writeup/web-hacking/knock-on/12-2_IDOR_3.png)

회원가입을 할 수 있음

일단 user로 회원가입

|

|

### /login

---

![12.2 IDOR 4](/assets/images/writeup/web-hacking/knock-on/12-2_IDOR_4.png)

로그인

|

![12.2 IDOR 5](/assets/images/writeup/web-hacking/knock-on/12-2_IDOR_5.png)

로그인을 하면 개인 게시판이 나오고, 글을 작성할 수 있음

|

|

|

## Exploit

![12.2 IDOR 6](/assets/images/writeup/web-hacking/knock-on/12-2_IDOR_6.png)

글을 작성하고나면 경로가 나옴

|

![12.2 IDOR 7](/assets/images/writeup/web-hacking/knock-on/12-2_IDOR_7.png)

궁금해서 post/1로 들어가봄

다른 사용자의 리소스지만 접근 가능

|

|

|

## Payload

```bash
http://war.knock-on.org:10017/post/1
```

|

|

### FLAG

---

```sh
K0{IDOR_is_very_easy}
```

|

---