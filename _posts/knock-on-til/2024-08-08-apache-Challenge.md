---
title: "[2주차 TIL] KnockOn Bootcamp - Apache (Challenge)"
categories:
  - Web Architecture
tags:
  - Knockon Bootcamp 2nd
  - Apache
last_modified_at: 2024-08-08T05:54:00-05:00
published: true
---

|

# 아파치와 Nginx의 차이점 이해하기

## 아키텍처

- **아파치 (Apache)**

**`Process-driven (프로세스 기반)`**: 각 클라이언트 요청에 대해 새로운 프로세스를 생성하거나 쓰레드를 생성

이를 MPM (Multi-Processing Module)이라는 모듈을 통해 관리

|

**`대표적인 MPM`**: prefork, worker, event

`prefork`: 각 요청마다 별도의 프로세스를 생성하여 안정적이지만 메모리 사용량이 많음

`worker`: 각 요청마다 쓰레드를 생성하여 메모리 사용 효율이 좋음

`event`: worker 기반이지만 Keep-Alive 연결을 보다 효율적으로 처리함

|

- **Nginx**

**`Event-driven (이벤트 기반)`**: 비동기 이벤트 기반 아키텍처를 사용

적은 수의 워커 프로세스로 많은 수의 클라이언트 요청을 처리할 수 있음

-- 높은 성능과 낮은 리소스 사용

|

## 성능

- **아파치 (Apache)**

동시 연결 처리 능력이 Nginx에 비해 상대적으로 낮음

*동적 콘텐츠* 처리 (CGI, PHP)에서 성능이 좋음

|

- **Nginx**

높은 동시 연결 처리 능력. 트래픽이 많은 사이트에서 뛰어난 성능을 보임

*정적 콘텐츠* 제공 속도가 매우 빠름

|

## 설정 파일

- **아파치 (Apache)**

주로 httpd.conf 또는 apache2.conf를 사용

.htaccess 파일을 통해 디렉터리별 설정을 덮어쓸 수 있음

.htaccess 파일을 통해 개별 디렉터리에서 설정을 변경할 수 있는 유연성을 제공하지만, 파일을 매 요청마다 읽어야 하기 때문에 성능 저하가 발생할 수 있음

|

- **Nginx**

설정 파일은 주로 nginx.conf를 사용

.htaccess와 같은 디렉터리별 설정 파일을 지원하지 않음

모든 설정이 단일 또는 소수의 파일에 집약되어 있어, 설정 관리가 상대적으로 단순하며 성능 상의 이점이 있음

|

# 모듈 및 기능 확장

- **아파치 (Apache)**

다양한 모듈을 통해 기능을 확장할 수 있음

동적으로 모듈을 로드하고 언로드할 수 있음

모듈이 많아 다양한 요구 사항을 충족할 수 있지만, 모듈 로드로 인한 성능 저하가 있을 수 있음

|

- **Nginx**

핵심 기능을 확장할 수 있는 모듈을 지원하지만, *컴파일 시점*에 모듈을 포함해야 합니다.

동적 모듈 로드를 지원하지 않음

*경량화*된 코어와 모듈로 높은 성능을 유지할 수 있음

|

## 프록시 및 로드 밸런싱

**`리버스 프록시`**

`포워드 프록시`: 클라이언트 -- 포워드 프록시 서버 -- 웹 서버

클라이언트를 대신해주는 프록시 서버

클라이언트가 프록시를 설정함

|

`리버스 프록시`: 클라이언트 -- 리버스 프록시 서버 -- 백엔드 서버

서버를 대신해주는 프록시 서버

서버가 프록시를 설정함

자체적으로 로드 밸런싱 기능이 있음

|

**`로드 밸런싱`**

여러 서버에 걸쳐 네트워크 트래픽을 분산시킴

서버의 과부하 방지, 웹 서비스 성능과 안정성을 향상시키는 기술

로드 밸런서는 클라이언트의 요청을 여러 서버에 균등하게 배분하여 각 서버 부하를 최소화함

