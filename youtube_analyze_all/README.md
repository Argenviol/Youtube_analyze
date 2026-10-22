# 분석 파이프라인

스텔라이브 팬덤 지표 12개 프로젝트의 수집·분석 코드입니다. 포트폴리오 소개는 루트
[`README.md`](../README.md), 운영(쿼터·실패 조치·다음 할 일)은 [`HANDOVER.md`](../HANDOVER.md)에 있습니다.

## 프로젝트

| # | 폴더 | 내용 | 갱신 |
|---|---|---|---|
| 01 | [`01_member_channel_performance/`](01_member_channel_performance/) | 멤버별 유튜브 채널 성과 (규모·참여율·도달 효율) | daily |
| 02 | [`02_cover_song_ranking/`](02_cover_song_ranking/) | 커버곡 성과 — 곡 단위, MV + Topic 음원 판 합산 | daily |
| 03 | [`03_chzzk_stream_pattern/`](03_chzzk_stream_pattern/) | 치지직 방송 패턴 (시간대·길이·카테고리) | daily |
| 04 | [`04_kirinuki_ecosystem/`](04_kirinuki_ecosystem/) | 키리누키(2차창작) 생태계 | weekly |
| 05 | [`05_comment_sentiment/`](05_comment_sentiment/) | 댓글 여론·감성 (직접 라벨링) | weekly |
| 06 | [`06_competitor_comparison/`](06_competitor_comparison/) | 경쟁사 비교 — 데뷔 코호트 매칭 | daily |
| 07 | [`07_market_analysis/`](07_market_analysis/) | 버추얼 크리에이터 시장 (외부 리서치, 재분석만) | daily |
| 08 | [`08_live_viewership/`](08_live_viewership/) | 동시시청자 시계열 — 소급 수집 불가 | live(10분) |
| 09 | [`09_dart_financials/`](09_dart_financials/) | DART 재무 (플랫폼 vs IP 회사) | monthly |
| 10 | [`10_hoyoverse/`](10_hoyoverse/) | 게임 캐릭터 인기도 (호요버스 4 + 블루 아카이브) | weekly |
| 11 | [`11_fan_commerce/`](11_fan_commerce/) | 팬 커머스 (크라우드펀딩·구독 가격·매진) | weekly |
| 12 | [`12_event_impact/`](12_event_impact/) | 이벤트 임팩트 — 01·02·03·08 데이터 재사용 | daily |

프로젝트 폴더는 같은 모양입니다.

```
NN_project/
  collect.py   analyze.py   build_site.py      수집 → 분석 → 대시보드
  data/        원천·정제 CSV, _meta.json(수집 시각·방법 변경 이력), history.csv(일자별 축적)
  sql/         스키마·SQLite
  charts/      PNG
  site/        HTML 대시보드 + data.json(통합 앱이 읽음)
  README.md    방법 · REPORT.md 결과(매 실행 재생성)
```

## 실행

```bash
pip install -r requirements.txt
setx YOUTUBE_API_KEY "..."      # Windows. 발급은 SETUP_KEYS.md. 키는 환경변수로만 쓴다
setx DART_API_KEY "..."

python scripts/refresh.py --group daily          # 그룹 단위: 수집 → 분석 → 축적 → 결과물/
python 01_member_channel_performance/collect.py  # 프로젝트 하나만: collect → analyze → build_site
python scripts/refresh.py --group daily --skip-collect   # 키 없이 분석·사이트만
```

| 그룹 | 주기 | 프로젝트 | 비고 |
|---|---|---|---|
| `live` | 10분 | 08 | 놓치면 영구 공백. Windows 는 `수집시작.cmd` 를 열어 두면 됨 |
| `daily` | 일 1회 | 01·02·03·06·07·12 | 07 은 수집 없이 재분석만(`NO_COLLECT`) |
| `weekly` | 주 1회 | 04·05·10·11 | YouTube 검색 쿼터를 가장 많이 씀 |
| `monthly` | 월 1회 | 09 | DART 공시 주기가 분기·연간 |

GitHub Actions(`.github/workflows/`)가 같은 그룹을 자동으로 돌립니다. 로컬 작업 스케줄러는
`scripts/register_tasks.ps1`(`-Apply` 없이 dry-run). `refresh.py` 는 프로젝트별로 실패를 격리합니다.

### 종합 리포트 (HTML · PDF)

```bash
python scripts/build_unified.py            # 결과물/_build/ — 스텔라이브·게임 전체판
python scripts/build_unified.py --digest   # 요약판: 계산된 숫자·표·차트만
```

