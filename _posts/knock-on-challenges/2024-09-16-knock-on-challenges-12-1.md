---
title: "KnockOn Bootcamp 2nd - 12.1 Business Logic Error"
categories:
  - Web Hacking
tags:
  - Wargame
  - KnockOn Bootcamp 2nd
  - Business Logic Error
last_modified_at: 2024-09-17T05:30:00+09:00
published: true
---
## 문제

<http://war.knock-on.org:10016/>

![12.1 Business_logic_error 1](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-1-ble-1.png)

![12.1 Business_logic_error 2](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-1-ble-2.png)

### 목표

Business Logic Error를 이용해 flag 얻기

### 공격 기법

Business Logic Attack

## 분석

![12.1 Business_logic_error 3](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-1-ble-3.png)

플래그는 비싸서 구매할 수 없음

## 풀이

![12.1 Business_logic_error 4](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-1-ble-4.png)

개발자 도구에서 보면 `type`이 `number`로 되어있는데 이걸 `text`로바꿈

![12.1 Business_logic_error 5](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-1-ble-5.png)

그럼 플래그를 -1개 사서 돈을 얻을 수 있음

![12.1 Business_logic_error 6](/assets/images/writeup/web-hacking/knock-on/knock-on-challenge-12-1-ble-6.png)

얻은 돈으로 정직하게 `flex`

## 페이로드

```sh
type = "text"
```

### FLAG

```bash
K0{business_logic_error_is_very_very_Common!}
```
