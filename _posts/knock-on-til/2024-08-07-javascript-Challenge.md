---
title: "KnockOn Bootcamp 2nd - 2주차 JavaScript 실습"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - JavaScript
last_modified_at: 2024-08-07T19:54:00+09:00
published: true
---
## var, let과 const의 차이점 이해하기

변수는 선언, 초기화, 할당 3단계를 거쳐 생성됨

**`호이스팅`**

변수와 함수의 선언이 해당 스코프의 **최상단으로 끌어올려지는** 동작

**코드 작성 순서와 상관없이** 변수와 함수 선언을 사용할 수 있음

**`TDZ(일시적인 사각지대, Temporal Dead Zone)`**

선언만 되고 초기화가 되지 않은 변수가 머무르는 공간. let, const에서 발생

(변수가 선언되었지만 초기화가 되지 않은 상태)

이 공간에 있는 변수를 참조하게 되면 "ReferenceError" 발생

프로그래밍 오류를 줄이기 위한 목적

## var

선언 전, 선언 단계와 초기화 단계를 동시에 진행

이로 인해 변수 선언 전 호출을 해도 undefined로 호출되는 호이스팅 발생

**`Scope`**: 함수 스코프

**`Hoisting`**: 선언과 초기화가 호이스팅됨 (호이스팅 시 'undefined'로 초기화됨)

**`Redeclaration`**: 같은 스코프 내에서 재선언 가능

**`Initialization`**: 선언과 초기화를 **나중에 할 수 있음**,

**`Reassignment`**: 재할당 가능

```js
function varExample() { // 함수
    var x = 10; // 함수 스코프
    var y; // 초기화 X

    console.log(y); // undefined

    if (true) {
        var x = 20; // 같은 함수 내 재선언. 덮어쓰기
        y = 1; // 재할당

        console.log(x); // 20
        console.log(y); // 1
    }

    y = 2;

    console.log(x); // 20
    console.log(y); // 2
}
```

### var 호이스팅

```js
console.log(a); // undefined
var a = 10;
console.log(a); // 10
```

> 실행 코드

```js
var a; // 호이스팅으로 변수 선언이 최상단으로 끌어올려짐
console.log(a); // undefined
a = 10;
console.log(a); // 10
```

> 해석되는 코드

호이스팅으로 undefined으로 초기화 되었고, 이후 값이 할당됨

## let

선언 단계와 초기화 단계가 분리되어 진행

초기화를 하지 않으면 undefined로 초기화가 이루어지는 var와 달리, let은 메모리 할당이 되지 않음

선언만 하고 값에 접근하면 변수에 등록이 되었기 때문에 호이스팅은 되지만, TDZ 구간에 의해 메모리 할당이 되지 않아 **참조 에러(RefferenceError)** 발생

**`Scope`**: 블록 스코프

**`Hoisting`**: 선언만 호이스팅됨, 초기화는 안 됨

**`Redeclaration`**: 같은 스코프 내에서 재선언 불가능

**`Initialization`**: 선언 시 **초기화 필요 없음**(TDZ 발생)

**`Reassignment`**: 재할당 가능

### let 호이스팅

```js
console.log(b); // ReferenceError: Cannot access 'b' before initialization
let b = 20;
console.log(b); // 20
```

> 실행 코드

```js
let b; // 호이스팅으로 선언은 되었지만 초기화는 안 됨
console.log(b); // ReferenceError
b = 20;
console.log(b); // 20
```

> 해석되는 코드

선언된 변수는 호이스팅 되었지만 초기화 되기 전에 접근 시 TDZ 구간에 의해 "ReferenceError" 발생

## const

let과 마찬가지로 선언 단계와 초기화 단계가 분리되어 진행됨

const는 선언과 동시에 반드시 초기화를 해야된다는 차이점이 있음

선언만 할 경우 **문법 오류(SyntaxError)** 발생

**`Scope`**: 블록 스코프

**`Hoisting`**: 선언만 호이스팅됨, 초기화는 안 됨

**`Redeclaration`**: 같은 스코프 내에서 재선언 불가능

**`Initialization`**: 선언 시 **초기화 필수**

**`Reassignment`**: 재할당 불가능

### const 호이스팅

```js
console.log(c); // ReferenceError: Cannot access 'c' before initialization
const c = 30;
console.log(c); // 30
```

> 실행 코드

```js
const c; // SyntaxError: Missing initializer in const declaration
console.log(c); // ReferenceError
c = 30; // TypeError: Assignment to constant variable.
console.log(c); // 30
```

> 해석되는 코드

