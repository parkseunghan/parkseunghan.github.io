---
title: "KnockOn Bootcamp 2nd - 2주차 MySQL 실습"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - MySQL
last_modified_at: 2024-08-10T19:54:00+09:00
published: true
---
## MySQL 명령어 옵션 (Ubuntu)

**`-u, --user=USERNAME`**: MySQL에 접속할 사용자 이름 지정

**`-p, --password[=PASSWORD]`**: MySQL 사용자 암호 입력. 암호를 바로 입력하지 않으면, 프롬프트에서 암호를 입력하도록 요구

**`-h, --host=HOSTNAME`**: MySQL 서버의 호스트 이름 또는 IP 주소 지정 (기본값: localhost)

**`-P, --port=PORT`**: MySQL 서버에 연결할 포트 지정 (기본 포트: 3306)

**`-D, --database=DB_NAME`**: 연결 시 기본으로 사용할 데이터베이스 지정

**`-e, --execute=STATEMENT`**: MySQL에 접속하지 않고 SQL 명령문을 직접 실행

**`-s, --silent`**: 출력 포맷을 간단하게 설정. 결과만 출력되며, 표준 헤더와 패키지는 생략됨

**`-N, --skip-column-names`**: 쿼리 결과에서 열 이름을 생략

**`--ssl`**: SSL을 사용하여 MySQL 서버에 연결

**`--default-character-set=CHARSET`**: 연결 시 사용할 기본 문자 집합을 지정

**`--verbose`**: 실행 중의 정보를 자세히 출력

**`--help`**: MySQL 명령어의 도움말 출력

**`--version`**: MySQL 클라이언트의 버전 출력

```sh
# MySQL 서버에 접속
mysql -u root -p

# 특정 DB에 접속
mysql -u root -p -D my_database

# SQL 명령문 실행 및 종료
mysql -u root -p -e "SHOW DATABASES;"

# 원격 MySQL 서버에 접속
mysql -u username -p -h 192.168.149.137

```

## Mysql 로컬 환경에서 설치 후 실습하기

## 설치

```sh
sudo apt update

# MySQL 설치
sudo apt install mysql-server

# 보안 설정
sudo mysql_secure_installation

# MySQL 접속
sudo mysql -u root -p
```

> -u 사용자 이름: root, -p 비밀번호: (없음)

![MySQL 접속 성공](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-01.png)

- MySQL 접속 성공 !

## 실습 1

```sql
-- MySQL의 기본 구조와 데이터베이스 생성 예시

-- example 이라는 이름의 데이터베이스 생성
CREATE DATABASE example;

-- example 데이터베이스를 사용하도록 설정
USE example;

-- users라는 이름의 테이블 생성
-- id, username, email 필드
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL
);
```

![DB 생성 전](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-02.png)

- SHOW DATABASES 명령어로 확인한 데이터베이스를 생성하기 전 모습. 기본적으로 4개의 데이터베이스가 있음

![DB 생성 후](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-03.png)

- example 데이터베이스 생성

- 만약 USE 명령어로 DB를 사용하도록 설정을 하지 않았다면 테이블을 생성할 때 에러가 발생함

![테이블 생성](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-04.png)

- USE 명령어 사용 후 테이블 생성 후, SHOW TABLES 명령어로 테이블이 잘 생성된걸 확인

## 실습 2

```sql
-- 데이터 조작 및 관리를 위한 기본적인 SQL 쿼리문

-- 데이터 삽입
-- 새로운 레코드 삽입
INSERT INTO users (username, email) VALUES ('user1', 'user1@example.com');

-- 데이터 조회
-- users 데이블의 모든 데이터 조회
SELECT * FROM users;

-- 데이터 업데이트
-- id가 1인 레코드의 email 값을 업데이트
UPDATE users SET email = 'newemail@example.com' WHERE id = 1;

-- 데이터 삭제
-- id가 1인 레코드 삭제
DELETE FROM users WHERE id = 1;
```

![레코드 삽입 및 데이터 조회](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-05.png)

- 레코드 삽입 전 데이터를 조회하면 비어있는 걸 확인할 수 있음

- 레코드를 삽입하고 데이터를 조회하면 삽입한 데이터가 잘 나옴

![데이터 업데이트 및 삭제](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-06.png)

- id가 1인 레코드의 email 값을 변경하고, 삭제함

## 실습 3

```sql
-- 데이터베이스 관리

-- newuser라는 사용자 생성 후 비밀번호를 password123으로 설정
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password123';

-- newuser에게 example_db에 대한 모든 권한 부여
GRANT ALL PRIVILEGES ON example.* TO 'newuser'@'localhost';
```

![유저 생성 확인](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-07.png)

