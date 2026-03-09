---
title: "[3주차 TIL] KnockOn Bootcamp - 게시판 만들기(4) - 검색 & Read/Delete"
categories:
  - Web Architecture
tags:
  - Knockon Bootcamp 2nd
  - CRUD
  - board
last_modified_at: 2024-08-20T09:54:00-05:00
published: true
---

|

# 게시물 검색: search.php

search.php에서는 index.php는 같은 함수를 재사용해서 쓰기 때문에 따로 추가하지 않아도 됨.

**`getTotalPosts()`**: 총 게시물 수를 계산

**`getPosts()`**: 모든 게시물 가져오기

**`truncateContent()`**: 게시물 내용(content) 미리보기

|

```php
// functions.php

function getTotalPosts($mysqli, $query) {
    if ($query) { // 이 부분
        $stmt = $mysqli->prepare("SELECT COUNT(*) FROM posts WHERE title LIKE ? OR content LIKE ?");
        $search_term = '%' . $query . '%';
        $stmt->bind_param("ss", $search_term, $search_term);
    } else { 
        $stmt = $mysqli->prepare("SELECT COUNT(*) FROM posts");
    }
    $stmt->execute();
    $stmt->bind_result($total_posts);
    $stmt->fetch();
    $stmt->close();
    
    return $total_posts;
}
```

> $query: 검색어

> title 또는 content에 검색어가 포함된 게시물의 수 계산

> $search_term: '%검색어%' 의 형식으로 문장에서 부분 일치하는 부분을 찾아냄

|

```php
// functions.php

function getPosts($mysqli, $offset, $post_per_page, $query) {
    if ($query) {
        $stmt = $mysqli->prepare("SELECT id, title, content, created_at, updated_at FROM posts WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT ?, ?");
        $search_term = '%' . $query . '%';
        $stmt->bind_param("ssii", $search_term, $search_term, $offset, $post_per_page);
    } else { // 이 부분
    $stmt = $mysqli->prepare("SELECT posts.id, posts.title, posts.content, posts.created_at, posts.updated_at, posts.file_path, users.username 
                               FROM posts 
                               LEFT JOIN users ON posts.user_id = users.id 
                               ORDER BY posts.created_at DESC 
                               LIMIT ?, ?");
    }

    $stmt->bind_param("ii", $offset, $post_per_page);
    $stmt->execute();
    $result = $stmt->get_result();
    $stmt->close();
    return $result;
}
```

> title 또는 content에 검색어가 포함된 게시물을 가져옴

> ORDER BY created_at DESC: 최신 게시물이 먼저 나오도록 내림차순 정렬(default는 ASC로, 오름차순)

> LIMIT ?, ?: 페이지네이션 적용 offset만큼의 게시물을 건너뛰고, post_per_page개의 레코드를 가져옴

|

---

|

# 게시물 읽기: read_post.php

## functions

**`getPostById()`**: 게시물 가져오기

**`getAuthorUsername()`**: 작성자 이름 가져오기

|

```php
// functions

function getPostById($mysqli, $id) {
    // (1)
    $stmt = $mysqli->prepare("SELECT title, content, file_path, created_at, updated_at, user_id FROM posts WHERE id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $stmt->bind_result($title, $content, $file_path, $created_at, $updated_at, $post_user_id);

    if (!$stmt->fetch()) {
        return null; // 게시물이 존재하지 않으면 null 반환
    }

    $stmt->close();

    // (2)
    return [
        'title' => $title,
        'content' => $content,
        'file_path' => $file_path,
        'created_at' => $created_at,
        'updated_at' => $updated_at,
        'user_id' => $post_user_id
    ];
}
```

> (1) 게시물 id를 기반으로 조회

> (2) 게시물 정보를 배열로 반환

|

```php
// functions

function getAuthorUsername($mysqli, $post_user_id) {
    $stmt = $mysqli->prepare("SELECT username FROM users WHERE id = ?");
    $stmt->bind_param("i", $post_user_id);
    $stmt->execute();
    $stmt->bind_result($author_username);
    $stmt->fetch();
    $stmt->close();
    return $author_username;
}
```

> 파라미터로 posts의 user_id(작성자 id)를 넘겨받음

> users테이블에서 id를 통해 username을 가져와 반환

|

## read_post

```php
require_once 'init.php';

// URL에서 게시물 ID 가져오기
if (isset($_GET['id']) && !is_array($_GET['id'])) {
    $id = intval($_GET['id']);
} else {
    echo "잘못된 요청입니다.";
    exit();
}

// 게시물 가져오기
$post = getPostById($mysqli, $id);
if (!$post) {
    echo "게시물이 존재하지 않습니다.";
    exit();
}

// 작성자 이름 가져오기
$author_username = getAuthorUsername($mysqli, $post['user_id']);
$mysqli->close();

// (1)
$created_at = new DateTime($post['created_at']);
$updated_at = $post['updated_at'] ? new DateTime($post['updated_at']) : null;
$display_date = $created_at->format('Y. m. d H:i');

if ($updated_at) {
    $display_date .= ' (수정일: ' . $updated_at->format('Y. m. d H:i') . ')';
}

// (2)
$is_author = isset($_SESSION['id']) && $_SESSION['id'] === $post['user_id'];
```

