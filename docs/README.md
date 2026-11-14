# 문서 목차 · Documentation Index

[한국어](#한국어) · [English](#english)

---

## 한국어

Custom HTS의 문서 목록입니다. 프로젝트 소개와 빠른 시작은 루트 [README](../README.md)를 먼저 보세요.

### 시작하기

| 문서 | 내용 |
|------|------|
| [SETUP.md](SETUP.md) | 개발 환경 설치, `.env` 설정, 서버 실행 |
| [RUNNING_TESTS_LOCALLY.md](RUNNING_TESTS_LOCALLY.md) | 백엔드·프론트엔드 테스트와 점검 실행 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 기여 방법, 코드 스타일, 문서 형식 |
| [USER_GUIDE_CHARTS.md](USER_GUIDE_CHARTS.md) | 화면별 기능과 차트 사용법 |

### 레퍼런스

| 문서 | 내용 |
|------|------|
| [API.md](API.md) | 백엔드 REST API 전체 엔드포인트 |
| [KDEVELOPERS_API.md](KDEVELOPERS_API.md) | 한국투자증권 Open API 연동 (토큰, 속도 제한, 사용하는 API) |
| [OPENDART_API.md](OPENDART_API.md) | OpenDART 연동 (재무제표, 기업 개황, 공시, 고유번호) |
| [MASTER_FILES.md](MASTER_FILES.md) | 주식·채권·선물옵션 마스터 파일 |
| [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md) | (선택) Supabase 재무제표 저장 |
| [../database/schema.md](../database/schema.md) | 재무제표 테이블 스키마 |
| [../backend/README.md](../backend/README.md) · [../frontend/README.md](../frontend/README.md) | 백엔드·프론트엔드 구조 |

### 프로젝트 정책

| 문서 | 내용 |
|------|------|
| [../SECURITY.md](../SECURITY.md) | 보안 모델, 취약점 신고, 키 노출 시 조치 |
| [../LICENSE](../LICENSE) | MIT 라이선스 |
| [../CLAUDE.md](../CLAUDE.md) · [../.github/skills.md](../.github/skills.md) | AI 코딩 에이전트용 안내 |

### 문서 작성 규칙

- 사람이 읽는 문서는 **한국어 먼저, 영어 다음** 형식으로 한 파일에 씁니다. 상단에 `[한국어](#한국어) · [English](#english)` 링크를 두고 `## 한국어`, `## English` 섹션으로 나눕니다.
- 두 언어를 항상 함께 갱신합니다.
- 내부 링크는 상대 경로로 씁니다.
- 예시에는 실제 키·계좌번호 대신 자리표시자(`your_api_key`, `12345678`)를 씁니다.
- [archive/](archive/README.md)는 과거 구현·테스트 보고서 보관함이며 갱신하지 않습니다.

---

## English

This is the list of Custom HTS documents. For the project overview and quick start, read the root [README](../README.md) first.

### Getting started

| Document | Contents |
|----------|----------|
| [SETUP.md](SETUP.md) | Installing the dev environment, `.env` settings, running the servers |
| [RUNNING_TESTS_LOCALLY.md](RUNNING_TESTS_LOCALLY.md) | Running backend and frontend tests and checks |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute, code style, doc format |
| [USER_GUIDE_CHARTS.md](USER_GUIDE_CHARTS.md) | What each page does and how to use the charts |

### Reference

| Document | Contents |
|----------|----------|
| [API.md](API.md) | Every backend REST endpoint |
| [KDEVELOPERS_API.md](KDEVELOPERS_API.md) | KIS Open API integration (tokens, rate limits, APIs used) |
| [OPENDART_API.md](OPENDART_API.md) | OpenDART integration (financial statements, company overview, filings, corp codes) |
| [MASTER_FILES.md](MASTER_FILES.md) | Stock, bond and futures/options master files |
| [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md) | (optional) Supabase financial-statement storage |
| [../database/schema.md](../database/schema.md) | Financial-statement table schema |
| [../backend/README.md](../backend/README.md) · [../frontend/README.md](../frontend/README.md) | Backend and frontend structure |

### Project policies

| Document | Contents |
|----------|----------|
| [../SECURITY.md](../SECURITY.md) | Security model, vulnerability reporting, what to do if a key leaks |
| [../LICENSE](../LICENSE) | MIT License |
| [../CLAUDE.md](../CLAUDE.md) · [../.github/skills.md](../.github/skills.md) | Guides for AI coding agents |

### Writing docs

- Human-facing docs are written **Korean first, then English**, in a single file: `[한국어](#한국어) · [English](#english)` links at the top, then `## 한국어` and `## English` sections.
- Always update both languages together.
- Use relative paths for internal links.
- Use placeholders (`your_api_key`, `12345678`) instead of real keys or account numbers in examples.
- [archive/](archive/README.md) holds historical implementation and test reports and is not updated.