- 유저 생성 후, mysql DB에서 mysql.user의 user와 host를 확인하면 방금 생성했던 newuser@localhost가 있음

![권한 부여 전후](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-08.png)

- 권한 부여 전에는 (GRANT USAGE) 아무런 권한이 없었음

- 권한 부여 후 (ALL PRIVILEGES) 모든 권한을 갖게됨

## 실습 4

```sh
# 데이터베이스 백업
# example_db 를 백업하여 example_db_backup.sql 파일로 저장
sudo mysqldump -u username -p example_db > example_db_backup.sql

# 데이터베이스 복원
# example_db_backup.sql 파일을 사용하여 example_db 를 복원
sudo mysql -u username -p example_db < example_db_backup.sql
```

![백업 및 복권](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-09.png)

- mysqldump와 mysql 명령어를 통해 백업 및 복원할 수 있음

## JOIN을 사용하여 여러 테이블 간 관계 설정하기

```sql
-- 테이블 생성

-- 고객 테이블: id, name, email
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- 주문 테이블: id, customer_id, order_date, amount
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- 샘플 데이터 삽입
INSERT INTO customers (name, email) VALUES ('Park', 'Park@example.com');
INSERT INTO customers (name, email) VALUES ('Lee', 'Lee@example.com');
INSERT INTO customers (name, email) VALUES ('Kim', 'Kim@example.com');
INSERT INTO customers (name, email) VALUES ('Choi', 'Choi@example.com');

INSERT INTO orders (customer_id, order_date, amount) VALUES (1, '2024-08-10', 10.5);
INSERT INTO orders (customer_id, order_date, amount) VALUES (2, '2024-08-11', 20.1);
INSERT INTO orders (customer_id, order_date, amount) VALUES (1, '2024-08-12', 400);
INSERT INTO orders (customer_id, order_date, amount) VALUES (3, '2024-08-14', 50);
```

## INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN

### INNER JOIN

두 테이블 간에 일치하는 행만 반환

```sql
-- 고객과 해당 고객들의 주문 내역을 조회
SELECT customers.name, customers.email, orders.order_date, orders.amount
FROM customers
INNER JOIN orders ON customers.id = orders.customer_id;

-- 이렇게 써도 됨
SELECT customers.name, customers.email, orders.order_date, orders.amount
FROM orders
INNER JOIN customers ON customers.id = orders.customer_id;
```

![INNER JOIN 결과](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-10.png)

- INNER JOIN 결과

- customers.id와 orders.customer_id가 일치하는 행만 반환됨

### LEFT JOIN (LEFT OUTER JOIN)

왼쪽 테이블의 모든 행을 반환하고, 오른쪽 테이블에 일치하는 행이 있으면 함께 반환

일치하지 않는 오른쪽 테이블의 값은 NULL로 표시

```sql
SELECT ~
FROM 왼쪽테이블
LEFT JOIN 오른쪽테이블 ON ~ = ~;

-- 모든 고객 정보를 보여주고, 주문이 없는 고객도 함께 표시
SELECT customers.name, customers.email, orders.order_date, orders.amount
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id;
```

![LEFT JOIN 결과](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-11.png)

- LEFT JOIN 결과

- (customers의 모든 행) + (orders테이블에서 customers.id와 orders.customer_id가 일치하는 행) 반환

- orders에 일치하는 데이터가 없는 'Choi'의 orders 컬럼들은 NULL로 채워짐

### RIGHT JOIN (RIGHT OUTER JOIN)

오른쪽 테이블의 모든 행을 반환하고, 왼쪽 테이블에 일치하는 행이 있으면 함께 반환

일치하지 않는 왼쪽 테이블의 값은 NULL로 표시

```sql
SELECT ~
FROM 오른쪽테이블
LEFT JOIN 왼쪽테이블 ON ~ = ~;

-- 모든 고객 정보를 보여주고, 주문이 없는 고객도 함께 표시
SELECT customers.name, customers.email, orders.order_date, orders.amount
FROM customers
RIGHT JOIN orders ON customers.id = orders.customer_id;
```

![RIGHT JOIN 결과](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-12.png)

- RIGHT JOIN 결과

- (orders의 모든 행) + (customers테이블에서 orders의 id와 customers의 id가 일치하는 행) 반환

- customers에서 일치하는 데이터가 없는 컬럼들은 NULL로 채워짐

- 현재 샘플 데이터의 외래 키 제약 조건에 의해 orders.customer_id는 반드시 customer.id 값 중 하나와 일치해야 하기 때문에 NULL 값을 발생할 데이터를 추가할 수 없음

### FULL JOIN (FULL OUTER JOIN)

두 테이블의 모든 행을 반환

어느 한쪽 테이블에만 일치하는 데이터가 있으면 NULL로 표시