|

- **아파치 (Apache)**

'mod_proxy' 모듈을 통해 리버스 프록시와 로드 밸런싱 기능을 제공

|

- **Nginx**

리버스 프록시와 로드 밸런싱 기능이 기본적으로 내장되어 있어, 설정이 간단하고 성능이 우수

주로 프록시 서버 및 로드 밸런서로 많이 사용

|


# 사용

- **아파치 (Apache)**

다양한 기능과 모듈을 필요로 하는 경우 사용

PHP와의 통합이 용이하여 LAMP 스택에서 많이 사용

|

`LAMP`: 웹 개발 환경을 구성하는 소프트웨어 스택

(Linux, Apache, MySQL, PHP) 4가지 소프트웨어 기술의 번들

정적, 동적 웹 콘텐츠 모두 제작 가능

|

- **Nginx**

높은 성능과 낮은 리소스 사용이 요구되는 경우 사용

정적 콘텐츠 제공, 리버스 프록시, 로드 밸런싱 역할에 적합

LEMP (Linux, Nginx, MySQL, PHP) 스택에서 많이 사용

|

## 정리

| 특징 | Apache | Nginx |
|:----|:----|:----|
| 아키텍처 | 프로세스 기반 (MPM) - prefork, worker, event | 이벤트 기반 |
| 성능 | 동적 콘텐츠 처리에 강점 (CGI, PHP)  동시 연결 처리 능력이 Nginx보다 낮음 | 정적 콘텐츠 제공 속도가 빠름  높은 동시 연결 처리 능력 |
| 설정 파일 | httpd.conf 또는 apache2.conf 사용  .htaccess 파일로 디렉터리별 설정 가능 | nginx.conf 사용  .htaccess와 같은 디렉터리별 설정 파일 없음 |
| 모듈과 기능 확장 | 다양한 모듈을 동적으로 로드 가능 | 컴파일 시 모듈 포함, 동적 모듈 로드 불가 |
| 프록시와 로드 밸런싱 | mod_proxy 모듈로 제공 | 기본적으로 내장된 리버스 프록시 및 로드 밸런싱 기능 |
| 사용 사례 |	다양한 기능과 모듈이 필요한 경우 유리  LAMP 스택에서 많이 사용됨 | 높은 성능과 낮은 리소스 사용이 요구되는 경우 유리  정적 콘텐츠 제공, 리버스 프록시, 로드 밸런싱에 적합  LEMP 스택에서 많이 사용됨

|

---

|

# Tomcat의 대해 이해하기

오픈 소스 서블릿 컨테이너(Servlet Container) 및 웹 서버

주로 Java 기반 웹 애플리케이션을 실행하는 데 사용

|

## 기능

**`서블릿 컨테이너(Servlet Container)`**: 서블릿(Servlet)과 JSP(JavaServer Pages)를 실행할 수 있는 환경을 제공

클라이언트의 요청을 받아 서블릿과 JSP로 처리하고, 응답을 반환

|

**`웹 서버(Web Server)`**: HTTP 웹 서버로서 정적 콘텐츠(HTML, CSS, 이미지 등)를 제공

웹 클라이언트로부터 HTTP 요청을 받아 정적 및 동적 콘텐츠를 제공

|

**`Java EE 지원`**: Java EE(Enterprise Edition)의 일부 사양을 지원하여, 엔터프라이즈급 웹 애플리케이션을 실행 가능

서블릿, JSP, JDBC, JNDI 등 Java EE 사양의 일부를 구현하여 웹 애플리케이션 개발을 지원

|

## 구조

Tomcat은 모듈식 구조로 설계됨

|

**`Catalina`**: Tomcat의 서블릿 컨테이너

서블릿과 JSP를 실행하는 핵심 엔진

클라이언트 요청을 처리하고, 서블릿을 로드하고 실행하며, 응답을 생성

|

**`Coyote`**: Tomcat의 커넥터(Connector)

