# 프론트엔드 · Frontend

[한국어](#한국어) · [English](#english)

---

## 한국어

Custom HTS의 웹 화면입니다. React 18, TypeScript, Vite로 만들었고 TanStack React Query(데이터 요청·캐시), React Router, Recharts(차트), axios를 씁니다. 화면 문구는 한국어입니다.

### 준비물

Node.js 20.19 이상 또는 22.12 이상(Vite 7 요구 사항)이 필요합니다.

### 설치와 실행

```bash
cd frontend
npm install
npm run dev
```

http://localhost:5173 에서 열립니다. 개발 서버는 `/api` 요청을 `http://localhost:8000`의 백엔드로 프록시하므로 백엔드도 실행 중이어야 합니다. 저장소 루트의 `bash run-dev.sh`로 둘을 함께 띄울 수 있습니다.

### npm 스크립트

| 명령 | 설명 |
|------|------|
| `npm run dev` | 개발 서버(포트 5173, 핫 리로드) |
| `npm run build` | `tsc` 타입 검사 후 `dist/`에 프로덕션 빌드 |
| `npm run preview` | 빌드 결과를 로컬에서 미리 보기 |
| `npm run lint` | ESLint 검사(경고도 실패로 처리) |
| `npm run format` | Prettier로 `src` 전체를 다시 씀. 기존 코드도 바뀌므로 기능 PR에서는 쓰지 않습니다. |

테스트 스크립트(`npm test`)는 없습니다. 변경 후에는 `npm run lint`와 `npm run build`로 점검합니다.

### 화면

| 경로 | 페이지 파일 | 메뉴 | 내용 |
|------|-------------|------|------|
| `/` | `HomePage.tsx` | 홈 | 시작 화면 |
| `/korean` | `KoreanMarketPage.tsx` | 국내주식 | 종목 검색, 시세, 일봉·분봉 차트, 밸류에이션, 추정실적, 재무제표 |
| `/bonds` | `BondMarketPage.tsx` | 장내채권 | 채권 시세와 수익률 분석 |
| `/futures-options` | `DomesticFuturesOptionsPage.tsx` | 선물옵션 | 선물옵션 종목 선택, 일봉·분봉 차트 |
| `/basis` | `BasisPage.tsx` | 베이시스 | 선물 베이시스와 풋콜 패리티 |
| `/us` | `USMarketPage.tsx` | 해외주식 | 미국 주식 시세, 캔들 차트, 밸류에이션, 재무제표 (yfinance) |
| `/account-check` | `AccountCheckPage.tsx` | 계좌조회 | 한국투자증권 계좌 잔고와 보유 종목 |

화면별 사용법은 [화면 사용 가이드](../docs/USER_GUIDE_CHARTS.md)를 참고하세요.

### 프로젝트 구조

```
frontend/
├── src/
│   ├── main.tsx             # entry point, React Query client
│   ├── App.tsx              # routes
│   ├── pages/               # one component per page
│   ├── components/          # charts, panels, search, navigation
│   │   └── ui/              # shared UI primitives (Button, Panel, DataTable, ...)
│   ├── hooks/               # React Query hooks
│   ├── services/            # axios API clients (base URL /api)
│   ├── types/               # API response types
│   ├── theme/               # design tokens, up/down colour convention
│   ├── i18n/ko.ts           # shared Korean UI strings
│   ├── utils/               # formatting, error and colour helpers
│   └── index.css            # global styles
├── index.html
├── vite.config.ts           # dev server port and /api proxy
├── eslint.config.js
└── tsconfig.json
```

- 등락 색상은 한국식(상승 빨강·하락 파랑)과 글로벌식(상승 초록·하락 빨강) 중 고를 수 있으며, 선택은 브라우저 `localStorage`에 저장됩니다.
- 색·간격·글자 크기는 `src/theme/tokens.ts`의 토큰을 씁니다.

### 배포

이 앱은 자기 컴퓨터에서 쓰는 것을 전제로 합니다. 백엔드 API에는 인증이 없고 계좌 잔고를 조회할 수 있으므로, 빌드 결과를 공용 서버에 올리거나 외부 네트워크에 공개하지 마세요. 자세한 내용은 [SECURITY.md](../SECURITY.md)를 참고하세요.

---

## English

The web UI of Custom HTS, built with React 18, TypeScript and Vite. It uses TanStack React Query (data fetching and caching), React Router, Recharts (charts) and axios. UI text is in Korean.

### Prerequisites

Node.js 20.19+ or 22.12+ (required by Vite 7).

### Install and run

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server proxies `/api` requests to the backend at `http://localhost:8000`, so the backend must be running too. `bash run-dev.sh` at the repository root starts both.

### npm scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Dev server (port 5173, hot reload) |
| `npm run build` | `tsc` type check, then a production build into `dist/` |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | ESLint (warnings count as failures) |
| `npm run format` | Rewrites all of `src` with Prettier. It also changes existing code, so do not use it in a feature PR. |

There is no test script (`npm test`). After making changes, check with `npm run lint` and `npm run build`.

### Pages

| Route | Page file | Menu | What it shows |
|-------|-----------|------|---------------|
| `/` | `HomePage.tsx` | 홈 (Home) | Landing page |
| `/korean` | `KoreanMarketPage.tsx` | 국내주식 (KR stocks) | Stock search, quotes, daily and minute charts, valuation, earnings estimates, financial statements |
| `/bonds` | `BondMarketPage.tsx` | 장내채권 (KR bonds) | Bond quotes and yield analytics |
| `/futures-options` | `DomesticFuturesOptionsPage.tsx` | 선물옵션 (Futures & options) | Contract picker, daily and minute charts |
| `/basis` | `BasisPage.tsx` | 베이시스 (Basis) | Futures basis and put-call parity |
| `/us` | `USMarketPage.tsx` | 해외주식 (US stocks) | US quotes, candle charts, valuation, financial statements (yfinance) |
| `/account-check` | `AccountCheckPage.tsx` | 계좌조회 (Account) | KIS account balance and holdings |

For how to use each page, see the [user guide](../docs/USER_GUIDE_CHARTS.md).

### Project structure

```
frontend/
├── src/
│   ├── main.tsx             # entry point, React Query client
│   ├── App.tsx              # routes
│   ├── pages/               # one component per page
│   ├── components/          # charts, panels, search, navigation
│   │   └── ui/              # shared UI primitives (Button, Panel, DataTable, ...)
│   ├── hooks/               # React Query hooks
│   ├── services/            # axios API clients (base URL /api)
│   ├── types/               # API response types
│   ├── theme/               # design tokens, up/down colour convention
│   ├── i18n/ko.ts           # shared Korean UI strings
│   ├── utils/               # formatting, error and colour helpers
│   └── index.css            # global styles
├── index.html
├── vite.config.ts           # dev server port and /api proxy
├── eslint.config.js
└── tsconfig.json
```

- Up/down colours follow either the Korean convention (up red, down blue) or the global one (up green, down red); the choice is saved in the browser's `localStorage`.
- Take colours, spacing and font sizes from the tokens in `src/theme/tokens.ts`.

### Deployment

The app is meant to run on your own computer. The backend API has no authentication and can read your account balance, so do not put the build on a shared server or expose it to a network. See [SECURITY.md](../SECURITY.md).
