---
title: "KnockOn Bootcamp 2nd - 1주차 HTTP/HTTPS"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - HTTP/HTTPS
last_modified_at: 2024-08-03T15:54:00+09:00
published: true
---
## HTTP (HyperText Transfer Protocol)

**웹**에서 데이터를 주고 받기 위한 프로토콜

*웹 브라우저 - 웹 서버* 간 데이터를 주고 받을 때 사용됨

요청-응답(request-response) 구조를 기반으로 작동
> *클라이언트*(예: 웹 브라우저)가 *서버*에 *요청*을 보냄 -> *서버*는 *클라이언트*에 그에 대한 *응답*을 보냄

웹의 기본 프로토콜로서, 웹 페이지의 로드, 데이터 전송 및 다양한 웹 애플리케이션의 작동을 가능하게 하는 역할

## 특징

### `무상태 프로토콜 (Stateless Protocol)`

HTTP는 무상태 프로토콜

각 요청은 *독립적*으로 처리되며, 이전 요청과 *연관성을 갖지 않음*
-> 서버는 각 요청을 별도로 처리할 수 있음

### `HTTP 메서드`

다양한 작업을 수행하기 위해 여러 메서드 제공
(GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS 등)

**`GET`**: 서버로부터 데이터 요청 (예: 웹 페이지 로드)

**`POST`**: 서버로 데이터 보냄 (예: 폼 제출)

**`PUT`**: 서버에 데이터 업데이트

**`DELETE`**: 서버에서 데이터 삭제

**`PATCH`**: 서버에서 데이터를 부분적으로 업데이트

**`HEAD`**: GET과 동일하지만, 응답 본문(body) 반환 X

**`OPTIONS`**: 서버가 지원하는 메서드 확인

### `HTTP 상태 코드`

서버는 클라이언트의 요청에 대한 응답으로 *상태 코드* 반환

상태 코드: 요청의 성공 여부 및 기타 정보를 나타냄

**`200 OK`**: 요청이 성공적으로 처리됨

**`404 Not Found`**: 요청한 자원을 찾을 수 없음

**`500 Internal Server Error`**: 서버 내부 오류 발생

**`302 Found`**: 요청한 자원이 다른 URL로 이동됨

### 헤더

HTTP 요청/응답에는 *헤더(header)*가 포함되어 있어, 메타데이터(데이터에 대한 데이터)를 전송할 수 있음

헤더: 콘텐츠 유형, 길이, 인코딩 방식, 인증 정보 등의 다양한 정보 포함

### HTTPS (HyperText Transfer Protocol Secure)

HTTP의 보안 버전, 데이터를 암호화하여 전송

HTTPS는 SSL/TLS 프로토콜을 사용해 데이터의 무결성과 기밀성을 보장함

## 동작 과정

### 1. 클라이언트가 서버에 HTTP 요청을 보냄

웹 브라우저 주소 창에 URL 입력

또는 링크 클릭

### 2. 서버가 요청을 처리하고 응답을 보냄

서버는 요청을 받아들임

해당 요청에 맞는 데이터를 준비하여 HTTP 응답을 클라이언트에 보냄

응답에는 상태 코드, 요청한 데이터(예: HTML 페이지)가 포함됨

### 3. 클라이언트가 응답을 받아 처리

클라이언트는 서버로부터 받은 응답을 처리하여, 사용자에게 필요한 정보를 표시함

## HTTP, HTTPS

HTTP와 HTTPS는 웹에서 데이터를 전송하기 위한 주요 프로토콜로, 주요 차이점은 보안성

## HTTP (HyperText Transfer Protocol)

HTTP는 데이터를 암호화하지 않고 전송하는 프로토콜

**`보안`**: HTTP는 암호화되지 않아 데이터가 전송되는 동안 *도청*이나 *중간자 공격(man-in-the-middle attack)*에 취약함

**`포트 번호`**: 80 포트 사용

**`사용 예`**: 보안이 중요하지 않은 일반적인 웹사이트에서 사용(뉴스 사이트, 블로그 등)

