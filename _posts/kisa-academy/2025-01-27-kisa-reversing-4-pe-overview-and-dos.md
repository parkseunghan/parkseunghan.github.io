---
title: "KISA 아카데미 정리 - 리버싱 4. PE 파일 개요와 DOS 헤더, DOS Stub"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Reverse Engineering
  - Windows Internals
  - PE Format
last_modified_at: 2025-01-27T18:00:00+09:00
published: true
permalink: /security-academy/2025-01-27-kisa-reversing-4-pe-overview-and-dos/
---
## 개요

이번 파트에서는 PE 파일이 어떤 큰 구조로 이루어져 있는지와, 파일 맨 앞에 위치하는 DOS Header, DOS Stub의 역할을 정리함

현재 Windows에서는 DOS 환경을 직접 사용하지 않더라도, PE 파일은 과거 호환성을 위해 DOS 관련 구조를 여전히 포함하고 있음

## 용어 정리

- `Portable Executable, PE(이식 가능 실행 파일)`: Windows에서 실행파일과 DLL이 따르는 표준 포맷. `.exe`, `.dll`, `.sys`가 이
- `Common Object File Format, COFF(공통 객체 파일 포맷)`: 오브젝트 파일과 실행파일 구조에 영향을 준 포맷 계열. PE는 PE-COFF라고 함께 부르는 경우가 많음
- `DOS Header(DOS 헤더)`: 파일 맨 앞에 위치하며 `MZ` 시그니처와 `e_lfanew` 등을 포함하는 구조. 로더는 여기서 PE 헤더 위치를 찾음
- `DOS Stub`: 구형 MS-DOS 환경에서 실행 시 메시지를 출력하기 위해 남아 있는 코드 영역. "이 프로그램은 DOS 모드에서 실행할 수 없습니다." 같은 문자열이 존재할 수 있음
- `Loader(로더)`: 실행파일을 메모리에 매핑하고, 헤더를 읽고, 최초 실행 지점까지 제어를 넘기는 주체. `MZ` 확인, `e_lfanew` 확인, PE 헤더 확인 순으로 진행될 수 있음
- `ImageBase(이미지 베이스)`: 실행파일이 기본적으로 매핑되길 기대하는 가상 주소 기준점. 이후 섹션과 엔트리 포인트 계산의 기준이 됨
- `AddressOfEntryPoint, Entry Point(엔트리 포인트)`: 메모리에 로드된 뒤 가장 먼저 실행될 코드의 시작 위치. 보통 `.text` 섹션 내부를 가리킴
- `Padding(패딩)`: 정렬 단위에 맞추기 위해 비워두는 공간. 헤더가 페이지보다 작아도 다음 페이지부터 섹션이 시작될 수 있음

## PE 파일의 큰 구조

PE 파일은 헤더와 여러 개의 섹션으로 구성됨

운영체제는 실행파일을 메모리에 올릴 때 헤더를 먼저 읽고, 이후 각 섹션을 어떤 주소에 어떤 권한으로 배치할지 판단함

실행 전 저장장치에 존재하는 구조와, 실행 후 메모리에 매핑된 구조는 일부 차이를 제외하면 상당히 유사함

![PE 파일 개괄 구조](/assets/images/writeup/kisa-academy/notion/reversing/reversing-024.png)

`A.exe` 구조를 먼저 이해하면 이후 DOS Header, PE Header, 섹션테이블의 역할을 연결해서 보기 쉬워짐

## 헤더가 먼저 중요한 이유

운영체제 입장에서는 다음 정보가 먼저 필요함

- 파일을 어느 가상 주소에 올릴지
- 처음 실행할 코드가 어디인지
- 이후 어떤 섹션들을 어떤 순서로 읽을지

이 기준 정보가 헤더에 존재함

헤더가 페이지보다 작더라도, 남는 영역을 그대로 사용하지 않고 다음 페이지부터 섹션이 시작될 수 있음

![헤더와 패딩 개념](/assets/images/writeup/kisa-academy/notion/reversing/reversing-025.png)

이 구조를 보면 파일 내부 정렬과 메모리 매핑 정렬이 항상 동일하지는 않음을 확인할 수 있음

## DOS Header와 DOS Stub

DOS Header는 파일의 가장 앞에 위치하며, 로더가 가장 먼저 확인하는 구조

현재 환경에서는 DOS Header의 모든 멤버를 적극적으로 사용하지는 않음

실제 분석에서 중요하게 보는 값은 다음 두 가지다

- `MZ`: PE 파일 여부를 판단하기 위한 시작 시그니처
- `e_lfanew`: PE 헤더 시작 위치를 가리키는 오프셋

DOS Stub은 MS-DOS 환경에서 실행되었을 때 메시지를 출력하기 위한 코드 영역

![DOS Stub 개념](/assets/images/writeup/kisa-academy/notion/reversing/reversing-026.png)

![DOS Header와 Stub 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-027.png)

Stub 앞부분에는 기계어 코드가, 뒷부분에는 문자열이 존재할 수 있음

![DOS Stub 문자열 영역](/assets/images/writeup/kisa-academy/notion/reversing/reversing-029.png)

## 로더가 DOS 영역을 읽는 방식

로더는 실행파일을 메모리에 올릴 때 DOS 영역 전체를 세세하게 해석하는 것이 아니라, PE 헤더로 진입하기 위한 핵심 정보 위주로 참조함

정리하면 흐름은 다음과 같음

1. `MZ` 시그니처 확인
2. `e_lfanew`를 따라 PE 헤더 위치 확인
3. PE 시그니처 확인
4. 이후 PE Header와 섹션 정보를 기준으로 파일 매핑 진행

이 때문에 DOS Header와 DOS Stub은 과거 호환성 흔적이면서도, 분석 시작점으로는 여전히 중요함

## 확인한 내용

HxD로 `sample_x32.exe`를 열어보면 DOS Header와 DOS Stub 영역을 직접 확인할 수 있음

![HxD에서 DOS Header 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-030.png)

이어지는 DOS Stub 코드도 IDA나 헥스 에디터에서 확인 가능함

![DOS Stub 코드 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-031.png)

IDA로 보면 DOS Stub 또한 코드와 문자열이 섞여 있는 구조임을 확인할 수 있음

![IDA에서 DOS Stub 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-032.png)

DOSBox 환경에서 문자열을 바꾸어 실행 결과를 확인해보면, Stub 영역이 단순 장식이 아니라 실제 코드와 문자열을 포함하는 영역임을 체감할 수 있음

![DOSBox 실습 화면](/assets/images/writeup/kisa-academy/notion/reversing/reversing-034.png)

![문자열 변경 결과](/assets/images/writeup/kisa-academy/notion/reversing/reversing-035.png)

## 정리

PE 파일은 헤더와 섹션으로 이루어지는 Windows 실행 포맷임

DOS Header는 파일 진입점 역할을 하며, `MZ`와 `e_lfanew`를 통해 로더가 PE 헤더로 이동할 수 있게 함

DOS Stub은 현재 Windows 실행에 핵심은 아니지만, 과거 호환성과 파일 구조 이해 측면에서는 여전히 의미가 있음

이 구조를 이해하면 다음 단계인 PE Header, Entry Point, Section Table 분석으로 자연스럽게 이어질 수 있음




