<style>
  .portfolio-container {
    max-width: 850px;
    margin: 0 auto;
    font-size: 15px;
    line-height: 1.6;
    color: #333;
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
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
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

  .portfolio-item:last-child {
    margin-bottom: 0;
  }

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
  <div class="portfolio-grid">

    <div class="portfolio-card">
      <h3>프로젝트</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">AI를 활용한 Logical Validation 기반 침투테스트 프로세스 자동화 시스템</span>
          <span class="item-desc">주요정보통신기반시설/금융보안 기준과 내부 정책을 불변조건으로 정의하고, 스캐너 결과를 AI가 JSON 형태로 구조화해 위반 여부, 위험도, 공격 가능 흐름을 판단하는 진단 자동화 프로세스를 설계 중입니다. 불변조건 정의, AI 취약점 판단, 위험도 분류, 모의해킹 시나리오 생성, Red Team 검증, 보고서 생성, Blue Team 개선의 7단계 흐름을 목표로 진행하고 있습니다.</span>
          <span class="badge badge-progress">진행 중</span><span class="badge">2026.04 - 2026.06</span><span class="badge">6인 팀 프로젝트</span><span class="badge">Python/LLM</span><span class="badge">JSON 구조화</span><span class="badge">MITRE ATT&CK</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">AI 기반 내과 자가진단 모바일 앱</span>
          <span class="item-desc">Node.js/Express API와 PostgreSQL/Prisma 모델을 기반으로 사용자, 증상 기록, 예측 결과 저장 흐름을 구현했습니다. JWT 인증을 적용해 사용자별 진단 기록 접근을 분리하고, React Native/Expo 앱과 백엔드 API 및 FastAPI AI/NLP 서버를 연동했습니다. 프로젝트 결과로 영어 논문 공동 저자 참여 및 SW 공동 저작권 등록 성과를 얻었습니다.</span>
          <span class="badge badge-status">완료</span><span class="badge">2025.03 - 2025.06</span><span class="badge">3인 팀 프로젝트</span><span class="badge">React Native/Expo</span><span class="badge">Node.js</span><span class="badge">PostgreSQL</span><span class="badge">JWT/bcrypt</span><span class="badge">FastAPI</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">PHP 게시판 취약점 재현 및 시큐어코딩 학습</span>
          <span class="item-desc">Linux/Apache/MySQL/PHP 기반 게시판을 구현한 뒤 SQL Injection, XSS, File Upload, Directory Listing, Path Traversal/LFI, 소스코드 내 중요 정보 노출 등 8개 취약점 항목을 코드 관점에서 확인했습니다. Prepared Statement, htmlspecialchars 기반 출력 인코딩, 허용 확장자 화이트리스트와 업로드 파일 실행 제한 방향을 정리하고, 취약점 발생 위치와 패치 전후 코드를 보고서로 문서화했습니다.</span>
          <span class="badge badge-status">완료</span><span class="badge">2024.08 - 2024.09</span><span class="badge">개인 프로젝트</span><span class="badge">Linux</span><span class="badge">Apache</span><span class="badge">MySQL</span><span class="badge">PHP</span><span class="badge">Secure Coding</span>
        </li>
      </ul>
    </div>

    <div class="portfolio-card">
      <h3>기술 역량</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">웹 요청 분석 / Burp Suite</span>
          <span class="item-desc">시큐리티아카데미 웹 보안 실습과 워게임 기반 취약 환경에서 Burp Suite로 HTTP 요청·응답 구조를 분석하고, 쿠키, URL 파라미터, Header, HTTP Method, 파일 업로드 요청 변조로 IDOR, 인증/인가 우회 및 파일 업로드 취약점을 검증했습니다.</span>
          <span class="badge">숙련도 중</span><span class="badge">Burp Suite</span><span class="badge">HTTP</span><span class="badge">IDOR</span><span class="badge">File Upload</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">웹 취약점 공격 검증</span>
          <span class="item-desc">SQL Injection, XSS, IDOR, File Upload 등 주요 웹 취약점을 실습 환경에서 직접 검증했습니다. SQLi는 UNION 기반 및 error/time-based 방식으로 데이터 추출 과정을 검증했고, XSS는 Reflected/Stored/DOM XSS 및 Webhook 기반 쿠키·세션 탈취 시나리오를 수행했습니다.</span>
          <span class="badge">숙련도 중</span><span class="badge">SQLi</span><span class="badge">XSS</span><span class="badge">IDOR</span><span class="badge">Webhook</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">공격 흐름 재현</span>
          <span class="item-desc">취약 환경에서 서비스 구조 분석, 요청 변조, 파일 업로드 기반 RCE, 초기 쉘 획득, 설정 파일 및 계정 정보 확인, 권한 상승 가능 경로 식별로 이어지는 공격 흐름을 수행했습니다.</span>
          <span class="badge">숙련도 중</span><span class="badge">Attack Flow</span><span class="badge">RCE</span><span class="badge">Privilege Escalation</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">클라우드 보안 / AWS</span>
          <span class="item-desc">AWS CLI를 활용해 S3 버킷 공개 여부, 객체 접근 권한, EC2 metadata 기반 임시 자격증명 노출 및 기본 IAM 권한 구조를 분석했습니다.</span>
          <span class="badge">숙련도 하</span><span class="badge">AWS CLI</span><span class="badge">S3</span><span class="badge">EC2 Metadata</span><span class="badge">IAM</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">개발 / 시큐어코딩</span>
          <span class="item-desc">PHP/MySQL/Apache 게시판에서 SQLi, XSS, File Upload, Path Traversal/LFI 발생 지점을 코드로 확인하고 Prepared Statement, 출력 인코딩, 확장자 검증, 사용자 입력 제거 방식으로 보완했습니다.</span>
          <span class="badge">숙련도 중</span><span class="badge">PHP</span><span class="badge">MySQL</span><span class="badge">Prepared Statement</span><span class="badge">Output Encoding</span>
        </li>
      </ul>
    </div>

    <div class="portfolio-card">
      <h3>교육</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">시큐리티아카데미 7기</span>
          <span class="item-desc">한국정보보호산업협회에서 2026.02.23.부터 2026.06.18.까지 이수 중입니다.</span>
          <span class="badge badge-progress">이수 중</span><span class="badge">한국정보보호산업협회</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">KISA 아카데미 버그헌팅 실습 훈련</span>
          <span class="item-desc">한국인터넷진흥원 초급 25년 12차 과정과 중급 26년 5차 과정을 이수했습니다.</span>
          <span class="badge badge-status">이수</span><span class="badge">2025.08 / 2026.04 - 2026.05</span><span class="badge">Bug Hunting</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">KISIA 온택트 융합보안 교육</span>
          <span class="item-desc">리눅스, OT보안, 정보보호, 네트워크, 시스템, 클라우드 보안 기초 교육 34시간을 이수했습니다.</span>
          <span class="badge badge-status">이수</span><span class="badge">2026.02.23 - 2026.03.09</span><span class="badge">34H</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">KISA 아카데미 침해사고 대응 훈련</span>
          <span class="item-desc">리버스 엔지니어링, 멀웨어 식별, YARA 룰 작성, 스피어피싱 이메일·첨부파일 분석, 쉘 코드 분석 실습 133시간을 이수했습니다.</span>
          <span class="badge badge-status">이수</span><span class="badge">2025.01.24 - 2025.02.18</span><span class="badge">133H</span>
        </li>
        <li class="portfolio-item">
          <span class="item-title">ELITE WHITE HACKER Bootcamp 2기</span>
          <span class="item-desc">웹 워게임 30문항 풀이, 웹 취약점 분석·공격 기법 학습, 취약점 진단 기반 시큐어 코딩 적용을 수행했고 Top 7 우수 수료로 마무리했습니다.</span>
          <span class="badge badge-status">이수</span><span class="badge">2024.07.01 - 2024.10.01</span><span class="badge">KnockOn</span><span class="badge">Top 7</span>
        </li>
      </ul>
    </div>

    <div class="portfolio-card">
      <h3>수상</h3>
      <ul class="portfolio-list">
        <li class="portfolio-item">
          <span class="item-title">충남 IT Hackathon (CTF 보안 경진대회)</span>
          <span class="item-desc">고급 부문 1위로 대상을 수상했습니다. 웹 문제 풀이 및 플래그 획득을 담당했습니다.</span>
          <span class="badge">대상</span><span class="badge">고급 부문 1위</span><span class="badge">2025.09.27 - 2025.09.28</span><span class="badge">상명대학교</span>
        </li>
      </ul>
    </div>

  </div>
</div>
