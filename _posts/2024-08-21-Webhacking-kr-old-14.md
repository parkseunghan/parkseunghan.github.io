---
title: "[Writeup] Webhacking.kr - old-14"
categories:
  - Web Hacking
tags:
  - Writeup
  - Webhacking.kr
  - old-14
last_modified_at: 2024-08-22T00:00:00-05:00
published: false
---

|

## 문제

<https://webhacking.kr/challenge/js-1/>

|

|

|

## 문제 코드

```js
<form name="pw" onsubmit="ck();return false">
	<input type="text" name="input_pwd">
	<input type="button" value="check" onclick="ck()">
</form>

<script>
function ck(){
  var ul=document.URL;
  ul=ul.indexOf(".kr");
  ul=ul*30;
  if(ul==pw.input_pwd.value) { location.href="?"+ul*pw.input_pwd.value; }
  else { alert("Wrong"); }
  return false;
}
</script>
```

|

|

|

## 코드 분석

### <form>

```js
<form name="pw" onsubmit="ck();return false">
	<input type="text" name="input_pwd">
	<input type="button" value="check" onclick="ck()">
</form>
```

**`onsubmit="ck();return false"`**: 사용자가 엔터를 통해 폼을 제출하면, ck() 함수를 실행하고 return false로 폼 제출을 막음.

**`onclick="ck()"`**: 마우스로 check 버튼을 클릭하면 ck() 함수 실행

> 단순히 ck() 함수 실행이 목적

|

### ck()

```js
var ul=document.URL;
```

**`document.URL`**: 현재 웹 페이지의 전체 URL을 나타내는 속성

현재 웹 페이지의 URL을 ‘ul’ 변수에 저장

> ul = “https://webhacking.kr/challenge/js-1/”

|

```js
ul=ul.indexOf(".kr");
```

**`string.indexOf(searchValue, fromIndex)`**: 문자열(`string`) 내에서 찾고자 하는 부분(`searchValue`)이 처음 나타내는 위치 반환. 없으면 ‘-1’ 반환

`fromIndex`는 선택 사항으로, 검색을 시작할 위치 지정. 기본값 0

‘ul’변수에 저장된 문자열에서 “.kr” 문자열이 처음 나타내는 위치를 숫자로 반환

.kr은 18번째에 등장

> ul = 18

|

```js
ul=ul*30;
```

> ul = 18 * 30; // 540

|

```js
if(ul==pw.input_pwd.value) { location.href="?"+ul*pw.input_pwd.value; }
```

ul 값과 사용자 입력 값이 같으면, href 속성이

`"?" + ul * 사용자 입력 값`

=> `"?" + 540 * 540`

=> `?291600`

로 설정됨

|

---

|

## Exploit

### 방법 1 

텍스트 입력창에

```jsx
540
```

입력 후 엔터 또는 check 버튼 클릭

|

### 방법 2 

경로 직접 입력

```
https://webhacking.kr/challenge/js-1/?291600
```

|

---