---
title: "KnockOn Bootcamp 2nd - 1주차 HTML, CSS, JavaScript"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - HTML
  - CSS
  - JavaScript
last_modified_at: 2024-08-06T17:54:00+09:00
published: true
---
## HTML, CSS, JS의 기본 개념, 용도, 사용방법, 관계 등등

## HTML (HyperText Markup Language)

웹 문서의 *뼈와 살*을 담당

웹 페이지의 구조와 콘텐츠를 정의

태그와 속성을 통해 구조화된 문서 작성 지원

## CSS (Cascading Style Sheets)

웹 문서의 *생김새* 지정

HTML 콘텐츠의 시각적 스타일 설정

웹 리소스들의 시각화 방법을 기재한 스타일 시트

글자 색, 모양, 배경 색, 이미지 크기, 위치 등 지정 가능

브라우저는 CSS를 참고하여 웹 문서를 시각화

## JS (JavaScript)

웹 문서의 *동작* 정의

HTML 콘텐츠에 동적인 기능

버튼 클릭 시 어떻게 반응할지, 데이터 입력 시 어디로 전송할지 등 구현

사용자 브라우저에서 실행됨 -> 클라이언트가 실행하는 코드 (Client-Side Script)

## 웹 페이지 제작에 필요한 기본적인 HTML 태그들

```html
<!DOCTYPE html>
<html lang="ko-KR">
<head>
    <title>Pack's Blog</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { color: navy; }
        p { line-height: 1.6; }
    </style>
</head>
<body>
    <h1>Welcome to Pack's Blog</h1>
    <p>This is a paragraph of text. Here is a <a href="https://www.naver.com">link</a>.</p>

    <h2>h2태그. 이미지</h2>
    <img src="image.jpg" alt="이미지 설명" width="300">

    <h2>List</h2>
    <ul>
        <li>First item</li>
        <li>Second item</li>
        <li>Third item</li>
    </ul>

    <h2>Table</h2>
    <table border="1">
        <thead>
            <tr>
                <th>Header 1</th>
                <th>Header 2</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
            <tr>
                <td>Data 3</td>
                <td>Data 4</td>
            </tr>
        </tbody>
    </table>

    <h2>Form</h2>
    <form action="/submit" method="post">
        <label for="name">Name:</label>
        <input type="text" id="name" name="name">
        <button type="submit">Submit</button>
    </form>
</body>
</html>
```

## 문서 구조 태그

**`<!DOCTYPE html>`**: 문서 형식을 정의

**`<html>`**: HTML 문서의 루트 요소

**`<head>`**: 메타데이터, 스타일, 링크, 스크립트 등을 포함

**`<title>`**: 브라우저 탭에 표시되는 문서 제목

**`<body>`**: 웹 페이지의 본문 콘텐츠를 포함

## 텍스트 관련 태그

**`<h1> ~ <h6>`**: *제목 태그*. <h1>이 가장 크고 중요함, <h6>이 가장 작음

**`<p>`**: *단락*

**`<a>`**: *하이퍼링크*. *href 속성*으로 링크할 URL을 지정

**`<span>`**: *인라인 요소*. 텍스트의 일부를 묶어 *스타일을 적용*할 때 사용

**`<strong>`**: *굵은* 텍스트

**`<em>`**: *이탤릭체* 텍스트

**`<br>`**: *줄 바꿈* 삽입

**`<hr>`**: *수평선* 삽입

## 목록 태그

**`<ul>`**: *순서 없는* 목록

**`<ol>`**: *순서 있는* 목록

**`<li>`**: *목록 항목*

## 이미지 및 멀티미디어 태그

**`<img>`**: *이미지*. *src 속성*으로 이미지 파일의 URL을 지정

**`<audio>`**: *오디오* 콘텐츠

**`<video>`**: *비디오* 콘텐츠

## 표 관련 태그

**`<table>`**: *표*

**`<tr>`**: 표의 *행*

**`<td>`**: 표의 *데이터*

**`<th>`**: 표의 *헤더 셀*

**`<thead>`**: 표의 *헤더* 부분을 그룹화