HTTP/1.1 프로토콜을 처리하는 HTTP 커넥터

클라이언트와 서버 간의 네트워크 통신을 관리하고, HTTP 요청과 응답을 처리

|

**`Jasper`**: Tomcat의 JSP 컴파일러

JSP 파일을 서블릿으로 변환

JSP 페이지를 컴파일하여 실행 가능한 서블릿 코드로 변환

|

**`Cluster`**:Tomcat의 클러스터링 모듈

여러 Tomcat 인스턴스 간에 세션 상태를 공유

로드 밸런싱과 세션 복제를 통해 고가용성과 확장성을 제공

|

## 설정 파일

**`server.xml`**: Tomcat의 주요 구성 설정을 정의하는 파일

커넥터, 엔진, 호스트, 컨텍스트 등을 설정

|

```xml
<Connector port="8080" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="8443" />
```

|

**`web.xml`**: 웹 애플리케이션의 배포 설명자(Deployment Descriptor)

각 웹 애플리케이션의 설정을 정의

서블릿 매핑, 필터, 리스너 등을 설정

|

```xml
<servlet>
    <servlet-name>exampleServlet</servlet-name>
    <servlet-class>com.example.ExampleServlet</servlet-class>
</servlet>
<servlet-mapping>
    <servlet-name>exampleServlet</servlet-name>
    <url-pattern>/example</url-pattern>
</servlet-mapping>
```

|

**`context.xml`**: 개별 웹 애플리케이션의 컨텍스트 설정을 정의

데이터 소스, 자바빈즈, 환경 변수 등을 설정

|

```xml
<Context path="/example" docBase="example" reloadable="true">
    <Resource name="jdbc/ExampleDB" auth="Container"
              type="javax.sql.DataSource" maxActive="100" maxIdle="30" maxWait="10000"
              username="dbuser" password="dbpassword" driverClassName="com.mysql.jdbc.Driver"
              url="jdbc:mysql://localhost:3306/exampledb"/>
</Context>
```

|

## 동작 원리

### 1. 클라이언트 요청 수신

클라이언트가 웹 브라우저를 통해 HTTP 요청을 보냄

|

### 2. Coyote 커넥터 처리

Coyote 커넥터가 HTTP 요청을 수신하고 처리

|

### 3. Catalina 엔진 실행

Catalina 서블릿 컨테이너가 요청을 받아 서블릿 또는 JSP로 처리

|

### 4. Jasper 컴파일

JSP 요청의 경우, Jasper가 JSP를 서블릿으로 컴파일

|

### 5. 서블릿 실행 및 응답 생성

서블릿이 비즈니스 로직을 처리하고, 응답을 생성

|

### 6. 클라이언트 응답 반환

생성된 응답이 Coyote 커넥터를 통해 클라이언트에게 반환됨

|

---

|

# apache 로컬환경 or 클라우드서버 에서 설치 후 실습해보기

## 로컬 환경 설치

```sh
# 1. 패키지 목록 업데이트
sudo apt update

# 2. Apache 설치
sudo apt install apache2

# 3. 실행 확인
sudo systemctl status apache2
```

|

![아파치 로컬 실행](./assets/images/아파치1.png)

- "Active: active"로 아파치 웹서버 서비스가 실행되는 걸 확인

- <http://localhost>로 접속. "Apache2 Default Page"가 뜸. 설치가 성공적으로 이루어짐

|

### 실습

```sh
# 설정 파일

# Apache 설정 파일
sudo vi /etc/apache2/sites-available/000-default.conf

--- vi
# 000-default.conf 파일 내부

# 루트 디렉토리 확인
DocumentRoot /var/www/html
---

# 수정했다면, 완료 후
sudo systemctl restart apache2
# 또는
sudo service apache2 restart
```

|

![아파치 설정 파일](./assets/images/아파치2.png)

|

### UFW 방화벽 설정 - HTTP, HTTPS 포트 개방

