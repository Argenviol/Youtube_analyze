# StelLive 데이터 분석 포트폴리오

버추얼 크리에이터 그룹 **스텔라이브(StelLive)**를 소재로, 공개 데이터(YouTube Data API 등)를
수집·정제·분석하는 데이터 분석 포트폴리오입니다. 설문/응답 수집 없이 **이미 공개된 지표**만
사용하며, 각 프로젝트는 **수집 → 정제 → SQL → 시각화(그래프) → 웹 대시보드**의 동일한
파이프라인을 따릅니다.

## 프로젝트 목록

| # | 프로젝트 | 상태 | 폴더 |
|---|----------|------|------|
| 1 | 멤버별 유튜브 채널 성과 분석 | ✅ 완료 | [`01_member_channel_performance/`](01_member_channel_performance/) |
| 2 | 커버곡 성과 랭킹 분석 | ✅ 완료 | [`02_cover_song_ranking/`](02_cover_song_ranking/) |
| 3 | 치지직 방송 패턴 분석 | ✅ 완료 | [`03_chzzk_stream_pattern/`](03_chzzk_stream_pattern/) |
| 4 | 키리누키(2차창작) 생태계 분석 | ✅ 완료 | [`04_kirinuki_ecosystem/`](04_kirinuki_ecosystem/) |
| 5 | 댓글 여론/감성 분석 | ✅ 완료 | [`05_comment_sentiment/`](05_comment_sentiment/) |
| 6 | 경쟁사 비교 분석 | ✅ 완료 | [`06_competitor_comparison/`](06_competitor_comparison/) |
| 7 | 버추얼 크리에이터 시장 분석 | ✅ 완료 | [`07_market_analysis/`](07_market_analysis/) |
| 8 | 동시시청자 시계열 | ✅ 완료 | [`08_live_viewership/`](08_live_viewership/) |
| 9 | DART 재무 분석 | ✅ 완료 | [`09_dart_financials/`](09_dart_financials/) |
| 10 | 호요버스 캐릭터 인기도 | ✅ 완료 | [`10_hoyoverse/`](10_hoyoverse/) |
| 11 | 팬 커머스 분석 | ✅ 완료 | [`11_fan_commerce/`](11_fan_commerce/) |
| 12 | 이벤트 임팩트 분석 | ✅ 완료 | [`12_event_impact/`](12_event_impact/) |

각 프로젝트 폴더는 `data/`(원천·정제), `sql/`(스키마·INSERT·분석쿼리·SQLite),
`charts/`(PNG 그래프), `site/`(HTML 대시보드), `README.md`/`REPORT.md`(설명·결과)로 구성됩니다.

결과만 모아 본 것은 저장소 루트의 [`결과물/`](../결과물/) 에 있습니다
(`scripts/build_deliverables.py` 가 생성 — `refresh.py` 가 분석 후 자동 호출).

## 한 파일 종합본 (HTML · PDF)

`결과물/` 은 프로젝트별로 나뉘어 있어 전체 상태를 한눈에 보려면 12개 폴더를 돌아야
합니다. `scripts/build_unified.py` 가 같은 소스에서 **한 페이지짜리 종합본**을 만듭니다.
차트 전량을 base64 로 인라인해 파일 하나로 자체완결하므로, 링크나 인터넷 없이 열립니다.

```bash
python scripts/build_unified.py          # 결과물/_build/ 에 HTML 3종 생성
chromium --headless=new --no-pdf-header-footer \
  --print-to-pdf=결과물/_build/StelLive-리포트.pdf \
  file://$PWD/결과물/_build/_print.html   # 인쇄용 → PDF (71쪽)
```

| 파일 | 용도 |
|---|---|
| `StelLive-리포트.html` | 단독 문서 — doctype·charset·viewport 포함, 모바일에서 그냥 열립니다 |
| `stellive-analytics.html` | 본문 fragment — 아티팩트로 퍼블리시할 때 |
| `_print.html` | PDF 렌더 소스 — `<details>` 를 펼치고 웹폰트를 걷어냅니다 |

