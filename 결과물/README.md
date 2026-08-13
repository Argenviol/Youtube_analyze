# 결과물

StelLive 데이터 분석 포트폴리오 **11개 프로젝트의 결과물만** 모았습니다.
코드·원천 데이터·SQLite 는 각 프로젝트 폴더(`youtube_analyze_all/`)에 그대로 있고,
여기에는 읽을 것만 있습니다 — 리포트(`REPORT.md`)·차트(`charts/`)·대시보드(`index.html`).

## 프로젝트

| # | 프로젝트 | 핵심 발견 | 리포트 | 차트 | 대시보드 |
|---|----------|-----------|--------|------|----------|
| 1 | 멤버별 유튜브 채널 성과 | 구독자 규모와 도달 효율은 반대로 간다 — 참여율↔구독자 상관 -0.72 | [REPORT.md](01_member_channel_performance/REPORT.md) | [8종](01_member_channel_performance/charts/) | [index.html](01_member_channel_performance/index.html) |
| 2 | 커버곡 성과 랭킹 | 커버 362곡 집계 · 총 조회수 1위 아카네 리제 102.4M(40곡) | [REPORT.md](02_cover_song_ranking/REPORT.md) | [7종](02_cover_song_ranking/charts/) | [index.html](02_cover_song_ranking/index.html) |
| 3 | 치지직 방송 패턴 | 다시보기 3,243건 · 방송이 가장 많이 시작되는 시간대는 새벽 1시(KST) | [REPORT.md](03_chzzk_stream_pattern/REPORT.md) | [8종](03_chzzk_stream_pattern/charts/) | [index.html](03_chzzk_stream_pattern/index.html) |
| 4 | 키리누키(2차창작) 생태계 | 팬 클립 257개·팬채널 66개 · 생태계 표본 합계 조회수 20.4M | [REPORT.md](04_kirinuki_ecosystem/REPORT.md) | [6종](04_kirinuki_ecosystem/charts/) | [index.html](04_kirinuki_ecosystem/index.html) |
| 5 | 댓글 여론/감성 | 상위 댓글 330개 직접 분류 · 긍정 80% · 최다 토픽은 성격·개그 | [REPORT.md](05_comment_sentiment/REPORT.md) | [4종](05_comment_sentiment/charts/) | [index.html](05_comment_sentiment/index.html) |
| 6 | 경쟁사 비교 | StelLive 도달 효율 57% — 홀로라이브 13%, 이세돌 23%보다 높다 | [REPORT.md](06_competitor_comparison/REPORT.md) | [7종](06_competitor_comparison/charts/) | [index.html](06_competitor_comparison/index.html) |
| 7 | 버추얼 크리에이터 시장 | VTuber 시장 2026년 약 31.3억 달러 · 치지직 MAU 242만(YoY +17%) | [REPORT.md](07_market_analysis/REPORT.md) | [5종](07_market_analysis/charts/) | [index.html](07_market_analysis/index.html) |
| 8 | 동시시청자 시계열 | 소급 불가능한 유일한 지표 — 10분 간격 자체 수집으로만 얻어진다 | [REPORT.md](08_live_viewership/REPORT.md) | [4종](08_live_viewership/charts/) | [index.html](08_live_viewership/index.html) |
| 9 | DART 재무 분석 | 핵심 발견은 부재 — 스텔라이브 운영법인이 DART 기업코드 마스터에 없다 | [REPORT.md](09_dart_financials/REPORT.md) | [5종](09_dart_financials/charts/) | [index.html](09_dart_financials/index.html) |
| 10 | 호요버스 캐릭터 인기도 | 회사가 미는 캐릭터(길가메시)와 유저가 반응하는 캐릭터(반디)는 다르다 | [REPORT.md](10_hoyoverse/REPORT.md) | [8종](10_hoyoverse/charts/) | [index.html](10_hoyoverse/index.html) |
| 11 | 팬 커머스 | 팬딩 크리에이터 111명·67티어 · 멤버십 가격대 1,000원~550,000원 | [REPORT.md](11_fan_commerce/REPORT.md) | [5종](11_fan_commerce/charts/) | [index.html](11_fan_commerce/index.html) |

프로젝트 11개 · 리포트 11건 · 차트 67종 · 대시보드 11건.

## 대시보드 여는 법

`index.html` 은 CSS·데이터를 안에 품은 자체완결 파일이라 그냥 브라우저로 열면 됩니다
(GitHub 웹에서는 HTML 이 렌더링되지 않으니 내려받아서 열어야 합니다).

> 이 폴더는 `youtube_analyze_all/scripts/build_deliverables.py` 가 생성합니다.
> 직접 고치면 다음 실행에서 덮어써집니다 — 원본을 고치고 스크립트를 다시 도세요.
