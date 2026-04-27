---
title: "시큐리티아카데미 7기 정리 - 리눅스 심화 2. 파일시스템, 서비스, 네트워크 관찰"
date: 2026-03-09T18:10:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Linux
  - Filesystem
  - Systemd
  - Network
permalink: /security-academy/linux-filesystem-service-and-network/
last_modified_at: 2026-03-30T20:20:00+09:00
published: true
---
## 개요

리눅스의 파일시스템, 서비스, 네트워크 관찰 방법을 한 번에 묶어 다루는 내용

디스크와 네트워크를 둘 다 `커널이 추상화한 I/O` 관점에서 보는 것이 핵심임

## 용어 정리

- `VFS(Virtual File System)`: 여러 파일시스템을 공통 인터페이스로 다루는 계층
- `Superblock`: 파일시스템 기본 메타데이터 영역
- `Inode`: 파일의 속성과 위치 정보를 담는 메타데이터 구조
- `Block Device`: 블록 단위로 읽고 쓰는 장치
- `Character Device`: 문자 스트림 단위로 입출력하는 장치
- `Daemon`: 백그라운드에서 지속적으로 동작하는 서비스 프로세스
- `tmpfs`: 메모리를 파일시스템처럼 사용하는 방식

## 파일시스템과 디스크 관점

리눅스에서는 사용자가 파일처럼 접근하더라도, 내부에서는 VFS와 실제 파일시스템이 블록 장치를 해석해 주는 구조로 동작함

`ext4`, `xfs`, `f2fs`, `fat32`, `ntfs` 같은 포맷은 결국 디스크 블록을 어떤 규칙으로 배치하고 읽고 쓸지 정한 정책 차이에 해당함

중요했던 포인트는 다음과 같음

- 슈퍼블록은 파일시스템 전체 정보를 담음
- 아이노드는 파일 메타데이터를 담음
- 데이터 블록은 실제 내용을 담음

이 구분을 이해해야 포맷, 마운트, 손상 분석 같은 주제를 이어서 볼 수 있음

## 관찰 명령어

### `df -h /`

루트 파일시스템의 전체 용량과 사용량을 보는 가장 기본적인 명령어

```shell
df -h /
```

- `df`: 디스크 사용량 요약 출력
- `-h`: `K`, `M`, `G` 단위로 보기 쉽게 변환
- `/`: 루트 파일시스템만 대상으로 지정

전체 마운트 목록을 한 번에 보기 전에 가장 먼저 `/`부터 확인하면 현재 시스템의 기본 저장소 상태를 빠르게 파악 가능

### `df -Th /`

용량뿐 아니라 파일시스템 타입까지 같이 확인하는 명령어

```shell
df -Th /
```

- `-T`: 파일시스템 타입 출력
- `-h`: 사람이 읽기 쉬운 단위 유지

`ext4`, `xfs`, `tmpfs` 같은 값이 같이 보이면 "어떤 경로가 어떤 저장 구조 위에 올라가 있는가"를 같이 읽을 수 있음

### `df -h /run`

`/run` 경로가 실제로 어떤 성격의 공간인지 확인하는 명령어

```shell
df -h /run
```

- `/run`: 런타임 상태 파일이 올라가는 경로

`/run`은 디스크처럼 보이더라도 실제로는 메모리 기반 파일시스템인 경우가 많음

### `systemctl list-units --type=service --state=running`

현재 실제로 동작 중인 서비스만 골라보는 명령어

```shell
systemctl list-units --type=service --state=running
```

- `systemctl`: systemd 관리 명령
- `list-units`: 현재 로드된 unit 목록 출력
- `--type=service`: service 타입만 필터링
- `--state=running`: 실행 중 상태만 표시

운영 상태 확인 기준: `list-units`

### `netstat -tpaln`

열린 TCP 포트와 프로세스 매핑을 빠르게 보는 전통적인 방식

```shell
netstat -tpaln
```

- `netstat`: 네트워크 상태 출력
- `-t`: TCP 소켓만 출력
- `-p`: 프로세스 정보 표시
- `-a`: 전체 소켓 표시
- `-l`: LISTEN 상태 중심 확인
- `-n`: 이름 해석 없이 숫자로 출력

서비스가 실제로 외부에서 접근 가능한 상태인지 판단할 때 가장 직접적인 단서가 됨

### `ss -tplan`

`netstat`보다 현대적인 대체 명령으로, 같은 목적을 더 빠르게 처리하는 경우가 많음

```shell
ss -tplan
```

- `ss`: 소켓 상태 확인
- `-t`: TCP만 표시
- `-p`: 프로세스 정보 포함
- `-l`: LISTEN 상태 중심
- `-a`: 전체 소켓 포함
- `-n`: 숫자 형식 출력

