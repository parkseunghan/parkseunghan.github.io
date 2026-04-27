---
title: "KISA 아카데미 정리 - YARA 3. Rule 구조와 기본 작성법"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - YARA
last_modified_at: 2025-02-07T18:00:00+09:00
published: true
permalink: /security-academy/2025-02-07-kisa-yara-3-rule-structure-and-basics/
---
## 개요

YARA는 도구 자체보다 Rule을 어떻게 설계하느냐가 중요함

YARA 개념, Rule 구조, 가장 기본적인 문자열/바이트 패턴 Rule 작성 방식을 정리함

## 용어 정리

- `Rule(룰)`: 특정 파일을 어떤 기준으로 탐지할지 정의한 단위. `.yar` 파일 안에 여러 개 존재할 수 있음
- `Meta Section(메타 영역)`: 룰 설명, 작성자, 목적 같은 부가정보를 적는 영역. 탐지에는 직접 영향이 없음
- `Strings Section(문자열 영역)`: 찾고 싶은 문자열, 바이트 패턴, 정규표현식을 적는 영역. `$a = "potato"` 형태
- `Condition Section(조건 영역)`: 어떤 문자열 조합이 만족되면 탐지할지 정하는 영역. `all of them`, `any of them`
- `include`: 다른 Rule 파일을 불러와 함께 실행하는 기능. 유사 그룹 Rule 묶음에 유용함

## YARA의 기본 성격

YARA는 이미 알려진 패턴을 빠르게 분류하는 데 강함

즉, 본격 분석 전에 대량 파일을 좁히는 트리아지 용도로 적합함

다만 알려지지 않은 샘플이나 패턴이 크게 바뀐 변종에 대해서는 탐지율이 낮아질 수 있음

![YARA 개념 1](/assets/images/writeup/kisa-academy/notion/yara/yara-025.png)

![YARA 개념 2](/assets/images/writeup/kisa-academy/notion/yara/yara-026.png)

![YARA 개념 3](/assets/images/writeup/kisa-academy/notion/yara/yara-027.png)

![YARA 개념 4](/assets/images/writeup/kisa-academy/notion/yara/yara-028.png)

![트리아지 관점](/assets/images/writeup/kisa-academy/notion/yara/yara-029.png)

## Rule 구조

YARA Rule은 보통 다음 구조로 작성함

```yara
rule sample_rule {
    meta:
        author = "ParkSeungHan"
        description = "설명"
    strings:
        $a = "sample"
    condition:
        all of them
}
```

Rule 파일 하나 안에 여러 Rule을 넣을 수 있고, `include`로 다른 파일을 불러와 함께 실행할 수도 있음

![Rule 구조 1](/assets/images/writeup/kisa-academy/notion/yara/yara-030.png)

![Rule 구조 2](/assets/images/writeup/kisa-academy/notion/yara/yara-031.png)

![include 개념](/assets/images/writeup/kisa-academy/notion/yara/yara-033.png)

메타 영역 역할: 탐지 직접 영향 없음, 룰 유지보수용

![meta 설명 1](/assets/images/writeup/kisa-academy/notion/yara/yara-036.png)

![meta 설명 2](/assets/images/writeup/kisa-academy/notion/yara/yara-037.png)

## 기본 Rule 작성 예시

기본 유형은 다음과 같음

- 고정 문자열 탐지
- 16진수 바이트열 탐지
- 대소문자 무시 탐지
- 여러 문자열 중 하나 또는 전부 만족

![문자열 Rule](/assets/images/writeup/kisa-academy/notion/yara/yara-043.png)

![HxD로 확인](/assets/images/writeup/kisa-academy/notion/yara/yara-045.png)

![16진수 Rule](/assets/images/writeup/kisa-academy/notion/yara/yara-046.png)

![nocase Rule](/assets/images/writeup/kisa-academy/notion/yara/yara-049.png)

이 단계의 핵심은 복잡한 조건보다 `내가 무엇을 잡고 싶은가`를 명확히 적는 일임

## 정리

YARA Rule의 기본은 `meta`, `strings`, `condition` 세 부분으로 이해하면 됨

문자열, 바이트 패턴, 정규표현식, `all of them`, `any of them` 정도만 익숙해져도 기본적인 분류 Rule은 빠르게 만들 수 있음

이후에는 실제 악성코드 특성을 반영한 Rule 설계가 중요해짐



