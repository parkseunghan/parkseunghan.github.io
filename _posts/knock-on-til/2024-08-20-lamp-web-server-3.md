---
title: "KnockOn Bootcamp 2nd - 3주차 게시판 만들기 3 - 파일 업로드 & Create/Update"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - File Upload
  - Board
last_modified_at: 2024-08-20T22:54:00+09:00
published: true
---
## 파일 업로드

## config

```php
// config.php

define('UPLOAD_DIR', '/your_project_root_path/uploads/'); // 업로드 경로
define('MAX_FILE_SIZE', 5 * 1024 * 1024); // 업로드 최대 허용 크기
define('ALLOWED_EXTS', ['jpg', 'jpeg', 'png', 'gif', 'pdf']); // 업로드 허용 파일 형식
```

## functions

**`handleFileUpload()`**: 파일 업로드 함수

```php
// functions.php

function handleFileUpload($existing_file_path) {
    $upload_dir = UPLOAD_DIR;
    $file_path = $existing_file_path; // 기본값: 기존 파일 경로, 새로 업로드되면 변경
    $error_message = '';

    // (1)
    if (isset($_FILES['file']) && $_FILES['file']['error'] !== UPLOAD_ERR_NO_FILE) {

        // (2)
        if ($_FILES['file']['error'] === UPLOAD_ERR_OK) {
            $allowed_exts = ALLOWED_EXTS;

            // (3)
            $file_ext = strtolower(pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION));
            $max_file_size = MAX_FILE_SIZE; // 5MB

            // (4)
            if ($_FILES['file']['size'] > $max_file_size) {
                $error_message = "파일 용량 초과 (최대 5MB)";
            } elseif (!in_array($file_ext, $allowed_exts)) {
                $error_message = "허용되지 않는 파일 형식입니다.";
            } else {

                // (5)
                $file_name = time() . '_' . uniqid() . '_' . basename($_FILES['file']['name']);
                $new_file_path = $upload_dir . $file_name;

                // (6)
                if (!is_dir($upload_dir)) {
                    mkdir($upload_dir, 0777, true);
                }

                // (7)
                if (move_uploaded_file($_FILES['file']['tmp_name'], $new_file_path)) {
                    // (8) 기존 파일이 있으면 삭제
                    if ($existing_file_path && file_exists($existing_file_path)) {
                        unlink($existing_file_path);
                    }
                    $file_path = $new_file_path;
                } else {
                    $error_message = "파일 업로드 실패!";
                }
            }
        } else {
            $error_message = "파일 업로드 중 오류가 발생했습니다.";
        }
    }

    return [
        // (9)
        'file_path' => $file_path,
        'error_message' => $error_message,
    ];
}
```

> 기존 파일의 경로를 $existing_file_path 파라미터를 통해 받아와 $file_path에 저장

> (1) 파일이 업로드 되었는지($_FILES['file'] 설정) 확인, 업로드된 파일이 없는 경우 UPLOAD_ERR_NO_FILE이 아닌지 확인

> (2) 파일이 정상적으로 업로드되었는지 확인. UPLOAD_ERR_OK: 파일이 오류 없이 업로드된 상태

> (3) strtolower(): 파일의 확장자를 소문자로 변환 후 $file_ext에 저장

> pathinfo(): 파일 경로 정보 추출

> (4) 파일 용량 초과 또는 허용되지 않는 파일인 경우 오류 메시지 설정

> (5) time()과 uniqid()로 고유 파일명을 생성하여 파일명 충돌 방지

> (6) 디렉토리가 존재하지 않으면 0755 권한으로 생성. true 옵션으로 필요한 상위 디렉토리도 함께 생성

> (7) 업로드된 파일을, 임시 디렉토리에서 $new_file_path로 이동. 성공 시 파일 업로드 완료

> (8) 업로드된 기존 파일이 있다면, unlink()함수를 사용해 삭제

> (9) 파일이 업로드되지 않았거나, 파일이 없는 경우 업로드 처리를 하지 않고 기존 파일을 유지

## 게시물 생성: create_post.php

## functions

**`handleFileUpload()`**: 파일 업로드

