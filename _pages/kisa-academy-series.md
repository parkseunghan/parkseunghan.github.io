---
title: "KISA Academy"
layout: single
permalink: /series/kisa-academy/
author_profile: true
sidebar:
  nav: "category_sidebar"
---

KISA Academy 정리 글을 주제별로 모아둔 페이지

{% assign kisa_posts = site.posts | where_exp: "post", "post.path contains '_posts/kisa-academy/'" %}

## 리버싱

{% for post in kisa_posts %}
  {% if post.categories contains "Reverse Engineering" %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}

## 멀웨어 분석

{% for post in kisa_posts %}
  {% if post.categories contains "Malware Analysis" %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}

## 주요 태그

- `KISA Academy`
- `Reverse Engineering`
- `Malware Analysis`
- `YARA`
- `Shellcode`
- `Spear Phishing`

