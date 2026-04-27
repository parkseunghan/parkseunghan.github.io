---
title: "KnockOn Bootcamp 2nd - 1주차 Cookie & Session 실습"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - Cookie
  - Session
last_modified_at: 2024-08-04T16:54:00+09:00
published: true
---
## 네이버 접속 시 사용되는 쿠키들 확인해보기

## 1. 크롬 브라우저에 ID와 PW가 이미 기억되어 있는 상황

1-1. 네이버 접속 시 다음과 같은 쿠키가 생성됨

```
BUC
NAC
NACT
NM_srt_chzzk
NNB
PM_CK_loc
```

1-2. 로그인 버튼을 클릭(로그인 화면)

```
BUC
NAC
NACT
NNB
nid_buk
nid_slevel
```

| - NM_srt_chzzk
| - PM_CK_loc
| + nid_buk
| + nid_slevel

1-3. 아이디와 비밀번호 입력 후 로그인 버튼을 클릭(네이버 홈)

```
BUC
NAC
NACT
NID_AUT
NID_JKL
NID_SES
NM_srt_chzzk
NNB
PM_CK_loc
nid_buk
nid_inf
nid_slevel
```

| + NM_srt_chzzk
| + PM_CK_loc
| + NID_AUT
| + NID_JKL
| + NID_SES
| + nid_inf

1-3-1. 사용자 등록 페이지가 뜬 경우

```
BUC
NAC
NACT
NID_AUT
NID_JKL
NID_SES
NNB
nid_buk
nid_slevel
```

| + NID_AUT
| + NID_JKL
| + NID_SES
| + nid_inf

1-3-2. 등록 버튼을 클릭(네이버 홈)

```
BUC
NAC
NACT
NID_AUT
NID_JKL
NID_SES
NNB
nid_buk
nid_slevel
```

| + NM_srt_chzzk
| + PM_CK_loc

## 2. 크롬 게스트 모드로 접속하여 ID와 PW를 처음 입력하는 상황

2-1. 네이버 접속 시 다음과 같은 쿠키가 생성됨

```
BUC
NAC
NACT
NNB
PM_CK_loc
```

2-2. 로그인 버튼 클릭 시

```
BUC
NAC
NACT
NNB
nid_slevel
```

| - PM_CK_loc
| + nid_slevel

2-3. 로그인 시 (사용자 등록 화면)

```
BUC
NAC
NACT
NID_AUT
NID_JKL
NID_SES
NNB
nid_inf
nid_slevel
```

| + NID_AUT
| + NID_JKL
| + NID_SES
| + nid_inf

2-4. 등록 버튼 클릭 시(네이버 홈)

(등록 안함 눌러도 똑같음)

```
BUC
NAC
NACT
NID_AUT
NID_JKL
NID_SES
NM_srt_chzzk
NNB
PM_CK_loc
nid_inf
nid_slevel
```

| + NM_srt_chzzk
| + PM_CK_loc

## 위에서 얻은 쿠키를 변조한 후 결과 분석하기

로그인 된 상태임

```
BUC
NAC
NACT
NID_AUT
NID_JKL
NID_SES
NM_srt_chzzk
NNB
PM_CK_loc
nid_buk
nid_inf
nid_slevel
```

### 1. BUC

변조 후 새로고침하면 다시 원래대로 돌아옴. 알 수 없음

### 2. NAC

값을 변조 후 새로고침 하면 값은 유지가 되지만, 자세한 기능을 알 수 없음

### 3. NACT

변조 후 새로고침하면 다시 원래대로 돌아옴. 알 수 없음

### 4. `NID_AUT`

Session

값을 변조 후 새로고침을 하면 로그아웃이 됨

**`로그인을 유지하는 기능`**

### 5. NID_JKL

Session

값을 변조 후 새로고침을 해도 값은 유지됨. 알 수 없음

### 6. `NID_SES`

Session

*NID_AUT*와 마찬가지로, 값을 변조 후 새로고침을 하면 로그아웃이 됨

**`로그인을 유지하는 기능`**

### 7. NM_srt_chzzk

값을 변조 후 새로고침을 해도 값은 유지됨. 알 수 없음

### 8. NNB

변조 후 새로고침하면 다시 원래대로 돌아옴. 알 수 없음

### 9. PM_CK_loc

변조 후 새로고침하면 다시 원래대로 돌아옴. 알 수 없음

### 10. `nid_buk`

값을 변조 후 새로고침 하면 값은 유지됨

로그아웃 후 다시 로그인할 때 사용자 등록 여부가 뜸

**`등록에 관한 정보를 기억함`**

### 11. nid_inf

Session

값을 변조 후 새로고침을 해도 값은 유지됨. 알 수 없음

### 12. nid_slevel

값을 변조 후 새로고침을 해도 값은 유지됨. 알 수 없음

## 추가

로그인 후, 네이버 검색창을 클릭하면

![naver 검색창](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-cookie-session-challenge-01.png)
```
_naver_usersession_
```
이 추가됨

**`분석`**

사용자의 검색 기록을 기억함

![naver 프로필](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-cookie-session-challenge-02.png)

메일, 카페, 블로그 등을 클릭하면

```
JSESSIONID
```
가 추가됨

**`분석`**

세션 유지를 통해 로그인 상태를 유지한 채로 메일, 카페, 블로그 등의 페이지로 이동할 수 있게 해줌

