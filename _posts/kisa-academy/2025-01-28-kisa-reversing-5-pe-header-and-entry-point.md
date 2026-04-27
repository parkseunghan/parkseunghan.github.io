---
title: "KISA 아카데미 정리 - 리버싱 5. PE 헤더와 Entry Point"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Reverse Engineering
  - Windows Internals
  - PE Format
last_modified_at: 2025-01-28T18:00:00+09:00
published: true
permalink: /security-academy/2025-01-28-kisa-reversing-5-pe-header-and-entry-point/
---
## 개요

이번 파트에서는 DOS 영역 뒤에 위치하는 PE Header와, 실행파일이 메모리에 올라간 뒤 가장 먼저 실행될 코드를 가리키는 Entry Point를 정리함

PE Header는 로더가 실행파일을 어디에 매핑할지, 어떤 코드부터 실행할지를 판단하는 핵심 기준에 해당함

## 용어 정리

- `PE Header, IMAGE_NT_HEADER(PE 헤더)`: DOS Header 뒤에 위치하는 핵심 헤더 구조. 로더는 `e_lfanew`를 따라 이 위치로 이동함
- `PE Signature(PE 시그니처)`: PE Header 시작부에 위치하는 식별 값. `PE\\0\\0` 형태로 저장됨
- `Virtual Address, VA(가상 주소)`: 메모리에 로드된 뒤 기준이 되는 주소 표현 방식. `ImageBase + RVA` 형태로 계산되는 경우가 많음
- `Relative Virtual Address, RVA(상대 가상 주소)`: 이미지 베이스를 기준으로 한 상대 위치 값. `AddressOfEntryPoint`는 보통 RVA로 저장됨
- `File Offset(오프셋)`: 파일 시작 지점을 기준으로 얼마나 떨어져 있는지를 나타내는 값. `e_lfanew`가 대표적 예시
- `ImageBase(이미지 베이스)`: 실행파일이 기본적으로 적재되길 기대하는 가상 주소 기준점. `0x00400000`이 자주 보이는 예시
- `AddressOfEntryPoint, Entry Point(엔트리 포인트)`: 메모리에 적재된 뒤 가장 먼저 실행되는 코드의 시작 위치. RVA이므로 실제 실행 주소를 구할 때는 ImageBase를 더해야 함
- `SectionAlignment(정렬 단위)`: 메모리에서 섹션을 어느 단위에 맞추어 배치할지 정하는 값. 보통 페이지 크기와 연결해서 이해함

## PE Header의 위치와 역할

PE Header는 DOS Header와 DOS Stub 뒤에 위치함

로더는 DOS Header의 `e_lfanew` 값을 따라 이동하여 PE Header를 찾고, 여기에 있는 정보를 바탕으로 실행파일 매핑을 진행함

![PE Header 진입 구조](/assets/images/writeup/kisa-academy/notion/reversing/reversing-037.png)

PE Header는 단순 식별 정보만 담는 것이 아니라, ImageBase, Entry Point, 섹션 개수, 정렬 단위 등 이후 로딩 과정 전반에 필요한 값을 포함함

![IMAGE_NT_HEADER 구조](/assets/images/writeup/kisa-academy/notion/reversing/reversing-038.png)

## 가상 주소와 오프셋 구분

리버싱 과정에서 자주 혼동되는 값이 가상 주소와 오프셋임

- 오프셋은 파일 시작 기준 위치임
- 가상 주소는 메모리에 매핑된 뒤의 위치임

PE 구조에서 `ImageBase`는 절대적인 가상 주소 기준이고, 다른 멤버들은 오프셋 또는 RVA로 표현되는 경우가 많음

![가상 주소와 오프셋](/assets/images/writeup/kisa-academy/notion/reversing/reversing-039.png)

![ImageBase 기준 설명](/assets/images/writeup/kisa-academy/notion/reversing/reversing-040.png)

![Offset 개념 정리](/assets/images/writeup/kisa-academy/notion/reversing/reversing-041.png)

이 차이를 정확히 구분해야 파일 상 위치와 메모리 상 위치를 혼동하지 않게 됨

## 로더가 실제로 보는 값

로더는 PE Header를 읽은 뒤 적재 기준 주소와 최초 실행 코드를 판단함

예를 들어 `ImageBase`가 `0x00400000`이라면, 실행파일은 이 값을 기준으로 가상주소공간에 매핑되는 것을 기대함

![ImageBase 예시](/assets/images/writeup/kisa-academy/notion/reversing/reversing-042.png)

실행파일이 메모리에 올라간 뒤에도 전체 구조는 파일 구조와 상당히 유사하게 유지됨

![메모리 매핑 후 구조](/assets/images/writeup/kisa-academy/notion/reversing/reversing-043.png)

그리고 로더는 `AddressOfEntryPoint`를 확인하여 가장 먼저 실행할 코드에 제어를 넘김

![Entry Point 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-044.png)

여기서 중요한 점은 `AddressOfEntryPoint`가 파일 오프셋이 아니라, 보통 ImageBase를 기준으로 계산해야 하는 값이라는 점임

![AddressOfEntryPoint 계산](/assets/images/writeup/kisa-academy/notion/reversing/reversing-045.png)

## 확인한 내용

`Stud_PE`와 같은 PE 분석 도구를 사용하면 헤더 구조를 시각적으로 확인할 수 있음

![Stud_PE 기본 화면](/assets/images/writeup/kisa-academy/notion/reversing/reversing-046.png)

![헤더 레이아웃 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-047.png)

확인한 주요 값은 다음과 같음

- `ImageBase = 0x00400000`
- `AddressOfEntryPoint = 0x000014A0`

따라서 실제 최초 실행 코드는 `0x004014A0`으로 계산됨

또한 `SectionAlignment` 값을 통해 각 섹션이 메모리에서 어떤 간격으로 배치되는지도 확인 가능함

![SectionAlignment 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-049.png)

![패딩과 정렬](/assets/images/writeup/kisa-academy/notion/reversing/reversing-050.png)

![권한이 다른 페이지 배치](/assets/images/writeup/kisa-academy/notion/reversing/reversing-051.png)

## 정리

PE Header는 실행파일 적재와 최초 실행을 결정하는 핵심 구조

로더는 `e_lfanew`를 통해 PE Header로 이동한 뒤, `ImageBase`와 `AddressOfEntryPoint`를 확인하고 실행 준비를 마침

분석 과정에서는 파일 오프셋, RVA, 가상 주소를 구분해서 보는 습관이 중요함

이 기준이 잡혀야 다음 단계인 Section Table과 각 섹션의 권한 분석도 자연스럽게 이어짐




