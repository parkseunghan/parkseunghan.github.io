---
title: "KISA 아카데미 정리 - 쉘코드 1. 개요와 주요 구성 요소"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Shellcode
  - Windows Internals
  - Assembly
permalink: /security-academy/2025-02-12-kisa-shellcode-1-overview-and-components/
last_modified_at: 2025-02-12T18:00:00+09:00
published: true
---
## 개요

쉘코드의 정의, 분석 목적, 실행 제약, 주요 구성 요소를 먼저 다루는 파트

쉘코드는 일반 실행 파일처럼 정돈된 형식을 갖지 않는 경우가 많으므로, 반복적으로 등장하는 루틴을 기준으로 파악하는 편이 효율적임

## 용어 정리

- `Shellcode`: 취약점 공격이나 문서형 악성코드의 페이로드로 사용되는 기계어 코드 조각
- `Payload`: 공격자가 최종적으로 실행시키려는 기능 단위. 다운로드, 명령 실행, 정보 탈취 등이 해당함
- `ASLR(Address Space Layout Randomization)`: 메모리 주소 배치를 무작위화하는 기법
- `GetPC`: 현재 코드가 적재된 시작 위치를 파악하기 위한 루틴
- `Self-Decoding`: 인코딩 또는 암호화된 본체 코드를 해제하는 루틴
- `Self-Binding`: 필요한 DLL과 API 주소를 스스로 확보하는 과정

## 쉘코드란 무엇인가

쉘코드는 공격 대상 프로그램의 메모리 공간에서 임의로 로드되어 실행되는 작은 크기의 코드다

오늘날 쉘코드는 실행 파일 형태보다, 기계어 코드와 데이터로만 구성된 형태로 더 자주 등장함

![WinDbg](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-001.png)

분석의 핵심은 다음 두 가지다

- 어떤 라이브러리와 API를 호출하는지
- 각 API에 어떤 파라미터를 넘기는지

이 두 가지를 확인하면 쉘코드가 최종적으로 무엇을 하려는지 방향을 빠르게 잡을 수 있음

## 분석 방식

분석 방법은 크게 에뮬레이터 기반 동적 분석과 디버거 기반 분석으로 나뉨

![디버거 메모](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-002.png)

`scdbg` 같은 에뮬레이터는 빠르게 흐름을 보는 데 유리함

반면 `x32dbg`, `WinDbg` 같은 디버거는 메모리 조작과 중단점 제어가 자유롭지만, 리버싱 기초 지식이 더 많이 필요함

## 쉘코드가 마주치는 제약

쉘코드는 메모리의 무작위 공간에 적재될 수 있으므로, 자신이 어디에 올라와 있는지 먼저 알아야 함

![가상주소공간](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-004.png)

실행 파일은 정식 로딩 과정을 거치지만, 쉘코드는 보통 힙이나 스택과 같은 임시 공간에 적재됨

![임의 적재](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-007.png)

또한 쉘코드 내부에 필요한 문자열과 함수명을 그대로 두면 탐지가 쉬워지므로, 인코딩·암호화·해시화가 자주 사용됨

![디코딩 필요성](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-003.png)

## 주요 구성 요소

쉘코드에서 반복적으로 확인되는 구성 요소는 다음과 같음

![주요 구성 요소](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-010.png)

- `GetPC`: 현재 코드 위치 파악
- `Self-Decoding`: 은닉 데이터 해제
- `PEB 기반 DLL 추적`: `KERNEL32.DLL` 등 핵심 라이브러리 위치 확보
- `API 주소 확보`: `LoadLibrary`, `GetProcAddress` 등을 통한 바인딩
- `API 해시 계산`: 문자열 은닉 상태 복원
- `기능 구현 루틴`: 네트워크 통신, 파일 조작, 프로세스 생성 등 실제 행위 수행

![GetPC 의미](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-011.png)

## 정리

쉘코드 분석은 형태보다 루틴을 보는 작업임

현재 위치 확인, 디코딩, DLL 추적, API 바인딩이라는 반복 구조를 기준으로 보면 복잡한 코드도 단계적으로 따라갈 수 있음





