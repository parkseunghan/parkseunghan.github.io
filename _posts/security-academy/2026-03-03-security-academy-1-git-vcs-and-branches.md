---
title: "시큐리티아카데미 7기 정리 - Git 1. VCS와 브랜치 흐름"
date: 2026-03-03T18:00:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Git
  - VCS
  - Branch
permalink: /security-academy/git-vcs-and-branches/
last_modified_at: 2026-03-30T20:30:00+09:00
published: true
---
## 개요

Git의 기본 구조와 브랜치 동작 방식을 다루는 파트

실습 흐름: `작업 디렉터리 -> 스테이징 영역 -> 커밋 -> 브랜치 -> 병합`

중점: `.git` 내부의 `HEAD`와 브랜치 파일 변화

## 용어 정리

- `VCS(Version Control System)`: 파일 변경 이력을 관리하는 체계
- `DVCS(Distributed Version Control System)`: 저장소 전체 이력을 로컬에 복제하는 방식
- `Repository(저장소)`: Git이 커밋과 브랜치를 기록하는 공간
- `Staging Area`: 커밋 후보를 올려두는 중간 영역
- `Commit`: 특정 시점 상태를 저장한 스냅샷
- `HEAD`: 현재 작업 중인 브랜치 또는 커밋을 가리키는 포인터
- `Branch`: 독립된 작업 흐름을 위한 참조
- `Fast-forward Merge`: 병합 커밋 없이 포인터만 전진시키는 병합 방식
- `3-way Merge`: 공통 조상과 양쪽 브랜치를 함께 비교하는 병합 방식

## Git과 버전 관리

- `Local VCS`: 로컬 복사본 중심 관리 방식
- `CVCS`: 중앙 서버 중심 관리 방식
- `DVCS`: 로컬에도 전체 이력이 존재하는 방식

Git은 `DVCS`에 해당함

이 구조에서는 네트워크 연결이 없더라도 커밋, 로그 확인, 브랜치 생성 같은 기본 작업을 계속 진행할 수 있음

또한 원격 저장소가 잠시 불안정하더라도 로컬 이력 자체는 유지되므로 복구와 비교 작업이 쉬움

## 기본 작업 흐름

### `git config --global user.name "park"`

커밋 작성자 이름을 먼저 설정하는 명령어

```shell
git config --global user.name "park"
```

- `git config`: Git 설정 변경
- `--global`: 현재 사용자 계정 전체에 공통 적용
- `user.name`: 커밋 작성자 이름 항목

### `git config --global user.email "secpack@proton.me"`

커밋 작성자 이메일을 설정하는 명령어

```shell
git config --global user.email "secpack@proton.me"
```

- `user.email`: 커밋 작성자 이메일 항목

이 두 설정이 없으면 커밋 기록에 작성자 식별 정보가 제대로 남지 않음

### `git clone <repository>`

원격 저장소를 로컬로 복제하는 시작 명령어

```shell
git clone <repository>
```

- `clone`: 저장소 복제
- `<repository>`: 원격 저장소 주소

복제 직후에는 `.git` 디렉터리까지 같이 내려오므로, 이력과 브랜치 정보가 함께 들어옴

### `git status`

작업 디렉터리와 스테이징 영역 상태를 확인하는 가장 기본적인 명령어

```shell
git status
```

- `status`: 수정됨, 스테이징됨, 추적되지 않음 상태를 요약 출력

우선 확인 명령어: `git status`

### `git add .`

변경 내용을 스테이징 영역으로 올리는 명령어

```shell
git add .
```

- `add`: 스테이징 영역에 반영
- `.`: 현재 디렉터리 이하 전체

`git add`는 저장이 아니라 "커밋 후보 선택"에 가까움

### `git restore .`

작업 디렉터리의 수정 내용을 마지막 커밋 상태로 되돌리는 명령어

```shell
git restore .
```

- `restore`: 파일 상태 복원
- `.`: 현재 경로 기준 전체

아직 커밋하지 않은 변경을 버릴 때 사용함

### `git restore --staged .`

스테이징만 해제하고 작업 파일 수정은 유지하는 명령어

```shell
git restore --staged .
```

- `--staged`: 인덱스, 즉 스테이징 영역만 대상으로 지정

작업은 살리고 커밋 후보에서만 빼고 싶을 때 유용함

### `git commit -m "메시지"`

스테이징된 내용을 이력으로 저장하는 명령어

```shell
git commit -m "메시지"
```