```sh
# UFW에 등록된 프로그램 목록 확인
sudo ufw app list
```

|

![ufw app list](./assets/images/아파치3.png)

> 80포트: Apache

> 80, 443포트: Apache Full

> 443포트: Apache Secure

|

```sh
# 80, 443 포트 개방
sudo ufw allow 'Apache Full'
```

|

![아파치 포트 개방](./assets/images/아파치4.png)

- ufw가 활성화 되지 않아 포트가 열리지 않는다

- ufw를 활성화 하자

|

```sh
# ufw 활성화
sudo ufw enable
```

|

![ufw 활성화](./assets/images/아파치5.png)

- 이전에 이미 룰을 추가했기 때문에 활성화만 해주면 된다.

|

### 페이지 수정

```sh
# 로컬 페이지
sudo vi /var/www/html/index.html 

# 수정 후 서버 재시작
sudo systemctl restart apache2
```

> 로컬 접속시 나타나는 페이지는 /var/www/html에 위치한 index.html파일

|

### 외부 접속 확인

```sh
# ubuntu

# ifconfig 명령어 사용을 위해 툴 설치
sudo apt install net-tools

# 우분투 ip 확인
ifconfig
```

|

![ip 확인](./assets/images/아파치6.png)

|

```sh
# windows

# ubuntu의 ip로 핑 보내보기
ping 192.168.149.137
```

|

![해당 ip로 접속](./assets/images/아파치7.png)

> 192.168.149.137로 접속.

|

---

|

## 클라우드 서버에서 설치

### AWS EC2 인스턴스 생성

![인스턴트 시작](./assets/images/AWS_EC2_1.png)

AWS 가입 후 EC2 서비스 검색 후 들어가기

- 서울로 지역 변경

- 인스턴트 시작

|

![유형 선택](./assets/images/AWS_EC2_2.png)

- Ubuntu 선택

- Ubuntu Server 프리티어 사용 가능으로 선택

- 인스턴스 유형 프리티어 사용 가능으로 선택

- 새 키 페어 생성

|

![키 페어 생성](./assets/images/AWS_EC2_3.png)

- RSA 선택

- .pem 선택

- 키 페어 생성

|

![보안 그룹 확인 및 인스턴트 시작](./assets/images/AWS_EC2_4.png)

- 보안 그룹을 확인하고(이따 설정할 거 있음), 인스턴트 시작

|

![인스턴트 생성 완](./assets/images/AWS_EC2_5.png)

- 인스턴트가 생성되면 모든 인스턴트 보기 클릭

|

![인스턴트 클릭](./assets/images/AWS_EC2_6.png)

- 생성된 인스턴트 클릭

|

### 인바운드 규칙

![보안 그룹](./assets/images/AWS_EC2_7.png)

- 왼쪽 목록에 보안 그룹 클릭

|

![보안 그룹 선택](./assets/images/AWS_EC2_8.png)

- 아까 봐둔 보안 그룹에 해당하는 거 클릭

|

![인바운드 규칙 편집](./assets/images/AWS_EC2_9.png)

- 인바운드 규칙 편집 클릭

|

![규칙 추가](./assets/images/AWS_EC2_10.png)

- 규칙 추가 누르고

- HTTP, HTTPS 생성 후 규칙 저장

|

### SSH 접속

![연결](./assets/images/AWS_EC2_11.png)

- 다시 인스턴스로 돌아와서 연결 클릭

|

![보안 그룹](./assets/images/AWS_EC2_12.png)

- SSH 클라이언트 클릭

-  *예: ssh -i "~.pem" ubuntu@~.compute.amazonaws.com* 부분 복사

-  터미널에서, 이전에 다운받은 "~.pem" 키 디렉토리로 이동

-  붙여넣기

```sh
ssh -i "~.pem" ubuntu@~.compute.amazonaws.com
```

|

안되면 아래 명령어 입력 후 다시 시도

```sh
chmod 400 ~.pem
```

|

---

|