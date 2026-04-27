---
title: "시큐리티아카데미 7기 정리 - 네트워크보안 2. 스푸핑, 스니핑, 접근 통제"
date: 2026-03-25T18:10:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Network Security
  - ARP Spoofing
  - DNS Spoofing
  - Access Control
permalink: /security-academy/network-security-spoofing-sniffing-and-access-control/
last_modified_at: 2026-03-30T21:20:00+09:00
published: true
---
## 개요

ARP Spoofing, IP Spoofing, DNS Spoofing, ACL을 이용한 접근 통제를 하나의 흐름으로 묶어 다루는 내용

핵심은 `로컬 네트워크 신뢰 관계가 어떻게 깨지는지`와 `라우터/스위치에서 이를 어떻게 통제하는지`를 함께 보는 데 있음

## 용어 정리

- `ARP Spoofing`: ARP 응답을 속여 MAC-IP 매핑을 변조하는 공격
- `IP Spoofing`: 출발지 IP를 속여 우회하는 기법
- `DNS Spoofing`: 도메인 해석 결과를 변조하는 공격
- `ACL(Access Control List)`: 트래픽 허용/차단 규칙 목록
- `Standard ACL`: 출발지 주소만 기준으로 제어하는 ACL
- `Extended ACL`: 프로토콜, 목적지, 포트까지 포함해 제어하는 ACL

## ARP Spoofing

먼저 정상 상태의 ARP 테이블을 확인한 뒤, 공격자가 XP와 라우터 사이에 끼어드는 구조를 만듦

### `arp -a`

호스트의 ARP 캐시를 먼저 확인하는 명령어

```shell
arp -a
```

- `arp`: ARP 테이블 확인/관리 명령
- `-a`: 전체 ARP 항목 출력

### `sh arp`

Cisco 장비 쪽 ARP 테이블을 보는 명령어

```shell
sh arp
```

- `sh`: `show` 축약형

공격 전 정상 매핑을 먼저 기록해 두면, 이후 MAC 주소가 바뀌는 지점을 비교하기 쉬움

### `fragrouter -B1`

실습 환경에서 포워딩 보조 동작에 사용한 명령어

```shell
fragrouter -B1
```

- `fragrouter`: 패킷 전달/변형 실습 도구
- `-B1`: 실습 환경에서 사용한 브리지/포워딩 옵션

### `arpspoof -i eth1 -t 10.0.0.30 10.0.0.200`

피해자 쪽에 공격자 MAC을 라우터처럼 보이게 만드는 명령어

```shell
arpspoof -i eth1 -t 10.0.0.30 10.0.0.200
```

- `arpspoof`: ARP 응답 위조 도구
- `-i eth1`: 사용할 인터페이스 지정
- `-t 10.0.0.30`: 타깃 호스트 지정
- 마지막 `10.0.0.200`: 가장할 대상 IP

### `arpspoof -i eth1 -t 10.0.0.200 10.0.0.30`

반대 방향도 같이 속여 양방향 중간자 구조를 만드는 명령어

```shell
arpspoof -i eth1 -t 10.0.0.200 10.0.0.30
```

양방향으로 ARP 응답을 보내야 양쪽 모두 공격자를 상대방으로 오인하게 됨

이후 ARP 테이블을 보면 공격자 MAC이 정상 호스트를 대신하게 되는 흐름이 관찰됨

## IP Spoofing과 우회

라우터에 특정 IP만 Telnet 접속을 허용하는 ACL을 걸고, 이후 우회 가능성을 관찰함

### `access-list 1 permit 10.0.0.100`

특정 출발지 주소만 허용하는 Standard ACL을 만드는 명령어

```shell
access-list 1 permit 10.0.0.100
```

- `access-list 1`: ACL 번호 1 사용
- `permit 10.0.0.100`: 해당 출발지 주소 허용

### `line vty 0 4`

원격 접속 라인을 설정 대상으로 잡는 명령어

```shell
line vty 0 4
```

### `access-class 1 in`

방금 만든 ACL을 VTY 라인 inbound 방향에 적용하는 명령어

```shell
access-class 1 in
```

- `1`: 적용할 ACL 번호
- `in`: 들어오는 연결에 적용

IP 기반 접근 통제는 단독으로는 충분하지 않을 수 있음

같은 브로드캐스트 도메인에서 신뢰 관계가 깨지면 ARP 변조나 우회 기법과 결합될 수 있기 때문임

## DNS Spoofing과 스니핑

`dnsspoof`와 `Cain`을 이용한 DNS 변조 및 스니핑 흐름

핵심: 사용자가 정상 도메인을 입력했더라도, 로컬 구간에서 이름 해석이 바뀌면 전혀 다른 시스템으로 유도될 수 있다는 점

따라서 DNS 응답 무결성과 로컬 네트워크 신뢰 관계를 함께 봐야 함

## ACL 적용 예시

### `access-list 10 deny host 192.168.10.10`

특정 호스트를 먼저 차단하는 Standard ACL 규칙임

```shell
access-list 10 deny host 192.168.10.10
```

- `deny`: 차단
- `host 192.168.10.10`: 단일 호스트 지정

### `access-list 10 permit any`

나머지 출발지는 모두 허용하는 규칙임

```shell
access-list 10 permit any
```

- `any`: 모든 주소

### `interface fa0/0`

ACL을 붙일 인터페이스를 지정하는 단계

```shell
interface fa0/0
```

### `ip access-group 10 in`

ACL 10을 인터페이스 inbound 방향에 적용하는 명령어

```shell
ip access-group 10 in
```

- `ip access-group`: 인터페이스 단 ACL 적용
- `10`: ACL 번호
- `in`: 들어오는 방향

### `access-list 100 permit tcp host 192.168.10.20 host 10.10.10.10 eq 21`

특정 출발지에서 특정 목적지의 FTP 제어 포트만 허용하는 Extended ACL 규칙임

```shell
access-list 100 permit tcp host 192.168.10.20 host 10.10.10.10 eq 21
```

- `100`: Extended ACL 번호 영역
- `permit tcp`: TCP 트래픽 허용
- `host 192.168.10.20`: 출발지 단일 호스트
- `host 10.10.10.10`: 목적지 단일 호스트
- `eq 21`: 목적지 포트 21

### `access-list 100 permit tcp host 192.168.10.20 host 20.20.20.20 eq 80`

같은 방식으로 HTTP 포트만 허용하는 규칙임

```shell
access-list 100 permit tcp host 192.168.10.20 host 20.20.20.20 eq 80
```

- `eq 80`: 목적지 포트 80

### `access-list 100 deny ip any any`

허용한 것 외 나머지 모든 IP 트래픽을 막는 마무리 규칙임

```shell
access-list 100 deny ip any any
```

- `deny ip`: 모든 IP 프로토콜 차단
- `any any`: 출발지/목적지 모두 전체

### `interface fa0/1`

Extended ACL을 붙일 인터페이스를 지정하는 단계

```shell
interface fa0/1
```

### `ip access-group 100 in`

ACL 100을 inbound 방향에 적용하는 명령어

```shell
ip access-group 100 in
```

ACL은 위에서 아래로 순서대로 평가되므로, 구체 규칙을 먼저 두고 마지막에 차단 규칙을 두는 흐름을 이해해야 함

## 정리

스푸핑과 스니핑은 로컬 네트워크의 암묵적 신뢰를 깨는 문제이고, ACL은 그 신뢰를 경계 단위로 재설정하는 도구

공격 기법과 방어 기법을 따로 외우기보다, `누가 누구를 어떤 정보로 신뢰하는가`를 기준으로 보면 구조가 정리됨




