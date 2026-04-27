---
title: "시큐리티아카데미 7기 정리 - 데이터베이스 3. SQL 실습과 입력값 위험"
date: 2026-03-16T18:20:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Database
  - SQL
  - SQL Injection
permalink: /security-academy/database-query-practice-and-risk/
last_modified_at: 2026-03-30T21:40:00+09:00
published: true
---
## 개요

기본 SQL 문법과 입력값 처리 위험을 함께 묶어 다루는 내용

단순 조회 문법을 익히는 데서 끝나는 것이 아니라, 어떤 조건식이 어떻게 결과를 바꾸는지 직접 확인하는 흐름이 중요했음

## 용어 정리

- `SELECT`: 데이터 조회 명령
- `WHERE`: 조건절
- `ORDER BY`: 정렬 기준 지정
- `LIKE`: 패턴 검색
- `NULL`: 값이 비어 있음을 의미하는 상태
- `Predicate`: 참/거짓을 판단하는 조건식

## 기본 조회 문법

`students`, `employees2`, `employees` 같은 샘플 테이블을 이용해 기본 조회 흐름을 확인함

자주 나온 문법은 다음과 같음

- `SELECT * FROM table`
- `WHERE name = 'value'`
- `WHERE salary BETWEEN a AND b`
- `WHERE department IS NULL`
- `ORDER BY name ASC`
- `LIKE 'u%'`

`WHERE` 조건은 단순 필터로 보이지만, 실제로는 데이터 의미를 바꾸는 핵심 구문임

## 조회 예시

### `SELECT * FROM students;`

테이블 전체를 보는 가장 기본적인 조회문임

```sql
SELECT * FROM students;
```

- `SELECT`: 조회할 컬럼 지정
- `*`: 모든 컬럼 선택
- `FROM students`: `students` 테이블에서 조회

### `SELECT * FROM students WHERE name = 'John Kim';`

문자열 일치 조건으로 특정 행만 고르는 예시다

```sql
SELECT * FROM students WHERE name = 'John Kim';
```

- `WHERE`: 조건절 시작
- `=`: 정확히 같은 값 비교

### `SELECT * FROM employees2 WHERE salary >= 2000;`

비교 연산자를 이용한 범위 필터 예시다

```sql
SELECT * FROM employees2 WHERE salary >= 2000;
```

- `>=`: 크거나 같음 비교

### `SELECT * FROM employees2 WHERE salary BETWEEN 6000.00 AND 6200.00;`

숫자 범위를 지정할 때 쓰는 예시다

```sql
SELECT * FROM employees2 WHERE salary BETWEEN 6000.00 AND 6200.00;
```

- `BETWEEN a AND b`: `a` 이상 `b` 이하 범위 비교

### `SELECT * FROM employees2 WHERE department = 'IT' AND salary BETWEEN 5000.00 AND 6000.00;`

조건을 여러 개 결합할 때 쓰는 예시다

```sql
SELECT * FROM employees2 WHERE department = 'IT' AND salary BETWEEN 5000.00 AND 6000.00;
```

- `AND`: 모든 조건을 동시에 만족해야 참

### `SELECT * FROM employees2 WHERE department IS NULL;`

값이 비어 있는 행만 고르는 예시다

```sql
SELECT * FROM employees2 WHERE department IS NULL;
```

- `IS NULL`: NULL 여부 비교

### `SELECT * FROM employees2 ORDER BY name ASC;`

조회 결과를 정렬해서 보는 예시다

```sql
SELECT * FROM employees2 ORDER BY name ASC;
```

- `ORDER BY`: 정렬 기준 지정
- `ASC`: 오름차순

### `SELECT * FROM employees2 WHERE name LIKE 'u%';`

패턴 검색 예시다

```sql
SELECT * FROM employees2 WHERE name LIKE 'u%';
```

- `LIKE`: 와일드카드 패턴 비교
- `'u%'`: `u`로 시작하는 문자열

## mysql 클라이언트 명령어

### `mysql -uroot -p`

MySQL 프롬프트로 들어가는 가장 기본적인 접속 명령어

```shell
mysql -uroot -p
```

- `mysql`: MySQL 클라이언트 실행
- `-u root`: 접속 사용자 지정
- `-p`: 비밀번호 입력 프롬프트 활성화

DB 쉘 명령과 SQL 명령이 섞여 있으므로, 현재 위치가 운영체제 셸인지 MySQL 프롬프트인지 구분하는 습관이 필요함

## 입력값 위험

다음과 같은 조회 코드는 구조상 매우 위험함

```php
$sql = "SELECT id, name, age, class, grade FROM students WHERE name LIKE '%$search_name%'";
```

사용자 입력이 그대로 SQL 문자열 안으로 들어가므로, 작은 따옴표나 연산자를 통해 쿼리 의미가 바뀔 수 있음

`department = 't' or 1` 같은 입력은 바로 이 위험성을 보여주는 예시에 가까움

즉 문제의 본질은 `SQL 구문을 사용자가 닫고 다시 열 수 있게 만든 구조`에 있음

## 안전하게 보는 기준

- 문자열 연결 대신 준비된 문장 사용
- 조회 전 입력값 형식 검증
- 애플리케이션 계정 권한 최소화
- 오류 메시지 직접 노출 금지

조회 문법 연습과 보안 관점을 따로 떼어 보지 않고 함께 보는 것이 중요한 이유가 여기에 있음

## 정리

SQL 실습은 단순 문법 암기보다, 조건식 하나가 결과를 어떻게 바꾸는지 이해하는 연습에 가까움

특히 웹 애플리케이션과 연결되는 순간 입력값 처리 방식이 곧 보안 문제가 됨




