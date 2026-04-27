---
title: "KISA 아카데미 정리 - 리버싱 6. 섹션테이블과 메모리 권한"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Reverse Engineering
  - Windows Internals
  - PE Format
last_modified_at: 2025-01-29T18:00:00+09:00
published: true
permalink: /security-academy/2025-01-29-kisa-reversing-6-section-table-and-protection/
---
## 개요

이번 파트에서는 Section Table이 로더에게 어떤 기준 정보를 제공하는지와, 섹션별 권한이 어떻게 결정되는지를 정리함

PE Header가 전체 적재 기준을 제공한다면, Section Table은 각 섹션을 실제로 어디에 어떻게 올릴지 알려주는 상세 지도에 해당함

## 용어 정리

- `Section(섹션)`: 실행파일 내부에서 용도별로 구분된 영역. `.text`, `.data`, `.rdata`, `.idata` 등이 이
- `Section Table(섹션테이블)`: 각 섹션의 이름, 파일 상 위치, 메모리 상 위치, 속성을 저장하는 구조. 로더는 이를 읽고 섹션을 매핑함
- `PointerToRawData(원시 데이터 위치)`: 파일 상에서 해당 섹션이 시작되는 위치를 뜻함. 디스크에 저장된 바이트 위치를 찾을 때 사용함
- `VirtualAddress(가상 주소)`: 메모리 상에서 해당 섹션이 배치될 상대 위치를 뜻함. ImageBase를 더하면 실제 가상 주소를 구할 수 있음
- `Characteristics(특성 값)`: 섹션의 권한과 성격을 나타내는 속성 값. 읽기, 쓰기, 실행 권한이 여기에 포함됨
- `Read(읽기 권한)`: 메모리 내용을 읽을 수 있는 권한. `.rdata` 영역에서 자주 확인됨
- `Write(쓰기 권한)`: 메모리 내용을 변경할 수 있는 권한. `.data` 영역에서 주로 사용됨
- `Execute(실행 권한)`: 메모리 내용을 코드로 실행할 수 있는 권한. `.text` 영역이 대표적

## 섹션테이블이 필요한 이유

PE 파일은 섹션 수가 고정되어 있지 않음

따라서 로더는 PE Header에 기록된 섹션 개수를 먼저 확인하고, 그 개수만큼 Section Table 엔트리를 해석해야 함

![섹션테이블 개념](/assets/images/writeup/kisa-academy/notion/reversing/reversing-055.png)

섹션 이름이 `.text`, `.data`처럼 익숙한 경우가 많지만, 이름 자체보다 중요한 것은 각 엔트리가 가진 위치 정보와 속성 정보임

## 로더가 보는 핵심 멤버

Section Table에서 특히 중요하게 보는 값은 다음과 같음

- `PointerToRawData`: 파일 상 위치
- `VirtualAddress`: 메모리 상 위치
- `Characteristics`: 권한 정보

로더는 이 정보를 읽어 디스크에 있는 섹션 내용을 적절한 가상 주소에 배치함

![로더가 섹션테이블을 읽는 흐름](/assets/images/writeup/kisa-academy/notion/reversing/reversing-056.png)

![PointerToRawData와 VirtualAddress](/assets/images/writeup/kisa-academy/notion/reversing/reversing-057.png)

![파일 위치와 메모리 위치 대응](/assets/images/writeup/kisa-academy/notion/reversing/reversing-058.png)

즉, 파일 내부에서 어디에 저장되어 있는지와 메모리에서 어디에 올라가는지는 같은 값이 아닐 수 있음

## 권한 정보와 프로텍션

섹션이 메모리에 올라갈 때는 위치만 중요한 것이 아니라 권한도 중요함

`.text`는 일반적으로 읽기와 실행 권한이 필요함

`.data`는 전역 변수 등이 위치하므로 읽기와 쓰기 권한이 필요함

`.rdata`는 상수 데이터가 많기 때문에 읽기 전용인 경우가 많음

이 권한 정보는 `Characteristics`를 통해 전달되며, 로더는 이를 읽고 메모리 보호 속성을 부여함

![Characteristics와 권한](/assets/images/writeup/kisa-academy/notion/reversing/reversing-059.png)

권한 구분은 단순 분류가 아니라, 실행 가능한 영역과 데이터 영역을 나누는 보호 기법과도 연결됨

## 확인한 내용

`CFF Explorer`를 사용하면 섹션별 값과 권한을 직접 볼 수 있음

![CFF Explorer 섹션 보기](/assets/images/writeup/kisa-academy/notion/reversing/reversing-060.png)

파일 상 위치를 확인할 때는 `Raw Address`를 보면 됨

![Raw Address 확인 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-061.png)

![Raw Address 확인 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-062.png)

![Raw Address 확인 3](/assets/images/writeup/kisa-academy/notion/reversing/reversing-063.png)

메모리 상 위치를 확인할 때는 `ImageBase`와 `VirtualAddress`를 함께 봐야 함

![ImageBase 확인 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-064.png)

![ImageBase 확인 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-065.png)

![ImageBase 확인 3](/assets/images/writeup/kisa-academy/notion/reversing/reversing-066.png)

자주 보이는 권한 값은 다음과 같이 해석할 수 있음

- `.text = 6`: 읽기 + 실행
- `.data = C`: 읽기 + 쓰기
- `.rdata = 4`: 읽기

## 정리

Section Table은 로더를 위한 섹션별 매핑 지침에 해당함

`PointerToRawData`는 파일 상 위치를, `VirtualAddress`는 메모리 상 위치를, `Characteristics`는 권한을 설명함

이 구조를 이해하면 왜 `.text`는 실행 가능하고 `.data`는 보통 실행되지 않는지, 왜 리버싱 과정에서 섹션별 성격을 먼저 확인해야 하는지 자연스럽게 연결됨



