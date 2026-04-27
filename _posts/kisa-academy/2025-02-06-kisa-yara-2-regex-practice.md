---
title: "KISA 아카데미 정리 - YARA 2. 정규표현식 실습 정리"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - YARA
  - Regex
last_modified_at: 2025-02-06T18:00:00+09:00
published: true
permalink: /security-academy/2025-02-06-kisa-yara-2-regex-practice/
---
## 개요

정규표현식은 문법만 외우는 것보다 문제 형태로 반복해서 익히는 쪽이 빠름

정규표현식 예제를 유형별로 묶어서 정리함

## 용어 정리

- `Digit Class(숫자 클래스)`: 숫자만 매칭하는 표현. `\\d`
- `Non-word Character(비단어 문자)`: 영문자, 숫자, 밑줄을 제외한 문자. `\\W`
- `Non-whitespace(공백 제외 문자)`: 공백이 아닌 문자를 뜻함. `\\S`
- `Word Boundary(단어 경계)`: 문자열 경계나 단어 구분 위치. `\\b`
- `Quantifier(반복 횟수)`: 특정 패턴이 몇 번 반복되는지 정하는 표현. `*`, `+`, `{2,4}`

## 기본 문제

기본 문제에서는 숫자, 특수문자, 공백 제외 문자, 단어 경계 같은 가장 자주 쓰는 패턴을 반복적으로 사용함

```text
/\\d/g
/\\W/g
/\\S/g
```

![기본 문제 예시 1](/assets/images/writeup/kisa-academy/notion/yara/yara-008.png)

![기본 문제 예시 2](/assets/images/writeup/kisa-academy/notion/yara/yara-009.png)

![기본 문제 예시 3](/assets/images/writeup/kisa-academy/notion/yara/yara-010.png)

## 단어 끝, 반복, 그룹 처리

문제 유형이 조금만 복잡해지면 단어 경계, 반복 횟수, 그룹 캡처가 같이 등장함

예를 들어:

- 특정 접미사로 끝나는 문자열
- 같은 문자가 반복되는 형태
- 그룹 안에서 선택적으로 매칭되는 형태

![경계 처리](/assets/images/writeup/kisa-academy/notion/yara/yara-011.png)

![반복 처리](/assets/images/writeup/kisa-academy/notion/yara/yara-012.png)

![그룹 처리](/assets/images/writeup/kisa-academy/notion/yara/yara-013.png)

## 응용 문제

응용 문제에서는 실제 데이터 형식에 가까운 패턴을 다룸

예:

- 전화번호
- 이메일
- URL
- 해시값
- 형식이 정해진 코드 문자열

![전화번호 패턴](/assets/images/writeup/kisa-academy/notion/yara/yara-017.png)

![이메일 패턴](/assets/images/writeup/kisa-academy/notion/yara/yara-019.png)

![URL 패턴](/assets/images/writeup/kisa-academy/notion/yara/yara-022.png)

![해시 패턴](/assets/images/writeup/kisa-academy/notion/yara/yara-023.png)

이런 유형은 이후 YARA Rule 안에서 문자열 조건을 더 정교하게 만들 때 바로 연결됨

## 정리

정규표현식 실습의 핵심은 기호를 외우는 것이 아니라, "어떤 입력 형식을 잡고 싶은가"를 먼저 떠올리는 데 있음

숫자, 경계, 반복, 그룹, URL/이메일/해시 패턴 정도가 익숙해지면 YARA 문자열 조건 작성도 훨씬 수월해짐


