---
title: "KISA 아카데미 정리 - 리버싱 9. 스택 프레임과 복귀 주소"
categories:
  - Reverse Engineering
tags:
  - KISA Academy
  - Reverse Engineering
  - Windows Internals
  - Assembly
last_modified_at: 2025-02-03T18:00:00+09:00
published: true
permalink: /security-academy/2025-02-03-kisa-reversing-9-stack-frame-and-return-address/
---
## 개요

리버싱에서 함수 단위 분석이 어려운 이유는 호출될 때마다 스택 구조가 계속 바뀌기 때문임

IA-32 스택의 기본 동작, 스택 프레임 생성과 제거, 복귀 주소가 저장되고 사용되는 방식을 함께 정리함

## 용어 정리

- `Stack(스택)`: 함수 호출 과정에서 매개변수, 지역변수, 복귀 주소 등을 저장하는 메모리 구조. IA-32에서는 보통 `full descending stack`으로 동작함
- `Call Stack(콜 스택)`: 함수 호출 관계에 따라 쌓이는 스택 영역을 강조한 표현. `main -> A -> B` 호출 시 프레임이 차례대로 쌓
- `Stack Frame(스택 프레임)`: 특정 함수 하나가 사용하는 고유한 스택 영역. 지역변수, 저장된 EBP, 복귀 주소가 여기에 포함됨
- `Stack Pointer, ESP(스택 포인터)`: 현재 스택 최상단을 가리키는 레지스터. `push`, `pop` 때 값이 바뀜
- `Base Pointer, EBP(베이스 포인터)`: 현재 함수 프레임의 기준점을 가리키는 레지스터. `EBP-4`, `EBP+8`처럼 상대 접근에 사용됨
- `Function Prologue(프롤로그)`: 함수 시작 시 스택 프레임을 생성하는 코드 묶음. `push ebp`, `mov ebp, esp`, `sub esp, n`
- `Function Epilogue(에필로그)`: 함수 종료 시 스택 프레임을 해제하는 코드 묶음. `mov esp, ebp`, `pop ebp`, `ret`
- `Return Address(복귀 주소)`: 함수 호출 후 원래 위치로 돌아가기 위해 스택에 저장되는 주소. `call` 직후 다음 명령의 주소가 저장됨

## 스택의 기본 동작

IA-32 환경의 스택은 보통 아래 방향으로 자라며, `ESP`가 현재 최상단을 가리킴

함수 호출 과정에서는 지역변수, 매개변수, 복귀 주소, 저장된 레지스터 값 등이 이 영역에 쌓임

![ESP와 스택 개념](/assets/images/writeup/kisa-academy/notion/reversing/reversing-121.png)

`push`가 수행되면 `ESP`가 감소하고 값이 저장됨

![PUSH 동작 1](/assets/images/writeup/kisa-academy/notion/reversing/reversing-124.png)

![PUSH 동작 2](/assets/images/writeup/kisa-academy/notion/reversing/reversing-125.png)

`pop`이 수행되면 스택 최상단 값이 빠져나오고 `ESP`가 증가함

![POP 동작](/assets/images/writeup/kisa-academy/notion/reversing/reversing-126.png)

## 스택 프레임이 생기는 방식

함수가 호출되면 그 함수만을 위한 스택 프레임이 생성됨

`main()`이 실행 중일 때는 main의 프레임이 존재하고, 여기서 `A()`를 호출 시 `A()`의 프레임이 새로 생김

다시 `A()`가 `B()`를 호출 시 `B()` 프레임이 추가로 생성됨

![중첩 스택 프레임](/assets/images/writeup/kisa-academy/notion/reversing/reversing-127.png)

함수가 종료되면 해당 프레임은 더 이상 참조되지 않는 영역이 됨

![프레임 종료 후 상태](/assets/images/writeup/kisa-academy/notion/reversing/reversing-128.png)

`EBP`는 현재 함수 프레임의 바닥을 가리키고, `ESP`는 현재 꼭대기를 가리킴

![ESP 추적의 어려움](/assets/images/writeup/kisa-academy/notion/reversing/reversing-129.png)