> 게시물 id가 있는지 확인 후 id를 intval()을 사용하여 정수로 변환 

> id가 유효하지 않다면(NULL) 에러 메시지 출력 후 스크립트 종료

> getPostById()로 게시물 정보 가져옴

> getAuthorUsername()로 작성자 정보를 가져와 표시

> (1) 게시물 생성일 표시. 만약 수정일이 있다면 수정일도 표시

> (2) 게시물 수정 및 삭제 권한을 확인하는 데 사용. 현재 사용자와 작성자 id가 일치하면 &is_author를 true로 그렇지 않으면 false로 설정

|

html 부분

```php
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>게시물 읽기</title>
</head>
<body>
    <a href="index.php">메인으로</a>
    <hr>
    <h1><?php echo htmlspecialchars($post['title']); ?></h1>
    <p>게시일: <?php echo htmlspecialchars($display_date); ?></p>
    <p>작성자: <?php echo htmlspecialchars($author_username ?: '작성자 정보 없음'); ?></p>

    <?php if ($is_author): ?>
        <a href="update_post.php?id=<?php echo $id; ?>">수정</a>
        <a href="delete_post.php?id=<?php echo $id; ?>" onclick="return confirmDeletion();">삭제</a>
    <?php endif; ?>

    <hr>
    <br>
    <p><?php echo nl2br(htmlspecialchars($post['content'])); ?></p>
    <br>
  
    <?php if ($post['file_path']): ?>
    <hr>
    <p>첨부 파일: <a href="download.php?file=<?php echo urlencode($post['file_path']); ?>"><?php echo htmlspecialchars(basename($post['file_path'])); ?></a></p>
    <?php else: ?>
    <hr>
    <p>첨부 파일: 없음</p>
    <?php endif; ?>

    <hr>

    <script>
        function confirmDeletion() { 
            return confirm("정말로 삭제하시겠습니까?");
        }
    </script>
</body>
</html>
```

> &is_author를 통해 수정 및 삭제 버튼 활성(true)/비활성(false)

|

--

|

# 게시물 삭제: delete_post.php

## functions

**`deletePost()`**: 게시물 삭제

|

```php
// functions

function deletePost($mysqli, $postId, $userId) {
    // 게시물 데이터 가져오기
    $stmt = $mysqli->prepare("SELECT user_id, file_path FROM posts WHERE id = ?");
    $stmt->bind_param("i", $postId);
    $stmt->execute();
    $stmt->bind_result($post_user_id, $file_path);

    if (!$stmt->fetch()) {
        return ['success' => false, 'message' => '게시물이 존재하지 않습니다.'];
    }
    $stmt->close();

    // (1) 게시물 작성자 확인
    if ($userId !== $post_user_id) {
        return ['success' => false, 'message' => '게시물 삭제 권한이 없습니다.'];
    }

    // 게시물 삭제
    $stmt = $mysqli->prepare("DELETE FROM posts WHERE id = ?");
    $stmt->bind_param("i", $postId);
    $stmt->execute();
    $stmt->close();

    // 파일 삭제
    if ($file_path && file_exists($file_path)) {
        unlink($file_path);
    }

    return ['success' => true, 'message' => '게시물이 삭제되었습니다.'];
}
```

> 게시물 id와 현재 사용자 id를 파라미터로 받음

> 게시물 id를 통해 게시물 작성자 id와 파일 경로를 $post_user_id, $file_path에 바인딩

> (1) 현재 사용자 id와 게시물 작성자 id가 일치하지 않는지 확인

> 일치하면 게시물 삭제 및 파일 삭제

|

## delete_post

```php
<?php
require_once 'init.php';

// 게시물 ID 검증
if (isset($_GET['id']) && !is_array($_GET['id'])) {
    $id = intval($_GET['id']); // ID를 정수로 변환
} else {
    echo "<script>alert('잘못된 요청입니다.'); window.location.href='index.php';</script>";
    exit();
}

// 게시물 삭제
$result = deletePost($mysqli, $id, $_SESSION['id']);

// 결과 처리
if ($result['success']) {
    echo "<script>alert('" . $result['message'] . "'); window.location.href='index.php';</script>";
} else {
    echo "<script>alert('" . $result['message'] . "'); window.location.href='index.php';</script>";
}

$mysqli->close();
exit();
?>
```

> 게시물 id가 있는지 확인 후 id를 intval()을 사용하여 정수로 변환 

> id가 유효하지 않다면(NULL) 에러 메시지 출력 후 스크립트 종료

> deletePost()함수를 호출하여 게시물 삭제. 게시물 id와 현재 로그인한 사용자의 id를 인자로 받음

|

---

|