1. 실행 코드를 그대로 실행 시, 선언된 변수는 호이스팅 되지만 초기화 되기 전에 접근 시 TDZ 구간에 의해 "ReferenceError" 발생

2. 'const c;'를 먼저 작성 시, 'SyntaxError' 발생

3. 선언과 동시에 초기화를 했더라도 재할당이 불가능해 'c = 30;' 부분에서 'TypeError' 발생

## 정리

| 특징 | var | let | const |
|:----|:----|:----|:----|
| Scope | 함수 스코프 | 블록 스코프 | 블록 스코프 |
| Hoisting | 선언 O, 초기화 O | 선언 O, 초기화 X | 선언 O, 초기화 X |
| Redeclaration | 같은 스코프 내 재선언 O | 같은 스코프 내 재선언 X | 같은 스코프 내 재선언 X |
| Initialization | 선언과 초기화 나중에 O | 선언 시 초기화 필요 X | 선언 시 초기화 필수 |
| Reassignment | 재할당 O | 재할당 O | 재할당 X |

## Arrow Function 이해하기

**`화살표 함수(Arrow Function)`**

ES6에서 도입된 JavaScript의 함수 표현 방식 중 하나

간결한 문법과 this 바인딩의 차이점으로 자주 사용됨

## 문법

기본 형태

```js
(param1, param2, ..., paramN) => { // 매개변수가 하나인 경우 괄호 생략 가능
  // 함수 본문
  return expression; // 함수 본문이 단일 표현식인 경우, 중괄호와 'return' 생략 가능
};
```

**`매개변수가 없는 경우`**: 빈 괄호 사용

**`함수 본문이 단일 표현식인 경우`**: 중괄호와 'return' 키워드 생략

**`객체 리터럴을 반환하는 경우`**: 객체를 소괄호로 감쌈(감싸지 않으면 함수 본문의 블록으로 해석함)

```js
// 매개변수가 없는 경우
const sayHello = () => console.log("Hello!"); // 빈 괄호 사용

// 매개변수가 하나인 경우
const square = x => x * x; // 괄호 없이 매개변수만 씀

// 함수 본문이 단일 표현식인 경우, 중괄호와 return 생략
const multiply = (a, b) => a * b; // 암묵적 반환

// 함수 본문이 여러 줄인 경우
const add = (a, b) => { // 중괄호 사용 및 명시적 'return' 사용
  const sum = a + b;
  console.log(sum);
  return sum;
};

// 객체 리터럴을 반환하는 경우
const getPerson = () => ({ name: "John", age: 30 }); // 소괄호로 객체 감싸기
```

### 다른 함수 표현과 비교

```js
// 화살표 함수
const add = (a, b) => a + b;

console.log(add(2, 3)); // 5

// 함수 선언
function add(a, b) {
  return a + b;
}

// 함수 표현식 - 익명 함수
const add = function(a, b) {
  return a + b;
};

// 함수 표현식 - 이름 있는 함수
const add = function addFunction(a, b) {
  return a + b;
};

console.log(add(2, 3)); // 5

// 함수 표현식 - 즉시 실행
const result = (function(a, b) {
  return a + b;
})(2, 3);

console.log(result); // 5

// 메서드 정의
const obj = {
  add(a, b) {
    return a + b;
  }
};
console.log(obj.add(2, 3)); // 5
```

## this 바인딩

함수가 호출될 때 'this' 키워드가, 참조하는 객체를 결정하는 매커니즘

'this'는 함수가 어떻게 호출되었는지에 따라 값이 달라짐

일반 함수와 화살표 함수의 'this'바인딩 방식은 다름

### 화살표 함수에서의 this 바인딩

화살표 함수는 자신의 this 바인딩을 가지지 않음

**`렉시컬(lexical) 스코프`**: 외부의 'this'를 그대로 가져옴

화살표 함수가 정의된 위치에서 'this'의 값을 상속받아 사용

외부 스코프의 'this'를 그대로 사용하기 때문에 this 바인딩이 호출 방법에 따라 달라지지 않음

