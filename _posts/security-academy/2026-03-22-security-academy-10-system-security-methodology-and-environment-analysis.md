---
title: "시큐리티아카데미 7기 정리 - 시스템보안 1. 진단 방법론과 환경 분석"
date: 2026-03-22T18:00:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - System Security
  - Vulnerability Assessment
  - OS
permalink: /security-academy/system-security-methodology-and-environment-analysis/
last_modified_at: 2026-03-30T21:50:00+09:00
published: true
---
## 개요

취약점 진단과 모의해킹의 차이, 진단 전 준비 사항, 환경 분석 명령어를 한 번에 다루는 내용

진단 중점: 기준, 범위, 증적

## 용어 정리

- `Vulnerability Assessment`: 기준에 따라 취약 여부를 판단하는 점검
- `Penetration Test`: 취약점을 실제 공격 시나리오로 연결해 검증하는 활동
- `Evidence`: 진단 결과를 뒷받침하는 명령 출력, 설정 파일, 화면 증적
- `Port Forwarding`: 외부 포트를 내부 서비스에 연결하는 기능
- `Daemon`: 서비스로 동작하는 백그라운드 프로세스

## 진단과 모의해킹의 차이

취약점 진단은 가이드 기준으로 현재 설정이 안전한지 판단하는 작업임

모의해킹은 취약점 자체를 나열하는 것이 아니라, 실제 침투 시나리오로 이어지는지 검증하는 작업에 가까움

따라서 신입 단계에서는 우선 `기준을 정확히 읽고 항목별로 진단할 수 있는지`가 더 중요하게 평가됨

## 사전 준비

진단 전에는 다음 항목을 먼저 확정해야 함

- 계정 정보
- 접속 정보
- 대상 범위
- 진단 기준
- 보고 방식

실무에서는 접속 정보가 부족하거나 범위가 애매하면 진단 품질이 떨어지므로, 기술 역량보다 사전 협의가 더 중요해지는 경우도 많음

## 환경 분석 명령어

### `cat /etc/rocky-release`

배포판 버전을 가장 직접적으로 확인하는 명령어

```shell
cat /etc/rocky-release
```

- `cat`: 파일 내용 출력
- `/etc/rocky-release`: Rocky Linux 배포판 정보 파일

### `hostnamectl`

호스트명, 커널 버전, 가상화 여부 같은 기본 시스템 정보를 한 번에 보는 명령어

```shell
hostnamectl
```

- `hostnamectl`: systemd 기반 호스트 정보 출력

### `mariadb --version`

DBMS 버전을 확인하는 명령어

```shell
mariadb --version
```

- `--version`: 버전 정보 출력

### `httpd -v`

Apache HTTP Server 버전을 확인하는 명령어

```shell
httpd -v
```

- `-v`: 버전 정보 출력

### `/usr/sbin/tomcat version`

Tomcat 버전과 JVM 정보를 확인하는 명령어

```shell
/usr/sbin/tomcat version
```

- `version`: 버전/런타임 정보 출력

### `netstat -ntlp`

열려 있는 TCP LISTEN 포트와 연결된 프로세스를 확인하는 명령어

```shell
netstat -ntlp
```

- `-n`: 숫자 형식 출력
- `-t`: TCP 소켓만 확인
- `-l`: LISTEN 상태 중심
- `-p`: 프로세스 정보 표시

### `systemctl list-units --type=service --state=running`

현재 실행 중인 서비스만 골라보는 명령어

```shell
systemctl list-units --type=service --state=running
```

- `list-units`: 현재 로드된 unit 상태 출력
- `--type=service`: service 타입만 대상
- `--state=running`: 실행 중 상태만 대상

환경 분석의 목적은 단순 버전 확인이 아니라, `무슨 서비스가 떠 있는지`, `어느 포트가 열려 있는지`, `조합상 어떤 점검 항목이 필요한지`를 결정하는 데 있음

## Putty와 포트포워딩

VirtualBox 포트포워딩을 이용해 로컬 `127.0.0.1:2222`를 게스트 22번 포트에 연결함

이 구조를 이해하면 외부 노출 없이 내부 시스템에 SSH 접속할 수 있음

동시에 포트포워딩이 잘못 열리면 외부 노출 경로가 의도치 않게 생길 수 있다는 점도 함께 봐야 함

## 정리

시스템 진단의 시작점은 `환경 파악`임

OS, DBMS, Web Server, WAS, 포트, 실행 서비스가 정리되어야 그 다음에 계정, 파일 권한, 설정 항목 진단으로 넘어갈 수 있음





