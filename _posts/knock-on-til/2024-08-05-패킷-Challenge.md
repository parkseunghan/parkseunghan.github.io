---
title: "KnockOn Bootcamp 2nd - 1주차 패킷 실습"
categories:
  - Web Fundamentals
tags:
  - KnockOn Bootcamp 2nd
  - Packet
last_modified_at: 2024-08-05T16:54:00+09:00
published: true
---
## Wireshark를 사용하여 Naver접속 시 사용된 패킷 필터링하기

```sh
# 입력
ping naver.com
```

```sh
# 결과
Ping naver.com [223.130.192.247] 32바이트 데이터 사용:
```

> 네이버 IP 확인

1. "ip.addr == 223.130.192.247"로 패킷 필터링

2. 네이버 접속 후 트래픽 발생

3. Stop

4. 패킷 분석

![Wireshark IP 필터링](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-packet-challenge-01.png)

## Wireshark를 사용하여 자신의 DNS 서버 정보 확인해보기

"dns"로 필터링

![Wireshark DNS 필터링](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-packet-challenge-02.png)

> Standard query response 찾기

![Wireshark DNS 필터링](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-packet-challenge-03.png)

> 클릭 후 Internet Protocol ... 찾기

![Wireshark DNS 필터링](/assets/images/writeup/web-architecture/knock-on-til/knock-on-til-packet-challenge-04.png)

> 확장하여 Source Address 확인

