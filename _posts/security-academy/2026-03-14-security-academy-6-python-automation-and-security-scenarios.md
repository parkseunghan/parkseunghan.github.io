---
title: "시큐리티아카데미 7기 정리 - 파이썬 2. 로그 분석, 정규표현식, 자동화 보조 실습"
date: 2026-03-14T18:10:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Python
  - Log Analysis
  - Regex
  - Automation
permalink: /security-academy/python-automation-and-security-scenarios/
last_modified_at: 2026-03-30T22:00:00+09:00
published: true
---
## 개요

두 번째 파이썬 파트는 실제 보안 데이터 처리에 더 가까운 구성이다. `sample1.log`, `sample2.log`, 학생 목록 텍스트 파일, `ip-generator.py`를 읽어 `Counter`, 정규표현식, 집합 연산, 간단한 자동화 스크립트로 정리하는 흐름이 중심임

초점은 “파이썬으로 무엇을 할 수 있는가”보다 “실습 데이터를 어떻게 읽고 정리하는가”에 있다

## 용어 정리

- `Counter`: 값별 등장 횟수를 세는 표준 라이브러리 클래스
- `Regex(Regular Expression)`: 문자열 패턴을 표현하는 문법
- `Set Difference`: 두 집합 차이를 계산하는 연산
- `urllib`: 웹 자원을 읽기 위한 표준 라이브러리
- `Timer`: 일정 주기로 함수를 실행시키는 도구
- `Base64`: 바이너리 데이터를 문자 형태로 바꾸는 인코딩 방식

## 로그 파일 다루기

실습 파일은 두 종류의 로그로 구성됨

- `sample1.log`: 웹 접근 로그 형식
- `sample2.log`: Apache notice/error 로그 형식

파일 크기 기준은 다음과 같음

- `sample1.log`: `10,000`줄
- `sample2.log`: `56,482`줄

단순 문법 연습보다, 대용량 텍스트를 읽고 집계하는 실습 비중이 큼

### sample1.log 집계

웹 접근 로그는 IP, 시각, 요청 경로를 정규표현식으로 추출한 뒤 `Counter`로 집계하는 구조로 읽을 수 있음

### 사용한 코드

```python
from collections import Counter
import re

ip_counter = Counter()
path_counter = Counter()
hour_counter = Counter()

for line in sample1_lines:
    m = re.match(r'(?P<ip>\\S+) .*?\\[(?P<date>\\d{2}/\\w{3}/\\d{4}):(?P<hour>\\d{2}):\\d{2}:\\d{2} [^\\]]+\\] \"\\S+ (?P<path>\\S+)', line)
    if m:
        ip_counter[m.group("ip")] += 1
        path_counter[m.group("path")] += 1
        hour_counter[m.group("hour")] += 1
```

### 확인한 출력

상위 IP:

```text
[('66.249.73.135', 482), ('46.105.14.53', 364), ('130.237.218.86', 357)]
```

상위 경로:

```text
[('/favicon.ico', 807), ('/style2.css', 546), ('/reset.css', 538), ('/images/jordan-80.png', 533), ('/images/web/2009/banner.png', 516)]
```

시간대 빈도:

```text
[('14', 498), ('15', 496), ('19', 493), ('20', 486), ('17', 484)]
```

접근 로그 하나만으로도 “누가 많이 접근했는가”, “어느 경로가 많이 요청됐는가”, “어느 시간대에 집중됐는가”를 바로 확인 가능

### sample2.log 집계

`sample2.log`는 날짜, 로그 레벨, 라인 끝 경로 기준으로 읽을 수 있음

### 확인한 출력

날짜별 집계:

```text
Counter({21: 4247, 20: 4121, 22: 2431, 29: 2401, 16: 2345, ...})
```

로그 레벨 집계:

```text
[('error', 38081), ('notice', 13755), ('warn', 168)]
```

경로 패턴 집계:

