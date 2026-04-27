---
title: "버그헌팅 실습 정리 - Recon, OAST, SSRF로 공격 표면과 내부 자산 확인하기"
date: 2026-04-03T15:00:00+09:00
categories:
  - Web Hacking
tags:
  - Bug Hunting
  - Recon
  - OAST
  - Burp Collaborator
  - SSRF
  - Attack Surface Discovery
last_modified_at: 2026-04-17T18:46:18+09:00
published: true
---

## 도구

**공격 표면 식별**  
`Google Dork` `crt.sh` `amass` `GitHub Search` `AWS CLI`

**Blind 검증과 요청 재현**  
`Burp Suite` `Burp Repeater` `Burp Collaborator`

## 개요

버그헌팅에서 먼저 필요한 것은 취약점 이름이 아님  
우선 확인 항목: `어디가 노출되어 있는가`, `어떤 기능이 외부 입력을 받아 동작하는가`, `응답이 보이지 않아도 어떻게 검증할 것인가`

아래 흐름을 하나로 묶어 정리한 기록임

- 공개 자산과 공격 표면 식별
- `blind` 구간에서 외부 상호작용 기반 검증
- 내부 자산 접근 가능성을 확인하는 `SSRF` 흐름

핵심: `Recon`, `OAST`, `SSRF` 단일 탐색 흐름

## 1. 공격 표면 식별

### Google Dork

검색엔진은 예상보다 많은 운영 흔적을 그대로 드러냄  
로그인 경로, 백업 파일, 문서, 인덱싱된 디렉터리 같은 값은 초기에 빠르게 확인 가능한 단서임

자주 쓰는 형태는 아래와 같음

```text
site:example.com inurl:login
site:example.com ext:sql
site:example.com intitle:index.of
site:example.com "confidential"
```

이 검색 뒤에는 아래 값을 먼저 확인함

- 로그인 또는 관리자 경로
- 공개 문서와 PDF
- `.zip`, `.sql`, `.bak` 같은 백업 파일 흔적
- 디렉터리 인덱스 페이지
- 운영 중 남겨진 테스트 경로

중요한 점은 취약점을 바로 찾는 것이 아니라 `먼저 볼 경로를 줄이는 데 유리하다`는 점임

### S3 Bucket

정적 자산이 버킷에 직접 공개되면 웹 루트 밖 파일 구조까지 함께 노출되는 경우가 있음  
이때 중요한 것은 파일 내용보다 `외부에서 열거 가능한가` 여부임

```bash
aws s3 ls s3://<BUCKET_NAME> --no-sign-request
```

또는 엔드포인트 기반 스토리지를 쓰는 경우 아래처럼 확인 가능함

```bash
aws s3 ls s3://<BUCKET_NAME> --endpoint-url http://<S3_HOST>
```

명령 실행 뒤에는 아래 값을 우선 봄

- 익명 접근 가능 여부
- `index.html`, `app.js`, `backup.zip` 같은 파일명
- 정적 자산 외 문서나 설정 파일 존재 여부
- 디렉터리 구조가 운영 환경을 드러내는지 여부

즉 버킷은 단순 저장소가 아니라 배포 구조와 자산 범위를 드러내는 단서가 될 수 있음

### GitHub Recon

공개 저장소와 조직 계정은 코드보다 운영 흔적을 더 많이 남기는 경우가 많음  
도메인 이름, 내부 시스템 이름, 배포 환경, 정적 자산 경로 같은 값이 설명이나 커밋 메시지에 남아 있기도 함

우선 확인 문자열

- `dev`
- `staging`
- `internal`
- `api`
- `bucket`
- `s3`
- `admin`

중요하게 보는 값은 아래와 같음

- 하위 도메인 이름
- 내부 시스템 이름
- 배포 경로
- 외부 스토리지 이름
- 설정 파일에 남은 엔드포인트 흔적

즉 `GitHub Recon`은 비밀값 탐색보다 자산 범위 확장에 더 자주 쓰였음

### Domain Enumeration

메인 도메인 하나만 보는 것은 실제 노출면을 좁게 보는 방식임  
서브도메인 열거는 연결된 자산 전체를 보는 단계에 가까움

```bash
amass enum -passive -d example.com
```

또는 인증서 투명성 로그에서 직접 확인 가능함

이때 먼저 보는 값은 아래와 같음

- `admin`
- `dev`
- `api`
- `internal`
- `vpn`
- `staging`

이 값들은 곧바로 취약점이 아니라 `어느 환경을 먼저 확인할 것인가`에 대한 우선순위를 줌

## 2. Blind 구간에서 OAST로 검증

### 왜 OAST가 필요한가

입력값이 시스템 명령이나 외부 요청 기능과 연결된 것처럼 보여도 화면 응답은 항상 비슷할 수 있음  
이 경우 응답 본문만으로는 성공과 실패를 구분하기 어려움

대표적으로 아래 상황에서 `OAST`가 필요함

