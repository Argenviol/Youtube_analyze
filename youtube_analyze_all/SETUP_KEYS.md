# API 키 발급

파이프라인을 끝까지 돌리는 데 필요한 키는 **2개**입니다. 전부 무료이고 결제수단 등록이 필요 없습니다.
키는 코드·커밋에 넣지 않고 환경변수(로컬)나 저장소 시크릿(GitHub Actions)으로만 넣습니다.

## 바로 보기

| 키 | 환경변수 | 쓰는 프로젝트 | 없으면 | 발급 |
|---|---|---|---|---|
| YouTube Data API v3 | `YOUTUBE_API_KEY` | 01·02·04·05·06, 10(공식 채널 댓글) | 그 프로젝트의 수집이 멈춘다(분석·사이트 재생성은 `--skip-collect` 로 가능) | Google Cloud, 3~5분 |
| Open DART | `DART_API_KEY` | 09 | 09 수집이 즉시 중단 | opendart.fss.or.kr 개인 회원, 3분 |

03·07·08·11·12 는 키가 필요 없습니다(치지직 공개 API·공개 페이지·재사용 데이터).

## YouTube Data API v3

1. <https://console.cloud.google.com/> 에서 새 프로젝트를 만든다(이름은 아무거나, 예: `stellive-analytics`).
2. `API 및 서비스` → `라이브러리` → `YouTube Data API v3` → **`사용`**. 이 단계를 건너뛰면 키를 만들어도 403 이 난다.
3. `API 및 서비스` → `사용자 인증 정보` → `+ 사용자 인증 정보 만들기` → **`API 키`**. `AIza…` 로 시작하는 39자.
4. (권장) 키 제한 → `API 제한사항` → `YouTube Data API v3` 만 체크. 유출돼도 다른 API 에 쓰이지 않는다.

**쿼터** — 일반 엔드포인트 합산 **10,000 units/일**, `search.list` **100회/일**(별도 카운트, 1회 100 units).
태평양 시간 자정(KST 16~17시)에 초기화. `common/youtube.py` 가 모든 호출을 `_state/youtube_quota.json` 에
적고 자체 예산(8,000 units·검색 90회) 안에서만 호출하므로 한도를 넘기지 않는다. 그룹별 실측은 `scripts/refresh.py` 머리말.

## Open DART

1. <https://opendart.fss.or.kr/> → `인증키 신청/관리` → `인증키 신청`.
2. **개인 회원**으로 신청(법인은 사업자등록증 + 1~2 영업일 심사). API 사용 환경 `웹`, 목적은 "개인 포트폴리오용 기업
   재무데이터 분석" 정도, 확인 URL 은 저장소 주소(없으면 `http://localhost` 도 통과).
3. 이메일 인증 뒤 즉시 발급. 40자 인증키는 `오픈API 이용현황`에서 언제든 다시 볼 수 있다.

## 키 넣는 법

| 어디서 | 방법 |
|---|---|
| Windows (로컬) | PowerShell 에서 `setx YOUTUBE_API_KEY "…"`, `setx DART_API_KEY "…"` — **새로 여는 터미널부터** 적용. 확인은 `echo $env:YOUTUBE_API_KEY` |
| macOS · Linux (로컬) | `export YOUTUBE_API_KEY=…` (셸 프로필에 넣으면 영구) |
| GitHub Actions | 저장소 `Settings → Secrets and variables → Actions` 에 같은 이름으로 등록. `collect-scheduled.yml` 이 `secrets.YOUTUBE_API_KEY`·`secrets.DART_API_KEY` 로 읽는다 |

스크립트는 `os.environ` 만 읽습니다 — `.env` 파일은 읽지 않으므로 환경변수로 넣어야 합니다. 키가 노출됐으면 즉시
재발급(회전)하고 옛 키를 지웁니다.

## 키 외에 필요한 것

- **08 동시시청자는 소급 수집이 안 됩니다.** 지금은 GitHub Actions `collect-live` 가 10분 간격으로 대신 찍으므로 PC 를
  켜둘 필요가 없습니다. 로컬에서 직접 찍을 때만(`수집시작.cmd`) 절전을 끄고 창을 열어 둡니다.
- 파이썬 패키지는 `pip install -r requirements.txt` 하나로 끝납니다.