```js
// 화살표 함수의 this 바인딩
const person = {
  name: 'Pack',
  greet: function() {
    console.log('Hello, ' + this.name); // 'this'는 person 객체를 참조
  },
  delayedGreet: function() {
    setTimeout(() => { // 화살표 함수
      console.log('Delayed Hello, ' + this.name); // 'this'는 setTimeout이 아닌, 주변 스코프인 delayedGreet의 'this'를 참조
    }, 1000);
  }
};

person.greet(); // Hello, Pack
person.delayedGreet(); // Delayed Hello, Pack

// 기존 함수에서의 this 바인딩
const person = {
  name: 'Pack',
  greet: function() {
    console.log('Hello, ' + this.name); // 'this'는 person 객체를 참조
  },
  delayedGreet: function() {
    setTimeout(function() { // 기존 방식의 함수
      console.log('Delayed Hello, ' + this.name); // 'this'는 setTimeout의 'this'를 참조
    }, 1000);
  }
};

person.greet(); // Hello, Pack
person.delayedGreet(); // Delayed Hello, undefined
```

### 일반 함수에서의 this 바인딩

**`메서드로서의 호출`**: 객체의 메서드로서, 'this'는 해당 객체를 참조

**`단독 호출`**: 객체의 메서드가 아닌 경우(함수가 단독으로 호출), 'this'는 'undefined'가 됨

**`생성자로서 호출`**: 'new' 키워드를 사용해 호출된 경우, 'this'는 새로 생성된 객체를 참조

**`'call', 'apply', 'bind' 메서드`**: 'call', 'apply', 'bind' 메서드를 사용해 호출한 경우, 'this'를 명시적으로 설정 가능

```js
// 메서드로서의 호출
const obj = {
    name: 'Pack',
    greet: function () { // greet 함수는 obj 객체의 메서드임
        console.log(this.name); // this는 obj를 가리킴
    }
};
obj.greet(); // 'Pack'

// 단독 호출
function greet() {
    console.log(this.name); // undefined
    console.log(age); // 24
}

const name = 'pack';
const age = '24';
greet(); // undefined, 24

// 생성자로서 호출
function Person(name) {
    this.name = name; // 'this.name'에 'Pack'이 할당됨
}
const person = new Person('Pack');
console.log(person.name); // 'Pack'

// 'call', 'apply', 'bind' 메서드

// 'call': this를 명시적으로 설정, 추가적인 매개변수 전달
function greet(hello) {
    console.log(hello, this.name);
}
const obj = { name: 'Pack' };
greet.call(obj, 'hello'); // 'hello Pack'

// 'apply': 매개변수를 배열 형태로 전달
function greet(hello, p) {
    console.log(hello, this.name, p);
}
const obj = { name: 'Pack' };
greet.apply(obj, ['hello', '!']);

// 'bind': 함수 호출 시 'this'를 생성하는 새로운 함수 반환.
//      bind는 함수를 호출하지 않고 반환된 함수를 나중에 호출할 때 'this'를 설정함
function greet(greeting) {
    console.log(greeting, this.name);
}

const person = { name: 'Pack' };
const greetPerson = greet.bind(person);
greetPerson('Hello'); // Hello, Pack
```

## 룰렛 게임 완성하기

## 구현

**`startRoulette()`**

1. values 범위 안에서 숫자 1씩 증가

2. 실시간으로 바뀌는 숫자를 rouletteDisplay에 표시

## 필요 함수

**`setInterval()`**: 일정 시간 간격마다 주기적으로 지정된 함수 실행

```js
const intervalId = setInterval(callback, delay, [arg1, arg2, ...]);
```

`callback`: 주기적으로 실행할 함수

`delay`: 함수 호출 시간 간격 설정. 밀리초(ms) 단위

`[arg1, arg2, ...]`: (선택) 콜백 함수에 전달할 인수

```js
function sayHello() {
    console.log('Hello');
}

// 1초(1000ms)마다 sayHello 함수 실행
const intervalId = setInterval(sayHello, 1000);
```

**`clearInterval()`**: **'setInterval()'**에 의해 설정된 작업 중지

```js
clearInterval(intervalId);
```

`intervalId`: **setInterval()**이 반환한 식별자. 이 식별자를 사용해 해당 인터벌을 중지

**사용 예**

```js
function sayHello() {
    console.log('Hello');
}

// 1초(1000ms)마다 sayHello 함수를 실행
const intervalId = setInterval(sayHello, 1000);

// 5초 후에 인터벌을 중지
setTimeout(() => {
    clearInterval(intervalId);
    console.log('인터벌 중지');
}, 5000);
```

**`필요 DOM 조작`**

내용 변경

```js
element.textContent = "New content";
element.innerHTML = "<p>New content</p>";
```

## 룰렛 만들기 시작

