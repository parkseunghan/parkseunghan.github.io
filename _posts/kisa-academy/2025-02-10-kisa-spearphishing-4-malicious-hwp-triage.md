---
title: "KISA 아카데미 정리 - 스피어피싱 4. 악성 HWP 분석 흐름"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - Spear Phishing
  - HWP
  - Office Document
permalink: /security-academy/2025-02-10-kisa-spearphishing-4-malicious-hwp-triage/
last_modified_at: 2025-02-10T18:00:00+09:00
published: true
---
## 개요

한글 문서 기반 스피어피싱 사례에서 `HwpScan2`, `010 Editor`, OLE 구조 확인, 내부 스트림 점검 흐름을 다루는 파트

HWP는 국내 표적 공격에서 자주 사용되는 문서 형식이므로, 파일 구조와 포함 객체를 빠르게 확인하는 절차가 중요함

## 용어 정리

- `OLE(Object Linking and Embedding)`: 문서 내부에 다양한 스트림과 객체를 저장하는 복합 문서 구조
- `Section`: 문서 본문, 설정, 객체 데이터 등이 나뉘어 저장되는 구간
- `EPS(Encapsulated PostScript)`: 문서 내부에 포함될 수 있는 그래픽/스크립트 형식. 악성 코드 전달 매개로 악용될 수 있음
- `HwpScan2`: HWP 내부 구조와 취약 요소를 확인하는 분석 도구
- `PE Carver`: 문서나 바이너리 내부에서 포함된 PE 조각을 추출하는 도구

## HWP 분석의 출발점

HWP 파일 분석은 문서 외형보다 내부 구조를 먼저 보는 것이 중요함

공격자는 문서 내부에 OLE 객체, 스크립트, 쉘코드, 추가 페이로드를 숨길 수 있음

![HWP 구조 메모](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-093.png)

우선적으로 확인할 항목은 다음과 같음

- 문서가 OLE 기반 복합 구조인지
- 비정상 스트림이 존재하는지
- `Section`, `BinData`, 스크립트 계열 영역에 의심 데이터가 있는지
- PE 시그니처나 난독화된 데이터가 포함되어 있는지

![HwpScan2 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-095.png)

`HwpScan2`는 문서 구조를 빠르게 확인하는 데 유리하며, OLE dump보다 실무적으로 편하게 식별 가능한 경우가 있음

## 포함 객체와 PE 탐지

문서 내부에는 이미지나 정상 데이터처럼 보이는 영역 안에 PE 조각이 숨어 있을 수 있음

![내부 객체 확인](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-103.png)

`010 Editor`, `PE Carver`, Hex 단위 분석을 함께 사용하면 포함된 실행 파일 조각을 찾는 데 도움이 됨

![PE 추출 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-109.png)

의심 포인트는 아래와 같음

- `MZ`, `PE` 시그니처 존재 여부
- 비정상적으로 큰 `BinData`
- 압축 또는 XOR된 것처럼 보이는 반복 패턴
- 정상 문서 기능과 무관한 실행 구조 포함 여부

## 분석 시 주의점

HWP는 취약점 자체뿐 아니라, 외부 페이로드를 복호화하거나 메모리에 적재하는 전달 컨테이너로도 사용될 수 있음

따라서 `문서가 취약한가`만 볼 것이 아니라, `내부 객체가 추가 악성 행위를 준비하는가`도 함께 봐야 함

![구조 비교](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-118.png)

## 정리

악성 HWP 분석의 핵심은 문서 렌더링 결과가 아니라 내부 저장 구조 확인에 있음

`HwpScan2`로 큰 구조를 먼저 보고, `010 Editor`, `PE Carver`로 의심 객체와 포함 PE를 확인하는 순서가 효율적임




