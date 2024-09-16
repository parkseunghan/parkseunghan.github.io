---
title: "[Writeup] Webhacking.kr - old-10"
categories:
  - Web Hacking
tags:
  - Writeup
  - Webhacking.kr
  - old-10
last_modified_at: 2024-08-22T20:31:00-05:00
published: true
---

|

## 문제

<https://webhacking.kr/challenge/code-1/>

|

|

|

## 문제 코드

```jsx
<a id="hackme"
  style="position:relative;left:0;top:0"
  onclick="this.style.left=parseInt(this.style.left,10)+1+'px';if(this.style.left=='1600px')this.href='?go='+this.style.left"
  onmouseover="this.innerHTML='yOu'"
  onmouseout="this.innerHTML='O'">O</a>
```

|

|

|

## 코드 분석

```jsx
<a>O</a>
```

화면에 “O” 표시

|

```jsx
style="position:relative;left:0;top:0"
```

**`position:relative`**: 요소를 상대적으로 배치. 기본 위치를 기준으로 `left:0`, `top:0` 이동하여 배치. 초기 위치는 변하지 않음

|

```jsx
onclick="this.style.left=parseInt(this.style.left,10)+1+'px';if(this.style.left=='1600px')this.href='?go='+this.style.left"
```

**`this.style.left=parseInt(this.style.left,10)+1+'px';`**: 클릭 시 요소의 left 속성을 1px 증가시켜 오른쪽으로 이동 (left속성을 증가시키면 오른쪽으로 이동함)

**`parseInt(this.style.left,10)`**: left 속성의 값을 정수로 변환. ‘10’은 10진수로 변환하라는 뜻

**`+1+'px'`**: 위치를 1픽셀 증가시키고 ‘px’ 단위를 추가하여 새로운  left 값 설정

css에서는 숫자가 아닌 문자열을 받아들임 (’px’, ‘%’, ‘em’등) 그렇기 때문에 정수형으로 변환 후 뒤에 ‘px’ 단위를 추가해 문자열로 만들어주는 것

따라서, `10 + 1 + ‘px’`가 되어 `‘11px’`가 됨

**`if(this.style.left=='1600px')this.href='?go='+this.style.left"`**: left 값이 1600px가 되면, href 속성이 `?go=1600px`로 설정됨.

|

```jsx
onmouseover="this.innerHTML='yOu'"
onmouseout="this.innerHTML='O'"
```

화면에 보이는 O에 마우스를 가져다 대면 ‘yOu’로 바뀌고

마우스를 치우면 다시 ‘O’로 바뀜

> 

|

|

|

## Payload

a 태그의 요소를 1600px 위치에 도달시켜야 함

### 방법 1

‘O’를 1600번 클릭


### 방법 2

```jsx
style="position:relative;left:1599;top:0"
```

left 속성을 1599로 바꿔준 뒤, ‘O’ 요소를 한번 클릭해주어 1600px 위치에 도달

|

---