# 05 · 댓글 여론·감성

**질문** — 팬 댓글은 무엇에 반응하는가. 긍정/부정 비율이 멤버를 가르는가, 아니면 주제가 가르는가.

- 데이터: YouTube Data API — 멤버별 조회수 상위 영상의 추천순 상위 댓글
- 라벨: 규칙 기반 키워드가 아니라 **문맥을 읽어 직접 분류**(반어법·팬덤 용어·자조적 유머 고려).
  감성 `positive / neutral / negative`, 토픽 7종(목소리·노래 / 성격·개그 / 비주얼·디자인 / 방송내용·게임 / 멤버 케미 / 성장·추억 / 기타)
- 갱신: weekly(수집). 라벨은 표본이 바뀔 때 다시 단다

## 실행

```bash
export YOUTUBE_API_KEY=...
python collect.py --videos-per-member 4 --comments-per-video 40   # → comments_raw.csv, comments_sample.csv
# comments_sample.csv 를 읽고 sentiment·topic 을 달아 comments_labeled.csv 로 (저장소에 라벨링 결과 포함)
python analyze.py
python build_site.py
```

## 방법

1. 멤버별 조회수 상위 영상 4개 → 영상당 추천순 상위 댓글 최대 40개. 4자 미만 초단문(이모지 등) 제외.
2. **멤버당 좋아요 상위 30개**를 표본으로 라벨링 — 멤버 간 비교가 같은 건수·같은 기준이 되게.
3. 감성 점수 = 긍정 비율 − 부정 비율. 표본 영상이 3개 미만인 멤버(`MIN_SAMPLE_VIDEOS`, 데뷔 직후)는 표본 구성이
   달라 순위·전체 비율에서 빼고 리포트에 따로 적는다.

## 산출물

| 경로 | 내용 |
|---|---|
| `data/comments_raw.csv` · `comments_sample.csv` · `comments_labeled.csv` | 원천 · 표본(라벨 전) · 라벨링 결과 |
| `data/sentiment_metrics.csv` · `target_videos.csv` | 멤버별 집계 · 표본 영상 |
| `sql/` · `charts/`(4종) · `site/` · `REPORT.md` | 공통 산출물 |

## 읽는 법 · 한계

- 표본은 대부분 긍정이고 모든 멤버에서 긍정이 부정보다 많다 — **긍정/부정 비율은 멤버를 가르지 못한다.**
  신호는 주제에 있다: 성격·개그와 방송내용·게임이 가장 많고, 목소리·노래보다 우위다(건수는 `REPORT.md`).
- 부정 댓글은 대부분 영상 소재(응원 야구팀 등)를 향하거나 애정 어린 우려다. 12 가 이를 정규식으로 센다.
- 추천순 알고리즘은 재치 있고 공감받는 댓글을 먼저 보여 주므로 무작위 표본보다 긍정 쪽으로 치우친다.
- 멤버별 인기 영상 표본이라 이벤트별(신의상·합방) 여론 비교는 이 데이터로 할 수 없다.
