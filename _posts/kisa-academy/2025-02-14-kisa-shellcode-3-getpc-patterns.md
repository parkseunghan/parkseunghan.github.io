---
title: "KISA 아카데미 정리 - 쉘코드 3. GetPC 루틴 패턴"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Shellcode
  - GetPC
  - Assembly
permalink: /security-academy/2025-02-14-kisa-shellcode-3-getpc-patterns/
last_modified_at: 2025-02-14T18:00:00+09:00
published: true
---
## 개요

쉘코드가 자기 자신의 시작 위치를 찾기 위해 사용하는 `GetPC` 루틴의 의미와 대표 패턴을 다루는 파트

이 루틴은 이후 디코딩, 데이터 참조, API 해시 계산의 출발점이 됨

## 용어 정리

- `PC(Program Counter)`: 다음에 실행할 명령의 주소를 가리키는 개념. x86에서는 `EIP`, x64에서는 `RIP`가 대응됨
- `CALL/POP`: 반환 주소를 스택에 넣는 `CALL` 특성을 이용해 현재 위치를 얻는 패턴
- `FSTENV`: FPU 환경 저장 구조를 이용해 현재 명령 위치를 간접적으로 얻는 기법
- `Offset`: 기준 주소로부터 떨어진 상대적 거리값

## GetPC가 필요한 이유

쉘코드는 자신이 어느 주소에 적재될지 미리 알 수 없음

따라서 내부 데이터, 디코딩 루틴, 해시 테이블, 문자열 버퍼에 접근하려면 먼저 현재 시작 위치를 알아야 함

이 역할을 맡는 것이 `GetPC` 루틴임

## 대표 패턴

가장 기본적인 방식은 `CALL`이 반환 주소를 스택에 저장한다는 점을 이용하는 것임

즉, 특정 지점으로 `CALL`한 뒤 바로 `POP`하여 현재 근처 주소를 레지스터에 확보함

또 다른 방식은 `FSTENV`를 사용하여 FPU 환경에 저장된 명령 포인터 값을 읽어 오는 것임

이 두 방식은 문법은 다르지만 목적은 동일함

- 현재 쉘코드 기준 주소 확보
- 이후 데이터 참조에 사용할 기준점 마련

## 분석 관점

쉘코드 초반부에서 의미 없이 보이는 `CALL`, `POP`, 산술 연산, `FSTENV` 조합이 보이면 `GetPC` 가능성을 먼저 의심할 수 있음

이후 레지스터 값이 디코딩 루프나 문자열 참조에 사용됨면 확률이 더 높아짐

![GetPC 메모](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-026.png)

![GetPC 루틴 유형](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-031.png)

## 정리

`GetPC`는 쉘코드의 본격적인 기능 수행 이전에 반드시 선행되는 준비 단계

이 루틴을 식별하면 이후 디코딩, PEB 탐색, API 바인딩 흐름을 더 안정적으로 따라갈 수 있음





