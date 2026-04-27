---
title: "KISA 아카데미 정리 - 리버싱 3. 프로세스 가상주소공간 검증 실습"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Reverse Engineering
  - Windows Internals
  - Virtual Address Space
  - x64dbg
last_modified_at: 2025-01-26T18:00:00+09:00
published: true
permalink: /security-academy/2025-01-26-kisa-reversing-3-vas-lab/
---
## 개요

가상주소공간 개념은 이론만으로 보면 추상적으로 느껴질 수 있음

`calc.exe`, `procexp64.exe`, `x64dbg`를 이용해 프로세스의 가상주소공간이 실제로 어떻게 보이는지 확인한 내용을 정리함

핵심은 다음 두 가지다

- 프로세스마다 독립적인 가상주소공간을 가짐
- 동일한 라이브러리는 물리 메모리 차원에서 공유될 수 있음

## 용어 정리

- `Process(프로세스)`: 실행 중인 프로그램 인스턴스. `calc.exe`를 실행 시 하나의 프로세스가 생성됨
- `Process ID, PID(프로세스 ID)`: 운영체제가 각 프로세스를 구분하기 위해 부여하는 식별자. PID가 다르면 별도 실행 단위로 관리됨
- `Parent-Child Process(부모-자식 프로세스)`: 다른 프로세스를 시작한 주체와 시작된 대상의 관계. `explorer.exe`가 일반 GUI 프로그램의 부모가 되는 경우가 많음
- `Shell Process(셸 프로세스)`: 사용자의 입력을 받아 프로그램 실행과 화면 요소를 관리하는 핵심 프로세스. Windows에서는 `explorer.exe`가 대표적
- `Memory Map(메모리 맵)`: 프로세스 가상주소공간에 어떤 모듈과 섹션이 어느 권한으로 배치되어 있는지 보여주는 정보. 코드, 데이터, DLL 영역을 한눈에 확인할 수 있음
- `Debugger(디버거)`: 실행 중인 프로세스를 관찰하고 제어하는 도구. `x64dbg`가 대표 예시
- `Section(섹션)`: 실행파일 내부에서 목적별로 나뉜 영역. `.text`, `.data`, `.rdata` 등이 이
- `Permission(권한)`: 메모리 영역에 허용된 접근 방식. 읽기, 쓰기, 실행 권한 조합으로 설정됨
- `Shared Library(공유 라이브러리)`: 여러 프로세스가 함께 참조할 수 있도록 구성된 라이브러리 파일. 동일 DLL이 여러 프로세스에 로드되어도 물리 메모리는 공유될 수 있음
- `Module(모듈)`: 프로세스 주소공간에 로드된 실행파일이나 DLL 단위. `calc.exe`, `kernel32.dll` 모두 모듈로 볼 수 있음

## 실습 대상과 도구

실습 대상은 `calc.exe`다

사용한 도구는 다음과 같음

- `procexp64.exe`: 프로세스의 부모-자식 관계와 기본 정보를 확인하는 도구
- `x64dbg`: 디버거. 프로세스 메모리 공간을 직접 관찰하고 통제할 수 있음

## Process Explorer에서 확인한 내용

`procexp64.exe`를 통해 프로세스의 부모-자식 관계를 확인할 수 있음

![Process Explorer 실행 화면](/assets/images/writeup/kisa-academy/notion/reversing/reversing-018.png)

실습 화면에서는 `x64dbg.exe` 하위에 `calc.exe`가 존재하고, 상위에는 `explorer.exe`가 위치함

`explorer.exe`는 로그인 이후 실행되는 대표적인 사용자 셸 프로세스에 해당함

바탕화면, 아이콘, 탐색기, 클릭 이벤트 처리 등 GUI 상호작용의 중심 역할을 수행함

즉, 일반적인 사용자 프로그램은 `explorer.exe`를 통해 시작되는 경우가 많음

## x64dbg에서 메모리 맵 확인

`x64dbg`에서는 분석 대상 프로그램의 메모리 공간을 직접 관찰할 수 있음

![x64dbg 메모리 맵](/assets/images/writeup/kisa-academy/notion/reversing/reversing-019.png)

메모리 맵을 보면 분석 대상 프로세스의 가상주소공간이 어떤 영역으로 구성되어 있는지 확인할 수 있음

`.data` 영역은 전역 변수 등이 위치하는 공간이며, 일반적으로 코드 실행 권한은 부여되지 않음

![calc.exe 가상주소공간](/assets/images/writeup/kisa-academy/notion/reversing/reversing-020.png)

실행파일 자체뿐 아니라 여러 DLL도 함께 로드됨을 확인할 수 있음

![DLL 로드 상태](/assets/images/writeup/kisa-academy/notion/reversing/reversing-021.png)

실행파일은 필요한 시점에 DLL 내부의 API를 호출하며 동작함

## 동일한 DLL 주소가 보이는 이유

실습 중 서로 다른 프로세스에서 비슷한 DLL 주소가 보이는 경우가 있음

![동일 DLL 참조 예시](/assets/images/writeup/kisa-academy/notion/reversing/reversing-022.png)

겉보기에는 동일한 주소를 사용하는 것처럼 보일 수 있으나, 이것이 곧 프로세스 전체가 동일한 메모리를 공유한다는 의미는 아님

프로세스의 실행파일 본문은 서로 다른 물리 메모리에 매핑될 수 있음

반면, 동일한 DLL은 물리 메모리에 하나만 적재한 뒤 여러 프로세스의 가상주소공간에서 함께 참조하도록 구성할 수 있음

이는 메모리 중복 사용을 줄이기 위한 방식

## 프로세스 ID와 주소 공간의 구분

프로세스는 각각 다른 PID를 가짐

![프로세스 ID 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-023.png)

PID가 다르다는 것은 운영체제가 각 프로세스를 별도의 실행 단위로 관리하고 있음을 의미함

가상주소공간 역시 각 프로세스 단위로 독립적으로 제공됨

따라서 같은 DLL이 보임고 하더라도, 실행파일 본체와 프로세스 문맥 자체가 동일하다고 볼 수는 없음

## 실습을 통해 확인한 핵심

이번 확인한 핵심

- 실행파일은 각자의 가상주소공간에 적재됨
- 운영체제는 매핑 테이블을 통해 가상주소와 물리주소를 연결함
- 동일한 DLL은 여러 프로세스가 공유하여 사용할 수 있음
- 실행파일의 각 섹션은 페이지 단위로 메모리에 적재되며, 권한도 다르게 설정될 수 있음

![섹션과 권한 개념](/assets/images/writeup/kisa-academy/notion/reversing/reversing-024.png)

실행파일의 섹션별 권한 분리는 이후 코드 실행 가능 여부, 데이터 영역 특성, 메모리 보호 구조를 이해하는 데 중요한 기준이 됨

## 정리

가상주소공간은 단순히 주소를 가상으로 보이게 만드는 개념이 아니라, 실제 프로세스 실행 구조를 분리하고 보호하는 핵심 장치

실습을 통해 각 프로세스는 독립된 가상주소공간을 가지며, 같은 라이브러리는 물리 메모리 차원에서 공유될 수 있음을 확인 가능

이 관점을 이해하면 이후 PE 구조, 섹션 권한, DLL 로딩, API 호출 흐름을 해석할 때 훨씬 명확하게 접근할 수 있음




