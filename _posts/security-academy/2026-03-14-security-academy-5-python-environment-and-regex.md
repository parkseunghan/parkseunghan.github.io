---
title: "시큐리티아카데미 7기 정리 - 파이썬 1. 기초 문법과 자료구조 실습"
date: 2026-03-14T18:00:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Python
  - Jupyter
  - Data Structure
  - Counter
permalink: /security-academy/python-environment-and-regex/
last_modified_at: 2026-03-30T18:00:00+09:00
published: true
---
## 개요

타입, 진법, 문자열, 리스트, 딕셔너리, 집합, 큐, `Counter`, 함수, 클래스 문법 실습을 단계별로 다루는 글

핵심은 문법 이름보다 입력 코드와 출력 결과를 함께 읽는 데 있음

## 용어 정리

- `Interpreter`: 코드를 한 줄씩 해석하며 실행하는 방식
- `Notebook`: 코드 셀과 출력 결과를 함께 기록하는 실행 환경
- `Dynamic Typing`: 변수 선언 시 타입을 미리 고정하지 않는 방식
- `List`: 순서가 있는 가변 컨테이너
- `Dictionary`: 키-값 쌍으로 구성된 컨테이너
- `Deque(Double-Ended Queue)`: 양쪽 끝에서 삽입과 삭제가 가능한 큐
- `Counter`: 항목 빈도를 빠르게 세는 표준 라이브러리 클래스

## 실습 환경

`.venv` 가상환경과 실습 파일이 함께 구성된 형태다

주요 파일은 다음과 같음

- `exercise.ipynb`: 타입, 진법, 객체 ID 확인
- `exercise2.ipynb`: 자료형, 컬렉션, 함수, 파일 입출력, `Counter`, 정규표현식
- `sample1.log`, `sample2.log`: 로그 파싱 실습 데이터
- `student_list1.txt`, `student_list2.txt`: 대규모 텍스트 비교 실습용 데이터
- `checked_list1.txt`, `checked_list2.txt`: 비교 대상 결과 파일

로컬에서 자주 쓰는 실행 명령은 아래와 같음

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install jupyter notebook
jupyter notebook
```

- `python -m venv .venv`: 현재 파이썬으로 `.venv` 가상환경 생성
- `-m`: 파이썬 모듈을 스크립트처럼 실행
- `venv`: 표준 가상환경 모듈
- `Activate.ps1`: PowerShell용 가상환경 활성화 스크립트
- `python -m pip install ...`: 현재 가상환경 기준 패키지 설치
- `jupyter notebook`: 노트북 서버 실행

## 타입과 진법 실습

`exercise.ipynb`에서 가장 먼저 확인한 것은 파이썬 기본 타입과 숫자 표현 방식이었음

### 사용한 코드

```python
x = 3
y = 3.14

print(type(x))
print(type(y))
```

### 확인한 출력

```text
<class 'int'>
<class 'float'>
```

정수와 실수 타입이 실제로 어떻게 구분되는지 바로 확인 가능했음

진법 표기 실습도 함께 진행됨

### 사용한 코드

```python
a = 0x10
print(a)
print(hex(a))

b = 0o11
print(b)
print(oct(b))

c = 0b11
print(c)
print(bin(c))
```

### 확인한 출력

```text
16
0x10
9
0o11
3
0b11
```

정수 자체와 문자열 표현 결과는 구분 대상이다. 이후 로그나 네트워크 데이터를 다룰 때 16진수, 10진수, 문자열 변환 구분 기준이 됨

## 문자열과 컬렉션 실습

`exercise2.ipynb`는 자료구조를 직접 만들어 조작하는 예시 비중이 큰 편임

핵심 축은 다음과 같음

- 문자열 연결과 포맷팅
- 리스트 생성, 인덱싱, 슬라이싱
- 딕셔너리와 집합 순회
- `deque`, `Counter` 같은 표준 라이브러리 컨테이너

### Queue와 Deque

큐는 리스트 방식과 `deque` 방식을 함께 비교하는 구조로 정리함

```python
queue = []

from collections import deque
q2 = deque()
```

리스트도 큐처럼 사용할 수 있지만, 앞쪽 삽입과 삭제가 많아지면 `deque` 쪽이 더 적합함

### Counter 실습

`Counter`는 테스트 리스트 빈도 계산 예시와 함께 정리함

```python
from collections import Counter

testList = ["hi", "hey", "hi", "hi", "hello", "hey"]
print(Counter(testList))
```

실제 결과는 아래처럼 이해 가능함

```text
Counter({'hi': 3, 'hey': 2, 'hello': 1})
```

큰 데이터에서는 직접 반복문 방식과 `Counter` 방식을 비교함. `100,000`개 무작위 정수 데이터 기준으로 보면, 기본 문법만으로도 구현 가능하지만 표준 도구를 쓰면 더 짧고 읽기 쉬운 구조가 됨

## 함수와 클래스 실습

`*args`, `**kwargs`, 클래스, 데코레이터는 스켈레톤 예시와 함께 정리함

```python
def add_all(*args):
    pass

def print_html(**kwargs):
    pass

class Calculator:
    def __init__(self, result=0):
        self.result = result
```

- `*args`: 위치 인자를 여러 개 받을 때 사용
- `**kwargs`: 키워드 인자를 여러 개 받을 때 사용
- `__init__`: 객체 생성 시 초기화 함수

완성된 프로젝트 코드보다, 함수와 객체 문법을 직접 채워 보는 연습에 가까움

## 파일 입출력 실습

파일 입출력은 리스트를 텍스트 파일로 저장하는 예제부터 시작됨

```python
my_list = ["apple", "banana", "cherry", "date"]
```

실제 출력 파일도 함께 확인 가능

- `output1.txt`
- `output2.txt`
- `output3.txt`

### 확인한 출력

`output1.txt`

```text
apple
```

`output2.txt`

```text
apple
banana
cherry
date
```

`output3.txt`

```text
apple
banana
cherry
date
```

한 줄만 쓰는 방식과 여러 줄을 한 번에 쓰는 방식 차이를 실제 파일로 확인 가능

작업 경로 확인 코드도 함께 포함됨

```python
import os
os.getcwd()
```

확인한 출력 예시는 아래와 같음

```text
'C:\\Users\\user\\Documents\\jupyter'
```

또는 다른 실습 환경에서는

```text
'G:\\내 드라이브\\Lecture\\파이썬\\자료\\answer'
```

파일 입출력 현재 작업 경로 확인은 기본 단계에 가까움

## 정리

파이썬 1차 실습의 핵심은 언어 문법 암기보다, 아래 흐름을 직접 실행하며 구조를 익히는 데 있음

- 타입 확인
- 진법 변환
- 문자열과 컨테이너 조작
- `deque`, `Counter` 같은 표준 라이브러리 사용
- 함수, 클래스 문법 확인
- 텍스트 파일 쓰기와 작업 경로 확인

이후 로그 분석과 자동화 실습으로 넘어가기 위한 기본 도구 세트 정리 단계에 해당함





