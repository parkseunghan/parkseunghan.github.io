---
title: "KISA 아카데미 정리 - 리버싱 8. IA-32 레지스터와 주요 명령어"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Reverse Engineering
  - Windows Internals
  - Assembly
last_modified_at: 2025-01-31T18:00:00+09:00
published: true
permalink: /security-academy/2025-01-31-kisa-reversing-8-registers-and-instructions/
---
## 개요

리버싱 과정에서는 메모리 구조만 보는 것으로 충분하지 않음

실행 흐름을 따라가려면 레지스터가 무엇을 저장하는지와, 명령어가 값을 복사하는지, 점프하는지, 스택을 조작하는지 구분할 수 있어야 함

IA-32 환경에서 자주 보는 레지스터와 명령어를 정리함

## 용어 정리

- `General Purpose Register(범용 레지스터)`: 산술 연산, 주소 보관, 임시 값 저장에 널리 쓰이는 레지스터 집합. `EAX`, `EBX`, `ECX`, `EDX`, `ESI`, `EDI`, `EBP`, `ESP`
- `Instruction Pointer, EIP(명령 포인터)`: 다음에 실행할 명령의 주소를 저장하는 레지스터. 현재 코드 흐름을 추적할 때 가장 중요함
- `EFLAGS(플래그 레지스터)`: 비교와 산술 결과에 따른 상태 비트를 저장하는 레지스터. `ZF`, `CF`, `SF` 등이 조건 분기에 영향 줌
- `Source Index, ESI(소스 인덱스)`: 문자열 복사나 메모리 참조에서 원본 위치를 가리키는 경우가 많음. `movs`, `lods` 계열과 연결됨
- `Destination Index, EDI(목적지 인덱스)`: 문자열 복사나 메모리 참조에서 목적지 위치를 가리키는 경우가 많음. ESI와 함께 등장하면 복사 루틴을 의심할 수 있음
- `Stack Pointer, ESP(스택 포인터)`: 현재 스택 최상단을 가리키는 레지스터. `push`, `pop`, 함수 프롤로그와 연결됨
- `Base Pointer, EBP(베이스 포인터)`: 현재 함수의 기준 프레임을 가리키는 레지스터. 지역변수, 매개변수 접근의 기준이 됨
- `Load Effective Address, LEA(유효 주소 로드)`: 메모리 값을 읽는 것이 아니라 주소 계산 결과를 저장하는 명령. `lea eax, [edx+4]`는 `0x1004` 같은 주소를 넣음

## 자주 보는 레지스터

범용 레지스터는 값 저장, 연산, 주소 참조에 폭넓게 사용됨

특히 자주 보이는 레지스터는 다음과 같음

- `EAX`: 연산 결과나 API 반환값 저장
- `ECX`: 반복문 카운터로 자주 사용
- `ESI`, `EDI`: 문자열 복사나 버퍼 처리에서 자주 사용
- `EBP`, `ESP`: 함수 스택 프레임 추적의 핵심

![ESI, EDI 예시](/assets/images/writeup/kisa-academy/notion/reversing/reversing-083.png)

![ESP 의미](/assets/images/writeup/kisa-academy/notion/reversing/reversing-084.png)

세그먼트 레지스터와 EFLAGS, EIP, DR 레지스터도 함께 보면 코드 흐름과 디버깅 상태를 더 정확히 읽을 수 있음

![세그먼트 레지스터](/assets/images/writeup/kisa-academy/notion/reversing/reversing-085.png)

![EFLAGS](/assets/images/writeup/kisa-academy/notion/reversing/reversing-086.png)

![EIP](/assets/images/writeup/kisa-academy/notion/reversing/reversing-087.png)

![DR 레지스터](/assets/images/writeup/kisa-academy/notion/reversing/reversing-088.png)

## mov와 lea

`mov`는 값을 복사하는 명령

메모리, 상수, 레지스터 사이에서 값을 옮길 때 가장 자주 보게 됨

```assembly
mov edx, 0x1000
mov eax, [edx+4]
```

위 예시는 `0x1004` 위치에 있는 값을 읽어 `eax`에 저장하는 흐름

반면 `lea`는 메모리 값을 읽는 것이 아니라, 계산된 주소 자체를 저장함

```assembly
mov edx, 0x1000
lea eax, [edx+4]
```

이 경우 `eax`에는 `0x1004`라는 주소값이 들어감

## 흐름을 바꾸는 명령어

`call`은 현재 위치 다음 주소를 백업한 뒤 다른 함수로 이동함

`jmp`는 복귀 주소 백업 없이 바로 이동함

`ret`는 스택에 백업된 복귀 주소를 꺼내 다시 코드 흐름을 원래 위치로 되돌림

![분기 명령어 개요](/assets/images/writeup/kisa-academy/notion/reversing/reversing-092.png)

![ret 개념 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-093.png)

![ret 개념 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-094.png)

이 세 명령어를 구분하면 함수 호출과 분기 흐름 해석이 쉬워짐

## 스택을 조작하는 명령어

`push`는 값을 스택에 넣는 명령

`pop`은 스택 최상단 값을 꺼내 다른 레지스터나 메모리로 옮기는 명령

![push 개념](/assets/images/writeup/kisa-academy/notion/reversing/reversing-095.png)

![pop 개념 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-096.png)

![pop 개념 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-097.png)

스택은 낮은 주소 방향으로 자라는 `descending stack`으로 이해하면 됨

![스택 성장 방향 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-101.png)

![스택 성장 방향 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-102.png)

이 때문에 `push` 시 `ESP`가 감소하고, `pop` 시 `ESP`가 증가함

## 비교와 반복문 해석

비교 명령과 조건 분기 명령은 반복문과 조건문 해석의 핵심임

예를 들어 `cmp` 이후 `jl`, `jg` 같은 조건 점프가 이어지면, 앞선 비교 결과를 바탕으로 분기하는 흐름으로 해석할 수 있음

반복 코드에서 되돌아가는 점프가 보이면 루프 구조를 의심할 수 있음

![loop_count 예시](/assets/images/writeup/kisa-academy/notion/reversing/reversing-105.png)

`EIP` 값을 보면서 현재 어떤 명령이 실행 중인지 확인하고, `F7` 같은 단일 실행 기능으로 레지스터 변화와 분기 조건을 따라가는 연습이 중요함

![sample.c 실습](/assets/images/writeup/kisa-academy/notion/reversing/reversing-106.png)

![main 주소 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-107.png)

![EIP 추적](/assets/images/writeup/kisa-academy/notion/reversing/reversing-108.png)

![step into](/assets/images/writeup/kisa-academy/notion/reversing/reversing-109.png)

## 정리

레지스터는 현재 상태를 저장하고, 명령어는 그 상태를 바꾸는 단위다

`EIP`, `ESP`, `EBP`, `EAX` 계열을 읽을 수 있어야 함수 흐름과 데이터 흐름을 동시에 따라갈 수 있음

또한 `mov`, `lea`, `call`, `jmp`, `ret`, `push`, `pop`의 차이를 구분할 수 있어야 이후 스택 프레임과 호출 규약 분석도 자연스럽게 이어짐