⚠ PDF 페이지는 A4 가 아니라 **150×210mm** 로 잡았습니다. 휴대폰에서 A4 는 한 줄이 너무
길어 확대·좌우 스크롤을 하게 되는데, 좁은 페이지는 화면 폭에 맞춰도 글자가 읽힙니다.
인쇄용 HTML 은 웹폰트를 제거하고 로컬 한글 폰트로 확정합니다 — 렌더러가 네트워크를 못
쓰면 폰트를 기다리다 결국 폴백해서, 기다린 시간만 버리기 때문입니다 (`fonts-nanum` 필요).

빌드 산출물은 하나가 5.8MB 라 `.gitignore` 로 제외했습니다. 파생물이므로 필요할 때
다시 만들면 됩니다.

## 통합 대시보드

`../app/` 에 Next.js 대시보드가 있습니다. 각 프로젝트의 `site/data.json` 을 읽어
필터·드릴다운이 되는 하나의 사이트로 묶습니다. 07은 외부 리서치 기반이라 수집을
자동화할 수 없어 기존 정적 페이지로 링크만 겁니다. 다만 07은 06의 집계를 읽어
쓰므로, `daily` 에 포함시켜 **수집만 건너뛰고 재분석은 매일** 돌게 해두었습니다
(`refresh.py` 의 `NO_COLLECT`). 그러지 않으면 06이 갱신될 때마다 07이 낡습니다.

```bash
cd ../app && npm run build      # 정적 export (data.json 동기화 포함)
```

⚠ 빌드 결과물은 에셋을 `/_next/...` 절대경로로 참조합니다. **`file://` 로 열면 아무것도
로드되지 않으니** HTTP 로 서빙해야 합니다 (`.claude/launch.json` 의 `app-static` 참고).

## 자동화

```bash
python scripts/refresh.py --group daily     # 수집 → 분석 → 사이트 재생성
python scripts/refresh.py --group live --loop 10   # 포그라운드 상시 수집
powershell -File scripts/register_tasks.ps1        # dry-run
powershell -File scripts/register_tasks.ps1 -Apply # 작업 스케줄러 등록
```

| 그룹 | 주기 | 프로젝트 |
|---|---|---|
| `live` | 10분 | 08 (소급 수집 불가 — 놓치면 영구 공백) |
| `daily` | 일 1회 | 01·02·03·06·07·12 |
| `weekly` | 주 1회 | 04·05·10·11 |
| `monthly` | 월 1회 | 09 (DART 공시 주기가 분기·연간) |

## 이벤트 기억 (`12_event_impact/`)

대규모 합방·커버곡 발매·콘서트 같은 **사건**을 찾아 기억하고, 그 전후로 팔로워·구독자·
동시시청자가 어떻게 움직였는지 붙입니다. 신규 API 호출이 없습니다 — 01·02·03·08이 이미
모아 둔 데이터를 다시 읽을 뿐이라 `daily` 의 맨 뒤에서 돕니다.

합방은 치지직 VOD 의 **카테고리 동시성**(같은 날 같은 게임을 4명 이상)과 **제목 토큰
공유**(같은 날 4명 이상의 제목에 같은 단어)로 자동 감지합니다. 흔한 말이 걸리는 걸 막으려고
불용어 목록을 쓰는 대신, 토큰이 전체 방송일 중 몇 %에 등장하는지를 세서 **10%를 넘으면
고유명사가 아닌 것으로 봅니다** — 이 기준이 '오늘·같이·게임'을 자동으로 떨어뜨리고
'봉켓몬·갈틱폰·모라하지마'만 남깁니다.

```bash
python 12_event_impact/collect.py   # 이벤트 감지 + append-only 기억
python 12_event_impact/analyze.py   # 전후 변화 측정
```

⚠ 자동 감지는 **치지직 방송이 있는 이벤트만** 잡습니다. 콘서트·오프라인 행사·오리지널곡
발매는 흔적이 없어 `12_event_impact/data/events_manual.csv` 에 손으로 적어야 합니다.

⚠ **수익은 잴 수 없습니다.** 치지직 후원·구독 수익도 유튜브 광고 수익도 공개되지 않습니다.
대리 지표로 노출량(조회수·동시시청자 피크)만 냅니다. 회사 단위 수익성은 09가 연 단위로 답합니다.

