# Copilot 지침 · Copilot Instructions

전체 안내는 [CLAUDE.md](../CLAUDE.md)와 [.github/skills.md](skills.md)에 있습니다. 이 파일은 GitHub Copilot용 요약이며, 세부 코딩 규칙은 [.github/instructions/](instructions/)에 있습니다.
The full guide is in [CLAUDE.md](../CLAUDE.md) and [.github/skills.md](skills.md). This file is a summary for GitHub Copilot; detailed coding rules are in [.github/instructions/](instructions/).

[한국어](#한국어) · [English](#english)

---

## 한국어

### 프로젝트
국내·미국 시장 분석용 개인 웹 HTS입니다. **조회 전용**이며 주문 기능은 없습니다.
- 백엔드: `backend/` — FastAPI, Python 3.11+, `uv`. 계층은 `api/` → `services/` → `integrations/`, 모델은 `models/`, 설정은 `utils/config.py`의 `settings`.
- 프론트엔드: `frontend/` — React 18 + TypeScript(strict) + Vite, React Query, Recharts. 문구는 `i18n/ko.ts`, UI 요소는 `components/ui/`, 등락 색상은 `useMarketColors()`.
- 데이터: 한국투자증권 Open API, OpenDART, yfinance, Supabase(선택, 재무제표 테이블).

### 반드시 지킬 것
- 비밀값(`.env`, 키, 토큰, 계좌번호)을 코드·로그·문서·커밋에 넣지 않습니다.
- `backend/tests/test-results/`, `backend/.cache/`, `docs/kdevelopers_api/`는 커밋하지 않습니다.
- 백엔드를 `0.0.0.0`에 바인딩하지 않습니다(인증 없음).
- KIS 토큰 발급은 1분 1회 제한이 있으므로 `integrations/token_store.py` 캐시를 거칩니다.
- 테스트: 백엔드는 `backend/tests/`(계산 로직은 오프라인 테스트), 프론트엔드는 `npm run lint && npm run build`가 통과해야 합니다.
- 문서는 한국어 먼저, 영어 다음 형식이며 두 언어를 함께 갱신합니다. `docs/archive/`는 관리하지 않는 과거 기록입니다.

---

## English

### Project
A personal web HTS for analysing Korean and US markets. It is **read-only**, with no order placement.
- Backend: `backend/` — FastAPI, Python 3.11+, `uv`. Layers `api/` → `services/` → `integrations/`, models in `models/`, settings via `settings` in `utils/config.py`.
- Frontend: `frontend/` — React 18 + TypeScript (strict) + Vite, React Query, Recharts. Copy in `i18n/ko.ts`, UI building blocks in `components/ui/`, up/down colours via `useMarketColors()`.
- Data: KIS Open API, OpenDART, yfinance, Supabase (optional, financial-statement tables).

### Must follow
- Never put secrets (`.env` values, keys, tokens, account numbers) in code, logs, docs or commits.
- Never commit `backend/tests/test-results/`, `backend/.cache/` or `docs/kdevelopers_api/`.
- Do not bind the backend to `0.0.0.0` (it has no authentication).
- KIS token issuance is limited to once per minute, so always go through the `integrations/token_store.py` cache.
- Tests: backend in `backend/tests/` (offline tests for calculation logic); the frontend must pass `npm run lint && npm run build`.
- Docs are Korean first, then English; update both languages together. `docs/archive/` is unmaintained history.
