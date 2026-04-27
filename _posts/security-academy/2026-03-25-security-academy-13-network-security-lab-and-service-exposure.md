---
title: "시큐리티아카데미 7기 정리 - 네트워크보안 1. 실습 환경과 서비스 노출"
date: 2026-03-25T18:00:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Network Security
  - GNS3
  - Telnet
  - SNMP
permalink: /security-academy/network-security-lab-and-service-exposure/
last_modified_at: 2026-03-30T21:10:00+09:00
published: true
---
## 개요

Backtrack, XP, GNS3를 이용해 실습 환경을 구성하고, 노출된 서비스가 어떤 방식으로 식별되는지 확인하는 내용

실습 흐름: `환경 구성 -> 라우터 기본 설정 -> 포트 스캔 -> 서비스별 접근 확인`

## 용어 정리

- `GNS3`: 가상 네트워크 장비 실습 도구
- `Telnet`: 평문 기반 원격 접속 프로토콜
- `SNMP`: 네트워크 장비 관리용 프로토콜
- `Community String`: SNMP 접근 시 사용하는 문자열 기반 인증값
- `Service Exposure`: 외부에서 서비스가 식별되거나 접근 가능한 상태

## 라우터 기본 설정

Cisco 라우터에 IP를 할당하고, Telnet, SNMP, HTTP 관리 기능을 활성화함

### `conf t`

전역 설정 모드로 진입하는 첫 명령어

```shell
conf t
```

- `conf t`: `configure terminal` 축약형

### `interface fa0/0`

설정 대상 인터페이스를 지정하는 명령어

```shell
interface fa0/0
```

- `fa0/0`: FastEthernet 0/0 인터페이스

### `no shutdown`

관리적으로 꺼져 있는 인터페이스를 활성화하는 명령어

```shell
no shutdown
```

### `ip address 10.0.0.200 255.255.255.0`

인터페이스 IP와 서브넷 마스크를 지정하는 명령어

```shell
ip address 10.0.0.200 255.255.255.0
```

- 첫 번째 값: 인터페이스 IP
- 두 번째 값: 서브넷 마스크

### `service password-encryption`

평문 비밀번호가 설정 파일에서 그대로 보이지 않도록 처리하는 명령어

```shell
service password-encryption
```

### `line vty 0 4`

원격 접속용 가상 터미널 라인을 설정하는 명령어

```shell
line vty 0 4
```

- `0 4`: 보통 5개의 VTY 라인 범위

### `password cisco`

VTY 라인 접속 비밀번호를 설정하는 명령어

```shell
password cisco
```

### `enable password cisco`

특권 모드 진입 비밀번호를 설정하는 명령어

```shell
enable password cisco
```

### `enable secret abc`

해시 기반 특권 비밀번호를 설정하는 명령어

```shell
enable secret abc
```

`enable password`보다 `enable secret`이 우선되고, 보안성도 더 높음

### `snmp-server community abc rw`

SNMP community와 권한을 지정하는 명령어

```shell
snmp-server community abc rw
```

- `abc`: community string
- `rw`: 읽기/쓰기 허용

### `ip finger`

Finger 서비스를 활성화하는 명령어

```shell
ip finger
```

### `ip http server`

웹 기반 관리 인터페이스를 켜는 명령어

```shell
ip http server
```

### `write`

현재 설정을 저장하는 명령어

```shell
write
```

이 설정만으로도 Telnet, HTTP, SNMP 같은 관리 서비스가 외부에서 식별 가능한 상태가 됨

## 서비스 노출 확인

### `nmap -sT 10.0.0.200`

열린 TCP 포트를 확인하는 기본 스캔 명령어

```shell
nmap -sT 10.0.0.200
```

- `nmap`: 포트 스캔 도구
- `-sT`: TCP connect 스캔
- `10.0.0.200`: 대상 장비 IP

### `nmap -sU -p 161 10.0.0.200`

SNMP가 주로 사용하는 UDP 161 포트만 직접 확인하는 명령어

```shell
nmap -sU -p 161 10.0.0.200
```

- `-sU`: UDP 스캔
- `-p 161`: 161번 포트만 지정

실습 결과에서는 `23/tcp`, `79/tcp`, `80/tcp`, `161/udp`가 확인됨

이 출력만으로도 관리용 서비스가 여러 개 동시에 노출되어 있음을 판단할 수 있음

## 인증 추정과 서비스 확인

### `medusa -M telnet -h 10.0.0.200 -u cisco -P password.txt`

Telnet 인증 정책을 확인하는 실습 명령어

```shell
medusa -M telnet -h 10.0.0.200 -u cisco -P password.txt
```

- `medusa`: 다중 프로토콜 인증 시도 도구
- `-M telnet`: Telnet 모듈 사용
- `-h`: 대상 호스트 지정
- `-u`: 사용자명 지정
- `-P`: 비밀번호 목록 파일 지정

### `medusa -M ftp -h 10.0.0.30 -u root -P password.txt`

같은 방식으로 FTP 서비스 인증 정책을 확인하는 명령어

```shell
medusa -M ftp -h 10.0.0.30 -u root -P password.txt
```

- `-M ftp`: FTP 모듈 사용

### `./onesixtyone -c dict.txt 10.0.0.200`

SNMP community 문자열을 사전 기반으로 확인하는 명령어

```shell
./onesixtyone -c dict.txt 10.0.0.200
```

- `onesixtyone`: SNMP community 탐색 도구
- `-c dict.txt`: 사용할 딕셔너리 파일 지정

중요한 점은 도구 사용 자체보다, 평문 서비스와 약한 인증 정책이 결합되면 관리 인터페이스가 빠르게 노출되는 구조에 있음

## 실습 해석 포인트

- Telnet은 평문 인증이므로 보호 수준이 낮음
- SNMP community가 추정 가능하면 장비 정보 노출 위험이 커짐
- HTTP 관리 기능이 열려 있으면 웹 기반 설정 인터페이스 노출이 발생함

즉 장비 보안은 방화벽만의 문제가 아니라, 기본 서비스 활성화 상태부터 다시 봐야 함

## 정리

네트워크 장비는 구성만 끝나면 안전한 것이 아니라, 어떤 관리 서비스가 살아 있는지 먼저 확인해야 함

포트 스캔과 인증 확인 단계만으로도 운영 정책이 얼마나 느슨한지 상당 부분 드러남



