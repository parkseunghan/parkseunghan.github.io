---
title: "웹보안 및 모의해킹 Lab - IDOR와 요청 변조로 접근 통제 우회 확인하기"
date: 2026-04-08T14:30:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - Authorization
  - IDOR
  - Cookie Tampering
  - Header-Based Access Control
  - Method Override
  - Referer Spoofing
last_modified_at: 2026-04-17T18:46:18+09:00
published: true
---

## 도구

**요청 분석**  
`Burp Suite` `HTTP History` `Repeater`

**값 복원과 재구성**  
`Burp Decoder` `Base64` `DevTools`

## 개요

접근 통제는 로그인 여부만으로 끝나지 않음  
실제로 중요한 기준은 `누가`, `어떤 객체에`, `어떤 방식으로` 접근하는가임  
같은 기능처럼 보여도 서버가 `id`, `role`, `Header`, `Referer` 같은 값을 어떻게 해석하는지에 따라 결과가 달라짐

다음 내용을 다룸

- 객체 단위 인가 검증이 빠진 경우
- 조작 가능한 요청값을 신뢰해 우회가 가능한 경우

서버가 무엇을 믿고 권한을 판단하는지가 중요

## 접근 통제 점검 시 확인할 값

- `id`, `user_id`, `note_id`, `order_id`, `ticket_id`처럼 객체를 직접 가리키는 값
- `role`, `uid`처럼 권한을 해석하는 값
- `X-Forwarded-For`, `Referer`, `X-HTTP-Method-Override`처럼 클라이언트가 바꿀 수 있는 값
- `Base64`처럼 보호 기능 없이 읽기만 어렵게 만든 값
- 목록 화면과 상세 조회 API가 분리되어 있는 구조

이 값들이 요청에 직접 드러나면 서버가 어떤 기준으로 접근을 허용하는지 역으로 좁혀 보기 쉬워짐

## 1. 객체 단위 인가 결함

### 게시글 조회

목록에는 보이지 않는 게시글이어도 상세 조회 요청이 `id` 하나만으로 동작하면 접근 가능성부터 확인

```http
GET /vuln/auth/lab1.php?action=view&id=4 HTTP/1.1
Host: <TARGET_HOST>
Cookie: PHPSESSID=<SESSION_ID>
```

이 요청 뒤에는 아래 값 확인

- `title`
- `author`
- `content`
- 숨김 여부를 나타내는 필드 존재 여부

응답에 `hidden`, `private` 같은 표시가 있어도 본문이 그대로 내려오면 보호가 아니라 단순 표시로 해석 가능
`목록에서 감춰짐`과 `서버에서 차단됨`은 다름

### 사용자 프로필 조회

프로필 조회 기능은 사용자 전용 기능처럼 보이지만, `user_id=<숫자>` 형태로 동작하면 객체 소유권부터 검증

```http
GET /vuln/auth/lab2.php?action=get_profile&user_id=1 HTTP/1.1
Host: <TARGET_HOST>
Cookie: PHPSESSID=<SESSION_ID>
```

응답에서는 아래 항목 확인

- `username`
- `email`
- `role`
- `department`
- 메모나 내부 설명 필드

여기서 중요한 기준은 정보의 민감도보다 `내 계정이 아닌 객체가 같은 구조로 열리는가`임  
즉 다른 `user_id`로 바꿨을 때 동일 형식 응답이 오면 인가 검증 누락으로 판단 가능함

### 개인 메모 조회

개인 메모나 비공개 노트는 `is_private` 같은 필드로 구분됨
하지만 상세 조회가 `note_id` 하나로 열리면 그 값은 접근 제어와 무관한 표시값

```http
GET /vuln/auth/lab3.php?action=get_note&note_id=1 HTTP/1.1
Host: <TARGET_HOST>
Cookie: PHPSESSID=<SESSION_ID>
```

응답에서는 아래 값을 확인

- `user_id`
- `is_private`
- `title`
- `content`

응답 안에 `private=true`가 보이면서도 본문이 그대로 내려오면 서버가 보호를 수행하지 않는 구조

### 주문 내역과 문의 티켓

주문 내역과 문의 티켓은 대표적인 사용자 귀속 데이터
그런데 상세 조회가 `order_id`, `ticket_id`만으로 동작하면 같은 방식으로 확인 가능함

```http
GET /vuln/auth/lab4.php?action=view&order_id=1 HTTP/1.1
GET /vuln/auth/lab18.php?action=view&ticket_id=1 HTTP/1.1
```

응답에서는 아래 값을 확인
- `user_id`
- `status`
- `subject`
- 배송지, 결제정보, 내부 메모 같은 부가 필드

이 구조에서 가장 중요한 점은 `객체 소유자 확인 절차가 서버에서 수행되는가`임  
숫자 키 하나만 바꿨을 때 다른 사용자의 데이터가 열리면 전형적인 `IDOR`로 해석 가능함

## 2. 요청 변조 기반 우회

### Header 기반 우회

내부 시스템 접근 여부를 요청 헤더의 IP 값으로 판단하는 경우 `X-Forwarded-For`는 가장 먼저 확인할 후보가 됨

원본 요청은 아래처럼 단순함

```http
GET /vuln/auth/lab15.php?action=internal_api HTTP/1.1
Host: <TARGET_HOST>
Cookie: PHPSESSID=<SESSION_ID>
```

