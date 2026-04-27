---
title: "KISA 아카데미 정리 - YARA 5. 모듈 활용과 IOC 기반 트리아지"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - YARA
  - IOC
  - Triage
last_modified_at: 2025-02-11T18:00:00+09:00
published: true
permalink: /security-academy/2025-02-11-kisa-yara-5-modules-and-ioc-triage/
---
## 개요

YARA는 문자열 매칭만으로 끝나지 않음

`pe`, `hash`, `math`, `console` 같은 모듈을 쓰면 파일 크기, 해시, 엔트리포인트, imphash, timestamp 같은 메타정보까지 조건에 넣을 수 있음

모듈 활용과 IOC 조합 전략을 정리함

## 용어 정리

- `Module(모듈)`: YARA가 파일 구조나 부가정보를 해석하도록 도와주는 확장 기능. `pe`, `hash`, `math`, `console`
- `imphash(임프해시)`: 임포트 DLL과 함수 조합을 기반으로 계산한 해시값. 유사 계열 샘플 묶음에 자주 사용됨
- `Timestamp(타임스탬프)`: PE 헤더 등에 기록된 생성 또는 빌드 시각 정보. Epoch 시간과 함께 사용함
- `Icon Group(아이콘 그룹)`: 실행파일 리소스에 포함된 아이콘 데이터 집합. 특정 계열 샘플 식별에 IOC로 쓸 수 있음

## 자주 쓰는 모듈

대표 모듈은 다음과 같음

- `pe`
- `hash`
- `math`
- `time`
- `console`

![YARA 모듈 개요](/assets/images/writeup/kisa-academy/notion/yara/yara-069.png)

패킹 여부, 파일 크기, 엔트리포인트, 해시값처럼 문자열만으로 잡기 어려운 특징을 여기에 넣을 수 있음

![패킹과 EntryPoint](/assets/images/writeup/kisa-academy/notion/yara/yara-070.png)

## hash, pe, console 활용

`hash` 모듈은 파일 전체나 특정 범위의 MD5 계산에 사용할 수 있음

`pe` 모듈은 `imphash`, `entry_point`, `timestamp`, `subsystem` 같은 PE 구조 정보를 읽는 데 유용함

`console` 모듈은 값을 화면에 출력해 디버깅성 확인을 할 때 사용함

![MD5 모듈 예시](/assets/images/writeup/kisa-academy/notion/yara/yara-071.png)

![imphash 출력](/assets/images/writeup/kisa-academy/notion/yara/yara-072.png)

![imphash 비교](/assets/images/writeup/kisa-academy/notion/yara/yara-073.png)

파일 크기와 엔트로피도 조합 조건으로 넣을 수 있음

![filesize 조건](/assets/images/writeup/kisa-academy/notion/yara/yara-074.png)

![엔트로피 조건](/assets/images/writeup/kisa-academy/notion/yara/yara-075.png)

## 문서와 아이콘을 IOC로 쓰는 방법

후반부에서는 YARA 공식 문서를 찾아 필요한 필드를 직접 조합하는 방식도 다룸

예를 들어 GUI 실행파일이면서 특정 시기 제작된 샘플만 찾는 조건은 `pe.subsystem`, `filesize`, `pe.timestamp`를 묶어서 만들 수 있음

![문서 기반 Rule 작성 1](/assets/images/writeup/kisa-academy/notion/yara/yara-076.png)

![문서 기반 Rule 작성 2](/assets/images/writeup/kisa-academy/notion/yara/yara-077.png)

또한 마지막 `InternalName`, `imphash`만으로 해결되지 않을 때 아이콘 그룹 자체를 IOC로 쓰는 전략을 확인함

![아이콘 비교 1](/assets/images/writeup/kisa-academy/notion/yara/yara-078.png)

![아이콘 비교 2](/assets/images/writeup/kisa-academy/notion/yara/yara-079.png)

즉, 문자열이 흔들려도 리소스나 시각적 요소가 계열성을 유지하는 경우가 있다는 의미

## 정리

YARA의 강점은 문자열 탐지를 넘어서 파일 구조 메타데이터까지 조건에 넣을 수 있다는 점임

`pe`, `hash`, `console` 모듈을 익히면 Rule 품질이 크게 올라감

IOC 형태: 문자열, `imphash`, timestamp, 아이콘 그룹




