---
title: "시큐리티아카데미 7기 정리 - Git 2. Rebase와 Docker 입문"
date: 2026-03-03T18:10:00+09:00
categories:
  - Security Engineering
tags:
  - Security Academy 7th
  - Git
  - Rebase
  - Docker
permalink: /security-academy/git-rebase-and-docker-basics/
last_modified_at: 2026-03-30T20:40:00+09:00
published: true
---
## 개요

`rebase`를 이용한 커밋 정리와 Docker의 기본 실행 모델을 함께 다룸

Git에서는 이력 정리가 핵심이고, Docker에서는 이미지와 컨테이너를 분리해서 이해하는 것이 핵심임

## 용어 정리

- `Rebase`: 현재 브랜치의 커밋 기반점을 다른 커밋 위로 다시 올리는 작업
- `Interactive Rebase`: 커밋 순서, 병합, 메시지를 수동 정리하는 방식
- `Image`: 컨테이너 실행을 위한 읽기 전용 템플릿
- `Container`: 이미지로부터 실행된 인스턴스
- `ENTRYPOINT`: 컨테이너 시작 시 기본으로 실행할 명령
- `CMD`: 기본 인자 또는 대체 명령
- `Volume`: 컨테이너 밖에 유지되는 데이터 저장소

## Rebase의 의미

`merge`는 두 브랜치 이력을 그대로 합치는 방식이고, `rebase`는 현재 작업 브랜치의 출발 지점을 새 기준 위로 다시 올리는 방식

따라서 `rebase` 이후에는 커밋 부모가 바뀌므로, 같은 내용의 커밋이라도 해시가 달라질 수 있음

권장 범위: 실습용 브랜치, 개인 작업 브랜치

## Rebase 실습

### `git switch -c rebase`

rebase 실습용 브랜치를 만드는 단계

```shell
git switch -c rebase
```

### `git add .`

rebase 브랜치에서 만든 변경을 스테이징하는 단계

```shell
git add .
```

### `git commit -m "rebase 커밋 생성"`

현재 브랜치에 커밋 하나를 만드는 단계

```shell
git commit -m "rebase 커밋 생성"
```

### `git switch main`

기준 브랜치로 돌아가는 단계

```shell
git switch main
```

### `git add .`

`main`에서 만든 변경을 스테이징하는 단계

```shell
git add .
```

### `git commit -m "main 커밋 생성"`

기준 브랜치에도 별도 커밋을 남겨 분기 상태를 만드는 단계

```shell
git commit -m "main 커밋 생성"
```

### `git switch rebase`

다시 실습 브랜치로 이동하는 단계

```shell
git switch rebase
```

### `git rebase main`

현재 브랜치의 커밋 기반점을 `main` 위로 다시 올리는 명령어

```shell
git rebase main
```

- `rebase`: 현재 브랜치 커밋을 새 기준 위에 재배치
- `main`: 새 기준 브랜치

### `git rebase -i HEAD~3`

최근 커밋을 직접 정리하는 interactive rebase 명령어

```shell
git rebase -i HEAD~3
```

- `-i`: interactive 모드 진입
- `HEAD~3`: 현재 HEAD 기준 세 개 전 커밋까지 범위 지정

interactive rebase에서 자주 쓰는 키워드는 다음과 같음

- `pick`: 현재 커밋 그대로 유지
- `s` 또는 `squash`: 위 커밋에 내용을 합침
- `reword`: 내용은 유지하고 메시지만 수정

여러 개의 작은 커밋을 하나의 의미 있는 커밋으로 합치는 과정이 중요했음

## Docker의 기본 구조

Docker는 애플리케이션과 실행 환경을 이미지로 묶고, 이를 컨테이너로 실행하는 방식

이미지는 설계도에 가깝고, 컨테이너는 실제 실행 중인 프로세스 집합에 가까움

동일 이미지를 여러 번 실행 시 여러 컨테이너가 생성될 수 있음

