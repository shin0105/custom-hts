# 기여 가이드 · Contributing Guide

[한국어](#한국어) · [English](#english)

---

## 한국어

Custom HTS에 관심을 가져 주셔서 감사합니다. 버그 제보, 문서 개선, 기능 제안과 PR을 모두 환영합니다.

### 시작하기

1. 저장소를 포크하고 클론합니다.
2. [설치 가이드](SETUP.md)대로 개발 환경을 준비합니다. 개발 도구(black, flake8, mypy, pytest-cov)까지 설치하려면 `backend/`에서 `uv sync --extra dev`를 실행합니다.

### 브랜치와 PR

- `main`에서 브랜치를 만듭니다. 이름은 `feature/…`, `fix/…`, `docs/…`, `chore/…` 형식을 권장합니다.

  ```bash
  git checkout -b fix/short-description
  ```

- PR 하나에는 주제 하나만 담고, 관련 없는 파일의 서식 변경은 섞지 않습니다.
- 커밋 메시지는 무엇을 왜 바꿨는지 알 수 있게 씁니다. 한국어와 영어 모두 괜찮습니다.
- PR 설명에는 변경 내용, 관련 이슈, 확인 방법을 적습니다. 화면을 바꿨다면 스크린샷을 붙이되, 계좌번호나 잔고가 보이지 않게 하세요.
- 엔드포인트나 환경 변수를 바꿨다면 관련 문서도 같은 PR에서 고칩니다.

### PR 전 점검

백엔드:

```bash
cd backend
uv run pytest tests/test_bond_math.py tests/test_bond_analytics.py \
  tests/test_basis.py tests/test_option_parity.py \
  tests/test_stock_master.py tests/test_config.py tests/test_helpers.py
uv run black path/to/changed_file.py
uv run flake8 path/to/changed_file.py
```

프론트엔드:

```bash
cd frontend
npm run lint
npm run build
```

- 기존 백엔드 코드는 아직 black·flake8 기준을 모두 만족하지 않습니다. 저장소 전체가 아니라 **바꾼 파일에만** 실행해 주세요.
- 실제 API를 호출하는 라이브 테스트는 필수가 아닙니다. 자세한 내용은 [로컬 테스트 실행 가이드](RUNNING_TESTS_LOCALLY.md)를 참고하세요.

### 코드 스타일

**Python (백엔드)**

- PEP 8을 따르고 black으로 정리합니다. 한 줄은 79자까지입니다(`backend/pyproject.toml`의 `[tool.black]`).
- 타입 힌트와 docstring을 씁니다.
- 기존 구조를 따릅니다. 라우터는 `src/api/`, 비즈니스 로직은 `src/services/`, 외부 API 클라이언트는 `src/integrations/`, Pydantic 모델은 `src/models/`에 둡니다.
- 새 로직에는 네트워크 없이 도는 테스트를 추가합니다. 가짜 클라이언트나 캡처한 응답을 쓰는 `tests/test_basis.py`를 참고하세요.

**TypeScript (프론트엔드)**

- ESLint(`frontend/eslint.config.js`: typescript-eslint 권장 규칙, React Hooks 규칙)를 통과해야 하며, 경고도 실패로 처리됩니다.
- 함수형 컴포넌트와 훅을 씁니다. API 호출은 `src/services/`, 타입은 `src/types/`에 둡니다.
- 색·간격·글자 크기는 `src/theme/tokens.ts`의 토큰을 씁니다.
- UI 문구는 한국어로 쓰고, 여러 곳에서 쓰는 문구는 `src/i18n/ko.ts`에 둡니다.
- `npm run format`(Prettier)은 `src` 전체를 다시 쓰므로 기능 PR에서는 실행하지 말고 주변 코드 스타일을 따라 주세요.

### 비밀값과 개인 데이터

다음은 **절대 커밋하지 않습니다**.

- `.env` (API 키, 계좌번호). `.env.example`에는 자리표시자만 둡니다.
- `backend/.cache/` (KIS 접근 토큰)
- `backend/tests/test-results/`, `backend/test_results/` (라이브 테스트 결과. 계좌 정보가 담길 수 있습니다)
- 코드, 테스트 픽스처, 문서, 이슈, 스크린샷에 들어간 실제 키·토큰·계좌번호. 예시에는 `your_api_key`, `12345678` 같은 자리표시자를 씁니다.

커밋 전에 `git status`와 `git diff --staged`로 확인하세요. 실수로 올렸다면 [SECURITY.md](../SECURITY.md)의 절차대로 즉시 키를 교체하세요.

### 문서

문서는 한 파일에 한국어와 영어를 함께 씁니다. **한국어가 먼저**, 영어가 다음이며, 두 섹션의 내용과 구조가 같아야 합니다.

```markdown
# 한국어 제목 · English Title

[한국어](#한국어) · [English](#english)

---

## 한국어
...

---

## English
...
```

- 명령어, 파일 경로, 식별자, API 이름은 두 언어 모두 영어 그대로 쓰고, 코드 블록은 두 섹션에서 똑같이 둡니다.
- 링크는 상대 경로로 겁니다. `docs/archive/`는 과거 기록이므로 고치지 않습니다.

### 이슈 보고

- **버그**: 재현 단계, 기대 결과와 실제 결과, 환경(OS, Python·Node.js 버전, 브라우저)을 적어 주세요. 로그를 붙일 때는 키·토큰·계좌번호를 지웁니다.
- **기능 제안**: 쓰임새와 기대하는 동작을 설명해 주세요.
- **보안 취약점**: 공개 이슈 대신 [SECURITY.md](../SECURITY.md)에 안내된 방법으로 알려 주세요.

### 라이선스

기여하신 내용은 이 프로젝트의 [MIT 라이선스](../LICENSE)로 배포되는 데 동의하신 것으로 봅니다.

---

## English

Thank you for your interest in Custom HTS. Bug reports, documentation fixes, feature ideas and pull requests are all welcome.

### Getting started

1. Fork and clone the repository.
2. Set up your environment with the [setup guide](SETUP.md). To also install the dev tools (black, flake8, mypy, pytest-cov), run `uv sync --extra dev` in `backend/`.

### Branches and pull requests

- Branch off `main`. Names like `feature/…`, `fix/…`, `docs/…` or `chore/…` are recommended.

  ```bash
  git checkout -b fix/short-description
  ```

- Keep each PR to a single topic, and do not mix in formatting changes to unrelated files.
- Write commit messages that say what changed and why. Korean or English is fine.
- In the PR description, explain the change, link related issues and say how to verify it. Add screenshots for UI changes, making sure no account number or balance is visible.
- If you change an endpoint or an environment variable, update the related docs in the same PR.

### Checks before opening a PR

Backend:

```bash
cd backend
uv run pytest tests/test_bond_math.py tests/test_bond_analytics.py \
  tests/test_basis.py tests/test_option_parity.py \
  tests/test_stock_master.py tests/test_config.py tests/test_helpers.py
uv run black path/to/changed_file.py
uv run flake8 path/to/changed_file.py
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

- The existing backend code is not yet fully black/flake8 clean. Run them **on the files you changed**, not on the whole tree.
- Live tests that call real APIs are not required. See [Running tests locally](RUNNING_TESTS_LOCALLY.md).

### Code style

**Python (backend)**

- Follow PEP 8 and format with black. The line length is 79 (`[tool.black]` in `backend/pyproject.toml`).
- Use type hints and docstrings.
- Follow the existing layout: routers in `src/api/`, business logic in `src/services/`, external API clients in `src/integrations/`, Pydantic models in `src/models/`.
- Add tests for new logic that run without a network, using fake clients or captured responses; see `tests/test_basis.py`.

**TypeScript (frontend)**

- Code must pass ESLint (`frontend/eslint.config.js`: typescript-eslint recommended rules plus React Hooks rules); warnings count as failures.
- Use function components and hooks. Put API calls in `src/services/` and types in `src/types/`.
- Take colours, spacing and font sizes from the tokens in `src/theme/tokens.ts`.
- UI text is in Korean; strings used in several places belong in `src/i18n/ko.ts`.
- `npm run format` (Prettier) rewrites all of `src`, so do not run it in a feature PR; follow the style of the surrounding code instead.

### Secrets and personal data

**Never commit:**

- `.env` (API keys, account number). `.env.example` holds placeholders only.
- `backend/.cache/` (KIS access tokens)
- `backend/tests/test-results/`, `backend/test_results/` (live-test output, which can contain account data)
- Real keys, tokens or account numbers in code, test fixtures, docs, issues or screenshots. Use placeholders such as `your_api_key` or `12345678` in examples.

Check `git status` and `git diff --staged` before committing. If something slips through, rotate the keys right away as described in [SECURITY.md](../SECURITY.md).

### Documentation

Each document holds both languages in one file: **Korean first**, then English, with the same content and structure in both sections.

```markdown
# 한국어 제목 · English Title

[한국어](#한국어) · [English](#english)

---

## 한국어
...

---

## English
...
```

- Keep commands, file paths, identifiers and API names in English in both languages, and keep code blocks identical in both sections.
- Use relative links. `docs/archive/` is a historical record; do not edit it.

### Reporting issues

- **Bugs**: include steps to reproduce, expected and actual results, and your environment (OS, Python and Node.js versions, browser). Remove keys, tokens and account numbers from any logs you paste.
- **Feature requests**: describe the use case and the behaviour you expect.
- **Security vulnerabilities**: do not open a public issue; follow [SECURITY.md](../SECURITY.md).

### License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).
