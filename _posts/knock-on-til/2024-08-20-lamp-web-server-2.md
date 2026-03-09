---
title: "[3주차 TIL] KnockOn Bootcamp - 게시판 만들기(2) - 초기 설정 & 메인 화면"
categories:
  - Web Architecture
tags:
  - Knockon Bootcamp 2nd
  - board
last_modified_at: 2024-08-20T07:54:00-05:00
published: true
---

|

# 초기 설정 파일 생성 - init, config, db, functions

파일에서는 init.php만 require할 수 있도록 초기 파일들 생성 후 require

```php
// init.php

require_once 'config.php';

require_once 'db.php';

require_once 'functions.php';
```

> require: 필수적인 파일을 불러오지 못할 경우 *fatal error* 발생. 스크립트 실행이 중단됨

> include: 파일을 불러오지 못할 경우 *warning*만 출력되고 나머지 스크립트 계속 실행

> require_once, include_once: 파일이 이미 포함된 경우, 다시 포함하지 않음. 같은 파일을 여러 번 불러오는 것을 방지

|

---

|

# MySQL 연결

## config

config.php파일에서 DB 설정

```php
// config.php

define('DB_SERVER', 'your_servername');
define('DB_USERNAME', 'your_username');
define('DB_PASSWORD', 'your_password');
define('DB_NAME', 'your_dbname');
```

|

## db

db.php에서 MySQL 연결

```php
// db.php

// MySQL 연결
$mysqli = new mysqli(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME);

// 연결 확인
if ($mysqli->connect_error) {
    die("Connecion failed: " . $mysqli->connection_error);
}
```

|

## index

index.php에서 init.php파일 require

```php
// index.php

require_once 'init.php' 

// 추가 코드...
```

|

---

|

# 메인 페이지 - index

## config

```php
// config.php

define('POST_PER_PAGE', 7); // 한 페이지에 표시할 게시물 수
define('MAX_LENGTH', 100); // 미리보기 내용
```

|

## functions

**`getTotalPosts()`**: 총 게시물 수를 계산

**`getPosts()`**: 모든 게시물 가져오기

**`truncateContent()`**: 게시물 내용(content) 미리보기

|

```php
// functions.php

function getTotalPosts($mysqli, $query) {
    if ($query) { // search.php에서 다룰 예정
        $stmt = $mysqli->prepare("SELECT COUNT(*) FROM posts WHERE title LIKE ? OR content LIKE ?");
        $search_term = '%' . $query . '%';
        $stmt->bind_param("ss", $search_term, $search_term);
    } else { // 이 부분
        $stmt = $mysqli->prepare("SELECT COUNT(*) FROM posts");
    }
    $stmt->execute();
    $stmt->bind_result($total_posts);
    $stmt->fetch();
    $stmt->close();
    
    return $total_posts;
}
```

> $query는 search.php(검색기능)에서 코드 재사용을 위한 파라미터.

> else 부분: posts의 수(전체 게시물 수)를 계산

> $stmt에 쿼리 저장

> execute(): 쿼리 실행

> bind_result($total_posts): 쿼리 실행 결과를 $total_posts에 바인딩

> fetch(): 바인딩 된 결과 가져오기. 이때 $total_posts에 총 게시물 수가 저장됨

> close(): DB자원 해제

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

> $query는 search.php(검색기능)에서 코드 재사용을 위한 파라미터.

> 게시물과 작성자(username)을 가져오는 쿼리 준비

> LEFT JOIN: 게시물과 작성자 정보 결합

> ORDER BY created_at DESC: 최신 게시물이 먼저 나오도록 내림차순 정렬(default는 ASC로, 오름차순)

> LIMIT ?, ?: 페이지네이션 적용 offset만큼의 게시물을 건너뛰고, post_per_page개의 레코드를 가져옴

|

```php
// functions.php

function truncateContent($content, $maxLength = MAX_LENGTH) {
    return strlen($content) > $maxLength ? substr($content, 0, $maxLength) . '...' : $content;
}
```