## Docker 기본 명령어

### `docker run --rm hello-world`

Docker 엔진이 정상 동작하는지 가장 먼저 확인할 때 쓰는 테스트 명령어

```shell
docker run --rm hello-world
```

- `docker run`: 이미지 기반 컨테이너 생성 및 실행
- `--rm`: 종료 후 컨테이너 자동 삭제
- `hello-world`: 테스트용 이미지 이름

### `docker run -d --rm --name ubuntu ubuntu sleep 99999999999999`

오래 살아 있는 컨테이너를 하나 띄워 두는 실습 명령어

```shell
docker run -d --rm --name ubuntu ubuntu sleep 99999999999999
```

- `-d`: detached mode, 백그라운드 실행
- `--rm`: 종료 시 자동 삭제
- `--name ubuntu`: 컨테이너 이름 지정
- 첫 번째 `ubuntu`: 사용할 이미지 이름
- `sleep 99999999999999`: 컨테이너를 오래 유지하기 위한 실행 명령

### `docker exec -it ubuntu /bin/bash`

이미 실행 중인 컨테이너 내부로 들어가는 명령어

```shell
docker exec -it ubuntu /bin/bash
```

- `exec`: 실행 중 컨테이너 안에서 명령 수행
- `-i`: 표준 입력 유지
- `-t`: TTY 할당
- `ubuntu`: 대상 컨테이너 이름
- `/bin/bash`: 실행할 셸

### `docker run -d -p 8080:80 --name nginx nginx`

웹 서버 컨테이너를 띄우고 호스트 포트와 연결하는 명령어

```shell
docker run -d -p 8080:80 --name nginx nginx
```

- `-p 8080:80`: 호스트 8080 포트를 컨테이너 80 포트에 매핑
- `--name nginx`: 컨테이너 이름 지정
- 마지막 `nginx`: 사용할 이미지 이름

포트 매핑은 "호스트에서 어디로 들어오면 컨테이너 어디로 연결할 것인가"를 정하는 핵심 옵션임

### `docker build -t python-app:1.0 .`

현재 디렉터리의 Dockerfile을 바탕으로 이미지를 만드는 명령어

```shell
docker build -t python-app:1.0 .
```

- `build`: 이미지 생성
- `-t python-app:1.0`: 이미지 이름과 태그 지정
- `.`: 현재 디렉터리를 빌드 컨텍스트로 사용

`docker run --rm hello-world`는 Docker 엔진이 정상 동작하는지 가장 빠르게 확인할 수 있는 테스트에 가까움

`sleep`을 길게 주는 예시는 컨테이너를 바로 종료시키지 않고 살아 있는 상태로 유지하기 위한 목적임

## ENTRYPOINT와 CMD

`ENTRYPOINT`는 컨테이너가 시작될 때 반드시 실행할 도구를 정하는 데 적합함

`CMD`는 기본 인자를 주거나, 별도 지정이 없을 때 실행할 기본 명령을 정하는 데 적합함

중요했던 부분은 둘의 역할이 다르다는 점임

- `ENTRYPOINT`: 사용할 도구를 고정
- `CMD`: 기본 인자를 제공

따라서 실행 시 추가 인자를 붙이면 `ENTRYPOINT`에 인자가 전달되는 구조를 이해해야 함

## 볼륨과 네트워크

Docker 컨테이너는 기본적으로 휘발성 환경이므로, 데이터가 남아야 하는 경우 볼륨이 필요함

또한 여러 컨테이너를 연동할 때는 사용자 정의 네트워크를 두는 편이 관리가 쉬움

웹 애플리케이션, Redis, DB를 각각 분리하면서 네트워크 이름과 포트 연결을 함께 다루는 구조가 중요했음

## 정리

Git에서는 `rebase`를 이용해 커밋 의미를 정리할 수 있고, Docker에서는 이미지와 컨테이너의 역할을 분리해서 봐야 함

공통 중점: 결과보다 내부 구조 변화