- `commit`: 현재 스테이징 상태를 커밋으로 기록
- `-m`: 커밋 메시지를 명령행에서 직접 지정

### `git log --oneline`

커밋 이력을 짧게 보는 명령어

```shell
git log --oneline
```

- `log`: 커밋 이력 출력
- `--oneline`: 해시와 메시지를 한 줄로 축약

핵심은 `git add`와 `git commit`의 역할을 구분하는 데 있음

핵심은 `git add`와 `git commit`의 역할을 구분하는 데 있음

`git add`는 변경 내용을 커밋 후보로 올리는 작업이고, `git commit`은 그 후보 상태를 저장소 이력에 남기는 작업임

## HEAD와 브랜치 포인터

### `git switch -c dev`

새 브랜치를 만들고 바로 그 브랜치로 이동하는 명령어

```shell
git switch -c dev
```

- `switch`: 브랜치 이동 전용 명령
- `-c`: 브랜치 생성과 이동을 동시에 수행
- `dev`: 생성할 브랜치 이름

`.git/HEAD` 파일을 열어보면 현재 브랜치 경로가 기록되어 있음

해당 경로를 따라가면 `.git/refs/heads/<branch>` 파일이 존재하고, 그 안에는 현재 브랜치가 가리키는 커밋 해시가 저장됨

즉 브랜치는 폴더처럼 독립된 공간이 아니라, 특정 커밋을 가리키는 이동 가능한 참조로 이해하는 편이 맞음

## Fast-forward와 3-way merge

### `git switch main`

병합 대상 기준 브랜치로 이동하는 명령어

```shell
git switch main
```

### `git merge dev`

현재 브랜치에 `dev` 브랜치 변경을 합치는 명령어

```shell
git merge dev
```

- `merge`: 다른 브랜치 이력을 현재 브랜치에 병합
- `dev`: 병합할 대상 브랜치

### `git log --oneline`

병합 후 실제 커밋 그래프가 어떻게 바뀌었는지 확인하는 단계

```shell
git log --oneline
```

현재 브랜치에서 분기가 따로 발생하지 않았다면 `fast-forward`가 가능함

이 경우 Git은 병합 커밋을 새로 만들지 않고 `main` 포인터만 `dev` 최신 커밋 위치까지 전진시킴

반대로 양쪽 브랜치 모두에서 커밋이 누적된 상태라면 `3-way merge`가 수행됨

이때 Git은 공통 조상, 현재 브랜치, 병합 대상 브랜치를 함께 비교해 결과를 계산함

## 충돌 실습 포인트

### `git branch -D dev`

이전 실습용 브랜치를 강제로 삭제하는 명령어

```shell
git branch -D dev
```

- `branch`: 브랜치 관리 명령
- `-D`: 병합 여부와 무관하게 강제 삭제

### `git switch -c conflict`

충돌 실습용 브랜치를 새로 만드는 단계

```shell
git switch -c conflict
```

### `git add .`

충돌 실습용 수정 내용을 스테이징하는 단계

```shell
git add .
```

### `git commit -m "conflict에서 같은 곳 수정"`

충돌 브랜치 쪽 변경을 먼저 커밋하는 단계

```shell
git commit -m "conflict에서 같은 곳 수정"
```

### `git switch main`

기준 브랜치인 `main`으로 다시 돌아가는 단계

```shell
git switch main
```

### `git add .`

`main` 쪽 수정 내용을 스테이징하는 단계

```shell
git add .
```

### `git commit -m "main에서도 같은 곳 수정"`

같은 위치를 다르게 수정한 뒤 별도 커밋을 남기는 단계

```shell
git commit -m "main에서도 같은 곳 수정"
```

### `git merge conflict`

실제 충돌을 일으키는 병합 단계

```shell
git merge conflict
```

같은 파일의 같은 위치를 서로 다르게 수정하면 자동 병합이 실패하고 충돌이 발생함

충돌은 비정상 상태라기보다, Git이 어느 쪽을 살릴지 임의 결정하지 않고 사용자에게 판단을 넘기는 절차에 가까움

따라서 충돌이 발생했다면 충돌 마커를 정리하고 다시 `git add`, `git commit` 순서로 마무리해야 함

## 정리

Git의 핵심은 파일 복사본 관리가 아니라, 변경 이력을 `커밋`, `브랜치`, `포인터` 단위로 구조화하는 데 있음

브랜치를 자유롭게 다루려면 `HEAD`, 스테이징, 병합 구조를 같이 이해해야 함





