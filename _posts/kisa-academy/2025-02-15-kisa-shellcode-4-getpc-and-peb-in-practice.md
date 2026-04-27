---
title: "KISA 아카데미 정리 - 쉘코드 4. GetPC와 PEB 기반 주소 추적 실습"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Shellcode
  - GetPC
  - PEB
permalink: /security-academy/2025-02-15-kisa-shellcode-4-getpc-and-peb-in-practice/
last_modified_at: 2025-02-15T18:00:00+09:00
published: true
---
## 개요

`GetPC` 이후 실제로 `PEB`를 따라가며 `KERNEL32.DLL` 베이스 주소를 찾는 흐름을 다루는 파트

쉘코드는 OS가 제공하는 API를 사용해야 하므로, 핵심 DLL의 시작 주소를 확보하는 절차가 필수적임

## 용어 정리

- `PEB(Process Environment Block)`: 프로세스 환경 정보와 로드된 모듈 정보를 담고 있는 구조체
- `TEB(Thread Environment Block)`: 스레드 관련 정보를 담는 구조체이며, PEB 접근의 출발점이 될 수 있음
- `KERNEL32.DLL`: 프로세스 생성, 메모리 할당, 라이브러리 로딩 등 핵심 Windows API를 담고 있는 라이브러리
- `Base Address`: 모듈이 메모리에 로드된 시작 주소

## 왜 PEB를 보는가

쉘코드는 `LoadLibrary`, `GetProcAddress`를 사용하기 전, 이 함수들이 들어 있는 `KERNEL32.DLL`의 위치를 먼저 알아야 함

문제는 DLL이 어느 주소에 로드될지 고정되어 있지 않다는 점임

이때 `PEB`를 따라가면 현재 프로세스에 로드된 모듈 목록을 확인할 수 있음

![FSTENV 메모](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-035.png)

![PEB 개요](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-053.png)

## 추적 흐름

일반적인 흐름은 다음과 같음

- `GetPC`로 자기 위치 확보
- `TEB` 또는 세그먼트 레지스터를 통해 `PEB` 접근
- 로드된 모듈 리스트 순회
- `KERNEL32.DLL` 식별
- 베이스 주소 확보

![KERNEL32 추적](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-056.png)

이 단계가 완료되면 이후 `Export Table`을 따라가 필요한 API 이름과 주소를 대응시킬 수 있음

## 실습 관점

`GetPC` 루틴 직후 이어지는 포인터 추적과 구조체 접근을 확인하는 것이 핵심임

단순히 메모리를 읽는 코드처럼 보여도, 실제로는 `PEB -> Ldr -> 모듈 리스트`를 순회하는 흐름일 수 있음

분석 시 다음 질문을 두고 보면 도움이 됨

- 지금 읽는 포인터가 어떤 구조체를 가리키는가
- 반복문이 모듈 리스트 순회에 해당하는가
- 특정 문자열 비교 또는 해시 비교가 `KERNEL32.DLL` 식별에 사용되는가

## 정리

PEB 기반 주소 추적은 쉘코드의 셀프 바인딩에서 가장 중요한 준비 단계 중 하나다

이 흐름을 파악하면 이후 `Export Table`, `GetProcAddress` 대체 루틴까지 자연스럽게 이어서 분석할 수 있음