리포트는 소재별로 두 권(스텔라이브 01~09·11·12 / 게임 10)입니다. 차트와 서체(Noto Sans KR)를
파일 안에 넣어 인터넷 없이 열리고, 같은 그림은 문서 전체에서 한 번만 싣습니다. PDF 로 뽑는 법과
페이지 규격은 [`../결과물/리포트/README.md`](../결과물/리포트/README.md). `_build/` 는 파생물이라
git 에 올리지 않습니다.

### 통합 대시보드

`../app/`(Next.js)이 각 프로젝트의 `site/data.json` 을 읽어 필터·드릴다운이 되는 한 사이트로
묶습니다. `npm run build` 가 `out/` 에 정적 export 를 만들며, 에셋을 `/_next/...` 절대경로로 참조하므로
`file://` 이 아니라 HTTP 로 서빙해야 합니다(`.claude/launch.json` 의 `app-static`).

## 공통 모듈 (`common/`)

| 모듈 | 역할 |
|---|---|
| `config.py` | 로스터(채널 ID·치지직 ID·데뷔일·생일)·팔레트·분석 제외 규칙 |
| `youtube.py` | YouTube Data API 클라이언트 — 페이지네이션·재시도·**쿼터 장부와 자체 예산** |
| `chzzk.py` | 치지직 비공식 API — 꺼진 방송의 stale 시청자 수 정규화, VOD 시작 시각(게시 − 길이) |
| `songs.py` | 커버곡 MV ↔ Topic 음원 판 짝짓기 |
| `summary.py` | 리포트 요약 문장(분포·"상위 3명이 겹치는가") — 멤버 이름 순위를 쓰지 않는다 |
| `db.py` · `viz.py` · `montage.py` · `site_css.py` | SQLite 헬퍼 · matplotlib 스타일(한글 폰트) · Montage 토큰 · 대시보드 CSS |
| `fonts/` | Noto Sans KR 가변 서체(OFL) — 종합 리포트에 내장 |

## 데이터가 쌓이는 방식

- **지표 축적** — 01·02·03·06 은 실행마다 metrics 를 덮어쓰므로 `scripts/history.py` 가
  `data/history.csv` 에 (수집일 × 대상 × 지표)를 append-only 로 쌓습니다(`refresh.py` 가 자동 호출,
  `--backfill` 로 git 이력에서 소급, `--report` 로 1·7·28일 변화율). 유튜브 구독자는 1,000 단위
  반올림이라 짧은 창에서는 치지직 팔로워를 같이 봅니다.
- **이벤트 기억(12)** — 치지직 VOD 의 카테고리 동시성·제목 토큰으로 합방을 찾고 **연속 2일 이상**만
  이벤트로 인정합니다. 신의상은 제목 + 평소 조회수 2배 이상, 생일은 공식 프로필 날짜. 처음 감지한
  날짜는 `data/events_seen.csv` 에 남고, 콘서트·오리지널곡·3D 데뷔처럼 방송 흔적이 없는 이벤트는
  `data/events_manual.csv` 에 손으로 적습니다. 넓은 창의 신호는 `data/event_candidates.csv`
  검토 대기열로만 냅니다.
- **스냅샷 보존** — `scripts/archive_snapshot.py --label <이름>` 으로 갱신 전 상태를 `_archive/` 에
  두고 `scripts/compare_snapshot.py` 로 증감을 봅니다.
- **수익은 잴 수 없습니다.** 치지직 후원·유튜브 광고 수익은 공개되지 않아 노출량(조회수·동시시청자)만
  대리 지표로 내고, 회사 단위 수익성은 09 가 동종업계 공시로 답합니다.

## 분석 대상

수집은 15명(창립자 강지 + 탤런트 14명), 리포트·차트는 **탤런트 중 표본이 기준을 넘는 멤버**입니다.
강지는 운영자라 비교 지표를 왜곡하므로 표시에서 빼되 데이터는 계속 모읍니다
(`config.EXCLUDE_FOUNDER_FROM_ANALYSIS`).

| 유닛 | 멤버 | 비고 |
|---|---|---|
| EVERYS | 아야츠노 유니 · 사키하네 후야 | |
| UNIVERSE | 시라유키 히나 · 네네코 마시로 · 아카네 리제 · 아라하시 타비 | |
| cliché | 텐코 시부키 · 아오쿠모 린 · 하나코 나나 · 유즈하 리코 | |
| ABYSS | 시즈키 토아 · 코가네 랑 · 하나요 히요리 · 토키노 메리 | 2026-10-17·18 데뷔. 영상·방송이 기준(01 최근 영상 5개, 03 방송 10회, 05 영상 3개)을 넘으면 자동으로 들어옴 |

> 데이터는 수집 시점의 공개 스냅샷이며, 지표는 시간에 따라 변합니다.
