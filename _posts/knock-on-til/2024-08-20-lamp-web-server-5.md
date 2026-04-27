---
title: "KnockOn Bootcamp 2nd - 3주차 게시판 만들기 5 - 사용자 인증 & 관리"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - Authentication
  - Board
last_modified_at: 2024-08-21T00:54:00+09:00
published: true
---
## 로그인 상태 관리: auth.php

## auth

auth.php파일 생성 후, 사용자 인증이 필요한 페이지에 모두 require

쿠키와 세션을 통해 로그인 상태 관리

```php
// auth.php

if (!isset($_SESSION['id']) && isset($_COOKIE['id']) && isset($_COOKIE['username'])) {
    $_SESSION['id'] = $_COOKIE['id'];
    $_SESSION['username'] = $_COOKIE['username'];
}

if (!isset($_SESSION['id'])) {
    header('Location: login.php');
    exit();
}
```

> 현재 세션에 id가 설정되어 있지 않고, 쿠키 id와 username이 설정되어 있으면 쿠키 로그인 정보를 통해 자동 로그인

> 세션 id도 설정되어 있지 않고, 쿠키도 없으면 login.php로 리다이렉션

## 회원가입: register.php

## register

php 부분

```php
// register.php

require_once 'init.php';

$errors = [];

// (1)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && !isset($_POST['check_username'])) {
    $username = trim($_POST['username']);
    $nickname = trim($_POST['nickname']);
    $password = $_POST['password'];
    $password_confirm = $_POST['password_confirm'];

    // 입력 값 검증
    if (empty($username) || empty($nickname) || empty($password) || empty($password_confirm)) {
        $errors[] = "모든 필드를 입력해주세요.";
    }

    // 아이디 유효성 검사 (영문과 숫자의 조합, 20자 이하, 공백 불허)
    if (!preg_match('/^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{1,20}$/', $username)) {
        $errors[] = "아이디는 영문자와 숫자를 혼합하여 20자 이내로 입력해야 하며, 공백을 포함할 수 없습니다.";
    }

    // 닉네임 유효성 검사 (공백 불허)
    if (!preg_match('/^\S+$/', $nickname)) {
        $errors[] = "닉네임은 공백을 포함할 수 없습니다.";
    }

    // 비밀번호 유효성 검사 (영문, 숫자, 특수문자 포함, 10자 이상, 공백 불허)
    if (!preg_match('/^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{10,}$/', $password)) {
        $errors[] = "비밀번호는 영문, 숫자, 특수문자를 포함하여 10자 이상이어야 하며, 공백을 포함할 수 없습니다.";
    }

    // 비밀번호 확인
    if ($password !== $password_confirm) {
        $errors[] = "비밀번호와 비밀번호 확인이 일치하지 않습니다.";
    }

    if (empty($errors)) {
        // DB에 username이 없는지 확인
        $stmt = $mysqli->prepare("SELECT id FROM users WHERE username = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $stmt->store_result();

        // username이 존재하면 에러 메시지 추가
        if ($stmt->num_rows > 0) {
            $errors[] = "이미 존재하는 아이디입니다.";
        } else {

            // username 사용 가능이면, 비밀번호를 해시
            $password_hashed = password_hash($password, PASSWORD_DEFAULT);
            $stmt = $mysqli->prepare("INSERT INTO users (username, nickname, password) VALUES (?, ?, ?)");
            $stmt->bind_param("sss", $username, $nickname, $password_hashed);

            if ($stmt->execute()) {
                echo "<script>alert('회원가입 성공!'); window.location.href = 'login.php';</script>";
                exit();
            } else {
                $errors[] = "회원가입 실패!";
            }
        }

        $stmt->close();
    }

    $mysqli->close();
    exit();
}

// (2)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['check_username'])) {
    $username = trim($_POST['check_username']);

    // username이 DB에 있는지 확인
    $stmt = $mysqli->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $stmt->store_result();

    if ($stmt->num_rows > 0) {
        // 이미 존재하면 true
        echo json_encode(['exists' => true]);
    } else {
        // 존재하지 않으면 false
        echo json_encode(['exists' => false]);
    }

    $stmt->close();
    $mysqli->close();
    exit();
}
```

> (1) 회원가입 폼 제출시 실행됨. check_username이 설정되어 있지 않으면 회원가입 수행(javascipt 아이디 중복 함수)

> (2) check_username이 설정되어 있으면 로직 실행

html 부분