```text
[('/var/www/html/', 6746), ('/etc/httpd/conf/workers2.properties', 5708), ('/var/www/html/blog', 3359), ('/var/www/html/blogs', 1799), ('/var/www/html/drupal', 1714)]
```

날짜별 집계 예시는 `Counter({19: 2896, 18: 2893, 20: 2579, 17: 1632})` 형태로도 정리 가능. 로그 분석 초반에는 `Counter`만으로도 많은 패턴 확인이 가능함

## 파일 비교 실습

학생 목록과 확인 목록을 비교하는 텍스트 처리 실습도 가능했음. 폴더에는 아래 파일이 존재했음

- `student_list1.txt`: `219,001`줄
- `checked_list1.txt`: `219,000`줄
- `student_list2.txt`: `146,001`줄
- `checked_list2.txt`: `146,000`줄

### 사용한 코드

```python
students = set(student_lines)
checked = set(checked_lines)
missing = students - checked
```

### 확인한 출력

1번 목록 비교:

```text
students: 219000
checked: 219000
missing: 0
```

2번 목록 비교:

```text
students: 146001
checked: 146000
missing: 1
missing sample: ['seac']
```

대용량 텍스트 비교도 집합 연산으로 빠르게 처리 가능. 누락 항목 `seac`가 바로 드러나는 구조

## 정규표현식 실습

이메일, 휴대폰 번호, 주민등록번호 패턴 검증

### 사용한 코드

```python
import re

email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
kr_cell_phone_regex = r'^01[016789]-\\d{3,4}-\\d{4}$'
kr_id_regex = r'^\\d{6}-[1-4]\\d{6}$'
```

### 확인한 출력

이메일:

```text
test@example.com -> True
user.name@mail.co.kr -> True
invalid-email@.com -> False
user@domain -> False
```

휴대폰 번호:

```text
010-1234-5678 -> True
011-123-4567 -> True
019-12345-6789 -> False
010-123-4567 -> True
```

주민등록번호:

```text
900101-1234567 -> True
010203-4234567 -> True
990229-5234567 -> False
123456-123456 -> False
```

핵심은 정규표현식을 길게 쓰는 것보다, “허용할 형식”과 “거부할 형식”을 테스트 데이터로 같이 확인하는 구조에 있음

### 기본 기호를 보는 순서

정규표현식은 보통 아래 순서로 읽는 편이 이해가 쉬움

- `^`, `$`: 문자열 시작과 끝 고정
- `[]`: 허용 문자 집합 지정
- `[^...]`: 제외 문자 집합 지정
- `\d`, `\w`, `\s`: 숫자, 단어 문자, 공백 같은 축약 표기
- `+`, `*`, `?`, `{m,n}`: 반복 횟수 지정
- `()`: 그룹화
- `|`: OR 조건
- `\.` , `\-`: 특수문자를 문자 그대로 쓰기 위한 이스케이프

반복 기호: 별도 구분

- `*`: 앞 패턴이 `0번 이상` 반복
- `+`: 앞 패턴이 `1번 이상` 반복
- `?`: 앞 패턴이 `0번 또는 1번` 등장

짧게 보면 아래처럼 읽을 수 있음

```python
print(bool(re.fullmatch(r"ab*", "a")))
print(bool(re.fullmatch(r"ab*", "abbbb")))

print(bool(re.fullmatch(r"ab+", "a")))
print(bool(re.fullmatch(r"ab+", "abbbb")))

print(bool(re.fullmatch(r"ab?", "a")))
print(bool(re.fullmatch(r"ab?", "ab")))
print(bool(re.fullmatch(r"ab?", "abbb")))
```

출력:

```text
True
True
False
True
True
True
False
```

해석은 아래처럼 정리 가능

- `ab*`: `a` 뒤에 `b`가 없어도 되고, 여러 개 있어도 됨
- `ab+`: `a` 뒤에 `b`가 최소 1개는 있어야 함
- `ab?`: `a` 뒤에 `b`가 없거나 1개까지만 허용

