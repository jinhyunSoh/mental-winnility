# 멘탈 위닝리티 — 토론 교육 랜딩페이지

성인·직장인 대상 오프라인 다대다 토론 실습 교육 서비스 소개 페이지입니다.
빌드 도구나 프레임워크 없이 순수 HTML/CSS/JS로 만들어져 있어, 파일만 올리면 바로 동작합니다.

---

## 폴더 구조

```
mental-winnility/
├── index.html              # 메인 페이지
├── css/
│   └── style.css           # 전체 스타일 (반응형 · 애니메이션 포함)
├── js/
│   └── main.js             # 스크롤 등장 애니메이션 · 아코디언
├── assets/
│   ├── favicon.svg         # 파비콘
│   ├── apple-touch-icon.png# iOS 홈화면 아이콘 (180×180)
│   └── og-image.png        # 카톡·SNS 공유 썸네일 (1200×630)
├── robots.txt              # 검색엔진 크롤링 규칙
├── sitemap.xml             # 사이트맵
└── README.md
```

---

## 로컬에서 확인하기

파일을 더블클릭해서 열어도 되지만, 로컬 서버로 띄우면 실제 배포 환경과 동일하게 확인할 수 있습니다.

```bash
# Python이 설치되어 있다면
python -m http.server 8000

# Node.js를 쓴다면
npx serve .
```

이후 브라우저에서 `http://localhost:8000` 접속.

---

## 배포하기

빌드 과정이 없는 정적 사이트라 어디에 올려도 동작합니다.

### 1) Netlify (드래그 앤 드롭, 가장 쉬움)
1. [app.netlify.com/drop](https://app.netlify.com/drop) 접속
2. `mental-winnility` 폴더를 통째로 드래그
3. 즉시 URL 발급 → 이후 커스텀 도메인 연결 가능

### 2) Vercel
```bash
npm i -g vercel
vercel
```
프로젝트 루트에서 실행하면 됩니다. 프레임워크는 "Other"를 선택하세요.

### 3) GitHub Pages
1. GitHub에 저장소를 만들고 이 폴더의 내용을 push
2. 저장소 Settings → Pages → Source를 `main` 브랜치 / `root`로 설정
3. `https://<사용자명>.github.io/<저장소명>/` 으로 접속

### 4) 일반 웹호스팅 (카페24, 가비아 등)
FTP로 `public_html` 또는 `www` 폴더에 전체 파일을 업로드하면 됩니다.

---

## 배포 전 반드시 수정할 것

아래 항목은 `example.com`이 임시값으로 들어가 있습니다. 실제 도메인이 정해지면 바꿔주세요.

| 파일 | 위치 | 내용 |
|------|------|------|
| `index.html` | `<link rel="canonical">` | 실제 도메인 |
| `index.html` | `og:url`, `og:image`, `twitter:image` | 실제 도메인 |
| `index.html` | JSON-LD `url`, `logo` | 실제 도메인 |
| `robots.txt` | `Sitemap:` | 실제 도메인 |
| `sitemap.xml` | `<loc>` | 실제 도메인 |

### 링크 연결이 필요한 곳

현재 `href="#"` 로 비어 있는 버튼들입니다.

- 히어로 섹션 "상담 신청하기"
- 하단 CTA "상담 신청하기" / "문의처 바로가기"

연결 예시:

```html
<!-- 카카오톡 채널 -->
<a href="http://pf.kakao.com/_채널ID/chat" class="btn btn-primary btn-lg">상담 신청하기</a>

<!-- 구글 폼 -->
<a href="https://forms.gle/폼주소" target="_blank" rel="noopener" class="btn btn-primary btn-lg">상담 신청하기</a>

<!-- 전화 걸기 -->
<a href="tel:01012345678" class="btn btn-ghost btn-lg">전화 문의</a>

<!-- 이메일 -->
<a href="mailto:contact@도메인.com" class="btn btn-ghost btn-lg">이메일 문의</a>
```

---

## 구현된 인터랙션

| 기능 | 설명 | 구현 위치 |
|------|------|-----------|
| 스크롤 등장 애니메이션 | 화면에 들어오는 요소가 아래에서 페이드인. `IntersectionObserver` 사용, 한 번만 실행 | `main.js` / `.reveal` |
| 아코디언 확장 | 커리큘럼 4단계 · FAQ. 클릭 시 부드럽게 펼쳐지고 같은 그룹의 다른 항목은 자동으로 닫힘 | `main.js` / `.accordion` |
| 카드 롤오버 | 교육 특징 카드에 마우스를 올리면 하단에서 문구 레이어가 슬라이드업 | `style.css` / `.f-hover` |
| 헤더 스크롤 반응 | 스크롤 시 헤더에 그림자가 생기고 배경이 반투명 블러 처리 | `main.js` / `.is-scrolled` |
| 네비 밑줄 애니메이션 | 메뉴에 호버하면 밑줄이 좌우로 그어짐 | `style.css` |

### 접근성 · 예외 처리

- `prefers-reduced-motion` 설정 시 모든 애니메이션 비활성화
- JS가 꺼져 있어도 콘텐츠가 전부 보이도록 `.no-js` 폴백 처리
- 아코디언에 `aria-expanded` / `aria-controls` 적용, 키보드 조작 가능
- "본문 바로가기" 스킵 링크 제공
- 인쇄 시 전체 내용이 펼쳐지도록 `@media print` 처리

---

## 반응형 브레이크포인트

| 너비 | 동작 |
|------|------|
| 900px 이하 | 특징·추천대상 카드가 1열로, 상단 메뉴 간격 축소 |
| 720px 이하 | 상단 메뉴 숨김, 신뢰 배지 세로 배열, 버튼 전체 너비, 아코디언 헤더 2줄 배치 |
| 420px 이하 | 좌우 여백 및 카드 패딩 축소 |

폰트 크기와 섹션 여백은 `clamp()`를 써서 화면 폭에 따라 자연스럽게 변합니다.

---

## 커스터마이징

색상은 `css/style.css` 최상단 `:root`에서 한 번에 바꿀 수 있습니다.

```css
:root{
  --accent:#EA580C;   /* 포인트 컬러 (주황) */
  --navy:#0B1220;     /* 히어로 · CTA 배경 */
  --ink:#111827;      /* 본문 텍스트 */
}
```

---

© 2026 멘탈 위닝리티