```php
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>회원가입</title>
    <script>

        // 입력 필드에 input 이벤트가 발생할 때마다 유효성 검사 함수 실행
        document.addEventListener("DOMContentLoaded", function () {
            document.getElementById('username').addEventListener('input', checkUsername);
            document.getElementById('nickname').addEventListener('input', validateNickname);
            document.getElementById('password').addEventListener('input', validatePassword);
            document.getElementById('password_confirm').addEventListener('input', validatePasswordConfirm);
        });

        // 사용자가 id를 입력할 때마다 호출됨. 아이디 유효성 확인 후, 중복 확인 요청을 비동기적으로 보냄
        async function checkUsername() {
            const username = document.getElementById('username').value;
            const usernameMessage = document.getElementById('username_message');

            if (username.length < 1) {
                usernameMessage.textContent = "";
                return;
            }

            // 아이디 유효성 검사
            if (!/^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{1,20}$/.test(username)) {
                usernameMessage.textContent = "아이디는 영문자와 숫자를 혼합하여 20자 이내로 입력해야 하며, 공백을 포함할 수 없습니다.";
                usernameMessage.style.color = "red";
            } else {
                try {
                    const response = await fetch('register.php', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `check_username=${encodeURIComponent(username)}`,
                    });
                    const data = await response.json();

                    if (data.exists) {
                        usernameMessage.textContent = "이미 존재하는 아이디입니다.";
                        usernameMessage.style.color = "red";
                    } else {
                        usernameMessage.textContent = "사용 가능한 아이디입니다.";
                        usernameMessage.style.color = "green";
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
        }

        // 닉네임에 공백이 포함되었는지 확인
        function validateNickname() {
            const nickname = document.getElementById('nickname').value;
            const nicknameMessage = document.getElementById('nickname_message');

            if (/^\S+$/.test(nickname)) {
                nicknameMessage.textContent = "올바른 형식입니다.";
                nicknameMessage.style.color = "green";
            } else {
                nicknameMessage.textContent = "닉네임은 공백을 포함할 수 없습니다.";
                nicknameMessage.style.color = "red";
            }
        }

        // 비밀번호가 영문, 숫자, 특수문자 포함 10자 이상인지 확인
        function validatePassword() {
            const password = document.getElementById('password').value;
            const passwordMessage = document.getElementById('password_message');
            const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{10,}$/;

            if (passwordRegex.test(password)) {
                passwordMessage.textContent = "올바른 형식입니다.";
                passwordMessage.style.color = "green";
            } else {
                passwordMessage.textContent = "비밀번호는 영문, 숫자, 특수문자를 포함하여 10자 이상이어야 하며, 공백을 포함할 수 없습니다.";
                passwordMessage.style.color = "red";
            }
        }

        // 비밀번호가 일치하는지 확인
        function validatePasswordConfirm() {
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('password_confirm').value;
            const passwordConfirmMessage = document.getElementById('password_confirm_message');

            if (password === passwordConfirm) {
                passwordConfirmMessage.textContent = "비밀번호가 일치합니다.";
                passwordConfirmMessage.style.color = "green";
            } else {
                passwordConfirmMessage.textContent = "비밀번호와 비밀번호 확인이 일치하지 않습니다.";
                passwordConfirmMessage.style.color = "red";
            }
        }

        // 폼 제출 전 모든 유효성 검사 실행. 빨간 오류가 없으면 폼 제출 허용. 그렇지 않으면 제출되지 않음
        function validateForm() {
            checkUsername();
            validateNickname();
            validatePassword();
            validatePasswordConfirm();

            return document.querySelectorAll("div[style='color: red;']").length === 0;
        }
    </script>
</head>
<body>
    <a href="index.php">메인으로</a>
    <hr>

    <h1>회원가입</h1>

    <?php if (!empty($errors)): ?>
        <ul>
            <?php foreach ($errors as $error): ?>
                <li><?php echo htmlspecialchars($error); ?></li>
            <?php endforeach; ?>
        </ul>
    <?php endif; ?>

    <form method="POST" action="" onsubmit="return validateForm()">
        <label for="username">아이디:</label>
        <input type="text" id="username" name="username" required>
        <div id="username_message"></div>
        <br>

        <label for="nickname">닉네임:</label>
        <input type="text" id="nickname" name="nickname" required>
        <div id="nickname_message"></div>
        <br>

        <label for="password">비밀번호:</label>
        <input type="password" id="password" name="password" required>
        <div id="password_message"></div>
        <br>

        <label for="password_confirm">비밀번호 확인:</label>
        <input type="password" id="password_confirm" name="password_confirm" required>
        <div id="password_confirm_message"></div>
        <br>

        <button type="submit">회원가입</button>
    </form>
</body>
</html>
```

> 서버와 비동기적으로 통신해 사용자 경험 개선

## 로그인: login.php

## login

