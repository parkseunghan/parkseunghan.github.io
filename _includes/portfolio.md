<style>
  /* 뷰포트 버그 패치: 최대 너비 고정 및 절대 단위 폰트 적용 */
  .portfolio-container {
    max-width: 850px; 
    margin: 0 auto; 
    font-size: 15px; 
    line-height: 1.6;
    color: #333;
  }

  .profile-summary {
    padding: 1.2rem 1.5rem;
    background-color: rgba(128, 128, 128, 0.03);
    border-left: 4px solid #0366d6;
    margin-bottom: 2rem;
    font-weight: 500;
  }

  .portfolio-grid {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .portfolio-card {
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 4px;
    padding: 1.5rem;
    background-color: #fff;
    transition: box-shadow 0.2s ease;
  }
  
  .portfolio-card:hover {
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    border-color: rgba(3, 102, 214, 0.4);
  }

  .portfolio-card h3 {
    font-size: 1.2rem;
    margin-top: 0;
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid rgba(128, 128, 128, 0.15);
    color: #24292e;
    font-weight: 600;
  }

  .portfolio-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .portfolio-item {
    margin-bottom: 1.5rem;
    position: relative;
    padding-left: 1.2rem;
  }

  .portfolio-item:last-child { margin-bottom: 0; }

  .portfolio-item::before {
    content: "■";
    position: absolute;
    left: 0;
    color: #0366d6;
    font-size: 0.7em;
    top: 0.35rem;
  }

  .item-title {
    font-weight: 600;
    display: block;
    color: #24292e;
  }

  .item-desc {
    color: #586069;
    font-size: 0.95em;
    margin-top: 0.3rem;
    display: block;
    line-height: 1.5;
  }

  .badge {
    display: inline-block;
    padding: 0.15rem 0.4rem;
    font-size: 0.8em;
    background: rgba(3, 102, 214, 0.08);
    color: #0366d6;
    border-radius: 3px;
    margin-right: 0.4rem;
    margin-top: 0.5rem;
    font-weight: 600;
  }
  
  .badge-status {
    background: #e1e4e8;
    color: #24292e;
  }
  .badge-progress {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;
  }
</style>

<div class="portfolio-container">
  
  <div class="profile-summary">
    오펜시브 시큐리티 기반의 화이트햇 해커를 목표로, 웹 애플리케이션 보안과 취약점 분석을 심도 있게 연구하고 있습니다. 단순한 이론 학습에 머물지 않고, 실제 인프라 환경에서의 모의해킹 프로젝트를 직접 수행하며 실무 역량을 증명해 나가는 예비 정보 보안 전문가입니다.
  </div>

  <div class="portfolio-grid">

    <div class="portfolio-card">
      <h3>Projects</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">React2Shell 취약점 분석 및 AI 기반 파이프라인 구축</span>
          <span class="item-desc">React2Shell(CVE-2025-55182)의 근본 원인을 분석하고, AI 에이전트(OpenClaw)를 활용하여 취약점 스캐닝 및 익스플로잇(Exploit)을 자동화하는 DevSecOps 환경을 구축.</span>
          <span class="badge badge-progress">진행 중</span><span class="badge">React</span><span class="badge">AI Agent</span><span class="badge">Vulnerability Analysis</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">로컬 웹 모의해킹 및 시큐어 코딩 적용</span>
          <span class="item-desc">로컬 환경에 PHP 게시판을 구축하고 모의해킹 수행. SQL 삽입(SQL Injection), XSS, 디렉토리 리스팅 등 주요 취약점을 식별한 후, 소스코드 레벨의 보안 패치(Secure Coding)를 완료.</span>
          <span class="badge badge-status">완료</span><span class="badge">Web Pentesting</span><span class="badge">PHP</span><span class="badge">Secure Coding</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">AI 기반 자연어 증상 추출 및 질병 예측 시스템 개발</span>
          <span class="item-desc">사용자의 자연어 텍스트 입력을 분석하여 증상을 추출하고 질병 위험도(Risk Level)를 예측하는 풀스택 애플리케이션을 개발. 자연어 처리(NLP)와 거대 언어 모델(Mistral LLM)을 결합한 하이브리드 엔진을 구축하고, 다중 데이터셋을 병합하여 분석 로직을 구현.</span>
          <span class="badge badge-status">완료</span><span class="badge">NLP & LLM</span><span class="badge">React Native</span><span class="badge">Prisma</span>
        </li>
      </ul>
    </div>

    <div class="portfolio-card">
      <h3>Education & Training</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">ELITE WHITE HACKER Bootcamp 2nd</span>
          <span class="item-desc">웹 모의해킹 실무 과정 수행 및 프로젝트 우수 성과 달성 (Top 7 우수 수료).</span>
          <span class="badge">Bootcamp</span><span class="badge">Top 7 우수 수료</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">KISA 아카데미 실전형 사이버훈련장</span>
          <span class="item-desc">쉘 코드 분석, 멀웨어 식별, YARA 기반 정규표현식, 리버싱(Reversing), 스피어피싱 이메일 분석 실전 훈련 이수.</span>
          <span class="badge">Cybersecurity Training</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">KISIA 온택트 융합보안 교육</span>
          <span class="item-desc">리눅스 기초, 정보보호 개론, 네트워크/시스템/클라우드/OT 보안 교육 이수.</span>
          <span class="badge">Cybersecurity Training</span>
        </li>
      </ul>
    </div>

    <div class="portfolio-card">
      <h3>Activities & Certifications</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">대학교 정보보안 동아리</span>
          <span class="item-desc">회장(24년 1학기) 및 부회장(24년 2학기) 역임. 교내 보안 스터디 주도 및 기술 지식 공유 활동 수행.</span>
          <span class="badge">Leadership</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">자격 사항 (Certifications)</span>
          <span class="item-desc">정보보안기사(Information Security Engineer) 필기 합격 및 실기 응시 준비 중.</span>
          <span class="badge">Certification</span>
        </li>
      </ul>
    </div>

  </div>
</div>