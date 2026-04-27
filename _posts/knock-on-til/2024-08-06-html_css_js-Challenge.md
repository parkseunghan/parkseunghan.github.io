---
title: "KnockOn Bootcamp 2nd - 1주차 HTML, CSS, JavaScript 실습"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - HTML
  - CSS
  - JavaScript
last_modified_at: 2024-08-06T18:54:00+09:00
published: true
---
## 자신을 소개하는 페이지를 작성해 봅시다(형식 자유)

```html
<!DOCTYPE html>
<html lang="ko">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>자기소개</title>
    <style>
        body {
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .container {
            background-color: white;
            padding: 20px;
            border-radius: 100px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        h1 {
            color: #333;
        }

        p {
            color: #666;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>내이름은 박승한</h1>
        <p>나이는 24세</p>
        <p>열심히 공부중!</p>
        <p>이곳은 p태그</p>
    </div>
</body>

</html>
```

![자기소개](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-html-css-js-challenge-01.png)

> 코드 실행 결과

## 간단한 계산기 페이지를 만들어 봅시다

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>간단한 계산기</title>
    <style>
        body {
            background-color: powderblue;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .calculator {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        input[type="text"] {
            width: calc(100% - 22px);
            padding: 10px;
            margin: 10px 0;
            font-size: 18px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            font-size: 18px;
            background-color:  powderblue;
            color: black;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="calculator">
        <input type="text" id="expression" placeholder="계산 식 ㄱㄱ">
        <button onclick="calculateResult()">계산하기</button>
        <div id="result"></div>
    </div>
    <script>
        function calculateResult() {
            const expression = document.getElementById('expression').value;
            try {
                const result = eval(expression);
                document.getElementById('result').textContent = `결과: ${result}`;
            } catch (error) {
                document.getElementById('result').textContent = '제대로 쓰삼';
            }
        }
    </script>
</body>
</html>
```

![계산기](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-html-css-js-challenge-02.png)

> 코드 실행 결과 1

![계산기2](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-html-css-js-challenge-03.png)

> 코드 실행 결과 2