- 명령 결과가 응답에 포함되지 않음
- 필터링 때문에 에러가 보이지 않음
- 비동기 처리로 화면이 항상 같은 메시지를 반환함

즉 `응답이 없다`와 `실행이 안 됐다`는 같은 의미가 아님

### Burp Collaborator

`Burp Collaborator`는 외부 상호작용을 기준으로 성공 여부를 확인하는 도구임  
대상 서버가 외부 DNS 또는 HTTP 요청을 보내면 그 흔적이 기록됨

기본 흐름은 아래와 같음

1. `Collaborator` 주소 생성
2. 입력값에 외부 요청을 유도하는 문자열 삽입
3. 응답 본문과 별개로 interaction 기록 확인

예시 입력값은 아래처럼 잡을 수 있음

```text
|| nslookup <COLLABORATOR_DOMAIN> ||
```

또는

```text
& ping -c 1 <COLLABORATOR_DOMAIN> &
```

애플리케이션 응답은 아래처럼 평범할 수 있음

```http
HTTP/1.1 200 OK
Content-Type: text/html

Request received
```

하지만 실제로 먼저 확인할 값은 아래임

- `DNS interaction`
- `HTTP interaction`
- 호출 시각
- 호출을 보낸 서버 IP

즉 화면 변화가 없어도 외부 상호작용이 확인되면 `blind command injection` 가능성을 검증하는 근거가 됨

### Blind 검증에서 중요했던 기준

`OAST`가 특히 유효했던 조건은 아래와 같음

- 입력값이 시스템 명령과 연결되는 위치에 있음
- 시간 지연만으로는 성공 여부가 모호함
- 서버가 외부 네트워크로 나갈 수 있음

이 상황에서는 `sleep`, `delay` 기반 확인보다 `Collaborator` 기반 검증이 더 명확했음  
즉 반응이 보이지 않는 기능일수록 외부 콜백을 기준으로 보는 편이 정확함

## 3. SSRF로 내부 자산 확인

### 서버가 대신 요청하는 기능

외부 URL을 받아 서버가 대신 요청하는 기능은 단순 편의 기능처럼 보여도 내부 자산 접근 통로가 될 수 있음  
이 경우 가장 먼저 확인할 값은 `외부 URL 호출 가능 여부`보다 `어디까지 닿는가`임

예시 요청은 아래처럼 구성 가능함

```http
POST /product/stock HTTP/1.1
Host: <TARGET_HOST>
Content-Type: application/x-www-form-urlencoded

stockApi=http://127.0.0.1/admin
```

응답에서는 아래 값을 먼저 봄

- 상태코드 변화
- `Admin panel`, `Delete user`, `Internal dashboard` 같은 문자열
- 리다이렉트 위치
- 내부 주소나 서비스 이름을 드러내는 오류 문구

중점: 요청 발생보다 내부 경로 개방 범위

### localhost 계열 확인 순서

내부 자산 확인은 무작정 길게 시도하기보다 아래 순서가 자연스러웠음

```text
http://127.0.0.1/
http://localhost/
http://127.0.0.1/admin
http://localhost/admin
http://127.1/
```

이때 응답에서 확인한 값은 아래와 같음

- 관리자 기능 버튼 노출 여부
- 내부 전용 문구
- `200`, `302`, `403` 같은 상태코드 차이
- 외부에서는 보이지 않던 경로 이름

중점: 접근 경로와 기능 범위

## 4. 흐름으로 묶어서 보기

정찰, `OAST`, `SSRF`는 서로 다른 기법처럼 보이지만 실제 흐름은 자연스럽게 이어짐

1. `Google`, `GitHub`, `S3`, `도메인 열거`로 공개 자산과 노출면을 넓게 식별함
2. 입력값 중 시스템 명령과 연결될 가능성이 보이면 `Burp Collaborator`로 `blind` 여부를 확인함
3. 외부 요청 기능이 보이면 `localhost`, `admin` 경로를 중심으로 내부 자산 접근 가능성을 확인함

즉 버그헌팅형 탐색은 개별 도구 사용법보다 `노출면 식별 -> 가설 설정 -> 외부 상호작용 검증 -> 내부 자산 확인` 순서로 좁혀 가는 과정에 가까움

## 정리

반복적으로 중요했던 기준은 아래와 같음

- 정찰은 취약점 이름을 찾는 단계보다 `어디를 먼저 볼 것인가`를 정하는 단계임
- 공개 자산과 운영 흔적은 검색엔진, 공개 저장소, 스토리지, 도메인 정보에서 먼저 드러나는 경우가 많음
- `blind` 구간은 응답 본문보다 외부 콜백 기준으로 검증하는 편이 정확함
- `SSRF`는 외부 요청 자체보다 내부 자산 접근 범위를 확인해야 의미가 생김

즉 버그헌팅형 흐름은 단일 기법의 숙련보다 여러 단서를 연결해 우선순위를 좁혀 가는 과정에서 강해짐