**`createPost()`**: 게시물 추가

```php
// functions.php

function createPost($title, $content, $file_path) {
    global $mysqli;
    $stmt = $mysqli->prepare("INSERT INTO posts (title, content, file_path, user_id) VALUES (?, ?, ?, ?)");
    $stmt->bind_param("sssi", $title, $content, $file_path, $_SESSION['id']);
    $result = $stmt->execute();
    $stmt->close();
    return $result;
}
```

> 게시물 제목, 내용, 업로드된 파일 경로를 파라미터로 받음

> global 키워드를 사용해 전역 변수 $mysqli 사용

> title, content, file_path, user_id열에 데이터 삽입

> bind_param()에서 s와 i는 s(string), i(integer)를 의미

## create_post

php 부분

```php
// create_post.php

require_once 'init.php';

$error_message = '';
$file_error_message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') { // (1) POST 요청으로 폼 데이터를 제출했는지 확인

    // (2)
    if (!empty($_POST['title']) && !empty($_POST['content'])) {
        $title = trim($_POST['title']);
        $content = trim($_POST['content']);

        // 파일 업로드 처리
        $file_result = handleFileUpload(null); // 새 게시물이라 기존 파일 없음
        if (is_array($file_result)) {
            $file_path = $file_result['file_path'];
            $file_error_message = $file_result['error_message'];
        }

        if (empty($file_error_message)) {
            // 게시물 생성
            if (createPost($title, $content, $file_path)) {
                echo "<script>alert('게시물이 생성되었습니다.'); window.location.href='index.php';</script>";
                exit();
            } else {
                $error_message = "게시물 생성 실패!";
            }
        }
    } else {
        $error_message = "제목과 내용을 입력해야 합니다.";
    }
}
```

> (1) POST 방식으로 데이터를 처리했는지 확인

> (2) title과 content가 비어있지 않은지 확인

> trim(): 입력 데이터 앞뒤 공백 제거

> (3) 파일 업로드 처리. 파라미터는 update_post.php에서 필요

> handleFileUpload(): 파일 업로드 처리 후, 성공시 $file_path에 file_path 경로 저장 또는 실패시  $file_error_message에 error_message 저장

> $file_error_message가 비어있다면(성공), createPost함수로 새 게시물 데이터를 데이터베이스에 삽입 후 성공 메시지 알림 후 index.php로 리다이렉트

html 부분

```php
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>게시물 작성</title>
</head>
<body>
    <a href="index.php">메인으로</a>
    <h1>게시물 작성</h1>
    <hr>
    <form method="POST" action="" enctype="multipart/form-data">
        <label for="title"><strong>제목:</strong></label>
        <input type="text" id="title" name="title" required>
        <br>
        <label for="content">내용:</label>
        <textarea id="content" name="content" required></textarea>
        <br>
        <label for="file">파일 업로드(최대 5MB):</label>
        <input type="file" id="file" name="file">
        <br>
        <?php if ($error_message): ?>
            <p style="color: red;"><?php echo htmlspecialchars($error_message); ?></p>
        <?php endif; ?>
        <?php if ($file_error_message): ?>
            <p style="color: red;"><?php echo htmlspecialchars($file_error_message); ?></p>
        <?php endif; ?>
        <button type="submit">작성</button>
    </form>
</body>
</html>
```

## 게시물 수정: update_post.php

## functions

**`handleFileUpload()`**: 파일 업로드

**`fetchPost()`**: 게시물 데이터 가져오기

**`updatePost()`**: 게시물 수정

```php
// functions

function updatePost($id, $title, $content, $file_path) {
    global $mysqli;
    $stmt = $mysqli->prepare("UPDATE posts SET title = ?, content = ?, file_path = ? WHERE id = ?");
    $stmt->bind_param("sssi", $title, $content, $file_path, $id);
    $result = $stmt->execute();
    $stmt->close();
    return $result;
}
```

> 게시물 id, 제목, 내용, 파일 경로를 파라미터로 받음

> bind_param(): ? 자리에 실제 값을 바인딩