![A 함수 프레임](/assets/images/writeup/kisa-academy/notion/reversing/reversing-130.png)

![B 함수 프레임](/assets/images/writeup/kisa-academy/notion/reversing/reversing-131.png)

![프레임 복귀](/assets/images/writeup/kisa-academy/notion/reversing/reversing-132.png)

## 함수 프롤로그와 에필로그

프롤로그는 새 스택 프레임을 만드는 코드다

```assembly
push ebp
mov ebp, esp
sub esp, n
```

`push ebp`는 이전 함수의 기준점을 백업함

`mov ebp, esp`는 현재 함수의 기준 프레임을 세움

`sub esp, n`은 지역변수 공간을 확보함

![이전 EBP 백업 이유](/assets/images/writeup/kisa-academy/notion/reversing/reversing-133.png)

![push ebp](/assets/images/writeup/kisa-academy/notion/reversing/reversing-134.png)

![sub esp, n](/assets/images/writeup/kisa-academy/notion/reversing/reversing-135.png)

에필로그는 프레임을 해제하는 코드다

```assembly
mov esp, ebp
pop ebp
ret
```

이 과정에서 지역변수 공간이 정리되고, 저장해둔 이전 프레임 기준점이 복원됨

![mov esp, ebp 전](/assets/images/writeup/kisa-academy/notion/reversing/reversing-136.png)

![mov esp, ebp 후](/assets/images/writeup/kisa-academy/notion/reversing/reversing-137.png)

![pop ebp](/assets/images/writeup/kisa-academy/notion/reversing/reversing-138.png)

## 본 프레임 생성

`tmainCRTStartup`이 `main`을 호출하기 전 프레임을 먼저 사용하고 있음을 확인할 수 있음

![CRTStartup에서 main 호출](/assets/images/writeup/kisa-academy/notion/reversing/reversing-140.png)

![main 호출 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-141.png)

![프롤로그 전 프레임](/assets/images/writeup/kisa-academy/notion/reversing/reversing-142.png)

![EBP 값 확인](/assets/images/writeup/kisa-academy/notion/reversing/reversing-143.png)

![EBP를 최상단으로 이동](/assets/images/writeup/kisa-academy/notion/reversing/reversing-144.png)

![지역변수 공간 확보](/assets/images/writeup/kisa-academy/notion/reversing/reversing-147.png)

즉, 프롤로그를 실제 디버깅 화면에서 보면 스택 프레임이 만들어지는 과정을 명확히 추적할 수 있음

## 복귀 주소의 의미

`call`은 단순 점프가 아니라, 다음에 돌아와야 할 주소를 스택에 저장한 뒤 이동하는 명령

따라서 복귀 주소는 스택 최상단 근처에 존재하며, `ret`가 실행되면 다시 `EIP`로 복원됨

![복귀 주소 개념](/assets/images/writeup/kisa-academy/notion/reversing/reversing-149.png)

![RET 이후 ESP 변화](/assets/images/writeup/kisa-academy/notion/reversing/reversing-150.png)

![CALL/RET 흐름](/assets/images/writeup/kisa-academy/notion/reversing/reversing-151.png)

복귀 주소가 변조되면 원래 코드가 아니라 공격자가 원하는 코드로 흐름이 바뀔 수 있음

![복귀 주소 악용 가능성](/assets/images/writeup/kisa-academy/notion/reversing/reversing-152.png)

`sum()`과 `main()`의 복귀 주소가 각각 어떤 위치를 가리키는지 실제로 확인 가능

![sum의 Return Address](/assets/images/writeup/kisa-academy/notion/reversing/reversing-153.png)

![ret 실행 후 복귀](/assets/images/writeup/kisa-academy/notion/reversing/reversing-154.png)

![main의 Return Address](/assets/images/writeup/kisa-academy/notion/reversing/reversing-155.png)

## 정리

스택 프레임은 함수 호출 분석의 기본 단위다

프롤로그는 프레임 생성, 에필로그는 프레임 해제를 담당함

또한 복귀 주소는 함수 호출 이후 원래 코드 흐름을 복원하기 위한 핵심 값이며, 스택 기반 취약점과도 직접 연결되는 중요한 개념




