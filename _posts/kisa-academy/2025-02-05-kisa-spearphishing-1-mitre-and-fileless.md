---
title: "KISA 아카데미 정리 - 스피어피싱 1. MITRE ATT&CK와 파일리스 공격"
categories:
  - Malware Analysis
tags:
  - KISA Academy
  - Spear Phishing
  - MITRE ATT&CK
  - Fileless
  - LoLBin
permalink: /security-academy/2025-02-05-kisa-spearphishing-1-mitre-and-fileless/
last_modified_at: 2025-02-05T18:00:00+09:00
published: true
---
## 개요

스피어피싱 대응 관점에서 `MITRE ATT&CK`, `TTP`, `파일리스 공격`을 먼저 다루는 파트

표적 공격 분석 시 공격자가 어떤 전술과 기술을 선택했는지 구조적으로 보는 기준이 필요함

또한 파일을 직접 생성하지 않고 메모리와 정상 도구를 활용하는 공격 흐름을 이해해야 이후 메일 분석, 문서 분석, LoLBin 분석으로 자연스럽게 이어질 수 있음

## 용어 정리

- `MITRE ATT&CK`: 공격자의 전술, 기술, 절차를 체계적으로 분류한 프레임워크. 공격 단계별로 어떤 행위가 선택될 수 있는지 정리하는 기준이 됨
- `TTP(Tactics, Techniques, Procedures)`: 공격 목표, 수행 방법, 실제 절차를 묶어 부르는 표현. 특정 그룹의 공격 특성을 비교할 때 사용됨
- `BAS(Breach and Attack Simulation)`: 조직의 탐지·대응 역량을 공격 시나리오 기반으로 점검하는 솔루션 분야
- `Fileless Attack(파일리스 공격)`: 실행 파일을 디스크에 남기지 않거나 최소화하고 메모리, 스크립트, 정상 프로세스를 이용해 동작하는 공격 유형
- `LoLBin(Living Off the Land Binary)`: 운영체제에 기본 포함된 정상 바이너리를 악용하는 방식. `regsvr32.exe`, `rundll32.exe`, `bitsadmin.exe` 등이 예시가 됨
- `Persistence(지속성)`: 시스템 재부팅 이후에도 공격자가 거점을 유지할 수 있도록 만드는 기법. 레지스트리 Run 키, 서비스 등록, 작업 스케줄러가 대표적 예시가 됨

## MITRE ATT&CK 프레임워크

`MITRE ATT&CK`는 표적 공격 그룹의 TTP를 정리한 분석 프레임워크다

공격자는 하나의 고정된 도구만 사용하는 것이 아니라, 공격 단계에 따라 다른 Tactic과 Technique를 선택함

따라서 단순히 악성 파일 하나를 보는 것이 아니라, `초기 침투 - 실행 - 지속성 - 권한 상승 - 내부 이동`과 같은 전체 흐름을 함께 봐야 함

![MITRE ATT&CK Matrix](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-001.png)

`MITRE ATT&CK Matrix`는 이러한 공격 단계를 매트릭스 형태로 보여줌

하나의 그룹이 특정 Persistence 기법을 반복적으로 사용면, 다음 사건에서도 유사한 행위를 빠르게 의심할 수 있음

![BAS 개요](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-002.png)

`BAS`는 이 공격 흐름을 실제 환경에서 시뮬레이션하여 방화벽, IDS/IPS, 메일 보안 솔루션, 관제 체계가 적절히 동작하는지 확인하는 데 사용됨

![TTP 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-006.png)

공격 그룹마다 자주 사용하는 TTP가 존재하므로, 프레임워크는 단순 이론이 아니라 침해사고 분석과 위협 헌팅의 기준점으로 활용됨

## 파일리스 공격

`파일리스 공격`은 디스크에 실행 파일을 남기지 않거나, 최소한의 흔적만 남기면서 메모리와 정상 도구를 활용하는 공격 방식

보안 솔루션은 일반적으로 `WriteFile`, `CreateFile`, 신규 실행 파일 생성과 같은 디스크 행위를 우선적으로 감시함

공격자는 이러한 감시 지점을 우회하기 위해 코드를 프로세스 메모리에서 직접 실행하거나, 정상 프로그램이 외부 코드를 불러오게 만드는 방식을 선택함

![파일리스 시나리오](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-009.png)

파일리스 공격은 다음과 같은 흐름으로 전개될 수 있음

- 스피어피싱 메일 전달
- 문서 열람 유도
- 매크로 또는 스크립트 실행
- 정상 바이너리를 통한 외부 코드 로드
- 메모리 상에서 페이로드 실행

이 과정에서는 디스크에 명확한 실행 파일이 남지 않거나, 정상 프로그램만 잠깐 실행된 것처럼 보일 수 있음

## LoLBin과 프로세스 인젝션

공격자는 별도 도구를 업로드하지 않고 시스템에 이미 존재하는 바이너리를 활용함

![LoLBin 개요](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-010.png)

`bitsadmin.exe`는 파일 다운로드와 작업 예약 기능을 악용하는 데 사용될 수 있음

`regsvr32.exe`는 원격 스크립트 실행이나 DLL 기반 로딩에 악용될 수 있음

![regsvr32 악용 예시](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-012.png)

`프로세스 인젝션`은 정상 프로세스의 메모리 공간에 코드를 주입하여 그 프로세스의 일부처럼 실행시키는 방식

![프로세스 인젝션](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-013.png)

예를 들어 `explorer.exe`는 항상 존재하는 정상 프로세스이므로, 이 안에서 악성 코드가 동작하면 사용자는 이상 징후를 체감하기 어려움

![비정상 네트워크 행위](/assets/images/writeup/kisa-academy/notion/spearphishing/spearphishing-014.png)

평소 네트워크 통신을 거의 하지 않는 프로세스가 외부와 통신하는 경우, 프로세스 인젝션 가능성을 함께 의심할 수 있음

## 정리

스피어피싱 분석은 메일 한 통만 보는 작업이 아니라, `초기 접근 이후 어떤 TTP가 이어지는지`까지 보는 작업임

`MITRE ATT&CK`는 이 흐름을 정리하는 기준이 되며, `파일리스`, `LoLBin`, `프로세스 인젝션`은 최근 표적 공격에서 자주 확인되는 핵심 축에 해당함