## 지표 축적 (`data/history.csv`)

01·02·03·06 은 수집할 때마다 metrics CSV 를 통째로 덮어쓴다. 그래서 리포트는 항상
"지금"만 보여준다. `scripts/history.py` 가 각 프로젝트에 append-only `data/history.csv`
를 만들어 **(날짜 × 대상 × 지표)** 를 쌓는다. `refresh.py` 가 분석 후 자동 호출한다.

```bash
python scripts/history.py --backfill   # git 히스토리에서 과거분 소급 복원
python scripts/history.py --report     # 1일/7일/28일 변화율
```

행의 날짜는 스크립트를 돌린 날이 아니라 **데이터를 수집한 날**(`_meta.json`)이다.
같은 (날짜, 대상)이 이미 있으면 교체하므로 하루에 여러 번 돌아도 중복이 안 쌓인다.

⚠ 유튜브 구독자는 API 가 1,000 단위로 반올림해 준다. 13만 채널은 하루에 0 아니면
+1,000 으로만 움직여서 변화율이 계단처럼 튄다. 짧은 창(1일·7일)에서는 치지직
팔로워(정확한 정수)를 같이 보는 편이 낫다.

## 스냅샷 보존

```bash
python scripts/archive_snapshot.py --label 2026-08-03_original   # 갱신 전 보존
python scripts/compare_snapshot.py                                # 보존본과 증감 비교
```

수집 데이터는 덮어쓰면 복구할 수 없습니다. 갱신 전에 보존해두면 같은 지표를 두 시점에
걸쳐 비교할 수 있고, 그 자체가 성장률 분석이 됩니다.

## 공통 파이프라인 (`common/`)

| 모듈 | 역할 |
|------|------|
| `common/config.py` | 스텔라이브 로스터(검증된 채널 ID)·팔레트·유닛 설정 |
| `common/youtube.py` | YouTube Data API v3 얇은 클라이언트(채널·영상·검색·댓글, 페이지네이션·재시도) |
| `common/chzzk.py` | 치지직 비공식 API 클라이언트 (+ stale viewer 정규화) |
| `common/db.py` | pandas DataFrame ↔ SQLite / `.sql` 덤프 헬퍼 |
| `common/viz.py` | matplotlib 공통 스타일(한글 폰트 자동 선택·Montage 팔레트) |
| `common/montage.py` | Montage 디자인 토큰 (Wanted Lab Design System, MIT) |
| `common/site_css.py` | 대시보드 공통 스타일시트 (08 이후 프로젝트가 사용) |

## 실행 준비

```bash
pip install -r requirements.txt
```

키는 환경변수로만 씁니다. Windows 는 `setx` 로 한 번 등록하면 됩니다
(새로 여는 터미널부터 적용). 발급 절차는 [`SETUP_KEYS.md`](SETUP_KEYS.md) 참고.

```bash
setx YOUTUBE_API_KEY "발급받은_키"
setx DART_API_KEY "발급받은_키"
```

그런 다음 각 프로젝트 폴더의 README 순서대로 `collect.py → analyze.py → build_site.py`를 실행하면 됩니다.

## 분석 대상

**수집은 11명**(창립자 강지 + 탤런트 10명), **분석 산출물(리포트·차트)은 탤런트 10명**입니다.
강지는 운영자라 콘텐츠·규모 성격이 달라 비교 지표를 왜곡하므로 표시에서 제외하되,
데이터는 계속 수집합니다 — 특히 08 동시시청자는 소급이 불가능해서 기준이 바뀌어도
복구할 수 있어야 합니다 (`common/config.py` 의 `EXCLUDE_FOUNDER_FROM_ANALYSIS`).

탤런트 — EVERYS(아야츠노 유니·사키하네 후야),
UNIVERSE(시라유키 히나·네네코 마시로·아카네 리제·아라하시 타비),
cliché(텐코 시부키·아오쿠모 린·하나코 나나·유즈하 리코).

> 데이터는 수집 시점의 공개 스냅샷이며, 지표는 시간에 따라 변합니다.