```php
// login.php

require_once 'init.php';

// 이미 로그인 된 경우 접근할 수 없도록 index.php로 리다이렉트
if (isset($_SESSION['id'])) {
    header('Location: index.php');
    exit();
}

$errors = [];

// 로그인 폼 제출시 실행됨
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username']);
    $password = $_POST['password'];
    $remember_me = isset($_POST['remember_me']);  // "로그인 상태 유지" 체크박스 확인

    // 아이디, 비밀번호가 입력되었는지 확인
    if (empty($username) || empty($password)) {
        $errors[] = "아이디와 비밀번호를 입력해주세요.";
    } else {
        $stmt = $mysqli->prepare("SELECT id, password FROM users WHERE username = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $stmt->bind_result($id, $hashed_password);
        $stmt->fetch();
        $stmt->close();

        // password_verify() 함수를 통해 해시된 비밀번호와 비교
        if ($id && password_verify($password, $hashed_password)) {

            // 세션에 사용자 정보 저장
            session_regenerate_id(true); // 세션 ID 재생성
            $_SESSION['id'] = $id;
            $_SESSION['username'] = $username;

            // "로그인 상태 유지" 체크박스가 선택된 경우
            if ($remember_me) {
                // 쿠키 설정 (7일 동안 유효) - 보안 플래그 추가
                $cookie_time = time() + (7 * 24 * 60 * 60);  // 7일
                setcookie('id', $id, $cookie_time, "/", "", true, true); // Secure 및 HttpOnly 플래그 설정
                setcookie('username', $username, $cookie_time, "/", "", true, true);
                setcookie('remember_me', 'true', $cookie_time, "/", "", true, true);
            }

            echo "<script>alert('로그인 성공!'); window.location.href = 'index.php';</script>";
            exit();
        } else {
            $errors[] = "아이디 또는 비밀번호가 잘못되었습니다.";
        }
    }
    $mysqli->close();
}
```

html 부분

```php
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>로그인</title>
</head>
<body>
    <h1>로그인</h1>

    <?php if (!empty($errors)): ?>
        <ul>
            <?php foreach ($errors as $error): ?>
                <li><?php echo htmlspecialchars($error, ENT_QUOTES, 'UTF-8'); ?></li>
            <?php endforeach; ?>
        </ul>
    <?php endif; ?>

    <form method="POST" action="">
        <label for="username">아이디:</label>
        <input type="text" id="username" name="username" required>
        <br>
        <label for="password">비밀번호:</label>
        <input type="password" id="password" name="password" required>
        <br>
        <label for="remember_me">
            <input type="checkbox" id="remember_me" name="remember_me"> 로그인 상태 유지
        </label>
        <br>
        <button type="submit">로그인</button>
    </form>
    <a href="register.php">회원가입</a>
</body>
</html>
```

## 로그아웃: logout.php

## logout

```php
// logout.php

require_once 'init.php';

// POST 요청이 들어오면 실행
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 세션과 쿠키 삭제

    // 현재 세션 데이터를 빈 배열로 설정
    $_SESSION = [];

    // 세션에서 사용된 쿠키 삭제
    if (ini_get("session.use_cookies")) {
        $params = session_get_cookie_params();

        // 만료시간을 과거로 설정
        setcookie(session_name(), '', time() - 86400, $params["path"], $params["domain"], $params["secure"], $params["httponly"]);
    }

    // 세션 파기
    session_destroy();

    // 사용자 로그인 정보가 담긴 쿠키 삭제. 만료 시간을 과거로 설정
    setcookie('id', '', time() - 3600, '/');
    setcookie('username', '', time() - 3600, '/');
    setcookie('remember_me', '', time() - 3600, '/');

    // 로그아웃 후 login.php로 리다이렉션
    header('Location: login.php');
    exit();
}
```

> 쿠키는 유효 기간을 현재 시간보다 이전의 시간으로 설정하면 삭제됨 -1이든 -3600(1시간 전)이든 -86400(1일 전)이든 과거의 시간이면 다 됨. 확실하게 하기 위해 큰 수를 쓰는 것

html 부분

```php
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>로그아웃</title>
    <script>
        window.onload = function() {
            if (confirm("정말로 로그아웃하시겠습니까?")) {
                fetch('logout.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }).then(response => {
                    if (response.ok) {
                        window.location.href = 'login.php';
                    }
                }).catch(error => {
                    console.error('로그아웃 요청 실패:', error);
                });
            } else {
                window.location.href = 'index.php'; // 사용자가 취소했을 때
            }
        };
    </script>
</head>
<body>
    <!-- 페이지 내용은 필요 없음, 스크립트가 자동으로 동작합니다. -->
</body>
</html>
```

