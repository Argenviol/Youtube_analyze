# 결과물

12개 프로젝트의 **결과만** 모은 폴더입니다. 코드는 `youtube_analyze_all/`, 포트폴리오 소개는
루트 `README.md` 에 있습니다. 결론 문장에는 멤버 이름을 붙인 순위를 쓰지 않습니다 — 멤버별 수치는
각 리포트의 표·차트에 있습니다.

## 바로 보기

| 무엇을 | 어디서 |
|---|---|
| **리포트 PDF 4종** — 스텔라이브·게임 각각 전체판·요약판 (휴대폰에 맞춘 150×210mm) | [`리포트/`](리포트/) |
| 프로젝트별 리포트 — 결론이 맨 위, 근거·차트·상세분석이 아래 | 아래 표의 "최신 리포트" |
| 차트 PNG · 자체완결 대시보드 | 아래 표의 "차트"·"대시보드" |
| 지난 날짜 리포트 | [`_이전/`](_이전/) — 그날 기록 그대로, 지우지 않음 |

## 프로젝트

| # | 프로젝트 | 최신 리포트 | 기준일 | 축적 | 차트 | 대시보드 |
|---|---|---|---|---|---|---|
| 1 | 멤버별 유튜브 채널 성과 | [REPORT1 - 20261024.md](01_member_channel_performance/REPORT1%20-%2020261024.md) | 2026-10-24 | 63개 | [8종](01_member_channel_performance/charts/) | [index.html](01_member_channel_performance/index.html) |
| 2 | 커버곡 성과 랭킹 | [REPORT2 - 20261024.md](02_cover_song_ranking/REPORT2%20-%2020261024.md) | 2026-10-24 | 63개 | [7종](02_cover_song_ranking/charts/) | [index.html](02_cover_song_ranking/index.html) |
| 3 | 치지직 방송 패턴 | [REPORT3 - 20261024.md](03_chzzk_stream_pattern/REPORT3%20-%2020261024.md) | 2026-10-24 | 64개 | [8종](03_chzzk_stream_pattern/charts/) | [index.html](03_chzzk_stream_pattern/index.html) |
| 4 | 키리누키(2차창작) 생태계 | [REPORT.md](04_kirinuki_ecosystem/REPORT.md) | 2026-10-24 | — | [6종](04_kirinuki_ecosystem/charts/) | [index.html](04_kirinuki_ecosystem/index.html) |
| 5 | 댓글 여론/감성 | [REPORT.md](05_comment_sentiment/REPORT.md) | 2026-10-24 | — | [4종](05_comment_sentiment/charts/) | [index.html](05_comment_sentiment/index.html) |
| 6 | 경쟁사 비교 | [REPORT6 - 20261024.md](06_competitor_comparison/REPORT6%20-%2020261024.md) | 2026-10-24 | 64개 | [6종](06_competitor_comparison/charts/) | [index.html](06_competitor_comparison/index.html) |
| 7 | 버추얼 크리에이터 시장 | [REPORT.md](07_market_analysis/REPORT.md) | 2026-10-24 | — | [5종](07_market_analysis/charts/) | [index.html](07_market_analysis/index.html) |
| 8 | 동시시청자 시계열 | [REPORT8 - 20261024.md](08_live_viewership/REPORT8%20-%2020261024.md) | 2026-10-24 | 35개 | [4종](08_live_viewership/charts/) | [index.html](08_live_viewership/index.html) |
| 9 | DART 재무 분석 | [REPORT.md](09_dart_financials/REPORT.md) | 2026-10-04 | — | [5종](09_dart_financials/charts/) | [index.html](09_dart_financials/index.html) |
| 10 | 게임 캐릭터 인기도 | [REPORT.md](10_hoyoverse/REPORT.md) | 2026-10-24 | — | [8종](10_hoyoverse/charts/) | [index.html](10_hoyoverse/index.html) |
| 11 | 팬 커머스 | [REPORT.md](11_fan_commerce/REPORT.md) | 2026-10-24 | — | [5종](11_fan_commerce/charts/) | [index.html](11_fan_commerce/index.html) |
| 12 | 이벤트 임팩트 | [REPORT12 - 20261024.md](12_event_impact/REPORT12%20-%2020261024.md) | 2026-10-24 | 53개 | [4종](12_event_impact/charts/) | [index.html](12_event_impact/index.html) |

프로젝트 12개 · 차트 70종 · 대시보드 12건.

## 파일 규칙

- **축적**(6개 프로젝트, 수집마다 숫자가 바뀜) — `REPORT1 - 20260818.md` 처럼 날짜를 붙인 최신본 하나만
  프로젝트 폴더에 두고, 지난 날짜는 `_이전/<프로젝트>/` 로 옮깁니다. "축적" 열은 지금까지 쌓인 날짜 수입니다.
- 그 밖의 프로젝트는 `REPORT.md` 하나이고 "기준일"이 마지막 수집일입니다.
- 차트는 **최신 실행 기준 한 벌만** 둡니다(날짜별로 쌓으면 70종 × 날짜 수). 지난 날짜 리포트를 열면 본문
  숫자와 차트 시점이 다를 수 있고, 리포트의 차트 절에 어느 시점 기준인지 적혀 있습니다.
- `index.html` 은 CSS·데이터를 안에 품은 자체완결 파일이라 브라우저로 그냥 열면 됩니다. GitHub 웹에서는
  HTML 이 렌더링되지 않으니 내려받아서 엽니다.

> 이 폴더는 daily·weekly 수집이 끝날 때마다 `youtube_analyze_all/scripts/build_deliverables.py` 가 다시 만듭니다.
> 직접 고치면 다음 실행에서 덮어써집니다 — 원본(각 프로젝트 `REPORT.md`·이 스크립트)을 고치세요.
