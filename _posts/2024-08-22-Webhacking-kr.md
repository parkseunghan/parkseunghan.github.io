---
title: "[Writeup] Webhacking.kr - old-14"
published: true
---

|

# old-14

[Challenge 14](https://webhacking.kr/challenge/js-1/)

|

---

|

## 문제 코드

```js
<form name="pw" onsubmit="ck();return false">
	<input type="text" name="input_pwd">
	<input type="button" value="check" onclick="ck()">
</form>
```

```js
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

버튼을 누르면 ck() 함수가 실행됨

|

---

|

## 코드 분석

**`ck() 함수`**

|

```jsx
var ul=document.URL;
```

**`document.URL`**: 현재 웹 페이지의 전체 URL을 나타내는 속성

|

현재 웹 페이지의 URL을 ‘ul’ 변수에 저장

ul = “https://webhacking.kr/challenge/js-1/”

|

```jsx
ul=ul.indexOf(".kr");
```

**`string.indexOf(searchValue, fromIndex)`**: 문자열(`string`) 내에서 특정 부분(`searchValue`) 문자열이 처음 나타내는 위치 반환. 없으면 ‘-1’ 반환

`fromIndex`는 선택 사항으로, 검색을 시작할 위치 지정. 기본값 0

‘ul’변수에 저장된 문자열에서 “.kr” 문자열이 처음 나타내는 위치를 숫자로 반환

|

.kr은 18번째에 등장

ul = 18

|

```jsx
ul=ul*30;
```

ul = 18 * 30; // 540

|

---

|

## Exploit

```jsx
540
```

|

---

|