---
title: "KnockOn Bootcamp 2nd - 12.2 IDOR"
categories:
  - Web Hacking
tags:
  - Wargame
  - KnockOn Bootcamp 2nd
  - IDOR
last_modified_at: 2024-09-17T06:30:00+09:00
published: true
---
## 문제

<http://war.knock-on.org:10017/>

![12.2 IDOR 1](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-2-idor-1.png)

![12.2 IDOR 2](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-2-idor-2.png)

### 목표

다른 사용자의 리소스를 참조를 통해 flag 얻기

### 공격 기법

Insecure Direct Object References

## 분석

### /signup

![12.2 IDOR 3](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-2-idor-3.png)

회원가입을 할 수 있음

일단 user로 회원가입

### /login

![12.2 IDOR 4](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-2-idor-4.png)

로그인

![12.2 IDOR 5](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-2-idor-5.png)

로그인을 하면 개인 게시판이 나오고, 글을 작성할 수 있음

## 풀이

![12.2 IDOR 6](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-2-idor-6.png)

글을 작성하고나면 경로가 나옴

![12.2 IDOR 7](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-2-idor-7.png)

궁금해서 post/1로 들어가봄

다른 사용자의 리소스지만 접근 가능

## 페이로드

```bash
http://war.knock-on.org:10017/post/1
```

### FLAG

```sh
K0{IDOR_is_very_easy}
```