변조 요청은 아래처럼 구성 가능함

```http
GET /vuln/auth/lab15.php?action=internal_api HTTP/1.1
Host: <TARGET_HOST>
Cookie: PHPSESSID=<SESSION_ID>
X-Forwarded-For: 127.0.0.1
```

응답에서는 아래 값을 먼저 봄

- `your_ip`
- `success`
- `system_info`
- 내부 전용 응답 필드 존재 여부

실제 접속 IP가 아니라 서버가 어떤 값을 최종적으로 신뢰했는가가 중요
응답의 `your_ip`가 `127.0.0.1`처럼 바뀌면 헤더 신뢰 문제로 이어짐

### Base64 사용자 컨텍스트 쿠키

권한 정보가 쿠키에 직접 들어 있으면 먼저 `인코딩인가`, `보호값인가`를 구분하게 됨  
`Base64`는 보호 기능은 없음

원본 값 예시는 아래와 같음

```text
uc_ctx=eyJ1aWQiOjI1LCJyb2xlIjoidXNlciJ9
```

디코딩 결과는 아래처럼 해석 가능함

```json
{"uid":25,"role":"user"}
```

이 구조에서는 아래 순서로 보게 됨

1. 값이 읽히는지 확인
2. `uid`, `role` 같은 권한 관련 필드가 있는지 확인
3. 값을 수정하고 다시 인코딩
4. 서버가 무결성 검증 없이 이를 그대로 신뢰하는지 확인

조작 예시

```json
{"uid":25,"role":"admin"}
```

핵심: `읽을 수 있으면 바꿀 수도 있음`
서명이 없거나 무결성 검증이 없으면 `role=user`를 `role=admin`으로 바꾼 값이 그대로 권한 판단 기준이 될 수 있음

### Method Override

HTTP 메서드 제한은 클라이언트가 보낸 메서드보다 서버가 최종적으로 해석한 메서드가 중요
이때 `X-HTTP-Method-Override` 같은 헤더를 신뢰하는 구조가 우회 지점

원본 요청

```http
POST /vuln/auth/lab17.php?action=admin_dump HTTP/1.1
Host: <TARGET_HOST>
Cookie: PHPSESSID=<SESSION_ID>; uc_ctx=<ADMIN_CONTEXT>
```

변조 요청

```http
POST /vuln/auth/lab17.php?action=admin_dump HTTP/1.1
Host: <TARGET_HOST>
Cookie: PHPSESSID=<SESSION_ID>; uc_ctx=<ADMIN_CONTEXT>
X-HTTP-Method-Override: GET
```

응답에서는 아래 항목을 확인

- `success`
- `dump`
- `message`
- 요청 처리 방식 차이를 드러내는 문구

즉 프론트는 POST만 보내더라도 서버가 override 헤더를 신뢰하면 내부적으로 GET처럼 처리할 수 있음  
메서드 제한이 실제 보호가 아닐 경우 가능한 패턴


### Referer 기반 접근 통제

`Referer`는 요청이 어디서 왔는지에 대한 참고값. 인증 수단이 아님 
하지만 내부 페이지에서 들어온 요청만 허용하는 식으로 쓰이면, 바로 조작 대상

원본 요청

```http
GET /vuln/auth/lab19.php?action=internal_report HTTP/1.1
Host: <TARGET_HOST>
Referer: http://<TARGET_HOST>/vuln/auth/lab19.php
```

변조 요청

```http
GET /vuln/auth/lab19.php?action=internal_report HTTP/1.1
Host: <TARGET_HOST>
Referer: http://<TARGET_HOST>/internal/
```

응답에서는 아래 값을 먼저 확인함

- `success`
- `classification`
- `report_id`
- 내부 문서 식별자나 토큰 값

핵심: 사용자 세션보다 `어디서 왔는가`라는 쉽게 조작 가능한 문맥을 더 신뢰
이 경우 보호는 세션 기반 권한 검사가 아니라 문자열 비교 수준에 머무름

## 3. 반복적으로 확인한 흐름

접근 통제 검증은 복잡한 익스플로잇보다 아래 순서가 더 중요

1. 목록과 상세 조회 API를 분리해서 봄
2. 상세 요청의 객체 식별값을 먼저 바꿔봄
3. 응답에서 `user_id`, `role`, `is_private`, `classification` 같은 보호 관련 필드를 먼저 읽음
4. `Header`, `Cookie`, `Method`, `Referer`를 하나씩 바꿔봄
5. 응답의 `success`, `your_ip`, `token`, `system_info` 같은 차이를 기준으로 우회 여부를 판단함

즉 우회의 핵심: `서버가 무엇을 잘못 신뢰하는가`를 좁혀 가는 과정

## 정리

접근 통제 검증에서 반복적으로 보인 내용

- 화면에서 숨겨졌다고 보호되는 것 아님
- 숫자 키 하나로 객체를 조회하면 소유권 검증부터 의심
- `Header`, `Cookie`, `Referer`, `Method Override`는 모두 조작 가능한 입력값
- 권한 판단은 요청 안의 값이 아니라 서버 내부 상태를 기준으로 해야 함

즉 인증/인가 우회는 복잡한 공격기법보다 서버가 잘못 신뢰한 기준값 하나에서 시작되는 경우가 많음