예를 들어 휴대폰 번호 패턴

```python
r'^01[016789]-\d{3,4}-\d{4}$'
```

은 아래처럼 나눠서 읽을 수 있음

- `^`: 문자열 시작
- `01[016789]`: `010`, `011`, `016`, `017`, `018`, `019`
- `-`: 하이픈 1개
- `\d{3,4}`: 숫자 3자리 또는 4자리
- `-`: 하이픈 1개
- `\d{4}`: 숫자 4자리
- `$`: 문자열 끝

### `re` 함수별 활용

자주 헷갈리는 부분은 “패턴”보다도 어떤 함수를 써야 하는가에 있음

#### `re.match`

문자열 시작 부분부터 패턴이 맞는지 확인할 때 사용함

```python
import re

line = "ERROR connection failed"
print(bool(re.match(r"ERROR", line)))
print(bool(re.match(r"failed", line)))
```

출력:

```text
True
False
```

`match`는 문자열 맨 앞 기준 확인에 가깝고, 로그 레벨처럼 시작 위치가 고정된 값에 적합함

#### `re.search`

문자열 전체를 훑어 패턴이 한 번이라도 나오면 찾는 방식

```python
line = "GET /admin/login HTTP/1.1"
print(re.search(r"/admin/\S+", line).group())
```

출력:

```text
/admin/login
```

경로나 토큰처럼 “어디 있는지 모르지만 포함되어 있는 값”을 찾을 때 적합함

#### `re.fullmatch`

문자열 전체가 패턴과 정확히 일치해야 할 때 사용함

```python
print(bool(re.fullmatch(r"\d{4}", "2026")))
print(bool(re.fullmatch(r"\d{4}", "2026년")))
```

출력:

```text
True
False
```

입력값 검증에는 `match`보다 `fullmatch`가 더 안전한 경우가 많음

#### `re.findall`

일치하는 모든 결과를 리스트로 받을 때 사용함

```python
text = "open ports: 22, 80, 443"
print(re.findall(r"\d+", text))
```

출력:

```text
['22', '80', '443']
```

반복 출현하는 숫자, IP 일부, 에러 코드 목록을 한 번에 모을 때 편함

#### `re.finditer`

일치한 결과를 반복자 형태로 받아 위치 정보까지 함께 확인할 수 있음

```python
text = "error at /admin, retry at /login"
for m in re.finditer(r"/\w+", text):
    print(m.group(), m.start(), m.end())
```

출력:

```text
/admin 9 15
/login 26 32
```

단순 값뿐 아니라 “문자열 어디에서 나왔는가”까지 같이 봐야 할 때 유용함

#### `re.sub`

패턴에 맞는 부분을 다른 문자열로 치환할 때 사용함

```python
text = "card=1111-2222-3333-4444"
masked = re.sub(r"\d{4}-\d{4}-\d{4}-\d{4}", "[REDACTED]", text)
print(masked)
```

출력:

```text
card=[REDACTED]
```

로그 마스킹이나 개인정보 비식별화에 자주 연결됨

#### `re.split`

구분자 패턴을 기준으로 문자열을 나눌 때 사용함

```python
text = "ERROR,NOTICE|WARN INFO"
print(re.split(r"[,| ]+", text))
```

출력:

```text
['ERROR', 'NOTICE', 'WARN', 'INFO']
```

구분자가 하나가 아닐 때 유용함

#### `re.compile`

같은 패턴을 여러 번 쓸 때 미리 컴파일해 재사용하는 방식

```python
email_pattern = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

for value in ["test@example.com", "user@domain"]:
    print(value, bool(email_pattern.fullmatch(value)))
```

출력:

```text
test@example.com True
user@domain False
```

반복 검증: `compile` 패턴 객체

### 플래그와 옵션

`re.compile(pattern, flags)` 또는 함수 호출의 세 번째 인자로 플래그를 줄 수 있음

