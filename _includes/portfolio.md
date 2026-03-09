<style>
  /* 전체 컨테이너 및 폰트 사이즈 조절 */
  .portfolio-container {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif;
    font-size: 0.9em; 
    line-height: 1.6;
    color: #24292e;
  }

  /* 프로필 요약 박스 */
  .profile-summary {
    padding: 1.2rem 1.5rem;
    background-color: #f8f9fa;
    border-left: 4px solid #0366d6;
    margin-bottom: 2rem;
    font-weight: 500;
    color: #24292e;
    border-radius: 0 4px 4px 0;
  }

  /* 1열 (1 x N) 그리드 레이아웃 적용 */
  .portfolio-grid {
    display: grid;
    grid-template-columns: 1fr; 
    gap: 1.5rem; 
  }

  /* 카드 UI 디자인 정돈 */
  .portfolio-card {
    border: 1px solid #e1e4e8;
    border-radius: 6px; 
    padding: 1.5rem;
    background-color: #fff;
    transition: all 0.2s ease-in-out;
  }
  
  .portfolio-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border-color: #0366d6;
  }

  /* 섹션 헤더 디자인 */
  .portfolio-card h3 {
    font-size: 1.15em;
    margin-top: 0;
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #eaecef;
    color: #24292e;
    font-weight: 700;
    letter-spacing: -0.5px;
  }

  /* 커스텀 리스트 스타일 */
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

  .portfolio-item:last-child {
    margin-bottom: 0;
  }

  /* 불릿(Bullet) 기호 커스텀 */
  .portfolio-item::before {
    content: "■";
    position: absolute;
    left: 0;
    color: #0366d6;
    font-size: 0.6em;
    top: 0.45rem;
  }

  .item-title {
    font-weight: 700;
    display: block;
    color: #24292e;
    font-size: 1.05em;
  }

  .item-desc {
    color: #586069;
    font-size: 0.95em;
    margin-top: 0.3rem;
    display: block;
  }

  /* 키워드 강조 배지(Badge) 시스템 */
  .badge-container {
    margin-top: 0.6rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.5rem;
    font-size: 0.75em;
    background: #f1f8ff;
    color: #0366d6;
    border-radius: 2em; /* 둥근 알약 형태의 모던 뱃지 */
    font-weight: 600;
    border: 1px solid rgba(3, 102, 214, 0.2);
  }
  
  /* 특정 카테고리 배지 색상 커스텀 (옵션) */
  .badge.tech { background: #f0f4f8; color: #24292e; border-color: #d1d5da; }
  .badge.status { background: #fff8c5; color: #b08800; border-color: rgba(176, 136, 0, 0.2); }
</style>

<div class="portfolio-container">
  
  <div class="profile-summary">
    오펜시브 시큐리티(Offensive Security)와 침해사고대응(Incident Response)에 특화된 정보 보안 엔지니어입니다. 표면적인 툴 사용을 넘어, <strong>"취약점의 근본 원인(Root Cause)을 코어 레벨에서 해부하고, 시스템을 뚫어내며, 다시 완벽하게 방어해 내는 풀사이클(Full-lifecycle)"</strong>을 연구합니다.
  </div>

  <div class="portfolio-grid">

    <!-- 1. 핵심 보안 프로젝트 (메인 무기를 가장 위로 배치) -->
    <div class="portfolio-card">
      <h3>Core Security Projects (핵심 보안 리서치)</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">모던 웹 취약 환경 구축 및 모의해킹 (Custom Vuln. Testbed)</span>
          <span class="item-desc">Docker와 Python(Flask) 기반의 취약한 웹 마이크로서비스를 직접 설계하여, SSTI 등 모던 취약점을 엑스플로잇하고 시큐어 코딩을 적용한 오펜시브 프로젝트.</span>
          <div class="badge-container">
            <span class="badge">Web Pentesting</span><span class="badge tech">Python/Flask</span><span class="badge tech">Docker</span>
          </div>
        </li>
        <li class="portfolio-item">
          <span class="item-title">엔터프라이즈 1-Day CVE 심층 분석 (Deep Dive)</span>
          <span class="item-desc">글로벌 솔루션의 최근 RCE 취약점을 타겟으로, 패치 디핑(Patch Diffing)을 통해 근본 원인을 규명하고 Python 익스플로잇 코드를 자동화하는 리서치.</span>
          <div class="badge-container">
            <span class="badge status">In Progress</span><span class="badge">1-Day CVE</span><span class="badge">Patch Diffing</span>
          </div>
        </li>
        <li class="portfolio-item">
          <span class="item-title">ELK & YARA 기반 침해사고대응(IR) 파이프라인</span>
          <span class="item-desc">시큐리티 아카데미 팀 프로젝트. KISA 훈련과 연계하여 YARA 룰셋과 ELK를 결합한 능동형 위협 탐지(Threat Detection) 및 SOAR 환경 기획안.</span>
          <div class="badge-container">
            <span class="badge status">Planned</span><span class="badge">Incident Response</span><span class="badge tech">ELK Stack</span>
          </div>
        </li>
      </ul>
    </div>

    <!-- 2. 대외활동 및 기반 프로젝트 -->
    <div class="portfolio-card">
      <h3>Activities & Foundational Projects (대외 활동 및 기반 프로젝트)</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">2025 충남 IT 해커톤 (1박 2일 CTF)</span>
          <span class="item-desc">고급 부문 대상 (Grand Prize) 수상.</span>
          <div class="badge-container">
            <span class="badge">CTF</span><span class="badge">1st Place</span>
          </div>
        </li>
        <li class="portfolio-item">
          <span class="item-title">KnockOn Bootcamp 2기 (Web Pentesting)</span>
          <span class="item-desc">로컬 PHP 게시판을 구축하여 원시적인(Primitive) 웹 해킹 메커니즘을 체득하고 실전 웹 진단을 수행하여 Top 7 우수 수료.</span>
          <div class="badge-container">
            <span class="badge">Bootcamp Top 7</span><span class="badge tech">PHP/MySQL</span>
          </div>
        </li>
        <li class="portfolio-item">
          <span class="item-title">대학교 종합 프로젝트 (Secure Architecture)</span>
          <span class="item-desc">AI 연동 자가진단 플랫폼 개발. 마이크로서비스(MSA) 기반 통신 및 JWT/Bcrypt 인증을 구현하여 보안 내재화(Security by Design) 아키텍처 확립.</span>
          <div class="badge-container">
            <span class="badge">Architecture</span><span class="badge tech">Node.js</span><span class="badge tech">FastAPI</span>
          </div>
        </li>
      </ul>
    </div>

    <!-- 3. 교육 및 자격 -->
    <div class="portfolio-card">
      <h3>Education & Certifications (전문 교육 및 자격)</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">KISA 실전형 사이버훈련장 (Advanced Training)</span>
          <span class="item-desc">쉘코드 분석, 멀웨어 식별, 리버스 코드 엔지니어링, YARA 정규표현식 활용, 스피어피싱 첨부파일 분석 등 심화 침해대응 과정 이수.</span>
          <div class="badge-container">
            <span class="badge">Reversing</span><span class="badge">Malware Analysis</span>
          </div>
        </li>
        <li class="portfolio-item">
          <span class="item-title">KISIA 온택트(Ontact) 교육</span>
          <span class="item-desc">리눅스 기초, 정보보호 개론, 네트워크/시스템/클라우드/OT 보안 실무 교육 수료.</span>
          <div class="badge-container">
            <span class="badge">Cloud Security</span><span class="badge">Network Security</span>
          </div>
        </li>
        <li class="portfolio-item">
          <span class="item-title">보안 및 IT 자격 취득</span>
          <span class="item-desc">정보보안기사 필기 합격 (실기 응시 준비 중) / 정보처리기사 최종 합격.</span>
          <div class="badge-container">
            <span class="badge">Certification</span>
          </div>
        </li>
      </ul>
    </div>

    <!-- 4. 리더십 및 지식 공유 -->
    <div class="portfolio-card">
      <h3>Leadership & Knowledge Base (리더십 및 지식 아카이빙)</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">대학교 정보보안 동아리 cat2flag 리더십</span>
          <span class="item-desc">2024년 1학기 회장(President), 2학기 부회장(Vice President) 연임. 학회원 스터디 리딩 및 CTF 참가 독려. (2023. 03 ~ 2026. 02)</span>
          <div class="badge-container">
            <span class="badge">Leadership</span><span class="badge">Management</span>
          </div>
        </li>
        <li class="portfolio-item">
          <span class="item-title">기술 블로그 (Threat Intelligence Archive)</span>
          <span class="item-desc">KnockOn 워게임(Wargame) 30제 엑스플로잇 파이썬 스크립트 작성 및 KISA 아카데미 악성코드 분석 지식 문서화(Documentation).</span>
          <div class="badge-container">
            <span class="badge">Write-ups</span><span class="badge">Knowledge Sharing</span>
          </div>
        </li>
      </ul>
    </div>

  </div>
</div>