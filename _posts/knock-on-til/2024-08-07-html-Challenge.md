---
title: "[2주차 TIL] KnockOn Bootcamp - HTML (Challenge)"
categories:
  - Web Architecture
tags:
  - Knockon Bootcamp 2nd
  - HTML
last_modified_at: 2024-08-07T04:54:00-05:00
published: true
---

|

# 사과와 바나나를 소개하는 패이지를 제작하여 봅시다.

두 개의 페이지는 서로 a태그를 이용하여 서로 연결되어 있습니다.

제출 버튼을 눌렀을 때의 동작은 구현하지 않아도 좋습니다.

|

## 1. 복숭아

```html
<!DOCTYPE html>
<html lang="ko">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>복숭아ㅋ</title>
    <link rel="stylesheet" href="./main.css">
</head>

<body>
    <header>
        <h1>복숭아!</h1>
        <hr>
    </header>
    <main>
        <section>
            <h2>복숭아에 대하여</h2>
            <p>복숭아는 달콤하고 즙이 많은 과일로 부드러운 털이 있는 껍질이 특징입니다. 근-본 말랑숭아 체고</p>
            <img src="./images/peach.png" alt="복숭아 사진" style="width:200px;">
        </section>
        <section>
            <h2>복숭아의 건강 이점</h2>
            <ul>
                <li>소화 개선</li>
                <li>피부 건강</li>
                <li>눈 건강</li>
            </ul>
        </section>
        <section>
            <h2>맛있는 복숭아 레시피</h2>
            <label>이메일:</label>
            <br>
            <input type="text" placeholder="이메일" />
            <br>
            <label>당신의 좋아하는 복숭아 레시피를 공유해주세요:</label>
            <br>
            <textarea rows="4" cols="50"></textarea>
            <br>
            <button>제출</button>
        </section>
        <section>
            <p><a href="strawberry">딸기</a>에 대하여</p>
        </section>
    </main>

</body>

</html>
```

![복숭아 사진](./assets/images/peach.png)

|

## 2. 딸기

```html
<!DOCTYPE html>
<html lang="ko">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>딸기ㄷㄷ</title>
    <link rel="stylesheet" href="./main.css">
</head>

<body>
    <header>
        <h1>딸기!</h1>
        <hr>
    </header>
    <main>
        <section>
            <h2>딸기에 대하여</h2>
            <p>딸기는 작은 빨간 과일로 달콤하고 상큼한 맛이 특징입니다. 딸기조아</p>
            <img src="./images/strawberry.png" alt="딸기 사진" style="width:200px;">
        </section>
        <section>
            <h2>딸기의 건강 이점</h2>
            <ul>
                <li>항산화제 풍부</li>
                <li>심혈관 건강</li>
                <li>항염 효과</li>
            </ul>
        </section>
        <section>
            <h2>맛있는 딸기 레시피</h2>
            <label>이메일:</label>
            <br>
            <input type="text" placeholder="이메일" />
            <br>
            <label>당신의 좋아하는 딸기 레시피를 공유해주세요:</label>
            <br>
            <textarea rows="4" cols="50"></textarea>
            <br>
            <button>제출</button>
        </section>
        <section>
            <p><a href="peach">복숭아</a>에 대하여</p>
        </section>
    </main>
    
</body>

</html>
```

![딸기 사진](./assets/images/strawberry.png)

|

---

|