```php
// functions

function fetchPost($id) {
    global $mysqli;
    $stmt = $mysqli->prepare("SELECT title, content, file_path, user_id FROM posts WHERE id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result()->fetch_assoc();
    $stmt->close();
    return $result;
}
```

> posts 테이블에서 제목, 내용, 파일 경로, 작성자 id를 가져옴

> get_result(): 쿼리 실행 결과를 가져옴

> fetch_assoc(): 테이블의 열을 배열의 키, 값을 배열의 값으로 가져와 &result에 저장

> &result: 현재 게시물 데이터를 포함하는 배열이 됨

## update_post

php 부분

```php
require_once 'init.php';

// (1) 게시물 ID 검증
$id = isset($_GET['id']) && !is_array($_GET['id']) ? intval($_GET['id']) : null;
if ($id === null) {
    echo "잘못된 요청입니다.";
    exit();
}

// (2) 게시물 데이터 가져오기
$post = fetchPost($id);
if (!$post) {
    echo "게시물이 존재하지 않습니다.";
    exit();
}

// (3) 로그인한 사용자가 게시물의 작성자인지 확인
if ($_SESSION['id'] !== $post['user_id']) {
    echo "게시물 수정 권한이 없습니다.";
    exit();
}

$file_path = $post['file_path']; // 기존의 파일 경로 초기화
$error_message = '';
$file_error_message = '';

// (4)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!empty($_POST['title']) && !empty($_POST['content'])) {
        $title = trim($_POST['title']);
        $content = trim($_POST['content']);

        // (5) 파일 업로드 처리
        $file_result = handleFileUpload($file_path);
        if (is_array($file_result)) {
            $file_path = $file_result['file_path'];
            $file_error_message = $file_result['error_message'];
        }

        if (empty($file_error_message)) {
            // (6) 게시물 업데이트
            if (updatePost($id, $title, $content, $file_path)) {
                echo "<script>alert('게시물이 수정되었습니다.'); window.location.href='index.php';</script>";
                exit();
            } else {
                $error_message = "게시물 수정 실패!";
            }
        }
    } else {
        $error_message = "제목과 내용을 입력해야 합니다.";
    }
}

// (7) 게시물 데이터 재조회
$post = fetchPost($id);
```

> (1) 삼항연산자 사용. 게시물 id가 있는지 확인 후 id를 intval()을 사용하여 정수로 변환

> id가 유효하지 않다면(NULL) 에러 메시지 출력 후 스크립트 종료

> (2) fetchPost($id): id에 해당하는 게시물 데이터를 DB에서 가져오기

> (3) 현재 로그인한 사용자의 id와 게시물 작성자의 id가 일치하는지 확인

> (4) POST 요청으로 호출되었는지 확인 후 제목과 내용이 비어있지 않은지 확인

> (5) handleFileUpload($file_path): 파일 업로드 처리. 파라미터로 기존 파일의 경로를 넘겨줌

> (6) 파일 업로드에 문제가 없으면 updatePost()함수로 게시물 수정

> (7) 수정된 최신 게시물 데이터를 다시 가져옴

html부분

```php
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>게시물 수정</title>
</head>
<body>
    <a href="index.php">메인으로</a>
    <h1>게시물 수정</h1>
    <hr>
    <form method="POST" action="" enctype="multipart/form-data">
        <label for="title"><strong>제목:</strong></label>
        <input type="text" id="title" name="title" value="<?php echo htmlspecialchars($post['title']); ?>" required>
        <br>
        <label for="content">내용:</label>
        <textarea id="content" name="content" required><?php echo htmlspecialchars($post['content']); ?></textarea>
        <br>
        <label for="file">파일 업로드(최대 5MB):</label>
        <input type="file" id="file" name="file">
        <br>
        <?php if ($error_message): ?>
            <p style="color: red;"><?php echo htmlspecialchars($error_message); ?></p>
        <?php endif; ?>
        <?php if ($file_error_message): ?>
            <p style="color: red;"><?php echo htmlspecialchars($file_error_message); ?></p>
        <?php endif; ?>
        <button type="submit">수정</button>
    </form>
</body>
</html>
```