> 게시물 내용, 최대 길이를 파라미터로 받음

> 게시물 길이가 $maxLength보다 길면, $maxLength길이의 문자 + '...' 을 붙여서 반환

> 그렇지 않으면 전체 내용 그대로 반환

|

## index

php 부분

```php
//index.php

require_once 'init.php';

$post_per_page = POST_PER_PAGE; // config.php파일에서 지정한 페이지 수

// 현재 페이지
$page = isset($_GET['page']) ? intval($_GET['page']) : 1; // 페이지 기본값 1
$page = max(1, $page); // 페이지가 1보다 작은 경우 1로 설정
$offset = ($page - 1) * $post_per_page; // 몇 개의 게시물을 스킵할지 결정. ex)2페이지면 1*7 까지 스킵 후 8번째 게시물부터 보여줌

// 총 게시물 수 계산
$total_posts = getTotalPosts($mysqli, NULL);

// 총 페이지 수 계산
$total_pages = ceil($total_posts / $post_per_page);

// 게시물 가져오기
$result = getPosts($mysqli, $offset, $post_per_page, NULL);
$mysqli->close();
```

> getTotalPosts()와 getPosts()에서 query부분을 NULL로 넘겨줘서 무시함

|

html 부분

여기서 `truncateContent()` 사용

```php
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>게시판</title>
</head>
<body>
    <a href="index.php"><h1>게시판</h1></a>

    <!-- 검색 폼 -->
    <form method="GET" action="search.php">
        <input type="text" name="query" placeholder="검색어를 입력하세요" required>
        <button type="submit">검색</button>
    </form>

    <nav>
        <a href="create_post.php">새 글 쓰기</a> |
        <a href="user_posts.php">내가 쓴 글</a> |
        <a href="update_profile.php">프로필 수정</a> |
        <a href="logout.php">로그아웃</a>
    </nav>

    <hr>

    <?php if ($result->num_rows > 0): ?>
        <?php while($row = $result->fetch_assoc()): ?>
            <h2>
                <a href="read_post.php?id=<?php echo htmlspecialchars($row['id']); ?>">
                    <?php echo htmlspecialchars($row['title']); ?>
                </a>
            </h2>
            
            <p>게시일: <?php echo date('Y. m. d', strtotime($row['created_at'])); ?>

                <?php if ($row['updated_at']): ?>

                    (수정일: <?php echo date('Y. m. d', strtotime($row['updated_at'])); ?>)

                <?php endif; ?>
            </p>

            <p>작성자: <?php echo htmlspecialchars($row['username'] ?? '작성자 정보 없음'); ?></p>

            <p><?php echo htmlspecialchars(truncateContent($row['content'])); ?></p>

            <?php if ($row['file_path']): ?>
                <p>첨부파일: <?php echo htmlspecialchars(basename($row['file_path'])); ?></p>
            <?php else: ?>
                <p>첨부파일: 없음</p>
            <?php endif; ?>

            <hr>
        <?php endwhile; ?>

    <?php else: ?>

        <p>게시물이 없습니다.</p>

    <?php endif; ?>

    <!-- 페이지 네비게이션 -->
    <nav>
        <ul>
            <?php if ($page > 1): ?>
                <li><a href="?page=<?php echo $page - 1; ?>">이전</a></li>
            <?php endif; ?>

            <?php for ($i = 1; $i <= $total_pages; $i++): ?>
                <li>
                    <a href="?page=<?php echo $i; ?>" <?php if ($i === $page) echo 'style="font-weight:bold;"'; ?>><?php echo $i; ?></a>
                </li>
            <?php endfor; ?>

            <?php if ($page < $total_pages): ?>
                <li><a href="?page=<?php echo $page + 1; ?>">다음</a></li>
            <?php endif; ?>
        </ul>
    </nav>
</body>
</html>
```

|

---

|
