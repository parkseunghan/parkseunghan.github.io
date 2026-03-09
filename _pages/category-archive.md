---
title: "Categories"
layout: categories
permalink: /categories/
author_profile: true
sidebar:
  nav: "category_sidebar"
---

<style>
  /* --- [Design System: Compact Modern Minimal] --- */
  
  /* 1. 사이드바(Sidebar) - 글꼴 크기 축소 및 간격 밀착 */
  .sidebar .nav__title {
    font-size: 0.75rem; /* 타이틀 크기 축소 */
    text-transform: uppercase;
    color: #6a737d;
    margin-bottom: 0.8rem; /* 하단 여백 축소 */
    letter-spacing: 0.05em;
    font-weight: 700;
    border: none;
  }
  
  .sidebar .nav__items {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  
  .sidebar .nav__items a {
    color: #444d56;
    text-decoration: none;
    font-size: 0.85rem; /* 메뉴 글씨 크기 대폭 축소 */
    padding: 0.25rem 0.5rem; /* 상하 여백 축소하여 리스트 밀착 */
    margin-bottom: 0.1rem;
    border-radius: 4px;
    display: block;
    transition: background-color 0.2s ease, color 0.2s ease;
  }
  
  .sidebar .nav__items a:hover {
    background-color: rgba(3, 102, 214, 0.08);
    color: #0366d6;
  }

  /* 2. 상단 카테고리 인덱스 - 콤팩트 배지(Badge) */
  .taxonomy__index {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem; /* 배지 사이 간격 축소 */
    margin-bottom: 2.5rem; /* 전체 하단 여백 축소 */
    padding: 0;
  }
  
  .taxonomy__index li { 
    list-style: none; 
  }
  
  .taxonomy__index a {
    display: inline-block;
    background-color: #f1f8ff;
    color: #0366d6;
    padding: 0.25rem 0.7rem; /* 배지 내부 여백 축소 */
    border-radius: 12px;
    font-size: 0.8rem; /* 배지 글씨 축소 */
    font-weight: 600;
    border: none;
    text-decoration: none;
    transition: all 0.2s ease;
  }
  
  .taxonomy__index a:hover {
    background-color: #0366d6;
    color: #ffffff;
    transform: translateY(-1px); /* 애니메이션 폭 축소 */
    box-shadow: 0 2px 8px rgba(3, 102, 214, 0.2);
  }

  /* 3. 개별 게시물 및 섹션 헤더 - 정보 밀도(Information Density) 극대화 */
  .taxonomy__section .archive__subtitle {
    font-size: 1.1rem; /* 헤더 크기 축소 */
    color: #24292e;
    margin-top: 2rem; /* 섹션 간 간격 축소 */
    margin-bottom: 0.8rem;
    font-weight: 700;
    border: none;
    position: relative;
  }
  
  /* 포인트 바(Point Bar) 크기 축소 */
  .taxonomy__section .archive__subtitle::after {
    content: '';
    display: block;
    width: 20px;
    height: 2px;
    background-color: #0366d6;
    margin-top: 6px;
    border-radius: 2px;
  }
  
  .archive__item {
    margin-bottom: 0.4rem; /* 게시물 사이 간격(Margin) 대폭 축소 */
    padding: 0.1rem 0;
    transition: transform 0.2s ease;
  }
  
  .archive__item:hover {
    transform: translateX(4px); /* 호버 시 이동 폭 축소 */
  }
  
  .archive__item-title {
    font-size: 0.95rem; /* 게시물 제목 크기 대폭 축소 */
    margin: 0;
    font-weight: 500;
  }
  
  .archive__item-title a {
    color: #24292e;
    text-decoration: none;
    transition: color 0.2s ease;
  }
  
  .archive__item-title a:hover {
    color: #0366d6;
  }
</style>