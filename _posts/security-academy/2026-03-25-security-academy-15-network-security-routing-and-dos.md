---
title: "시큐리티아카데미 7기 정리 - 네트워크보안 3. VLAN, 라우팅, DoS"
date: 2026-03-25T18:20:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Network Security
  - VLAN
  - Routing
  - DoS
permalink: /security-academy/network-security-routing-and-dos/
last_modified_at: 2026-03-30T21:30:00+09:00
published: true
---
## 개요

VLAN, 트렁크, 정적 라우팅, ACL, DoS 실습까지 이어지는 네트워크 운영/공격 관점을 다루는 내용

핵심은 `망 분리`, `경로 설정`, `장애 우회`, `가용성 공격`을 하나의 흐름으로 연결해 보는 데 있음

## 용어 정리

- `VLAN`: 논리적으로 분리된 브로드캐스트 도메인
- `Access Port`: 하나의 VLAN에만 속하는 포트
- `Trunk Port`: 여러 VLAN 태그를 함께 전달하는 포트
- `Static Routing`: 관리자가 직접 경로를 설정하는 방식
- `Dynamic Routing`: 라우터끼리 경로를 교환하는 방식
- `DoS`: 단일 또는 제한된 소스로 서비스를 마비시키는 공격
- `SYN Flood`: TCP 연결 요청을 과도하게 보내 자원을 소모시키는 공격

## VLAN 실습

### `conf t`

스위치 전역 설정 모드로 들어가는 명령어

```shell
conf t
```

### `vlan 10`

VLAN 10을 생성하는 명령어

```shell
vlan 10
```

### `name vlantest10`

방금 만든 VLAN 10에 이름을 붙이는 명령어

```shell
name vlantest10
```

### `vlan 20`

두 번째 VLAN을 만드는 단계

```shell
vlan 20
```

### `name vlantest20`

VLAN 20 이름 지정 단계

```shell
name vlantest20
```

### `interface range fa0/1 - 12`

여러 포트를 한 번에 선택하는 명령어

```shell
interface range fa0/1 - 12
```

- `interface range`: 인터페이스 범위 선택
- `fa0/1 - 12`: FastEthernet 0/1부터 0/12까지

### `switchport mode access`

선택한 포트를 access 포트로 고정하는 명령어

```shell
switchport mode access
```

### `switchport access vlan 10`

선택한 포트를 VLAN 10에 소속시키는 명령어

```shell
switchport access vlan 10
```

### `interface range fa0/13 - 16`

다음 포트 묶음을 선택하는 단계

```shell
interface range fa0/13 - 16
```

### `switchport mode access`

두 번째 포트 묶음도 access 모드로 지정하는 단계

```shell
switchport mode access
```

### `switchport access vlan 20`

두 번째 포트 묶음을 VLAN 20에 할당하는 명령어

```shell
switchport access vlan 20
```

### `show vlan`

VLAN과 포트 소속 상태를 확인하는 명령어

```shell
show vlan
```

VLAN을 나누면 같은 스위치에 물려 있어도 서로 다른 네트워크처럼 동작함

즉 물리 연결과 논리 네트워크가 분리됨

## Trunk

### `switchport mode trunk`

포트를 trunk 포트로 전환하는 명령어

```shell
switchport mode trunk
```

### `switchport trunk allowed vlan 10,20`

트렁크 링크를 통해 통과 가능한 VLAN 범위를 제한하는 명령어

```shell
switchport trunk allowed vlan 10,20
```

- `allowed vlan 10,20`: VLAN 10과 20만 통과 허용

트렁크는 여러 VLAN 트래픽을 한 링크로 운반하므로 편리하지만, 허용 범위를 넓게 열어두면 분리 효과가 약해질 수 있음

## 정적 라우팅

### `ip route 192.168.2.0 255.255.255.0 172.16.1.1`

첫 번째 목적지 네트워크에 대한 정적 경로를 추가하는 명령어

```shell
ip route 192.168.2.0 255.255.255.0 172.16.1.1
```

- 첫 번째 값: 목적지 네트워크
- 두 번째 값: 서브넷 마스크
- 세 번째 값: 다음 홉 IP

### `ip route 192.168.3.0 255.255.255.0 172.16.3.2`

다른 네트워크에 대한 경로를 추가하는 명령어

```shell
ip route 192.168.3.0 255.255.255.0 172.16.3.2
```

### `sh ip route`

현재 라우팅 테이블을 확인하는 명령어

```shell
sh ip route
```

- `sh`: `show` 축약형
- `ip route`: 라우팅 테이블 출력

### `ping -t 192.168.3.1`

Windows 환경에서 연속적으로 ping을 보내며 경로 복구 여부를 확인하는 명령어

```shell
ping -t 192.168.3.1
```

- `ping`: ICMP Echo Request 전송
- `-t`: 중지할 때까지 계속 전송

정적 라우팅은 경로가 명확하고 예측 가능는 장점이 있지만, 장애가 생기면 관리자가 직접 대체 경로를 추가해야 함

한 경로를 차단한 뒤 우회 경로를 다시 추가하며 복구 흐름을 확인함

## ACL과 서비스 제한

정적 경로가 잡혀 있더라도 모든 트래픽을 허용해야 하는 것은 아님

특정 서버에는 FTP만, 다른 서버에는 HTTP만 허용하는 식으로 세분화된 ACL을 붙일 수 있음

이때 중요한 기준은 `출발지`, `목적지`, `프로토콜`, `포트` 네 가지다

## DoS 실습 관점

`hping3`, `slowloris`, `slowhttptest`, `Hulk` 같은 키워드가 함께 등장함

이 도구들의 목적은 공통적으로 가용성을 떨어뜨리는 데 있음

특히 `SYN Flood`는 서버가 아직 완료되지 않은 연결 상태를 계속 유지하게 만들어 자원을 소모시키는 구조

옵션 해석 포인트

- `-S`: SYN 플래그 사용
- `--flood`: 가능한 빠르게 연속 전송
- `-p`: 대상 포트 지정

중점: 한계 자원 식별

## 정리

네트워크 운영은 연결을 만드는 일이고, 보안은 그 연결을 어디까지 허용할지 정하는 일에 가까움

VLAN, 라우팅, ACL, DoS는 서로 다른 주제처럼 보이지만, 결국 모두 트래픽 흐름을 설계하고 통제하는 문제로 연결됨




