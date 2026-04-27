---
title: "KnockOn Bootcamp 2nd - 3주차 게시판 만들기 0 - LAMP 스택 설치"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - LAMP
  - Board
last_modified_at: 2024-08-20T19:54:00+09:00
published: true
---
## 게시판 세부 명세서

1. 리눅스 환경, Apache 웹 서버, Mysql 데이터베이스, PHP 언어를 사용해야 함

2. 다음 기능이 반드시 구현되어야 함

- 여러 개시물을 리스팅해주는 기능 (메인화면)
- 게시글을 검색하는 기능
- 게시물을 생성, 삭제, 수정하는 기능
- 게시글에 파일을 업로드하는 기능
- 회원가입 로그인 로그아웃(사용자 식별을 쿠키, 세션으로 해결 함)

3. 외부에서 접속이 가능할 것
(클라우드 사용 권장, 로컬일 경우 포트포워딩을 통해 외부로 접속해야함)

## LAMP 스택 설치

## Apache

```sh
sudo apt update

# Apache 설치
sudo apt install apache2
```

> Apache 설치 후 퍼블릭 IP 주소로 접속 하여 확인

## MySQL

```sh
# MySQL 설치
sudo apt install mysql-server

# 보안 설정 진행
sudo mysql_secure_installation
```

```sh
Securing the MySQL server deployment.

Connecting to MySQL using a blank password.

VALIDATE PASSWORD COMPONENT can be used to test passwords
and improve security. It checks the strength of password
and allows the users to set only those passwords which are
secure enough. Would you like to setup VALIDATE PASSWORD component?

Press y|Y for Yes, any other key for No:
```

**`Y`**: 암호 검증 구성 요소 활성화. 암호 길이, 복잡도 검사

이후 강도 낮은 암호 설정 제한

**`N`**: 암호 검증 구성 요소 비활성화

아무 제약 없이 설정 가능

```sh
Skipping password set for root as authentication with auth_socket is used by default.
If you would like to use password authentication instead, this can be done with the "ALTER_USER" command.
See https://dev.mysql.com/doc/refman/8.0/en/alter-user.html#alter-user-password-management for more information.

By default, a MySQL installation has an anonymous user,
allowing anyone to log into MySQL without having to have
a user account created for them. This is intended only for
testing, and to make the installation go a bit smoother.
You should remove them before moving into a production
environment.

Remove anonymous users? (Press y|Y for Yes, any other key for No) :
```

**`비밀번호 인증 사용`**

```sql
-- MySQL 콘솔에 접속
sudo mysql

-- 비밀번호 변경: your_password 부분 변경
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
FLUSH PRIVILEGES;
```

**`Y`**: 익명 사용자 제거

`익명 사용자`: 사용자 인증 없이 MySQL 접근 가능. 보안에 취약

**`N`**: 익명 사용자 그대로 유지

나중에 제거하려면 MySQL 콘솔에서 아래 명령 실행

```sql
DELETE FROM mysql.user WHERE User='';
FLUSH PRIVILEGES;
```

```sh
Normally, root should only be allowed to connect from
'localhost'. This ensures that someone cannot guess at
the root password from the network.

Disallow root login remotely? (Press y|Y for Yes, any other key for No) :
```

**`Y`**: root 사용자가 로컬에서만 로그인 가능하게 설정

서버가 설치된 시스템에서만 root 계정으로 접속 가능, 원격은 차단

**`N`**: root 사용자 원격 접속 허용

```sh
 ... skipping.
By default, MySQL comes with a database named 'test' that
anyone can access. This is also intended only for testing,
and should be removed before moving into a production
environment.

Remove test database and access to it? (Press y|Y for Yes, any other key for No) :
```

**`Y`**: test DB와 그에 대한 접근 권한 제거

**`N`**: test DB 그대로 유지

누구나 접근 가능

```sh
 ... skipping.
Reloading the privilege tables will ensure that all changes
made so far will take effect immediately.

Reload privilege tables now? (Press y|Y for Yes, any other key for No) :
```

**`Y`**: 권한 테이블 즉시 리로드. 변경 사항이 바로 적용됨

**`N`**: 현재 변경 사항이 적용되지 않은 상태로 남음

MySQL 서버를 재시작하거나, 수동으로 권한 테이블을 리로드할 떄까지 변경 사항이 반영되지 않음

## PHP

```sh
sudo apt install php libapache2-mod-php php-mysql
```

```php
# 설치 후, /var/www/html/phpinfo.php 생성
<?php
  phpinfo();
?>
```

> 퍼블릭IP주소/phpinfo.php 경로로 들어가서 php 페이지 잘 뜨는지 확인