**`<tbody>`**: 표의 *본문* 부분을 그룹화

**`<tfoot>`**: 표의 *바닥글* 부분을 그룹화

## 폼 관련 태그

**`<form>`**: 폼

**`<input>`**: 사용자 입력을 받는 *입력 필드*

**`<textarea>`**: *여러 줄*의 텍스트 *입력 필드*

**`<button>`**: 클릭 가능한 *버튼*

**`<label>`**: 폼 요소의 라벨

**`<select>`**: 드롭다운 목록

**`<option>`**: 드롭다운 목록의 항목

## 스타일링을 위한 CSS의 기본적인 문법과 속성들

## 기본 문법

CSS는 *선택자(selector)*와 *선언(declaration)*으로 구성됨

선언은 *속성(property)*과 *값(value)*으로 이루어짐

```css
선택자 {
    속성: 값;
}
```

```css
body {
    background-color: powderblue;
}
h1 {
    color: blue;
}
p {
    color: red;
}
```

> body 선택자의 배경 색상은 powderblue
> hi 선택자의 글자 색은 blue
> p 선택자의 글자 색은 red

## 선택자 (Selectors)

스타일을 적용할 HTML 요소를 지정

태그 선택자, 클래스 선택자, 아이디 선택자, 그룹 선택자, 자손 선택자, 자식 선택자, 형제 선택자, 일반 형제 선택자, 속성 선택자가 있음

**`태그 선택자 (Tag Selector)`**: *특정 태그*의 모든 요소를 선택

```css
body {
    background-color: powderblue;
}
p {
    color: red;
}
```

> body 태그와 p태그에 적용

```html
<body>바디 태그임</body>
<p>P 태그임</p>
```

> HTML에서 태그 선택자 적용 예
> 태그 자체에 적용됨

**`클래스 선택자 (Class Selector)`**: 특정 클래스에 속한 요소 선택. 클래스 *이름 앞에 점(.)*을 붙임

```css
.container {
    font-size: 20px;
    color: red;
}
```

> .container 클래스에 속한 모든 요소에 적용

```html
<p class=".container">이 P 태그는 ".container" 클래스임</p>
<div class=".container">이 div 태그도 ".container" 클래스</div>
```

> HTML에서 클래스 선택자 적용 예
> 해당 클래스를 지정한 태그에만 적용됨

