---
title: "KISA 아카데미 정리 - 쉘코드 2. 동적 분석과 디버깅 환경 준비"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Shellcode
  - Dynamic Analysis
  - x32dbg
  - scdbg
permalink: /security-academy/2025-02-13-kisa-shellcode-2-dynamic-analysis-and-debug-setup/
last_modified_at: 2025-02-13T18:00:00+09:00
published: true
---
## 개요

`scdbg`를 이용한 동적 분석과 `x32dbg` 기반 디버깅 환경 준비 과정을 다루는 파트

쉘코드는 단독 실행이 어려우므로, 에뮬레이터나 호스팅 프로세스를 이용해 분석 환경을 먼저 만들어야 함

## 용어 정리

- `scdbg`: 쉘코드를 에뮬레이션하여 API 호출 흐름을 보여주는 도구
- `x32dbg`: 32비트 사용자 모드 디버거. 메모리 수정과 단계 실행에 사용됨
- `WinDbg`: 마이크로소프트 디버거. 커널/유저 모드 분석에 모두 활용 가능함
- `Host Process`: 쉘코드를 삽입하여 실행 흐름을 관찰하기 위한 정상 프로세스
- `Breakpoint`: 특정 주소에서 실행을 멈추게 하는 디버깅 지점

## scdbg를 이용한 동적 분석

`scdbg`는 쉘코드의 전체 명령어를 완전히 이해하지 못해도, 어떤 API를 호출하는지 빠르게 확인하게 해줌

![scdbg 예시 1](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-013.png)

`LoadLibraryA`, `InternetOpenA`, `InternetConnectA`, `HttpOpenRequestA`, `HttpSendRequestA`, `InternetReadFile`, `VirtualAlloc` 흐름이 등장함

이는 네트워크 연결 이후 수신 데이터를 메모리에 적재하는 전형적인 로더 흐름으로 해석할 수 있음

![scdbg 한계](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-016.png)

다만 에뮬레이터는 잘못된 메모리 접근이나 특수한 환경 의존 코드에서 중간에 멈출 수 있음

이 경우에는 디버거로 넘어가 실제 메모리 상태를 보면서 분석해야 함

## findsc 옵션

쉘코드 파일의 앞부분에 실제 쉘코드와 무관한 데이터가 섞여 있으면, 시작 주소를 잘못 잡아 분석이 실패할 수 있음

이때 `findsc` 옵션을 사용하면 실행이 가능한 지점을 후보로 제시해 줌

이 기능은 `GetPC` 루틴 이전의 더미 데이터나 ROP 조각 때문에 흐름이 끊기는 상황에서 유용함

## 디버깅 환경 준비

디버거 기반 분석에서는 쉘코드를 직접 실행하는 대신, 메모장 같은 정상 프로세스에 메모리를 할당하고 쉘코드를 붙여 넣는 방식이 일반적임

![x32dbg 준비](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-022.png)

절차는 다음과 같음

- 호스팅 프로세스 실행
- 쉘코드 크기보다 큰 메모리 공간 확보
- 덤프 창에 쉘코드 붙여 넣기
- 디스어셈블러에서 쉘코드 시작 지점으로 이동
- EIP를 시작 위치로 설정

![메모리 할당](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-024.png)

![쉘코드 크기 확인](/assets/images/writeup/kisa-academy/notion/shellcode/shellcode-025.png)

## 정리

빠른 기능 파악은 `scdbg`, 세밀한 흐름 확인은 `x32dbg`나 `WinDbg`가 담당함

에뮬레이터에서 끊기는 시점이 곧 분석 종료를 의미하지는 않으며, 오히려 디버거로 넘어가야 할 신호가 될 수 있음




