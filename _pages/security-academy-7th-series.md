---
title: "Security Academy 7th"
layout: single
permalink: /series/security-academy-7th/
author_profile: true
sidebar:
  nav: "category_sidebar"
---

Security Academy 7th 정리 글을 보안 엔지니어링 관점의 기술 주제별로 모아둔 페이지

{% assign academy_posts = site.posts | where_exp: "post", "post.path contains '_posts/security-academy/'" %}

## Git & Docker

{% for post in academy_posts %}
  {% if post.tags contains "Git" or post.tags contains "Docker" or post.tags contains "Rebase" %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}

## Python

{% for post in academy_posts %}
  {% if post.tags contains "Python" %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}

## Linux

{% for post in academy_posts %}
  {% if post.tags contains "Linux" or post.tags contains "Kernel" or post.tags contains "Filesystem" %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}

## Database

{% for post in academy_posts %}
  {% if post.tags contains "Database" or post.tags contains "DBMS" or post.tags contains "MySQL" or post.tags contains "SQL" %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}

## System Security

{% for post in academy_posts %}
  {% if post.tags contains "System Security" or post.tags contains "Vulnerability Assessment" or post.tags contains "ISMS-P" or post.tags contains "Reporting" %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}

## Network Security

{% for post in academy_posts %}
  {% if post.tags contains "Network Security" %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}

## 주요 태그

- `Security Academy 7th`
- `Security Engineering`
- `Git`
- `Python`
- `Linux`
- `Database`
- `System Security`
- `Network Security`
