---
title: "KnockOn Bootcamp 2nd - 2주차 PHP 실습"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - PHP
last_modified_at: 2024-08-11T19:54:00+09:00
published: true
---
## php 설치 후 apache, MySQL과 연결해보기

## php 설치

```sh
# php와 필요한 모듈 설치
sudo apt install php libapache2-mod-php php-mysql
```

**`libapache2-mod-php`**: Apache와 PHP 연결

```php
<?php
    // Apache와 PHP 연결 확인 코드

    phpinfo();
?>
```

**`php-mysql`**: MySQL과 PHP 연결

```php
<?php
    // MySQL과 PHP 연결 확인 코드

    $servername = "localhost";
    $username = "newuser";
    $password = "password123";

    $conn = new mysqli($servername, $username, $password);

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    echo "Connected Successfully!";
?>
```

![](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-php-challenge-01.png)

- phpinfo.php 파일로 Apache와 PHP가 연결됨을 확인

- db_test.php 파일로 MySQL과 PHP가 연결됨을 확인

## GET과 POST의 차이점 이해하기

## GET

서버로 데이터 요청

웹 페이지를 요청할 때 가장 일반적으로 사용됨

데이터 조회나 검색 등의 작업에 적합하며, 서버의 상태를 변경하지 않는 요청에 사용됨

**`데이터 전송 방식`**: URL의 쿼리 문자열로 데이터를 서버로 전송함

<http://example.com/page?name=Park&age=24> 에서 name과 age는 **쿼리 문자열**

**`데이터 보안`**: 데이터가 URL에 포함되어 노출되므로, 민감한 정보 전송에 적합하지 않음

URL은 브라우저의 히스토리에 저장되며, 다른 사용자와 쉽게 공유될 수 있음

**`용량`**: URL의 길이에 제한이 있어 전송할 수 있는 데이터의 크기도 제한됨 (약 2048자)

**`캐싱`**: 브라우저에 의해 캐싱될 수 있어, 같은 요청 반복 시 서버에 대한 요청을 줄일 수 있음

**`북마크 가능`**: URL에 데이터가 포함되어 있어, 북마크를 통해 같은 요정 재사용 가능

```html
<form action="search.php" method="get">
    <input type="text" name="query" />
    <input type="submit" value="Search" />
</form>
```

> 예: 사용자가 입력한 쿼리는 URL의 쿼리 문자열로 전송됨

## POST

서버에 데이터를 제출하여 처리하도록 요청

폼 제출, 파일 업로드, 데이터베이스 업데이트 등에 사용됨

서버의 상태를 변경하거나 회원가입, 로그인, 데이터베이스 업데이트 등 서버에 데이터를 제출하는 요청에 적합

**`데이터 전송 방식`**: 데이터가 요청 본문(body)에 포함되어 서버로 전송됨

**`데이터 보안`**: URL 직접 노출 감소, GET 대비 상대적 우위

권장: HTTPS 사용

**`용량`**: 데이터 크기에 제한이 거의 없어, 대량의 데이터를 전송할 수 있음

서버와 클라이언트의 설정에 따라 전송 가능한 데이터의 양이 달라짐

**`캐싱`**: 캐싱되지 않음

일반적으로 URL을 통해 직접 액세스할 수 없음

**`북마크 불가`**: URL에 데이터가 포함되지 않으므로, 북마크를 통해 재사용 불가

```html
<form action="submit.php" method="post">
    <input type="text" name="username" />
    <input type="password" name="password" />
    <input type="submit" value="Login" />
</form>
```

> 예: 사용자가 입력한 데이터는 POST 요청의 본문에 포함되어 서버로 전송됨

## 파일 업로드 방법 이해하기

## HTML 폼 설정

폼의 'enctype' 속성을 'multipart/form-data'로 설정하여 파일 데이터를 포함하는 폼을 전송할 수 있게 해줌

```html
<form method="post" action="process.php" enctype="multipart/form-data">
        Name: <input type="text" name="name" />
	File: <input type="file" name="fileToUpload" />
        <input type="submit" value="Upload File" />
</form>
```

> process.html

**`method`**: post로 설정

**`action`**: 파일이 업로드될 PHP 스크립트의 URL

**`enctype`**: multipart/form-data로 설정

**`input type="file"`**: 파일 선택을 위한 입력 필드

## PHP 스크립트에서 파일 처리

파일 업로드 처리를 위해 '$_FILES' 배열을 사용

**`$_FILES`**: 업로드된 파일의 정보(이름, 크기, 임시 파일 경로 등)을 제공함

```php
<?php
$name = $_POST['name'];
echo "Hello, $name!";

// 업로드된 파일이 있는지 확인
if (isset($_FILES['fileToUpload'])) {
	$file = $_FILES['fileToUpload'];

  // 오류가 발생하지 않았는지 확인
	if ($file['error'] === UPLOAD_ERR_OK) {
	  // 파일의 임시 경로와 파일 이름 가져오기
		$tmpName = $file['tmp_name'];
		$name = $file['name'];

		// 파일을 저장할 디렉토리 설정
		// __DIR__ 은 현재 디렉토리
		$uploadDir = __DIR__.'/uploads/';

		// 디렉토리가 존재하지 않으면 생성
		if (!is_dir($uploadDir)) {
			if (!mkdir($uploadDir, 0755, true)) {
				die("Directory Creation Failed.");
			}
		}

		// 파일을 지정한 디렉토리에 저장
		$uploadFile = $uploadDir . basename($name);
		if (move_uploaded_file($tmpName, $uploadFile)) {
			echo "File Uploaded Successfully!";
		} else {
			die("File Upload Failed. Upload File Path: $uploadFile");
		}
	} else {
		echo "File Upload Error: " . $file['error'];
	}
} else {
	echo "File Not Uploaded.";
}
?>

```

안될 경우

```sh
# 권한 설정
sudo chown -R www-data:www-data /var/www/html/uploads
sudo chmod -R 755 /var/www/html/uploads
```

## 보안 및 유효성 검사

**`파일 타입 검증`**: 업로드할 파일의 MIME 타입이나 확장자를 검사하여 허용된 형식만 업로드되도록 함

**`파일 크기 제한`**: PHP의 `upload_max_filesize` 및 `post_max_size` 설정을 사용하여 업로드할 파일의 최대 크기를 제한

**`파일 이름 검사`**: 사용자 제공 파일 이름을 직접 사용하지 말고, 안전한 파일 이름으로 변경하여 저장

**`디렉토리 접근 제한`**: 업로드된 파일이 웹에서 직접 접근되지 않도록 적절한 파일 권한과 디렉토리 설정을 적용

```php
<?php
if (isset($_FILES['fileToUpload'])) {
    $file = $_FILES['fileToUpload'];
    $allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    $maxSize = 2 * 1024 * 1024; // 2MB

    if ($file['error'] === UPLOAD_ERR_OK) {
        if (in_array($file['type'], $allowedTypes) && $file['size'] <= $maxSize) {
            // 파일 처리 코드 (위의 예시와 동일)
        } else {
            echo "허용되지 않는 파일 형식이거나 파일 크기가 너무 큽니다.";
        }
    } else {
        echo "파일 업로드 오류: " . $file['error'];
    }
} else {
    echo "파일이 업로드되지 않았습니다.";
}
?>
```

