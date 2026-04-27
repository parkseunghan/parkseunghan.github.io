---
title: "KISA 아카데미 정리 - 리버싱 7. 임포트 매커니즘과 IAT"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Reverse Engineering
  - Windows Internals
  - PE Format
  - DLL
last_modified_at: 2025-01-30T18:00:00+09:00
published: true
permalink: /security-academy/2025-01-30-kisa-reversing-7-import-mechanism-and-iat/
---
## 개요

실행파일은 보통 혼자 모든 기능을 처리하지 않음

Windows API가 들어 있는 DLL을 함께 사용해야 정상 동작하는 경우가 많으며, 이 관계를 구조화해두는 영역이 임포트 매커니즘임

Import Table, Import Descriptor, IAT를 중심으로 실행파일이 DLL과 API를 연결하는 방식을 정리함

## 용어 정리

- `Import(임포트)`: 실행파일이 외부 DLL의 함수나 심볼을 사용하도록 연결하는 구조. `CreateFileA`, `LoadLibraryA` 호출이 대표적 예시
- `Import Table(임포트 테이블)`: 실행파일이 어떤 DLL과 API를 필요로 하는지 정리한 영역. 보통 `.idata` 섹션과 연결해서 봄
- `IMAGE_IMPORT_DESCRIPTOR(임포트 디스크립터)`: 하나의 DLL에 대한 임포트 정보를 담는 구조체. 여러 개가 배열처럼 이어질 수 있음
- `Name(이름 필드)`: 어떤 DLL을 참조하는지 가리키는 필드. `KERNEL32.dll` 문자열을 따라갈 수 있음
- `FirstThunk(퍼스트 thunk)`: 실제 함수 주소들이 기록될 IAT 시작 위치를 가리키는 필드. 로딩 이후 API 주소가 채워짐
- `Import Address Table, IAT(임포트 주소 테이블)`: 실행 시 실제 API 주소가 저장되는 배열 형태의 영역. 함수 호출은 이 값을 통해 이루어질 수 있음
- `Binding(바인딩)`: DLL이 로드된 뒤 실제 함수 주소를 찾아 테이블에 기록하는 과정. 로딩 전에는 정확한 주소를 알 수 없음
- `Address Space Layout Randomization, ASLR(주소 공간 배치 난수화)`: 모듈의 적재 주소를 실행할 때마다 바꿔 예측을 어렵게 만드는 기법. 고정 주소 가정을 어렵게 만듦

## 실행파일이 DLL을 필요로 하는 이유

실행파일은 메모리에 올라간 뒤에도 Windows API를 사용해야 하는 경우가 많음

즉, 실행파일만 로드되는 것으로 끝나는 것이 아니라, 필요한 DLL 역시 함께 메모리에 매핑되어야 함

![DLL도 함께 매핑되어야 하는 이유](/assets/images/writeup/kisa-academy/notion/reversing/reversing-068.png)

이 관계를 정리한 구조가 Import Table임

![Import 구조 개요](/assets/images/writeup/kisa-academy/notion/reversing/reversing-069.png)

보통 관련 정보는 `.idata` 영역에서 확인할 수 있음

## Import Table과 Descriptor

Import Table은 여러 개의 `IMAGE_IMPORT_DESCRIPTOR`가 모여 있는 구조로 이해할 수 있음

하나의 Import Descriptor는 일반적으로 하나의 DLL과 연결됨

![Import Descriptor 개념](/assets/images/writeup/kisa-academy/notion/reversing/reversing-070.png)

실행파일이 함수를 호출하려면, 결국 어떤 DLL에서 어떤 함수를 가져올지 먼저 알아야 함

![DLL과 API 호출 흐름](/assets/images/writeup/kisa-academy/notion/reversing/reversing-071.png)

이때 중요한 멤버는 `Name`과 `FirstThunk`다

- `Name`: 참조 대상 DLL 이름 확인
- `FirstThunk`: 실제 API 주소들이 저장될 IAT 위치 확인

![바인딩과 주소 채우기](/assets/images/writeup/kisa-academy/notion/reversing/reversing-072.png)

![FirstThunk와 IAT](/assets/images/writeup/kisa-academy/notion/reversing/reversing-073.png)

![Name과 DLL 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-074.png)

## 로딩 이후 주소가 채워지는 이유

빌드 시점에는 DLL과 API의 최종 메모리 주소를 확정할 수 없음

ASLR과 로딩 시점 환경에 따라 실제 적재 주소가 달라질 수 있기 때문임

따라서 실행파일이 메모리에 올라간 뒤, 로더가 DLL을 적재하고 실제 함수 주소를 찾아 IAT에 기록하는 과정이 필요함

이 과정을 바인딩 관점에서 이해할 수 있음

즉, 코드에서는 외부 함수 호출을 준비해두고, 실제 주소는 실행 시점에 채워짐

## 확인한 내용

`CFF Explorer`에서 Import Table을 열면 각 Descriptor와 포인터 값을 직접 확인할 수 있음

![CFF Explorer Import Table 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-075.png)

![CFF Explorer Import Table 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-076.png)

하나의 Import Descriptor는 여러 멤버로 이루어지며, 여기서 `Name`과 `FirstThunk`를 따라가면 DLL 이름과 API 주소 집합을 볼 수 있음

![Import Descriptor 구조](/assets/images/writeup/kisa-academy/notion/reversing/reversing-078.png)

`Name`이 가리키는 위치로 이동하면 `KERNEL32.dll` 같은 문자열이 나타남

![Name 필드 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-079.png)

`FirstThunk`가 가리키는 위치로 이동하면 API 주소 배열이 보임

![FirstThunk 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-080.png)

![IAT 끝 지점](/assets/images/writeup/kisa-academy/notion/reversing/reversing-081.png)

![sample_x32의 IAT 예시](/assets/images/writeup/kisa-academy/notion/reversing/reversing-082.png)

이 구조를 이해하면 IAT 후킹처럼 공격자가 API 주소를 바꾸는 기법도 자연스럽게 연결해서 이해할 수 있음

## 정리

실행파일은 DLL과 API 없이 완전하게 동작하지 않는 경우가 많음

Import Table은 필요한 DLL과 API를 구조화한 영역이며, `IMAGE_IMPORT_DESCRIPTOR`와 IAT가 핵심 역할을 담당함

`Name`은 DLL을, `FirstThunk`는 실제 함수 주소 배열을 가리킴

이 구조를 이해하면 DLL 로딩, API 호출, IAT 후킹 분석까지 하나의 흐름으로 이어서 볼 수 있음




