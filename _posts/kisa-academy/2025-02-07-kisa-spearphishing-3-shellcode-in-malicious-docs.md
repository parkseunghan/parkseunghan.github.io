---
title: "KISA 아카데미 정리 - 스피어피싱 3. 악성 문서 내부의 쉘코드와 바인딩"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - Spear Phishing
  - Shellcode
  - Office Document
permalink: /security-academy/2025-02-07-kisa-spearphishing-3-shellcode-in-malicious-docs/
last_modified_at: 2025-02-07T18:00:00+09:00
published: true
---
## 개요

문서형 악성코드 내부에 포함된 쉘코드, 바인딩, `scdbg` 분석 흐름을 다루는 파트

메일 분석 이후에는 첨부 문서가 어떤 방식으로 추가 페이로드를 내려받고 실행하는지 확인해야 함

## 용어 정리

- `Shellcode(쉘코드)`: 메모리에서 직접 실행되도록 구성된 기계어 코드 조각
- `Binding(바인딩)`: 필요한 DLL과 API 주소를 확보하여 실제 동작이 가능하도록 연결하는 과정
- `LoadLibrary(로드라이브러리)`: DLL을 메모리에 로드하는 API
- `GetProcAddress`: DLL 내부 함수 주소를 얻는 API
- `scdbg`: 쉘코드를 에뮬레이션하여 호출 API와 파라미터를 빠르게 확인하는 도구
- `VirtualAlloc`: 프로세스 가상 주소 공간에 메모리를 할당하는 API

## 문서형 악성코드와 쉘코드

스피어피싱 메일의 첨부 문서는 최종 페이로드가 아니라, 쉘코드를 실행시키는 전달 매개가 되는 경우가 많음

쉘코드는 문서 내부에 인코딩되거나 일부가 은닉된 형태로 존재할 수 있음

![바인딩 메모](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-039.png)

쉘코드가 실제 악성 행위를 수행하려면 우선 `LoadLibrary`, `GetProcAddress` 등을 통해 필요한 API 주소를 확보해야 함

![바인딩 흐름](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-040.png)

이 단계가 끝나야 네트워크 통신, 파일 생성, 프로세스 생성, 추가 다운로드가 가능해짐

## scdbg 기반 동작 확인

`scdbg`는 쉘코드가 호출하는 API와 인자를 빠르게 확인하는 데 유용함

![scdbg 메모](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-049.png)

`LoadLibraryA`, `InternetOpenA`, `InternetConnectA`, `HttpOpenRequestA`, `HttpSendRequestA`, `InternetReadFile`, `VirtualAlloc`과 같은 API 흐름이 등장함

이는 다음과 같은 의미를 가짐

- 통신 라이브러리 로드
- 외부 서버 연결
- HTTP 요청 생성 및 전송
- 응답 데이터 수신
- 수신 데이터 적재용 메모리 확보

즉, 문서 내부 쉘코드가 단독 악성코드라기보다 `추가 페이로드 로더`로 동작할 수 있음을 시사함

## API 해시와 은닉

쉘코드는 API 이름을 평문으로 두지 않고 해시 형태로 보관하는 경우가 많음

![API 해시 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-082.png)

이는 정적 탐지를 어렵게 만들고, 문자열 분석만으로 기능을 파악하기 어렵게 만듦

![디버깅 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-088.png)

따라서 분석 시에는 해시 계산 루틴과 비교 대상 문자열을 함께 확인해야 함

## 정리

문서형 악성코드 분석에서는 첨부 파일 자체보다, 내부 쉘코드가 `어떤 API를 확보하고 어떤 페이로드를 호출하는지`를 확인하는 것이 핵심임

`LoadLibrary`, `GetProcAddress`, `VirtualAlloc`, 네트워크 API 호출 흐름이 보임면 추가 다운로드형 공격일 가능성을 우선적으로 생각할 수 있음




