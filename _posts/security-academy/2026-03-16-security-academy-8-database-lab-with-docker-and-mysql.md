---
title: "시큐리티아카데미 7기 정리 - 데이터베이스 2. Docker와 MySQL 실습 구성"
date: 2026-03-16T18:10:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Database
  - MySQL
  - Docker
permalink: /security-academy/database-lab-with-docker-and-mysql/
last_modified_at: 2026-03-30T20:50:00+09:00
published: true
---
## 개요

Docker 위에 Apache, PHP, MySQL 환경을 올리고, 컨테이너 안에서 DB를 직접 구성하는 실습 흐름을 다루는 내용

핵심은 `호스트 준비 -> Docker 설치 -> 이미지 다운로드 -> 컨테이너 실행 -> 컨테이너 내부 진입 -> MySQL 구성` 순서다

## 용어 정리

- `Container`: 격리된 실행 환경
- `Image`: 컨테이너 생성용 템플릿
- `Port Mapping`: 호스트 포트와 컨테이너 포트를 연결하는 설정
- `Volume Mount`: 호스트 경로를 컨테이너 경로에 연결하는 방식
- `MySQL Client`: DB 서버에 접속하는 클라이언트 도구
- `MySQL Server`: 실제 DB 엔진

## Docker 설치 흐름

### `sudo apt update`

패키지 목록을 먼저 최신 상태로 갱신하는 단계

```shell
sudo apt update
```

- `apt`: Debian/Ubuntu 계열 패키지 관리자
- `update`: 패키지 목록 갱신

### `sudo apt upgrade -y`

이미 설치된 패키지를 한 번 최신 상태로 맞추는 단계

```shell
sudo apt upgrade -y
```

- `upgrade`: 설치된 패키지 업그레이드
- `-y`: 중간 확인 질문 자동 승인

### `sudo apt install -y ca-certificates curl gnupg`

Docker 저장소와 키를 추가하기 전 필요한 기본 도구를 설치하는 단계

```shell
sudo apt install -y ca-certificates curl gnupg
```

- `ca-certificates`: HTTPS 인증서 검증용 패키지
- `curl`: 파일 다운로드 도구
- `gnupg`: GPG 키 처리 도구

### `sudo install -m 0755 -d /etc/apt/keyrings`

키 저장 디렉터리를 만들고 권한까지 맞추는 단계

```shell
sudo install -m 0755 -d /etc/apt/keyrings
```

- `install`: 파일 복사/생성과 권한 설정을 함께 처리하는 명령
- `-m 0755`: 권한 지정
- `-d`: 디렉터리 생성
- `/etc/apt/keyrings`: 키 저장 경로

### `sudo apt-get update`

새 저장소와 키를 추가한 뒤 패키지 목록을 다시 읽어오는 단계

```shell
sudo apt-get update
```

`apt`와 `apt-get`은 목적이 비슷하지만, 저장소 반영 직후 `apt-get update`를 한 번 더 수행하는 방식으로 정리 가능

### `sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`

Docker 엔진과 관련 도구를 실제로 설치하는 단계

