---
title: "KISA 아카데미 정리 - YARA 1. 정규표현식과 YARA의 관계"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - YARA
  - Regex
last_modified_at: 2025-02-05T18:00:00+09:00
published: true
permalink: /security-academy/2025-02-05-kisa-yara-1-regex-and-yara/
---
## 개요

YARA는 파일을 분류하는 도구이고, 정규표현식은 문자열의 규칙을 표현하는 도구

둘은 역할이 다르지만 함께 쓰면 고정 문자열 기반 탐지보다 더 유연한 분류가 가능해짐

정규표현식이 왜 YARA와 연결되는지, 어떤 식으로 탐지율 조정에 기여하는지 정리함

## 용어 정리

- `YARA`: 파일 안의 문자열, 바이트 패턴, 조건을 이용해 대상을 분류하는 도구. 악성 파일 1차 분류와 트리아지에 적합함
- `Regular Expression, Regex(정규표현식)`: 문자열의 일정한 규칙을 표현하는 형식 언어. 대소문자 변형, 반복 패턴 탐지에 강함
- `Greedy Quantifier(탐욕적 수량자)`: 가능한 한 많이 매칭하려는 방식. 탐지 범위가 넓어져 오탐이 늘 수 있음
- `Lazy Quantifier(게으른 수량자)`: 가능한 한 적게 매칭하려는 방식. 과도한 탐지를 줄이는 데 유리함
- `Triage(트리아지)`: 대량의 파일 중 우선 분석 대상을 좁히는 과정. YARA의 대표 용도

## YARA와 정규표현식의 차이

YARA는 특정 파일이 어떤 패턴을 가지는지 기준으로 분류함

정규표현식은 문자열이 어떤 규칙을 가지는지 표현함

즉, YARA는 "무엇을 분류할 것인가"에 가깝고, 정규표현식은 "어떤 문자열 규칙으로 잡을 것인가"에 가까움

둘을 결합하면 단순 고정 문자열보다 더 유연한 룰을 만들 수 있음

예를 들어 대소문자 변형이나 일부 변형된 문자열은 단순 비교로 놓칠 수 있지만, 정규표현식을 쓰면 묶어서 표현할 수 있음

![정규표현식 활용 예시](/assets/images/writeup/kisa-academy/notion/yara/yara-001.png)

## 정규표현식 기본 요소

정규표현식의 기본 요소를 다음 순서로 정리함

- 문자 표현
- 이스케이프 문자열
- 앵커
- 그룹
- 수량자
- 플래그

![문자 표현](/assets/images/writeup/kisa-academy/notion/yara/yara-002.png)

![이스케이프 문자열](/assets/images/writeup/kisa-academy/notion/yara/yara-003.png)

![앵커](/assets/images/writeup/kisa-academy/notion/yara/yara-004.png)

![그룹](/assets/images/writeup/kisa-academy/notion/yara/yara-005.png)

![수량자](/assets/images/writeup/kisa-academy/notion/yara/yara-006.png)

![플래그](/assets/images/writeup/kisa-academy/notion/yara/yara-007.png)

## 정리

YARA는 분류 도구이고, 정규표현식은 문자열 규칙 표현 도구

정규표현식을 적절히 섞으면 변종 대응력과 표현력을 높일 수 있음

이 관점이 잡혀 있어야 이후 YARA Rule 작성 시 `문자열 하드코딩`을 넘어서 더 유연한 탐지 조건을 만들 수 있음