자주 쓰는 플래그는 아래와 같음

- `re.I`: 대소문자 무시
- `re.M`: 멀티라인 모드, `^`와 `$`를 각 줄 기준으로 동작시킴
- `re.S`: `.` 이 줄바꿈까지 포함하도록 변경
- `re.X`: 공백과 주석을 허용해 패턴을 읽기 쉽게 작성

#### `re.I`

```python
print(bool(re.search(r"error", "ERROR connection failed", re.I)))
```

출력:

```text
True
```

#### `re.M`

```python
text = "INFO start\nERROR failed\nINFO end"
print(re.findall(r"^ERROR.*$", text, re.M))
```

출력:

```text
['ERROR failed']
```

#### `re.S`

```python
html = "<title>SecuLab\\nPortal</title>"
print(re.search(r"<title>(.*?)</title>", html, re.S).group(1))
```

출력:

```text
SecuLab
Portal
```

### 섞어서 활용하는 패턴

실습 중점: 문법 단독 암기보다 실제 데이터 조합

#### 1. 로그 한 줄에서 여러 값 추출

```python
pattern = re.compile(
    r'(?P<ip>\S+) .*?'
    r'\[(?P<date>\d{2}/\w{3}/\d{4}):(?P<hour>\d{2}):\d{2}:\d{2} [^\]]+\] '
    r'"(?P<method>\S+) (?P<path>\S+)'
)

line = '83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023'
m = pattern.search(line)
print(m.groupdict())
```

출력:

```text
{'ip': '83.149.9.216', 'date': '17/May/2015', 'hour': '10', 'method': 'GET', 'path': '/presentations/logstash-monitorama-2013/images/kibana-search.png'}
```

그룹, 축약 문자, 반복, 이름 있는 그룹을 한 번에 섞는 방식

#### 2. 형식 검증과 추출을 동시에 수행

이메일은 단순 매칭 여부만 확인할 수도 있지만, 도메인만 따로 뽑아낼 수도 있음

```python
pattern = re.compile(r'^(?P<user>[A-Za-z0-9._%+-]+)@(?P<domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,})$')
m = pattern.fullmatch("user.name@mail.co.kr")
print(m.group("user"))
print(m.group("domain"))
```

출력:

```text
user.name
mail.co.kr
```

검증과 추출은 별개가 아니라 같이 설계 가능

#### 3. `Regex + Counter` 조합

정규표현식으로 먼저 값을 뽑고, 그 결과를 `Counter`로 세면 로그 분석이 쉬워짐

```python
paths = []
for line in sample1_lines:
    m = re.search(r'"[A-Z]+ (\S+)', line)
    if m:
        paths.append(m.group(1))

path_counter = Counter(paths)
print(path_counter.most_common(3))
```

출력:

```text
[('/favicon.ico', 807), ('/style2.css', 546), ('/reset.css', 538)]
```

정규표현식은 단독으로 끝나는 것이 아니라, 집계 도구와 붙을 때 더 실무적으로 변함

### 심화적으로 사용할 때

심화 단계에서는 아래 패턴들이 자주 등장함

#### Lookahead

비밀번호 정책처럼 “여러 조건을 동시에 만족해야 하는가”를 표현할 때 사용함

```python
password_regex = re.compile(
    r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{10,}$'
)

tests = ["password", "pass1234", "Pass1234!!"]
for value in tests:
    print(value, bool(password_regex.fullmatch(value)))
```

출력:

```text
password False
pass1234 False
Pass1234!! True
```

- `(?=.*[A-Za-z])`: 영문자 1개 이상 포함
- `(?=.*\d)`: 숫자 1개 이상 포함
- `(?=.*[@$!%*#?&])`: 특수문자 1개 이상 포함

문자를 “소비”하지 않고 조건만 검사하는 방식

#### Non-Greedy

중점: HTML 태그 구간의 greedy, non-greedy 차이