실무에서는 `ss`가 기본인 환경도 많아서 `netstat`과 함께 읽을 수 있어야 함

## 네트워크 관찰

### `sudo dnf install -y traceroute`

실습 도구를 먼저 설치하는 단계

```shell
sudo dnf install -y traceroute
```

- `sudo`: 관리자 권한 사용
- `dnf`: Red Hat 계열 패키지 관리자
- `install`: 패키지 설치
- `-y`: 중간 확인 질문 자동 승인
- `traceroute`: 설치할 패키지 이름

진단 명령 자체가 기본 설치가 아닐 수 있으므로, 도구 설치부터 환경 차이로 보는 습관이 필요함

### `traceroute -n www.google.com`

목적지까지 거치는 홉을 확인하는 명령어

```shell
traceroute -n www.google.com
```

- `traceroute`: 경유 라우터 추적
- `-n`: 호스트 이름 역조회 없이 숫자 IP만 출력

`-n`을 붙이면 DNS 역조회 때문에 느려지지 않아서 라우팅 경로 자체에 집중하기 쉬움

### `ping www.google.com`

가장 기초적인 연결 확인 명령어

```shell
ping www.google.com
```

- `ping`: ICMP Echo Request 전송

연결 확인: `ping`, 경로 확인: `traceroute`

## 서비스 기동 실습

`Spring` 애플리케이션과 `httpd`를 각각 올려 보면서 포트 기반으로 서비스 성격을 구분함

- `8080`: 주로 WAS나 애플리케이션 서버에서 자주 확인
- `80`: 전통적인 웹 서버 포트

### `mkdir spring_test && cd spring_test`

실습 디렉터리를 먼저 분리하는 단계

```shell
mkdir spring_test && cd spring_test
```

- `mkdir`: 디렉터리 생성
- `spring_test`: 생성할 디렉터리 이름
- `&&`: 앞 명령이 성공했을 때만 다음 명령 실행
- `cd spring_test`: 생성한 디렉터리로 이동

권장 습관: 시작 디렉터리 분리

### `sudo dnf install -y java-latest-openjdk maven`

Spring 프로젝트를 빌드하기 위한 런타임과 빌드 도구를 설치하는 단계

```shell
sudo dnf install -y java-latest-openjdk maven
```

- `java-latest-openjdk`: 자바 런타임/개발 도구
- `maven`: 자바 프로젝트 빌드 도구

### `git clone -b 1.5.x https://github.com/spring-projects/spring-petclinic.git`

예제 프로젝트를 특정 브랜치로 내려받는 단계

```shell
git clone -b 1.5.x https://github.com/spring-projects/spring-petclinic.git
```

- `git clone`: 저장소 복제
- `-b 1.5.x`: 체크아웃할 브랜치 지정

브랜치를 명시해두면 실습 중 문서와 코드 버전이 달라지는 문제를 줄일 수 있음

### `./mvnw package`

프로젝트를 실제로 빌드하는 명령어

```shell
./mvnw package
```

- `./mvnw`: 프로젝트에 포함된 Maven Wrapper 실행 파일
- `package`: 컴파일과 테스트를 거쳐 배포 가능한 산출물 생성

### `file target/spring-petclinic-1.5.1.jar`

빌드 산출물이 어떤 형식인지 확인하는 명령어

```shell
file target/spring-petclinic-1.5.1.jar
```

- `file`: 파일 형식 식별

JAR가 실제 자바 아카이브로 만들어졌는지, 손상 없이 생성됐는지 확인하는 용도로 자주 씀

### `java -jar target/spring-petclinic-1.5.1.jar`

빌드한 애플리케이션을 직접 실행하는 단계

```shell
java -jar target/spring-petclinic-1.5.1.jar
```

- `java`: 자바 실행기
- `-jar`: 실행 대상이 JAR 파일임을 지정

### `sudo dnf install -y httpd`

전통적인 웹 서버를 별도로 올려 보기 위한 설치 단계

```shell
sudo dnf install -y httpd
```

- `httpd`: Apache HTTP Server 패키지

### `sudo service httpd status`

서비스가 실제로 떠 있는지 확인하는 단계

```shell
sudo service httpd status
```

- `service`: SysV 스타일 서비스 제어 명령
- `httpd`: 대상 서비스명
- `status`: 현재 상태 확인

애플리케이션이 떴더라도, 실제 외부에서 접근 가능한지는 결국 `포트가 열렸는지`, `방화벽이 허용하는지`, `프로세스가 정상 LISTEN 상태인지`까지 확인해야 판단 가능함

## 정리

리눅스 운영 관점에서는 파일시스템, 서비스, 네트워크를 따로 보지 않고 모두 `자원 관찰` 문제로 보는 편이 효율적임

파일시스템은 저장 구조를, 서비스는 실행 상태를, 네트워크는 노출 범위를 설명해 주는 축임




