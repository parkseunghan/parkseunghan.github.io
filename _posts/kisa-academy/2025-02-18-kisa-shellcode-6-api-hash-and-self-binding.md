---
title: "KISA 아카데미 정리 - 쉘코드 6. API 해시와 셀프 바인딩"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Shellcode
  - API Hash
  - Self Binding
permalink: /security-academy/2025-02-18-kisa-shellcode-6-api-hash-and-self-binding/
last_modified_at: 2025-02-18T18:00:00+09:00
published: true
---
## 개요

쉘코드가 API 이름을 해시로 관리하고, 최종적으로 필요한 함수 주소를 테이블화하는 `셀프 바인딩` 과정을 다루는 파트

앞선 `GetPC`, `PEB`, `Export Table` 분석의 최종 연결점에 해당함

## 용어 정리

- `API Hash`: 함수명 문자열을 직접 저장하지 않고 해시 값으로 대체한 값
- `Self Binding`: 쉘코드가 스스로 필요한 API 주소를 수집하고 관리하는 과정
- `Hash Function`: 문자열을 고정 길이 값으로 변환하는 함수
- `Resolver`: 해시 또는 이름을 기준으로 실제 API 주소를 찾아내는 루틴

## 왜 API 해시를 쓰는가

쉘코드 안에 `CreateProcessA`, `URLDownloadToFileA`, `WinExec` 같은 문자열이 그대로 들어 있으면 탐지와 분석이 쉬워짐

따라서 공격자는 함수명을 해시로 바꿔 저장하고, 실행 시점에만 원래 함수와 대응시키는 방식을 자주 사용함

![API 해시 메모](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-094.png)

이 방식은 다음 장점이 있음

- 평문 문자열 노출 감소
- 크기 절감
- 단순 문자열 기반 탐지 우회

## 셀프 바인딩 흐름

셀프 바인딩은 보통 다음 절차로 진행됨

- `KERNEL32.DLL` 등 핵심 DLL 베이스 주소 확보
- `Export Table` 순회
- 각 함수명에 대해 해시 계산
- 내부에 저장된 해시와 비교
- 일치하는 함수 주소를 별도 테이블에 저장

![해시 계산 예시](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-100.png)

이후 실제 악성 행위 루틴은 평문 이름 대신, 미리 저장된 함수 주소 테이블을 호출하게 됨

## 분석 포인트

API 해시 루틴은 산술 연산, 비트 이동, 반복 비교가 많이 보이는 특징이 있음

다음과 같은 상황에서 해시 루틴 가능성을 생각할 수 있음

- 짧은 문자열 반복 순회
- 누산기 레지스터를 사용한 반복 계산
- 계산 결과와 상수 목록 비교

![셀프 바인딩 메모](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-108.png)

실제 분석에서는 해시 알고리즘을 복원하거나, 후보 API 이름에 같은 알고리즘을 적용해 대조하는 방식이 사용됨

## 정리

API 해시와 셀프 바인딩은 쉘코드의 은닉성과 독립성을 높이는 핵심 장치

따라서 쉘코드 분석은 단순 명령어 추적만으로 끝나지 않으며, 해시 비교와 주소 해석 과정을 함께 풀어야 전체 기능을 복원할 수 있음