```sql
SELECT customers.name, customers.email, orders.order_date, orders.amount
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id

UNION

SELECT customers.name, customers.email, orders.order_date, orders.amount
FROM customers
RIGHT JOIN orders ON customers.id = orders.customer_id;
```

![FULL JOIN 결과](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-mysql-challenge-13.png)

- FULL JOIN 결과

- 두 테이블의 모든 행을 반환하였음

- LEFT JOIN과 마찬가지로 'Choi'는 orders에서 일치하는 데이터가 없어 orders 컬럼들은 NULL로 채워짐

## 데이터베이스 접근 제한, 사용자 권한 설정하기

## 사용자 권한 명령어 (GRANT, REVOKE, SHOW GRANTS, FLUSH PRIVILEGES)

### GRANT: 권한 부여

```sql
GRANT privilege_type ON database_name.table_name TO 'username'@'host';

-- 예시
GRANT SELECT, INSERT ON example.users TO 'newuser'@'localhost';
```

> newuser에게 example 데이터베이스의 users 테이블에 대한 SELECT, INSERT 권한을 부여

**`privilege_type`**: 부여할 권한 유형

`ALL PRIVILEGES`: 모든 권한 부여

`SELECT`: 테이블에서 데이터를 조회할 수 있는 권한

`INSERT`: 테이블에 데이터를 삽입할 수 있는 권한

`UPDATE`: 테이블의 데이터를 수정할 수 있는 권한

`DELETE`: 테이블에서 데이터를 삭제할 수 있는 권한

`CREATE`: 데이터베이스나 테이블을 생성할 수 있는 권한

`DROP`: 데이터베이스나 테이블을 삭제할 수 있는 권한

`INDEX`: 인덱스를 생성 및 삭제할 수 있는 권한

`ALTER`: 테이블 구조를 변경할 수 있는 권한

`GRANT OPTION`: 사용자에게 권한을 부여할 수 있는 권한

**`database_name.table_name`**: 권한이 적용될 데이터베이스와 테이블

```sql
-- database_name.*: database_name 데이터베이스의 모든 테이블
GRANT privilege_type ON database_name.* TO 'username'@'host';

-- *.*: 모든 데이터베이스와 테이블
GRANT privilege_type ON *.* TO 'username'@'host';
```

**`username@host`**: 권한을 부여할 사용자와 호스트

### REVOKE: 권한 제거

```sql
REVOKE privilege_type ON database_name.table_name FROM 'username'@'host';

-- 예시
REVOKE INSERT ON example.users FROM 'newuser'@'localhost';
```

> newuser로부터 example 데이터베이스의 users 테이블에 대한 INSERT 권한을 제거

### SHOW GRANTS: 권한 확인

```sql
SHOW GRANTS FOR 'username'@'host';

-- 예시
SHOW GRANTS FOR 'newuser'@'localhost';
```

> newuser 사용자가 가지고 있는 모든 권한을 표시

### FLUSH PRIVILEGES: 권한 테이블 변경 사항 적용 (새로고침)

GRANT, REVOKE 명령어 사용 시 자동으로 권한이 적용됨

일반적으로 수동으로 사용할 필요는 없음

```sql
FLUSH PRIVILEGES;
```

## 사용자 및 권한 관리 명령어

### 사용자 생성

```sql
CREATE USER 'username'@'host' IDENTIFIED BY 'password';

-- 예시
CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'testpass';
```

> localhost에서만 접속 가능한 testuser라는 사용자를 생성하고, 비밀번호를 testpass로 설정

### 사용자 삭제

```sql
DROP USER 'username'@'host';

-- 예시
DROP USER 'testuser'@'localhost';
```

> testuser 사용자를 삭제

### 사용자 비밀번호 변경

```sql
ALTER USER 'username'@'host' IDENTIFIED BY 'newpassword';

-- 예시
ALTER USER 'testuser'@'localhost' IDENTIFIED BY 'newtestpass';
```

> testuser 사용자의 비밀번호를 newtestpass로 변경

### 정리

```sql
-- 1. 사용자 생성
CREATE USER 'exampleuser'@'localhost' IDENTIFIED BY 'securepassword';

-- 2. 데이터베이스에 대한 모든 권한 부여
GRANT ALL PRIVILEGES ON example.* TO 'exampleuser'@'localhost';

-- 3. 권한 적용
FLUSH PRIVILEGES;

-- 4. 사용자의 권한 확인
SHOW GRANTS FOR 'exampleuser'@'localhost';

-- 5. 특정 권한 철회
REVOKE DELETE ON example.* FROM 'exampleuser'@'localhost';

-- 6. 삭제된 권한을 확인
SHOW GRANTS FOR 'exampleuser'@'localhost';
```