```js
<!DOCTYPE html>
<html>
  <head>
    <title>Roulette Game</title>
    <script></script>
  </head>
  <body>
    <div id="roulette">1</div>
    <button id="stopButton">정지</button>

    <script>
      const values = [1, 2, 3, 4, 5, 6];

      const rouletteDisplay = document.getElementById("roulette");

      let intervalId = null;

      let currentIndex = 0;

      function startRoulette() {
        intervalId = //interval 설정하기
      }

      document.getElementById("stopButton").addEventListener("click", () => {
        clearInterval(intervalId);

        alert("선택된 숫자: " + values[currentIndex]);
      });

      startRoulette();
    </script>
  </body>
</html>
```

## 과정 1. startRoulette() 구현

### 1. setInterval()

```js
function startRoulette() {
    intervalId = setInterval(() => { // callback: 화살표 함수 추가
        // currentIndex 1씩 증가
        // rouletteDisplay에 숫자 표시
    }, 1000); // delay: 시간 추가
}

```

> callback, delay 매개변수 추가

```js
function startRoulette() {
    intervalId = setInterval(() => {
        // currentIndex 1씩 증가
        currentIndex = currentIndex + 1;

        // rouletteDisplay에 숫자 표시
    }, 1000);
}
```

> currentIndex가 1초에 1씩 증가

![currentIndex 구현](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-javascript-challenge-01.png)

- 1부터 6까지는 잘 나오는데 끝도 없이 커져, 그 다음 숫자부터는 undefined으로 나온다

- 7이 되면 다시 1로 돌아가게 만들어야 한다

```js
function startRoulette() {
    intervalId = setInterval(() => {
        // currentIndex 1씩 증가
        currentIndex = (currentIndex) + 1 % 6;

        // rouletteDisplay에 숫자 표시
    }, 1000);
}
```

> 나머지 연산을 사용해 배열의 길이(6)로 나누어 7이 되면 1로 돌아가게 함

![currentIndex 구현2](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-javascript-challenge-02.png)

- 1, 2, 3, 4, 5, 0, 다시 1, 2,... 순서로 잘 나옴

- 인덱스는 4지만 선택된 숫자가 5인 이유는 배열의 인덱스가 0부터 시작하기 때문이다. 0번째 배열 요소는 1, ..., 4번째 배열의 요소는 5가 됨

```js
function startRoulette() {
    intervalId = setInterval(() => {
        currentIndex = (currentIndex + 1) % 6;

        // rouletteDisplay에 숫자 표시
        rouletteDisplay.textContent = currentIndex;
    }, 1000);
}
```

> 'element.textContent'를 사용해 DOM 조작

> rouletteDisplay의 textContent를 currentIndex로 설정

![rouletteDisplay 숫자 표시 구현](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-javascript-challenge-03.png)

- 웹에서 숫자도 잘 바뀐다. 근데 선택한 숫자랑 인덱스가 다르다

- 난 지금 배열의 인덱스를 출력하고 있기 때문이다. 인덱스 번호에 해당하는 요소를 출력해야된다!

```js
function startRoulette() {
    intervalId = setInterval(() => {
        currentIndex = (currentIndex + 1) % 6;

        // rouletteDisplay에 숫자 표시
        rouletteDisplay.textContent = values[currentIndex];
    }, 1000);
}
```

> 배열의 요소가 출력되게 'values[currentIndex]'로 바꿈

![rouletteDisplay 숫자 표시 구현2](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-javascript-challenge-04.png)

- 진짜 잘됨!!

```js
function startRoulette() {
    intervalId = setInterval(() => {
        currentIndex = (currentIndex + 1) % values.lengh;
        rouletteDisplay.textContent = values[currentIndex];
    }, 50);
}
```

> 나누는 숫자 부분을 배열의 크기로 일반화하기 위해 values.lengh로 수정!

> delay도 빠르게 50으로 변경

## 최종 코드

```html
<!DOCTYPE html>
<html>

<head>
    <title>Roulette Game</title>
    <script></script>
</head>

<body>
    <div id="roulette">1</div>
    <button id="stopButton">멈춰!</button>

    <script>
        const values = [1, 2, 3, 4, 5, 6];

        const rouletteDisplay = document.getElementById("roulette");

        let intervalId = null;

        let currentIndex = 0;

        function startRoulette() {
            intervalId = setInterval(() => {
                currentIndex = (currentIndex + 1) % 6;
                rouletteDisplay.textContent = values[currentIndex];

                fetch('/updateIndex', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ currentIndex })
                });
            }, 50);
        }

        document.getElementById("stopButton").addEventListener("click", () => {
            clearInterval(intervalId);

            alert("선택된 숫자: " + values[currentIndex]);
        });

        startRoulette();
    </script>
</body>

</html>
```

> 완


