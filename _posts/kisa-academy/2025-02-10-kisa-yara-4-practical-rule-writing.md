---
title: "KISA 아카데미 정리 - YARA 4. 실전 Rule 작성과 유사 샘플 분류"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - YARA
  - IOC
last_modified_at: 2025-02-10T18:00:00+09:00
published: true
permalink: /security-academy/2025-02-10-kisa-yara-4-practical-rule-writing/
---
## 개요

실전에서는 단일 문자열 하나로 끝나지 않음

문자열, 라이브러리, 함수명, 고유 패턴을 조합해 점점 후보를 좁혀가는 방식이 필요함

유사 샘플 분류 과정을 정리함

## 용어 정리

- `Indicator of Compromise, IOC(지표)`: 악성 샘플을 식별하는 데 사용할 수 있는 특징 정보. 문자열, 도메인, 경로, API, 아이콘, 해시
- `Unique String(고유 문자열)`: 동일 계열 샘플에서 반복되지만 일반 프로그램에는 잘 없는 문자열. 패딩 문자열, 내부 식별자
- `Imported Library(임포트 라이브러리)`: PE 파일이 사용하는 DLL 목록. `WS2_32.dll`, `KERNEL32.dll`
- `Imported Function(임포트 함수)`: PE 파일이 사용하는 API 이름. `CreateFileA`, `FindFirstFileA`
- `Packing(패킹)`: 실행 코드를 압축/난독화해 원본 분석을 어렵게 만드는 기법. `UPX`가 대표적

## 문자열로 1차 분류

먼저 `bintext`를 통해 고유 문자열을 찾고, 그 문자열을 Rule에 넣어 1차 후보를 좁힘

예를 들어 `PADDINGXX`처럼 일반 프로그램에서는 잘 쓰지 않는 문자열이 있으면 좋은 출발점이 됨

![응용 문제 시작](/assets/images/writeup/kisa-academy/notion/yara/yara-061.png)

![bintext로 문자열 확인](/assets/images/writeup/kisa-academy/notion/yara/yara-062.png)

![1차 Rule 결과](/assets/images/writeup/kisa-academy/notion/yara/yara-063.png)

## 라이브러리와 함수로 2차 분류

같은 계열 샘플은 비슷한 라이브러리와 API를 사용할 가능성이 높음

따라서 문자열만으로 충분히 좁혀지지 않으면, 임포트 라이브러리와 함수명을 추가 조건으로 넣을 수 있음

![CFF Explorer로 라이브러리 확인](/assets/images/writeup/kisa-academy/notion/yara/yara-064.png)

![추가 필터링 결과](/assets/images/writeup/kisa-academy/notion/yara/yara-065.png)

이 방식은 문자열 하나만 쓸 때보다 오탐을 줄이는 데 유리함

## 패킹 샘플 분류

패킹된 샘플은 문자열보다 엔트리포인트 바이트 패턴이 더 유효할 수 있음

`UPX` 패킹 샘플을 기준으로 엔트리포인트 바이트열을 추출해 Rule에 적용함

![패킹 전후 비교 1](/assets/images/writeup/kisa-academy/notion/yara/yara-066.png)

![패킹 전후 비교 2](/assets/images/writeup/kisa-academy/notion/yara/yara-067.png)

![Stud_PE에서 EntryPoint 확인](/assets/images/writeup/kisa-academy/notion/yara/yara-068.png)

이후 `pe.entry_point` 위치에서 바이트 패턴이 맞는지 조건을 줄 수 있음

## 정리

실전 Rule 작성은 한 번에 정답을 맞히는 방식보다, 문자열 -> 라이브러리 -> 함수 -> 엔트리포인트처럼 점진적으로 좁히는 방식이 안정적임

결국 핵심은 "변동이 적은 특징"을 IOC로 고르는 일임

이 감각이 잡혀야 Rule을 많이 써도 유지보수가 가능해짐




