---
title: "KISA 아카데미 정리 - 스피어피싱 2. 이메일 구조와 헤더 분석"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - Spear Phishing
  - Email
  - Mail Header
permalink: /security-academy/2025-02-06-kisa-spearphishing-2-email-analysis/
last_modified_at: 2025-02-06T18:00:00+09:00
published: true
---
## 개요

스피어피싱 메일 분석 시 확인해야 하는 `Envelope`, `Header`, `Body`, `Received-SPF`, 표시 이름 위조 지점을 다루는 파트

메일 본문만 확인하면 정상 메일처럼 보일 수 있으므로, 실제 전달 경로와 발신자 위조 여부는 헤더 기준으로 판단해야 함

## 용어 정리

- `Envelope(메시지 엔벌로프)`: 메일 서버 간 전달 과정에서 사용하는 실제 발신자·수신자 정보
- `Header(헤더)`: 메일 클라이언트가 표시하거나 분석 도구가 해석하는 메타데이터 영역. 발신자, 수신자, 경유 서버 정보가 포함됨
- `Body(본문)`: 사용자가 직접 읽는 메일 내용 영역
- `Received-SPF`: 발신 서버가 SPF 정책을 통과했는지 기록하는 헤더 항목
- `Spoofing(스푸핑)`: 발신자, 도메인, IP 등 식별 정보를 위조하여 신뢰를 가장하는 행위
- `Display Name`: 메일 클라이언트에서 사람 이름처럼 보이게 표시되는 문자열. 실제 주소와 다를 수 있음

## 이메일 전달 구조

발신자에서 수신자까지 메일이 도착하는 과정에서는 여러 메일 서버를 경유할 수 있음

![메일 분석 이론](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-015.png)

이 과정에서 사용자는 보통 본문과 표시 이름만 보게 되지만, 분석가는 `Header`를 통해 실제 경로를 확인해야 함

![메일 전달 경로](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-017.png)

메일은 `Envelope`와 `Header/Body`로 나눠 생각할 수 있음

![Envelope와 Header](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-018.png)

- `Envelope`는 서버가 실제로 전달할 대상을 결정하는 정보임
- `Header/Body`는 사용자가 읽는 메일 표현과 분석용 메타데이터다

편지 봉투의 수신자와 편지 내용의 수신자가 반드시 같을 필요는 없음

따라서 사용자가 화면에서 보는 `From` 값만으로 정상 여부를 판단하면 안 됨

## 스푸핑 관점에서 봐야 하는 지점

공격자는 `display name`을 위조하여 공공기관, 기업, 내부 담당자처럼 보이게 만들 수 있음

![표시 이름 위조](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-030.png)

또한 `Envelope From`, `Header From`, `Reply-To`, 표시 이름을 서로 다르게 설정할 수 있음

![불일치 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-032.png)

분석 시 우선적으로 확인할 항목은 다음과 같음

- 표시 이름과 실제 주소가 일치하는지
- `From`과 `Reply-To`가 일치하는지
- `Received-SPF` 결과가 자연스러운지
- 실제 경유 서버 국가와 조직이 맥락상 자연스러운지

영국 정부 기관을 사칭한 메일이 전혀 무관한 해외 서버를 경유했다면 의심 근거가 될 수 있음

## 실습 흐름

`msg` 파일을 `eml`로 변환한 뒤 헤더를 분리하여 분석함

`msg`는 메일 클라이언트 전용 바이너리 구조이므로, 바로 해석하기보다 `eml` 변환 후 확인하는 편이 유리함

![msg to eml 변환](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-022.png)

`SysTools EML Viewer`를 사용하면 실제 사용자가 보는 형태와 헤더를 함께 확인할 수 있음

![EML Viewer](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-024.png)

이후 `Mail Header Analyzer (MHA)`에 헤더를 붙여 넣어 세부 필드를 해석함

![MHA 실행](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-026.png)

![MHA 결과 해석](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-028.png)

해더 해석 과정에서는 표시 이름이 신뢰 가능한지보다, 실제 메일 주소와 경유 기록이 자연스러운지 보는 것이 더 중요함

## 정리

스피어피싱 메일은 겉보기 정보보다 `Header`와 전달 경로 분석이 핵심임

`display name`, `From`, `Reply-To`, `Received-SPF`, 경유 서버 위치가 서로 자연스럽게 이어지지 않는다면 위조 가능성을 우선적으로 의심할 수 있음