## HTTPS (HyperText Transfer Protocol Secure)

HTTP의 보안 버전

데이터 전송 시 *SSL(Secure Sockets Layer)*/*TLS(Transport Layer Security)* 프로토콜을 사용해 데이터를 암호화하여 *기밀성*과 *무결성*을 보장

**`보안`**

데이터를 암호화하여 전송하므로 도청, 중간자 공격 등에 대해 보호 제공

데이터의 기밀성을 보장

서버와 클라이언트 간 데이터 무결성 검증

**`포트 번호`**: 443 포트 사용

**`인증서`**

SSL/TLS 인증서를 사용해 서버의 신원 검증

인증서는 공인된 인증 기관(CA, Certificate Authority)에서 발급됨

**`사용 예`**

보안이 중요한 웹사이트에서 사용하여 사용자 데이터 보호(온라인 쇼핑몰, 은행 웹사이트, 이메일 서비스 등)

## 차이점 비교

|            | HTTP                     |  HTTPS                        |
|:-----------|:-------------------------|:------------------------------|
| 보안       | 암호화 X                  | SSL/TLS 사용, 데이터 암호화    |
| 포트 번호  | 80                        | 443                          |
| 인증       | 인증서 x                  | SSL/TLS 인증서 사용, 서버 인증 |
| 데이터 보호 | 데이터 전송 중, 도청 및 변조에 취약 | 데이터 전송 중, 도청 및 변조 방지 |
| URL       | http://                            | https://             |

## HTTP 헤더, 바디의 구조

HTTP 요청/응답 메시지는 크게 세 부분으로 구성됨

시작줄(start line)

*헤더(header)*

*바디(body)*

## HTTP `요청(request)` 메시지 구조

### 1. 시작줄 (Start Line)

요청 메서드, 요청 대상(URI), HTTP 버전 포함

```js
GET /index.html HTTP/1.1
```

### 2. 헤더 (Headers)

요청에 대한 메타데이터 포함

각 헤더는 "name:value" 로 이루어져 있음

```js
Host: war.knock-on.org:10001
User-Agent: bot
Content-Type: application/x-www-form-urlencoded
Content-Length: 20
Cookie: A=a
```

### 3. 공백 줄 (Blank Line)

헤더와 바디를 구분하는 빈 줄

### 4. 바디(Body)

선택적으로 포함됨

주로 POST, PUT 등의 메서드에서 서버로 전송할 데이터를 포함

```js
request=get-flag
name=Pack&age=999
```

### 예

```js
POST / HTTP/1.1
Host: war.knock-on.org:10001
User-Agent: bot
Content-Type: application/x-www-form-urlencoded
Content-Length: 20
Cookie: API_KEY=h3ll0_Pack

request=get-flag
```

## HTTP `응답(response)` 메시지 구조

### 1. 상태줄 (Status Line)

HTTP 버전, 상태 코드, 상태 메시지 포함

```js
HTTP/1.1 200 OK
```

### 2. 헤더

응답에 대한 메타데이터 포함

```js
Content-Type: text/html; charset=UTF-8
Content-Length: 138
```

### 3. 공백 줄

헤더와 바디를 구분하는 빈 줄

### 4. 바디

요청에 대한 실제 응답 데이터 포함

```js
<html>
    <head>
        <title>Example</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
    </body>
</html>
```

### 예

```js
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 138

<html>
    <head>
        <title>HTTP Response</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
    </body>
</html>
```

## 헤더 종류

### **`일반 헤더 (General Headers)`**

요청 및 응답 모두에 적용

> Cache-Control, Connection, Date, Pragma, Trailer, Transfer-Encoding, Upgrade, Via, Warning

### **`요청 헤더 (Request Headers)`**

클라이언트가 서버로 보내는 요청에 대한 정보를 포함

> Accept, Accept-Charset, Accept-Encoding, Accept-Language, Authorization, Expect, From, Host, If-Match, If-Modified-Since, If-None-Match, If-Range, If-Unmodified-Since, Max-Forwards, Proxy-Authorization, Range, Referer, TE, User-Agent

### **`응답 헤더 (Response Headers)`**

서버가 클라이언트로 보내는 응답에 대한 정보를 포함

> Accept-Ranges, Age, ETag, Location, Proxy-Authenticate, Retry-After, Server, Vary, WWW-Authenticate

### **`엔터티 헤더 (Entity Headers)`**

요청 또는 응답의 본문에 대한 정보를 포함

> Allow, Content-Encoding, Content-Language, Content-Length, Content-Location, Content-MD5, Content-Range, Content-Type, Expires, Last-Modified

## 바디 내용

**`요청 바디`**: 주로 POST, PUT 등의 메서드에서 사용되며, 폼 데이터, JSON, XML 등의 형식으로 데이터를 포함할 수 있음

**`응답 바디`**: 서버가 클라이언트에게 보내는 실제 데이터로, HTML, JSON, XML, 이미지 등 다양한 형식이 될 수 있음

## HTTP method

주요 메서드

## **`GET`**

서버에서 지정된 리소스를 요청할 때 사용

데이터가 URL에 포함됨

서버의 리소스를 변경하지 않음

### 특징

캐싱 가능

브라우저 히스토리에 남음

URL 길이에 제한이 있을 수 있음

데이터가 *URL에 노출*됨

### 예

```js
GET / HTTP/1.1
Host: war.knock-on.org:10001
```

## **`POST`**

서버에 데이터를 제출할 때 사용

폼 데이터 제출, 파일 업로드 등에 사용

### 특징

캐싱 불가

브라우저 히스토리에 남지 않음

URL 길이 제한 없음

데이터가 *요청 본문(Request Body)* 에 포함됨

### 예

```js
POST / HTTP/1.1
Host: war.knock-on.org:10001
User-Agent: bot
Content-Type: application/x-www-form-urlencoded
Content-Length: 20
Cookie: API_KEY=h3ll0_Pack

request=get-flag
```

## **`PUT`**

서버에 리소스를 생성하거나 업데이트할 때 사용

지정된 URL에 데이터가 저장됨

### 특징

멱등성 (동일한 요청을 여러 번 수행해도 결과가 같음)

데이터가 *요청 본문(Request Body)* 에 포함됨

### 예

```js
PUT /resource/1 HTTP/1.1
Host: war.knock-on.org:10001
Content-Type: application/json

{"request": "get-flag"}
```

## **`DELETE`**

지정된 리소스를 삭제할 때 사용

### 특징

멱등성

### 예

```js
DELETE /resource/1 HTTP/1.1
Host: war.knock-on.org:10001
```

## **`PATCH`**

리소스의 일부를 업데이트할 때 사용

### 특징

부분 업데이트

### 예

```js
PATCH /resource/1 HTTP/1.1
Host: war.knock-on.org:10001
Content-Type: application/json

{"request": "get-new-flag"}
```

## **`HEAD`**

GET과 유사하지만, 서버는 *응답 본문(Response Body)*을 반환하지 않고 *HTTP 헤더*만 가져옴

### 특징

*응답 본문(Response Body)* 없음

리소스의 메타데이터 확인에 유용

### 예

```js
HEAD /index.html HTTP/1.1
Host: war.knock-on.org:10001
```

## **`OPTIONS`**

서버에서 지원하는 메서드를 확인할 때 사용

### 특징

*CORS(Cross-Origin Resource Sharing)* 설정 확인에 유용

### 예

```js
OPTIONS /resource/1 HTTP/1.1
Host: war.knock-on.org:10001
```

## **`CONNECT`**

프록시 서버를 통해 터널링을 설정할 때 유용

주로 SSL(HTTPS) 연결에 사용됨

### 예

```js
CONNECT war.knock-on.org:443 HTTP/1.1
Host: war.knock-on.org
```

## **`TRACE`**

서버에서 받은 요청을 그대로 반환할 때 사용

디버깅 목적으로 사용

### 예

```js
TRACE /resource/1 HTTP/1.1
Host: war.knock-on.org:10001
```

## HTTP 상태코드

HTTP 상태 코드는 클라이언트가 서버에 보낸 요청의 결과를 나타내는 3자리 숫자

웹 브라우저와 서버 간의 통신 상태를 나타냄

*1XX ~ 5XX*의 5가지 클래스로 구분됨. 첫 번째 자리로 클래스 구분

## 1xx (정보)

**`100 Continue`**: 서버가 요청을 잘 받았고, 클라이언트가 계속해서 요청을 보내도 됨

**`101 Switching Protocols`**: 클라이언트가 프로토콜 변경을 요청, 서버가 이를 승인하여 프로토콜을 변경할 것임

## 2xx (성공)

**`200 OK`**: 요청이 성공적으로 처리됨

**`201 Created`**: 요청이 성공적, 새로운 리소스가 생성됨

**`202 Accepted`**: 요청이 접수됐지만, 처리가 안됨

**`204 No Content`**: 요청이 성공적, 반환할 콘텐츠 없음

## 3xx (리다이렉션)

**`301 Moved Permanently`**: 요청한 리소스가 영구적으로 이동되었음을 나타냄. 새로운 URL이 응답에 포함됨

**`302 Found`**: 요청한 리소스가 임시적으로 다른 위치에 있음을 나타냄. 클라이언트는 다른 URL을 사용해 요청을 이어나가야 함

**`304 Not Modified`**: 요청한 리소스가 수정되지 않았음을 의미. 클라이언트는 캐시된 버전을 사용해야 함

## 4xx (클라이언트 오류)

**`400 Bad Request`**: 서버가 요청을 이해할 수 없거나 잘못된 요청임

**`401 Unauthorized`**: 인증이 필요하며, 인증 정보가 없거나 잘못됨

**`403 Forbidden`**: 서버가 요청을 이해했으나, 권한이 없어 요청을 거부함

**`404 Not Found`**: 요청한 리소스를 찾을 수 없음

**`405 Method Not Allowed`**: 요청한 메서드가 리소스에서 허용되지 않음

## 5xx (서버 오류)

**`500 Internal Server Error`**: 서버에서 요청을 처리하는 동안 오류가 발생함

**`501 Not Implemented`**: 서버가 요청을 수행할 수 있는 기능을 갖추지 않음

**`502 Bad Gateway`**: 서버가 게이트웨이, 또는 프록시로 동작하는 동안 잘못된 응답을 받았음

**`503 Service Unavailable`**: 서버가 일시적으로 과부하 상태이거나, 유지보수 중임

**`504 Gateway Timeout`**: 게이트웨이, 또는 프록시 서버가 지정된 시간 내에 응답을 받지 못했음

[상태 관련 코드 주요 RFC 문서(RFC 7231)](https://datatracker.ietf.org/doc/html/rfc7231#section-6)

## SSL인증서

SSL(Secure Sockets Layer)/TLS(Transport Layer Security)

웹사이트와 사용자 간의 *데이터 전송을 암호화*하여 *보안을 강화*하는 디지털 인증서

TLS는 SSL의 진화된 버전이며, 실제로는 TLS 프로토콜을 사용해 보안 통신을 설정함

(오랫동안 SSL이라는 용어를 사용해왔기 때문에 TLS대신 SSL이라는 용어를 계속 사용. SSL 인증서 = TLS 인증서)

SSL 인증서는 웹사이트 보안의 핵심 요소로, 사용자 데이터 보호와 신뢰성 확보를 위해 필수적임

## 기능

**`데이터 암호화`**: 클라이언트(브라우저)와 서버 간에 전송되는 데이터를 암호화

중간 공격자가 데이터를 훔쳐보거나 변조하지 못하도록 막음

**`인증`**: 신뢰할 수 있는 기관(CA, Certificate Authority)에서 발급한 인증서를 통해 웹사이트의 신뢰성 검증

**`데이터 무결성`**: 데이터가 전송 중에 변조되지 않았음을 보장

## SSL 인증서 구성 요소

**`도메인 이름`**: 인증서가 발급된 도메인 이름

**`조직 정보`**: 인증서를 요청한 조직의 정보

**`발급 기관`**: 인증서를 발급한 신뢰할 수 있는 인증 기관(CA)의 이름

**`유효 기간`**: 인증서의 발급일/만료일

**`공개 키`**: 데이터를 암호화하는 데 사용되는 공개 키(비밀 키와 쌍을 이룸)

**`디지털 서명`**: CA의 디지털 서명이 포함되어, 인증서의 진위성 보장

## SSL 인증서 종류

**`도메인 검증(DV, Domain Validation)`**: 도메인 소유권만 검증

발급 속도가 빠르고 비용이 저렴

**`조직 검증(OV, Organization Validation)`**: 도메인 소유권과 함께 조직의 신원도 검증

보다 높은 신뢰성을 제공

**`확장 검증(EV, Extended Validation)`**: 가장 엄격한 검증 절차를 거침

브라우저 주소창에 조직 이름이 녹색으로 표시되며, 최고 수준의 신뢰성을 제공

**`와일드카드 인증서(Wildcard Certificate)`**: 하나의 인증서로 도메인과 해당 도메인의 모든 서브도메인을 보호함

- 예: *.도메인이름.com

**`멀티 도메인 인증서(Multi-Domain Certificate)`**: 하나의 인증서로 여러 도메인을 보호함

*SAN(Subject Alternative Name)* 필드를 사용하여 여러 도메인을 지정할 수 있음

## SSL 인증서 발급 과정

**`CSR 생성`**: 서버에서 CSR(인증서 서명 요청, Certificate Signing Request)을 생성

CSR에는 도메인 이름, 조직 정보, 공개 키 등이 포함됨

**`CSR 제출`**: CSR을 인증 기관(CA)에 제출함

**`검증`**: CA가 도메인 소유권 및 조직 신원을 검증함

검증 방식은 이메일 검증, 파일 업로드, DNS 레코드 설정 등 다양한 방식이 있음

**`인증서 발급`**: 검증이 완료되면 CA가 SSL 인증서를 발급함

**`설치`**: 발급된 인증서를 서버에 설치하고, SSL/TLS 설정을 구성함

## 주요 SSL 인증서 제공 기관 (CA)

**`Comodo`**: 다양한 종류의 인증서를 제공하며, 비용 효율적인 옵션도 있음

**`DigiCert`**: 높은 신뢰성과 빠른 발급 속도로 유명함

**`Let's Encrypt`**: 무료 SSL 인증서를 제공하는 CA로, 자동화된 발급 및 갱신 시스템을 갖추고 있음

**`GlobalSign`**: 다양한 보안 솔루션과 함께 SSL 인증서를 제공함

**`Symantec`**: 현재는 DigiCert에 인수되었으며, 이전에 Symantec 브랜드로 발급된 인증서들이 여전히 사용되고 있음

## SSL 인증서의 설치와 관리

**`서버 설정`**: 웹 서버(Apache, Nginx, IIS 등)에 SSL/TLS 모듈을 활성화

**`인증서 및 키 파일 업로드`**: 발급된 인증서 파일과 개인 키 파일을 서버에 업로드

**`서버 설정 파일 수정`**: 서버 설정 파일에서 SSL 인증서와 키 파일의 경로를 지정하고, 필요한 SSL/TLS 설정을 구성

**`재시작`**: 설정을 적용하기 위해 웹 서버를 재시작

**`테스트`**: SSL 인증서가 올바르게 설치되었는지 확인하기 위해 SSL 테스트 도구(예: Qualys SSL Labs)를 사용하여 테스트

## SSL 인증서 관리

**`갱신`**: SSL 인증서는 유효 기간이 만료되기 전에 갱신해야 함

갱신 절차는 신규 발급 절차와 유사함

**`보안 유지`**: 개인 키를 안전하게 관리하고, 노출되지 않도록 함

만약 키가 유출되었다면 즉시 인증서를 폐기하고 재발급 받아야 함

**`정기 점검`**: SSL 설정과 인증서 상태를 정기적으로 점검하여 보안 수준을 유지