```shell
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- `docker-ce`: Docker 엔진
- `docker-ce-cli`: Docker CLI
- `containerd.io`: 컨테이너 런타임
- `docker-buildx-plugin`: 빌드 기능 확장
- `docker-compose-plugin`: Compose 기능 제공

### `sudo systemctl enable --now docker`

Docker 서비스를 등록하고 바로 시작하는 단계

```shell
sudo systemctl enable --now docker
```

- `systemctl`: systemd 관리 명령
- `enable`: 부팅 시 자동 시작 등록
- `--now`: 등록과 동시에 지금 바로 시작

### `docker --version`

설치가 끝난 뒤 버전 확인으로 실행 가능 여부를 점검하는 단계

```shell
docker --version
```

## 이미지 다운로드와 컨테이너 실행

### `docker image pull pensiero/apache-php-mysql`

실습에 사용할 통합 이미지를 먼저 내려받는 단계

```shell
docker image pull pensiero/apache-php-mysql
```

- `image pull`: 이미지 다운로드

### `mkdir db`

호스트 쪽 작업 디렉터리를 만드는 단계

```shell
mkdir db
```

### `cd db`

볼륨 마운트에 사용할 작업 디렉터리로 이동하는 단계

```shell
cd db
```

### `docker run --name mysql_server -v /home/ubuntu/db:/var/www/public -d -p 8000:80 pensiero/apache-php-mysql:php7.4`

웹과 DB가 들어 있는 실습용 컨테이너를 실행하는 핵심 명령어

```shell
docker run --name mysql_server -v /home/ubuntu/db:/var/www/public -d -p 8000:80 pensiero/apache-php-mysql:php7.4
```

- `--name mysql_server`: 컨테이너 이름 지정
- `-v /home/ubuntu/db:/var/www/public`: 호스트 경로를 컨테이너 웹 루트에 마운트
- `-d`: 백그라운드 실행
- `-p 8000:80`: 호스트 8000 포트를 컨테이너 80 포트에 연결
- `pensiero/apache-php-mysql:php7.4`: 사용할 이미지와 태그

볼륨 마운트를 해두면 호스트에서 파일을 수정해도 컨테이너 내부 웹 루트에 바로 반영되는 구조가 만들어짐

### `docker ps`

컨테이너가 실제로 올라왔는지 확인하는 단계

```shell
docker ps
```

- `ps`: 실행 중 컨테이너 목록 출력

### `docker exec -it mysql_server /bin/sh`

컨테이너 내부로 직접 들어가는 단계

```shell
docker exec -it mysql_server /bin/sh
```

- `exec`: 실행 중인 컨테이너 안에서 명령 수행
- `-i`: 표준 입력 유지
- `-t`: TTY 할당
- `mysql_server`: 대상 컨테이너 이름
- `/bin/sh`: 실행할 셸

볼륨 마운트를 해두면 웹 파일을 호스트에서 수정해도 컨테이너에 바로 반영되는 구조를 만들 수 있음

## 컨테이너 내부 MySQL 구성

### `apt update`

컨테이너 내부 패키지 목록 갱신 단계

```shell
apt update
```

### `apt install -y mysql-client`

MySQL 서버에 접속할 클라이언트 도구를 설치하는 단계

```shell
apt install -y mysql-client
```

- `mysql-client`: `mysql` 접속 명령을 제공하는 패키지

### `apt install -y mysql-server`

실제 DB 서버 엔진을 설치하는 단계

```shell
apt install -y mysql-server
```

- `mysql-server`: 데이터베이스 엔진 패키지

### `mysql --version`

클라이언트가 정상 설치됐는지 확인하는 단계

```shell
mysql --version
```

### `service mysql restart`

MySQL 서비스를 다시 시작해 설정과 설치 상태를 반영하는 단계

```shell
service mysql restart
```

- `service`: 서비스 제어 명령
- `mysql`: 대상 서비스명
- `restart`: 재시작

### `mysql -uroot -p`

실제로 DB에 접속하는 단계

```shell
mysql -uroot -p
```

- `-u root`: 접속 사용자 지정
- `-p`: 비밀번호 입력 프롬프트 활성화

컨테이너 내부에 클라이언트와 서버를 모두 설치하는 구조는 실습용으로는 편하지만, 운영 환경에서는 서비스 분리가 더 일반적임

## 웹 애플리케이션 연결

`table.php` 같은 파일에서 MySQL 연결을 직접 수행하고, GET 파라미터를 받아 조회하는 흐름을 확인함

이 과정의 핵심 포인트는 두 가지다

- 웹 애플리케이션과 DB가 실제로 연결되는 경로를 직접 확인할 수 있음
- 입력값이 그대로 SQL에 붙으면 위험해진다는 점을 다음 실습으로 연결할 수 있음

## 권한과 인증 방식

```shell
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';
FLUSH PRIVILEGES;
```

접속 편의를 위해 인증 방식을 조정했지만, 운영 환경에서는 빈 비밀번호나 광범위한 root 사용을 피해야 함

이 부분은 실습 편의 설정과 운영 보안 설정을 구분해서 이해해야 함

## 정리

이 실습의 핵심은 Docker를 통해 웹과 DB가 연결된 환경을 빠르게 재현하는 데 있음

이후 SQL 실습이나 입력값 검증 문제를 다룰 때도, 실제 데이터가 어디서 조회되는지 이해한 상태여야 흐름이 보임




