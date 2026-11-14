# 보안 정책 · Security Policy

[한국어](#한국어) · [English](#english)

---

## 한국어

### 취약점 신고

보안 취약점을 발견하셨다면 **공개 이슈로 올리지 마시고** GitHub의 [비공개 취약점 신고(Private vulnerability reporting)](https://github.com/shin0105/custom-hts/security/advisories/new) 기능으로 알려 주세요. 재현 방법과 영향 범위를 함께 적어 주시면 확인 후 답변드리겠습니다. 개인 프로젝트이므로 응답이 늦을 수 있습니다.

### 이 프로젝트의 보안 모델

- **로컬 단일 사용자용**입니다. 백엔드 API에는 인증이 없고 본인 계좌 잔고를 조회할 수 있으므로, 기본값대로 `127.0.0.1`에만 바인딩하세요. 공용 서버나 인터넷에 그대로 배포하는 것은 지원하지 않습니다.
- 모든 비밀값은 저장소 루트의 `.env`에서 읽습니다. `.env`는 gitignore 대상이며 `.env.example`에는 자리표시자만 있습니다.
- 한국투자증권 접근 토큰은 `backend/.cache/kis_tokens.json`(권한 0600, gitignore 대상)에 저장됩니다. 캐시 키로 앱키 자체가 아닌 SHA-256 해시를 씁니다.
- 실제 API를 호출하는 테스트의 결과(`backend/tests/test-results/`)에는 계좌 정보가 담길 수 있으므로 gitignore 대상입니다.

### 키가 노출되었을 때

API 키나 계좌 정보를 실수로 커밋하거나 공유했다면 즉시 다음을 하세요.

1. **한국투자증권**: [KIS Developers](https://apiportal.koreainvestment.com/)에서 앱키를 해지하고 재발급합니다.
2. **OpenDART**: [OpenDART](https://opendart.fss.or.kr/)에서 인증키를 재발급합니다.
3. **Supabase**: 프로젝트 설정에서 API 키를 교체(rotate)합니다.
4. 커밋 기록에서 해당 값을 제거합니다(예: [`git filter-repo`](https://github.com/newren/git-filter-repo)). 공개 저장소에 한 번 올라간 값은 이미 유출된 것으로 보고 반드시 키를 교체해야 합니다.

---

## English

### Reporting a vulnerability

If you find a security vulnerability, **please do not open a public issue**. Report it through GitHub's [private vulnerability reporting](https://github.com/shin0105/custom-hts/security/advisories/new) instead, with reproduction steps and the impact. This is a personal project, so replies may take a while.

### Security model

- The app is meant for **a single local user**. The backend API has no authentication and can read your account balance, so keep the default binding to `127.0.0.1`. Deploying it as-is to a shared server or the internet is not supported.
- All secrets are read from `.env` at the repository root. `.env` is gitignored, and `.env.example` contains placeholders only.
- KIS access tokens are stored in `backend/.cache/kis_tokens.json` (mode 0600, gitignored). The cache is keyed by a SHA-256 hash of the app key, not the key itself.
- Output from tests that call the real APIs (`backend/tests/test-results/`) can contain account data, so it is gitignored.

### If a key is exposed

If you accidentally commit or share an API key or account details, do the following right away:

1. **KIS**: revoke and reissue the app key at [KIS Developers](https://apiportal.koreainvestment.com/).
2. **OpenDART**: reissue the API key at [OpenDART](https://opendart.fss.or.kr/).
3. **Supabase**: rotate the API keys in the project settings.
4. Remove the value from the git history (for example with [`git filter-repo`](https://github.com/newren/git-filter-repo)). Anything that reached a public repository should be treated as leaked: always rotate the key.