```python
html = "<b>one</b><b>two</b>"
print(re.findall(r"<b>.*</b>", html))
print(re.findall(r"<b>.*?</b>", html))
```

출력:

```text
['<b>one</b><b>two</b>']
['<b>one</b>', '<b>two</b>']
```

`.*?`는 가능한 짧게 잡는 non-greedy 패턴임

#### 선택적 그룹

하이픈이 있는 형식과 없는 형식을 같이 받으려면 선택적 그룹을 사용할 수 있음

```python
phone_pattern = re.compile(r'^01[016789]-?\d{3,4}-?\d{4}$')

for value in ["010-1234-5678", "01012345678", "0111234567"]:
    print(value, bool(phone_pattern.fullmatch(value)))
```

출력:

```text
010-1234-5678 True
01012345678 True
0111234567 True
```

`-?` 하나만으로 형식 허용 범위를 넓힐 수 있음

### 정리한 기준

정규표현식을 실제로 사용할 때는 보통 아래 순서가 안정적임

1. 먼저 허용할 입력 예시와 거부할 입력 예시를 만든다
2. `fullmatch`가 필요한지, `search`가 필요한지 결정한다
3. 그룹 추출이 필요한지 판단한다
4. `Counter`, `split`, `sub` 같은 후처리와 붙인다
5. 필요할 때만 lookahead, non-greedy, named group 같은 심화 문법 추가

정규표현식은 한 줄짜리 마법 문장보다, 입력 형식과 후처리 흐름을 같이 설계하는 도구에 가까움

## 보조 자동화 스크립트 실습

보조 스크립트도 함께 포함됨

- `ip-generator.py`
- 입력 이벤트, 화면 수집 관련 실습 파일

### IP 생성 스크립트

`ip-generator.py`: Docker 내부망 대역을 10진수 정수로 변환하는 도구

### 사용한 코드

```python
import socket
import struct

def ip_to_decimal(ip):
    packed_ip = socket.inet_aton(ip)
    return struct.unpack("!I", packed_ip)[0]
```

- `socket.inet_aton(ip)`: IP 문자열을 4바이트 바이너리로 변환
- `struct.unpack("!I", ...)`: 네트워크 바이트 오더의 부호 없는 정수로 해석
- `"!I"`: big-endian unsigned int 형식

### 확인한 출력

```text
2886795265
2886795266
2886795267
2886860801
2886860802
2886860803
```

`172.17.0.1`, `172.17.0.2` 같은 내부 IP를 정수형 파라미터로 바꿔 넣는 상황을 가정한 예시로 읽을 수 있음

### 듀얼유즈 라이브러리 관찰

`keyboard`, `requests`, `pyautogui`, `Timer`, `base64`를 사용하는 예시도 포함됨. 다만 이런 조합은 운영 자동화 도구로도 쓰일 수 있지만, 반대로 입력 수집이나 화면 수집 같은 민감 기능으로 쉽게 전용될 수 있음

따라서 공개 글에서는 구현 세부 대신 아래 기준만 정리함

- 어떤 데이터를 다루는지
- 외부 전송이 있는지
- 사용자 동의와 정책 근거가 있는지
- 권한 범위가 어디까지인지

파이썬 자동화는 편리하지만, 입력 이벤트와 화면 데이터를 다루는 순간 통제와 윤리 기준이 먼저 와야 함

## 정리

이번 파이썬 실습의 핵심 정리는 아래와 같음

- `Counter` 기반 로그 집계
- 정규표현식 기반 형식 검증
- 집합 연산 기반 대용량 텍스트 비교
- 파일 입출력과 작업 경로 확인
- IP 문자열과 정수형 값 변환
- 자동화 스크립트의 생산성과 위험성 동시 확인

파이썬은 단순 문법 학습용 언어보다, 로그 분석과 보안 보조 자동화를 빠르게 실험하는 도구에 더 가까움




