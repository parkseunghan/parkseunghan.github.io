---
title: "KISA 아카데미 정리 - 쉘코드 5. Export Table 추적과 API 확보"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Shellcode
  - Export Table
  - PE Format
permalink: /security-academy/2025-02-16-kisa-shellcode-5-export-table-tracing/
last_modified_at: 2025-02-16T18:00:00+09:00
published: true
---
## 개요

`KERNEL32.DLL`의 베이스 주소를 확보한 뒤, `Export Table`을 따라 필요한 API 주소를 찾는 과정을 다루는 파트

쉘코드는 일반 프로그램처럼 IAT를 정식으로 구성하지 않으므로, 필요한 함수 주소를 직접 계산하는 경우가 많음

## 용어 정리

- `Export Table`: DLL이 외부에 제공하는 함수 이름, Ordinal, 주소 정보를 저장한 영역
- `RVA(Relative Virtual Address)`: 모듈 베이스 기준 상대 주소
- `Ordinal`: 함수에 부여된 정수 인덱스 값
- `Function Address Table`: 실제 함수 주소 목록을 담는 테이블
- `Name Pointer Table`: 함수 이름 문자열 위치를 가리키는 테이블

## Export Table을 보는 이유

쉘코드는 `KERNEL32.DLL` 베이스 주소만 알아서는 실제 API를 호출할 수 없음

어떤 위치에 `LoadLibraryA`, `GetProcAddress`, `VirtualAlloc` 등이 있는지 찾아야 함

이때 사용하는 것이 `Export Table`임

![Export Table 메모](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-069.png)

일반적인 추적 흐름은 다음과 같음

- DOS Header 확인
- NT Header 확인
- Optional Header에서 Export Directory 위치 확인
- 이름 테이블 순회
- 원하는 API 이름과 일치하는 항목 찾기
- 대응 함수 주소 계산

![테이블 순회](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-076.png)

## 분석 포인트

쉘코드 안에서 반복문이 돌면서 문자열을 비교하거나 해시를 계산하는 경우, `Export Table` 순회 가능성을 우선적으로 의심할 수 있음

특히 다음과 같은 패턴이 자주 보임

- 이름 포인터 배열 순회
- 각 함수명에 대한 비교 또는 해시 계산
- 일치 시 Ordinal 참조
- Ordinal을 이용해 실제 함수 주소 테이블 접근

![분석 메모](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-086.png)

## 정리

Export Table 추적은 쉘코드가 운영체제 API를 직접 확보하는 핵심 단계

이 과정을 이해하면 정적 IAT가 없는 코드에서도 어떤 함수를 호출하려는지 단계적으로 복원할 수 있음





