---
title: "KISA 아카데미 정리 - 리버싱 10. 호출 규약과 반복문 패턴 식별"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Reverse Engineering
  - Windows Internals
  - Assembly
last_modified_at: 2025-02-04T18:00:00+09:00
published: true
permalink: /security-academy/2025-02-04-kisa-reversing-10-calling-conventions-and-loop-patterns/
---
## 개요

함수 호출은 단순히 `call` 한 줄로 끝나지 않음

매개변수를 어디에 놓을지, 누가 스택을 정리할지, 어떤 레지스터를 보존할지에 대한 약속이 필요하며 이를 호출 규약이라고 부름

대표적인 IA-32 호출 규약과, 컴파일된 반복문에서 자주 보이는 패턴을 함께 정리함

## 용어 정리

- `Caller(호출자)`: 다른 함수를 호출하는 쪽. `main`이 `sum`을 호출하는 경우 `main`이 Caller
- `Callee(피호출자)`: 호출을 받아 실행되는 함수. `sum` 함수가 이
- `Calling Convention(호출 규약)`: 매개변수 전달, 스택 정리, 레지스터 보존 규칙을 묶은 약속. `cdecl`, `stdcall`, `fastcall`
- `Application Binary Interface, ABI(응용 프로그램 이진 인터페이스)`: 바이너리 수준에서 함수 호출, 스택 배치, 데이터 정렬 등을 규정하는 규칙 집합. 호출 규약은 ABI의 일부로 볼 수 있음
- `Caller Saved Register(호출자 저장 레지스터)`: 호출자가 필요하면 직접 백업해야 하는 레지스터. `EAX`, `ECX`, `EDX`가 대표적
- `Callee Saved Register(피호출자 저장 레지스터)`: 피호출자가 사용 전후 값을 보존해야 하는 레지스터. `EBX`, `ESI`, `EDI`가 대표적
- `Right to Left, RTL(우측에서 좌측)`: 인자를 오른쪽부터 스택에 쌓는 전달 순서. `func(a, b, c)`라면 `c -> b -> a` 순으로 push됨
- `Loop(순환문)`: 조건을 만족하는 동안 반복되는 코드 구조. `for`, `while`이 대표적

## 호출 규약이 필요한 이유

호출자와 피호출자가 서로 다른 방식으로 매개변수를 해석하면 함수 호출 자체가 깨질 수 있음

따라서 다음 항목에 대한 규칙이 필요함

- 매개변수를 어디에 둘지
- 어떤 순서로 전달할지
- 누가 스택을 정리할지
- 어떤 레지스터를 누가 보존할지

![호출 규약 개요](/assets/images/writeup/kisa-academy/notion/reversing/reversing-157.png)

## IA-32의 대표 호출 규약

`cdecl`과 `stdcall`은 모두 스택을 사용하고, 보통 `RTL` 순서로 매개변수를 전달함

차이는 스택 정리 주체에 있음

- `cdecl`: 호출자(Caller)가 스택 정리
- `stdcall`: 피호출자(Callee)가 스택 정리
- `fastcall`: 일부 매개변수를 레지스터로 전달

![호출 규약 유형](/assets/images/writeup/kisa-academy/notion/reversing/reversing-158.png)

리턴값은 보통 `EAX`에 저장되며, 더 큰 값은 `EDX:EAX` 조합을 사용할 수 있음

또한 `EAX`, `ECX`, `EDX`는 Caller Saved, `EBX`, `ESI`, `EDI`는 Callee Saved로 보는 경우가 많음

## 본 cdecl, stdcall, fastcall

실습 코드에서는 세 호출 규약을 각각 적용한 합계 함수 예제를 사용함

![IDA에서 호출 규약 실습 시작](/assets/images/writeup/kisa-academy/notion/reversing/reversing-160.png)

`cdecl`은 함수 호출 전 스택에 인자를 쌓고, 호출 뒤 `add esp, ...` 같은 코드로 호출자가 직접 정리함

![cdecl 호출부](/assets/images/writeup/kisa-academy/notion/reversing/reversing-161.png)

![cdecl 내부](/assets/images/writeup/kisa-academy/notion/reversing/reversing-162.png)

`stdcall`은 호출 뒤 별도의 `add esp, ...`가 없고, 함수 내부 `ret 8` 같은 방식으로 피호출자가 정리함

![stdcall 호출부](/assets/images/writeup/kisa-academy/notion/reversing/reversing-163.png)

![stdcall 내부](/assets/images/writeup/kisa-academy/notion/reversing/reversing-164.png)

`fastcall`은 스택 push보다 레지스터 사용이 더 두드러짐

![fastcall 호출부](/assets/images/writeup/kisa-academy/notion/reversing/reversing-165.png)

![fastcall 내부](/assets/images/writeup/kisa-academy/notion/reversing/reversing-166.png)

디버깅 시 ASLR로 인해 주소가 달라질 수 있으므로 Rebase를 통해 분석 주소를 맞추는 과정도 확인함

![IDA Rebase 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-167.png)

![IDA Rebase 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-168.png)

![IDA Rebase 3](/assets/images/writeup/kisa-academy/notion/reversing/reversing-169.png)

## 반복문 패턴 식별

컴파일된 `for`, `while`은 소스코드와 완전히 같은 모양으로 보이지 않음

다만 대체로 다음 세 영역으로 나누어 볼 수 있음

- 탈출 조건 점검 영역
- 반복 본문
- 조건 값 변경 영역

`while`의 경우 조건 점검 후 본문으로 진입하고, 다시 조건 확인 위치로 되돌아가는 패턴이 자주 보임

![while 패턴 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-178.png)

![while 패턴 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-180.png)

![while 패턴 3](/assets/images/writeup/kisa-academy/notion/reversing/reversing-181.png)

`for`도 결국 반복 구조라는 점에서는 유사하므로, 실제 분석에서는 "어떤 값이 비교되고 어떤 점프가 반복되는가"가 더 중요함

![for 패턴 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-182.png)

![for 패턴 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-183.png)

![Visual Studio 패턴 차이](/assets/images/writeup/kisa-academy/notion/reversing/reversing-184.png)

실습 후반에서는 반복문 기반으로 파일명을 생성하는 악성코드 코드 조각도 함께 확인함

![반복문 기반 문자열 생성 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-192.png)

![time, srand 사용](/assets/images/writeup/kisa-academy/notion/reversing/reversing-194.png)

![rand와 idiv](/assets/images/writeup/kisa-academy/notion/reversing/reversing-197.png)

![최종 파일명 생성](/assets/images/writeup/kisa-academy/notion/reversing/reversing-200.png)

## 정리

호출 규약은 함수 호출의 약속이며, 매개변수 전달 방식과 스택 정리 주체를 읽는 기준이 됨

`cdecl`, `stdcall`, `fastcall`을 구분할 수 있으면 디스어셈블된 함수 호출부를 훨씬 빠르게 해석할 수 있음

또한 반복문은 소스코드 형태보다 분기와 비교 패턴으로 읽는 습관이 중요함

이 관점은 악성코드의 문자열 생성 루틴, 조건 분기, 반복 동작 분석에도 그대로 이어짐



