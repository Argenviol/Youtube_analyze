# 01 · 멤버별 유튜브 채널 성과

**질문** — 멤버별 유튜브 채널은 규모·참여·도달 중 무엇이 강한가. 구독자가 많은 채널과 팬이 반응하는
채널은 같은 채널인가.

- 데이터: YouTube Data API v3 — 채널 지표 + 채널당 최근 50개 영상
- 대상: 탤런트 중 최근 영상 5개 이상·구독자 공개 채널(`MIN_RECENT_VIDEOS`). 데뷔 직후 멤버는 영상이 쌓이면 자동 편입
- 갱신: daily. 다른 프로젝트가 재사용하는 **파이프라인 기준 프로젝트**(02·06·12 가 `videos.csv`·`channel_metrics.csv` 를 읽음)

## 실행

```bash
export YOUTUBE_API_KEY=...
python collect.py --recent 50     # → data/
python analyze.py                 # → sql/ charts/ REPORT.md site/data.json
python build_site.py              # → site/index.html
```

## 지표 정의

| 지표 | 정의 |
|---|---|
| 도달 효율 (reach ratio) | 최근 영상 평균 조회수 ÷ 구독자 — 100% 넘으면 구독자보다 많은 사람이 본다 |
| 참여율 (engagement rate) | (좋아요 + 댓글) ÷ 조회수, 최근 영상 평균 |
| 업로드 빈도 | 최근 영상의 게시 간격으로 환산한 주당 업로드 수 |
| 쇼츠 비중 | 최근 영상 중 60초 이하 비율 |

창립자 강지는 콘텐츠 성격(합방·대형 기획)이 달라 집계·상관에서 분리한다(`common/config.py`).

## 산출물

| 경로 | 내용 |
|---|---|
| `data/channels.csv` · `videos.csv` · `channel_metrics.csv` | 채널 원천 · 영상 원천 · 파생 지표 |
| `data/history.csv` | 날짜별 축적(`scripts/history.py`) |
| `sql/` | 스키마·INSERT·분석 쿼리·실행 결과·`stellive.db` |
| `charts/` | 8종 — 구독자·조회수·참여율·업로드 주기·도달 효율·산점도·유닛 비교·시간대 히트맵 |
| `site/index.html` · `data.json` | 대시보드 · 통합 앱 입력 |
| `REPORT.md` | 핵심 요약(매 실행 재생성) |

## 읽는 법 · 한계

- 구독자 상위와 참여율·도달 효율 상위는 대체로 다른 멤버다. 규모가 클수록 구독자 대비 조회수와 참여율은
  낮다 — 겹치는 인원·상관계수는 `REPORT.md` 에 매일 갱신된다. 요약에는 멤버 이름을 붙인 순위를 쓰지 않는다.
- 유튜브 구독자는 API 가 1,000 단위로 반올림해 준다. 짧은 창의 변화율은 계단처럼 튄다.
- 채널 ID 는 `common/config.py` 의 `MEMBERS` 에 있고 전부 API 로 검증한 값이다(핸들 추측 아님).