**`아이디 선택자 (ID Selector)`**: 특정 아이디를 가진 요소에 스타일을 적용. 아이디 *이름 앞에 샵(#)*을 붙임. 아이디는 문서 내에서 유일함

```css
#header {
    background-color: yellow;
    padding: 10px;
}
```

> #header 아이디를 가진 모든 요소에 적용

```html
<h1 id="header">id가 header임</h1>
```

> HTML에서 아이디 선택자 적용 예
> 해당 아이디를 지정한 태그에만 적용됨

**`그룹 선택자 (Group Selector)`**: 여러 HTML 요소에 동일한 스타일 적용. *쉼표(,)*로 구분

```css
h1, h2, h3 {
    color: green;
}
```

> h1, h2, h3 태그에 적용

```html
<h1>h1 태그임</h1>
<h2>h2 태그임</h2>
<h3>h3 태그임</h3>
```

> HTML에서 그룹 선택자 적용 예
> 그룹으로 지정된 태그에 모두 적용됨

**`자손 선택자 (Descendant Selector)`**: 특정 요소의 모든 자손 요소에 스타일 적용. *공백*으로 구분

```css
div p {
    color: purple;
}
```

> div에 속한 p에 적용

```html
<div>
    <p>div의 자손 p. 적용됨</p>
    <span>div의 자손 span</span>
</div>
<p>div 밖에 있는 p. 적용 안됨</p>
```

> HTML에서 자손 선택자 적용 예
> 자손으로 지정된 태그에 모두 적용됨

**`자식 선택자 (Child Selector)`**: 특정 요소의 바로 아래 자식 요소에 스타일 적용. *(>) 기호*로 구분

```css
ul > li {
    list-style-type: square;
}
```

> ul 바로 아래에 있는 li에 적용

```html
<ul>
    <li>First item</li>
    <li>Second item
        <ul>
            <li>Sub item</li>
        </ul>
    </li>
</ul>
```

> HTML에서 자식 선택자 적용 예
> 바로 아래 자식 태그에 적용됨

**`형제 선택자 (Adjacent Sibling Selector)`**: 특정 요소의 바로 다음에 오는 형제 요소에 스타일 적용. *(+) 기호*로 구분

```css
h1 + p {
    margin-top: 0;
}
```

> h1바로 다음에 오는 p에만 적용

```html
<h1>Heading</h1>
<p>h1 바로 다음에 오는 p. 적용됨</p>
<p>두 번째 p. 적용 안됨</p>
```

> HTML에서 형제 선택자 적용 예
> 바로 다음에 오는 p태그에만 적용됨

**`일반 형제 선택자 (General Sibling Selector)`**: 특정 요소 뒤에 나오는 모든 형제 요소에 스타일 적용. *(~) 기호*로 구분

```css
h1 ~ p {
    color: teal;
}
```

> h1 다음에 오는 모든 p에 적용

```html
<h1>Heading</h1>
<p>첫 번째 p. 적용됨</p>
<p>두 번째 p. 적용됨</p>
```

> HTML에서 일반 형제 선택자 적용 예
> h1 다음에 오는 모든 p태그에 적용됨

**`속성 선택자 (Attribute Selector)`**: 특정 속성을 가진 HTML 요소에 스타일 적용

```css
a[href] {
    color: orange;
}
a[target="_blank"] {
    text-decoration: underline;
}
```

> 해당 태그에 있는 속성에 스타일을 적용함

```html
<a href="https://www.naver.com">a태그에 있는 href 속성에 적용됨</a>
<a target="_blank" href="https://www.naver.com">a태그에 있는 target="_blank" 속성과 href 속성에 적용됨</a>
<a>Link without href</a>
```

> HTML에서 속성 선택자 적용 예
> a태그 안에 있는 해당 속성에 적용됨

## 웹 페이지의 동적 기능을 위한 JS의 기본적인 문법과 함수들

## 기본 문법

### 1. 변수 선언

데이터를 저장하는 데 사용(var, let, const)

```js
var name = "Pack"; // 전역 또는 함수 스코프
let age = 24; // 블록 스코프 {}
const pi = 3.14; // 블록 스코프, 상수, 재할당 불가
```

### 2. 데이터 타입

```js
let num = 42;               // 숫자 (Number)

let str = "Hello, World!";  // 문자열 (String)

let isActive = true;        // 불리언 (Boolean)

let person = { name: "John", age: 30 };     // 객체 (Object)

let numbers = [1, 2, 3, 4, 5];              // 배열 (Array)

function greet() { console.log("Hello!"); } // 함수 (Function)
```

### 3. 연산자

**`산술 연산자`**: +, -, *, /, %

```js
// + (덧셈)
let sum = 5 + 3; // 8
let concat = "Hello, " + "World!"; // "Hello, World!"

// - (뺄셈)
let difference = 5 - 3; // 2

// * (곱셈)
let product = 5 * 3; // 15

// / (나눗셈)
let quotient = 6 / 3; // 2

// % (나머지)
let remainder = 5 % 2; // 1
```

**`대입 연산자`**: =, +=, -=, *=, /=

```js
// = (대입)
let x = 10; // x에 10을 대입

// += (덧셈 후 대입)
let x = 10;
x += 5; // x는 15 (10 + 5)

// -= (뺄셈 후 대입)
let x = 10;
x -= 5; // x는 5 (10 - 5)

// *= (곱셈 후 대입)
let x = 10;
x *= 5; // x는 50 (10 * 5)

// /= (나눗셈 후 대입)
let x = 10;
x /= 2; // x는 5 (10 / 2)
```

**`비교 연산자`**: ==, ===, !=, !==, >, <, >=, <=

```js
// == (동등): 값이 같은지 확인. 형 변환을 허용
console.log(5 == '5'); // true

// === (엄격 동등): 값과 타입이 모두 같은지 확인. 형 변환 X
console.log(5 === '5'); // false

// != (부등): 값이 다르면 true. 형 변환 허용
console.log(5 != '5'); // false

// !== (엄격 부등): 값이나 타입이 다르면 true. 형 변환 X
console.log(5 !== '5'); // true

// > (크다): 왼쪽 값이 오른쪽 보다 큰지 비교
console.log(5 > 3); // true

// < (작다): 왼쪽 값이 오른쪽 보다 작은지 비교
console.log(5 < 3); // false

// >= (크거나 같다): 왼쪽 값이 오른쪽 보다 크거나 같은지 비교
console.log(5 >= 5); // true

// <= (작거나 같다): 왼쪽 값이 오른쪽 값보다 작거나 같은지 비교
console.log(5 <= 3); // false
```

**`논리 연산자`**: &&, &#124;&#124;, !

```js
// && (논리 AND): 두 조건이 모두 true일 때 ture
console.log(true && false); // false

// || (논리 OR): 두 조건 중 하나라도 true일 때 true
console.log(true || false); // true

// ! (논리 NOT): 조건의 true/false를 반전시킴
console.log(!true); // false
```

### 4. 조건문

코드의 흐름 제어

```js
let age = 20;

if (age >= 18) {
    console.log("Adult");
} else {
    console.log("Minor");
}
```

### 5. 반복문

특정 코드를 여러 번 실행

**`for 루프`**

```js
for (let i = 0; i < 5; i++) {
    console.log(i);
}
```

**`while 루프`**

```js
let i = 0;
while (i < 5) {
    console.log(i);
    i++;
}
```

## 함수

재사용 가능한 코드 블록

**`함수 선언`**

```js
function greet(name) {
    return `Hello, ${name}!`;
}
```

**`함수 표현식`**

```js
const greet = function(name) {
    return `Hello, ${name}!`;
};
```

**`화살표 함수`**

```js
const greet = (name) => `Hello, ${name}!`;
```

## DOM 조작

JavsScript를 사용해 웹 페이지의 요소를 조작

**`요소 선택`**

```js
const element = document.getElementById("myElement");
const elements = document.getElementsByClassName("myClass");
const element = document.querySelector(".myClass");
const elements = document.querySelectorAll(".myClass");
```

**`내용 변경`**

```js
element.textContent = "New content";
element.innerHTML = "<p>New content</p>";
```

**`속성 변경`**

```js
element.setAttribute("class", "newClass");
element.id = "newId";
```

**`스타일 변경`**

```js
element.style.color = "red";
element.style.backgroundColor = "blue";
```

**`이벤트 리스너 추가`**

```js
element.addEventListener("click", function() {
    alert("Element clicked!");
});
```

## 사용 예

```html
<!DOCTYPE html>
<html>
<head>
    <title>JavaScript Example</title>
</head>
<body>
    <h1 id="header">Hello, World!</h1>
    <button id="changeTextButton">Change Text</button>

    <script src="script.js"></script>
</body>
</html>
```

> HTML 코드

```js
// 요소 선택
const header = document.getElementById("header");
const button = document.getElementById("changeTextButton");

// 이벤트 리스너 추가
button.addEventListener("click", function() {
    header.textContent = "Text has been changed!";
});
```

> JavaScript 코드

1. id가 changeTextButton인 버튼의 클릭을 감지

2. 이벤트 리스너를 통해 클릭했을 때 동작 구현

3. id가 header인 h1태그의 텍스트 내용 변경

## 내장 함수

**`alert(message)`**: 메시지를 경고 창으로 표시

**`console.log(message)`**: 메시지를 브라우저 콘솔에 로그

**`setTimeout(function, milliseconds)`**: 일정 시간이 지난 후 함수를 실행

**`setInterval(function, milliseconds)`**: 일정 시간 간격으로 함수를 반복 실행

```js
alert("Hello, World!");

console.log("Hello, World!");

setTimeout(function() {
    console.log("This will run after 2 seconds");
}, 2000);

setInterval(function() {
    console.log("This will run every 2 seconds");
}, 2000);
```

