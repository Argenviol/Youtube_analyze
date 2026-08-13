# 프로젝트 1 · StelLive 멤버별 유튜브 채널 성과 분석

스텔라이브(StelLive) 멤버 **11명**(창립자 강지 포함, 탤런트 10명)의 YouTube 채널을
Data API로 수집해 **구독자·조회수·업로드 빈도·참여율·도달 효율**을 비교 분석합니다.
이후 커버곡/경쟁사 분석에 그대로 재사용할 수 있는 **수집 → 정제 → SQL → 시각화 → 사이트**
파이프라인의 기준 프로젝트입니다.

## 실행 방법

```bash
pip install -r ../requirements.txt
export YOUTUBE_API_KEY="발급받은_키"          # 코드에 키를 넣지 않습니다

python collect.py --recent 50                  # 1) 수집  -> data/
python analyze.py                              # 2) 분석  -> sql/, charts/, REPORT.md, site/data.json
python build_site.py                           # 3) 사이트 -> site/index.html
```

## 산출물 구조

| 경로 | 내용 |
|------|------|
| `data/channels.csv` · `channels.json` | 채널 단위 원천 지표(구독자·총조회수·영상수·개설일 등) |
| `data/videos.csv` | 채널당 최근 50개 영상 지표(조회·좋아요·댓글·길이) |
| `data/channel_metrics.csv` | 파생지표(평균조회수·참여율·업로드빈도·도달효율 등) |
| `sql/schema.sql` | `channels` / `videos` / `channel_metrics` 테이블 스키마 |
| `sql/*.sql` | 각 테이블 INSERT 문 |
| `sql/analysis_queries.sql` | 랭킹·유닛요약·참여율 등 분석 쿼리 모음 |
| `sql/query_results.md` | 위 쿼리 **실행 결과**(표) |
| `sql/stellive.db` | 바로 질의 가능한 SQLite DB |
| `charts/*.png` | 차트 8종(구독자·조회수·참여율·업로드주기·도달효율·산점도·유닛비교·시간대 히트맵) |
| `site/index.html` | 자체완결 인터랙티브 대시보드(파일 하나로 열람) |
| `REPORT.md` | 핵심 요약 + 상관관계 해설 |

## 지표 정의

- **도달 효율(reach ratio)** = 최근 영상 평균 조회수 ÷ 구독자. 구독자 대비 실제 도달을 봄. 100%↑면 구독자보다 많은 조회수.
- **참여율(engagement rate)** = (좋아요 + 댓글) ÷ 조회수, 최근 영상 평균.
- **업로드 빈도** = 최근 영상들의 게시 간격으로 환산한 주간 업로드 수.
- **쇼츠 비중** = 최근 영상 중 60초 이하 비율.

## 주요 결과 (수집 시점 스냅샷)

- 구독자 1위(탤런트): **아야츠노 유니 357K**, 이어 아카네 리제·시라유키 히나.
- 도달 효율 1위: **유즈하 리코(약 123%)** — 구독자 대비 조회수가 가장 높음.
- 참여율 1위: **네네코 마시로(약 5.0%)**.
- 구독자↔평균조회수 상관 r≈0.47(약한 양), **도달효율↔구독자 r≈-0.39** — 구독자가 적은 채널일수록 구독자 대비 도달이 높은 경향.

> 창립자 강지는 콘텐츠 성격(합방·대형 기획)이 달라 탤런트 랭킹/상관 계산에서는 분리했습니다.
> `common/config.py`의 `INCLUDE_FOUNDER=False`로 완전히 제외할 수 있습니다.

## 대상 채널

`common/config.py`의 `MEMBERS`에 채널 ID가 하드코딩되어 있으며, 모두 YouTube API로
검증한 값입니다(핸들 추측 아님).
