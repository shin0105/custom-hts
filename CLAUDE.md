# CLAUDE.md

이 파일은 이 저장소에서 작업하는 AI 코딩 에이전트(Claude Code 등)를 위한 안내서입니다. 한국어 다음에 같은 내용의 영어가 이어집니다.
This file guides AI coding agents (Claude Code and others) working in this repository. The Korean section is followed by the same content in English.

[한국어](#한국어) · [English](#english)

---

## 한국어

### 프로젝트 한눈에 보기

Custom HTS는 국내·미국 시장을 분석하는 **개인용 웹 HTS**입니다. **조회·분석 전용**이며 주문 기능은 없습니다. 사용자가 명시적으로 요청하지 않는 한 주문·매매 기능을 추가하지 마세요.

- **백엔드**: `backend/` — FastAPI, Python 3.11+, `uv`로 관리. 진입점 `src.main:app`, `127.0.0.1:8000`.
- **프론트엔드**: `frontend/` — React 18 + TypeScript(strict) + Vite, React Query, Recharts. `:5173`, `/api`를 백엔드로 프록시.
- **데이터 출처**: 한국투자증권(KIS) Open API, OpenDART, yfinance. Supabase는 선택 사항이며 재무제표 테이블에만 씁니다.

### 자주 쓰는 명령

```bash
bash run-dev.sh                                   # 백엔드 + 프론트엔드 동시 실행 (stop-dev.sh로 종료)
cd backend && uv sync                             # 백엔드 의존성 설치
cd backend && uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
cd backend && uv run pytest tests/test_bond_math.py   # 단일 테스트 파일
cd backend && uv run pytest                       # 전체 (일부는 실제 API 키 필요)
cd backend && uv run python scripts/check_hantu_keys.py   # KIS 키 점검
cd frontend && npm run lint && npm run build      # 린트 + 타입 체크/빌드
```

### 코드 구조와 규칙

**백엔드** (`backend/src/`)
- 계층: `api/`(FastAPI 라우터) → `services/`(비즈니스 로직) → `integrations/`(외부 API 클라이언트). 라우터에 로직을 넣지 말고 서비스에 둡니다.
- 요청·응답 모델은 `models/`의 Pydantic 모델을 씁니다. 설정은 `from ..utils.config import settings`로만 읽습니다.
- KIS 클라이언트(`integrations/kdevelopers.py`)는 동기 방식이지만 여러 스레드에서 불러도 안전합니다(스레드 공용 속도 제한, 토큰 발급 잠금). 동기 클라이언트(KIS, OpenDART, 마스터 파일)를 `async def` 안에서 직접 부르면 이벤트 루프가 막히므로, `utils/concurrency.py`의 `run_blocking`이나 `@to_thread` 데코레이터로 블로킹 호출용 스레드 풀(워커 4개)에서 실행하세요. 호출 여러 개를 묶는 서비스는 `TTLCache`도 씁니다. `services/korean_market.py`(`@to_thread`), `services/bond_analytics.py`, `services/basis.py`(`run_blocking`)가 예시입니다.
- KIS 접근 토큰은 `integrations/token_store.py`가 로컬 파일(`backend/.cache/kis_tokens.json`)에 캐시합니다. 토큰 발급은 1분에 1회로 제한되므로 새 토큰을 남발하지 마세요.
- 순수 계산 로직(`services/bond_math.py`, `basis.py`, `option_parity.py`, `bond_analytics.py`)은 오프라인 단위 테스트가 있습니다. 수정하면 해당 테스트를 함께 고치고 실행하세요.
- 스타일: black(line-length 79), 타입 힌트 필수.

**프론트엔드** (`frontend/src/`)
- `pages/` 화면, `components/` 공용 컴포넌트, `components/ui/` 디자인 시스템(Button, Panel, StatTile, DataTable …), `services/` axios API 호출(기본 경로 `/api`), `hooks/` React Query 훅, `types/` 타입.
- 화면 문구는 한국어이며 `i18n/ko.ts`에 둡니다. 문자열을 컴포넌트에 직접 쓰지 마세요.
- 등락 색상은 하드코딩하지 말고 `theme/marketColorContext.ts`의 `useMarketColors()`를 쓰세요(한국식/글로벌식 전환 지원).

### 보안 규칙 (반드시 지킬 것)

- `.env`, API 키, 토큰, 계좌번호를 코드·로그·문서·커밋에 절대 넣지 마세요. 예시는 `12345678`, `your_api_key` 같은 자리표시자를 씁니다.
- `backend/tests/test-results/`(실제 API 응답, 계좌 정보 포함 가능)와 `backend/.cache/`는 커밋 금지입니다. 둘 다 gitignore되어 있습니다.
- 백엔드는 인증이 없으므로 `0.0.0.0`에 바인딩하거나 외부에 노출하는 변경을 하지 마세요.
- `docs/kdevelopers_api/`는 한국투자증권 공식 문서의 로컬 사본(gitignore 대상)일 수 있습니다. 참고는 해도 되지만 저장소에 다시 추가하지 마세요.

### 문서 규칙

- 사람이 읽는 문서(README, docs/, CLAUDE.md, .github/skills.md 등)는 **한국어 먼저, 영어 다음** 형식입니다: 상단에 `[한국어](#한국어) · [English](#english)`, 이어서 `## 한국어`와 `## English` 섹션. 한쪽만 고치지 말고 두 언어를 함께 갱신하세요.
- `docs/archive/`는 과거 기록이며 관리하지 않습니다. 새 문서를 그곳에 추가하거나 현재 정보의 근거로 삼지 마세요.
- 구현 보고서나 "완료 요약" 문서를 새로 만들지 마세요. 필요한 내용은 기존 문서를 갱신합니다.

---

## English

### Project at a glance

Custom HTS is a **personal web HTS** for analysing Korean and US markets. It is **read-only** and has no order placement. Do not add order or trading features unless the user explicitly asks.

- **Backend**: `backend/` — FastAPI, Python 3.11+, managed with `uv`. Entry point `src.main:app`, `127.0.0.1:8000`.
- **Frontend**: `frontend/` — React 18 + TypeScript (strict) + Vite, React Query, Recharts. `:5173`, proxies `/api` to the backend.
- **Data sources**: Korea Investment & Securities (KIS) Open API, OpenDART, yfinance. Supabase is optional and only used for the financial-statement tables.

### Common commands

```bash
bash run-dev.sh                                   # run backend + frontend together (stop with stop-dev.sh)
cd backend && uv sync                             # install backend dependencies
cd backend && uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
cd backend && uv run pytest tests/test_bond_math.py   # a single test file
cd backend && uv run pytest                       # everything (some tests need real API keys)
cd backend && uv run python scripts/check_hantu_keys.py   # check KIS keys
cd frontend && npm run lint && npm run build      # lint + type-check/build
```

### Code layout and conventions

**Backend** (`backend/src/`)
- Layers: `api/` (FastAPI routers) → `services/` (business logic) → `integrations/` (external API clients). Keep logic out of routers; put it in services.
- Use the Pydantic models in `models/` for requests and responses. Read settings only via `from ..utils.config import settings`.
- The KIS client (`integrations/kdevelopers.py`) is synchronous but safe to call from several threads (a shared rate limiter and a lock on token issuance). Calling a synchronous client (KIS, OpenDART, master files) directly inside `async def` blocks the event loop, so run it on the blocking-call pool (4 workers) with `run_blocking` or the `@to_thread` decorator from `utils/concurrency.py`. Services that fan out several calls also use `TTLCache`. See `services/korean_market.py` (`@to_thread`) and `services/bond_analytics.py` / `services/basis.py` (`run_blocking`).
- KIS access tokens are cached in a local file (`backend/.cache/kis_tokens.json`) by `integrations/token_store.py`. KIS allows one token issuance per minute, so do not request new tokens needlessly.
- The pure calculation modules (`services/bond_math.py`, `basis.py`, `option_parity.py`, `bond_analytics.py`) have offline unit tests. When you change them, update and run those tests too.
- Style: black (line-length 79), type hints required.

**Frontend** (`frontend/src/`)
- `pages/` screens, `components/` shared components, `components/ui/` design system (Button, Panel, StatTile, DataTable, …), `services/` axios API calls (base path `/api`), `hooks/` React Query hooks, `types/` types.
- UI copy is Korean and lives in `i18n/ko.ts`. Do not hard-code strings in components.
- Do not hard-code up/down colours; use `useMarketColors()` from `theme/marketColorContext.ts` (supports the Korean and global conventions).

### Security rules (must follow)

- Never put `.env` values, API keys, tokens or account numbers in code, logs, docs or commits. Use placeholders such as `12345678` or `your_api_key` in examples.
- Never commit `backend/tests/test-results/` (real API responses that may include account data) or `backend/.cache/`. Both are gitignored.
- The backend has no authentication: do not bind it to `0.0.0.0` or expose it to a network.
- `docs/kdevelopers_api/` may hold a local, gitignored copy of KIS's official docs. You may read it for reference, but never add it back to the repository.

### Documentation rules

- Human-facing docs (README, docs/, CLAUDE.md, .github/skills.md, …) are **Korean first, then English**: `[한국어](#한국어) · [English](#english)` at the top, then `## 한국어` and `## English` sections. Update both languages together, never just one.
- `docs/archive/` is historical and not maintained. Do not add new docs there or treat it as a source of current facts.
- Do not create new implementation reports or "completion summary" docs. Update the existing docs instead.
