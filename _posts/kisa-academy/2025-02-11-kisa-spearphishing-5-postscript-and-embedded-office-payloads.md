---
title: "KISA 아카데미 정리 - 스피어피싱 5. 포스트스크립트와 문서 내부 페이로드"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - Spear Phishing
  - PostScript
  - Office Document
permalink: /security-academy/2025-02-11-kisa-spearphishing-5-postscript-and-embedded-office-payloads/
last_modified_at: 2025-02-11T18:00:00+09:00
published: true
---
## 개요

문서 내부에 포함된 포스트스크립트, 인코딩 데이터, OOXML 기반 오피스 구조를 다루는 파트

문서형 악성코드 분석은 파일 확장자만으로 끝나지 않으며, 내부에 포함된 스크립트와 페이로드 전달 구조까지 확인해야 함

## 용어 정리

- `PostScript`: 인쇄와 그래픽 표현에 사용되는 페이지 기술 언어. 문서 내부에서 스크립트처럼 악용될 수 있음
- `Ghostscript`: PostScript, PDF 등을 해석하는 도구. 관련 행위를 추적할 때 활용 가능함
- `OOXML(Office Open XML)`: 최신 Office 문서의 압축 기반 XML 구조. `docx`, `xlsx`, `pptx`가 대표적 예시
- `VBA(Visual Basic for Applications)`: 오피스 매크로 구현에 사용되는 스크립트 언어
- `Base64`: 바이너리 데이터를 문자열로 표현하는 인코딩 방식

## 포스트스크립트 기반 페이로드

문서 내부에 포함된 포스트스크립트는 단순 렌더링 목적이 아니라, 추가 데이터를 해석하거나 실행 흐름을 이어 주는 매개로 사용될 수 있음

![포스트스크립트 메모](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-122.png)

이 경우 문서 내부 문자열이 곧바로 의미를 드러내지 않고, 인코딩 또는 난독화된 형태로 존재하는 경우가 많음

![인코딩 데이터 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-129.png)

따라서 문자열 추출 이후에는 `base64`, XOR, hex 인코딩 가능성을 함께 확인해야 함

## 오피스 문서 내부 구조

Office 문서는 외형상 하나의 파일이지만, 내부적으로는 여러 XML과 객체 파일이 묶인 압축 구조일 수 있음

![OOXML 구조](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-160.png)

이 구조 안에는 다음과 같은 의심 요소가 포함될 수 있음

- 외부 리소스를 참조하는 설정
- 매크로 관련 파일
- 인코딩된 스크립트
- 추가 바이너리 조각

![매크로 추출 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-166.png)

특히 `VBA`가 존재하는 경우, 자동 실행 매크로와 네트워크 호출, PowerShell 실행 흔적을 함께 확인해야 함

## 분석 관점

문서형 악성코드는 파일 형식에 따라 외형이 달라도 분석 질문은 비슷함

- 내부에 실행 가능한 코드가 있는지
- 외부에서 추가 데이터를 받는지
- 인코딩 또는 난독화가 적용되었는지
- 정상 사용자 문서 흐름과 무관한 객체가 포함되었는지

![최종 구조 메모](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-170.png)

## 정리

문서형 공격 분석은 첨부 파일을 여는 것으로 끝나지 않음

포스트스크립트, OOXML, VBA, 인코딩 데이터까지 함께 봐야 실제 페이로드 전달 구조를 파악할 수 있음




