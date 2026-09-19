# 프로젝트 2 · StelLive 커버곡 성과 랭킹 분석

스텔라이브 멤버 채널의 **커버곡 영상**을 모아 조회수·좋아요·참여율 기준으로 랭킹·비교합니다.
프로젝트 1의 수집→정제→SQL→시각화→사이트 파이프라인을 그대로 재사용합니다.

## 실행 방법

```bash
pip install -r ../requirements.txt
export YOUTUBE_API_KEY="발급받은_키"

python collect.py --per-query 45      # 채널별 cover/커버/歌ってみた 검색 -> data/covers.csv
python analyze.py                     # SQL/차트/리포트/사이트 데이터
python build_site.py                  # site/index.html
```

## 커버곡 식별 방법

각 멤버 채널에 대해 `cover`, `커버`, `歌ってみた` 3개 쿼리로 채널 내 검색을 수행하고,
제목에 커버 토큰(`cover|커버|歌ってみた|불러봤/본`)이 있는 영상만 커버로 확정합니다.
검색 노이즈를 제목 필터로 걸러 정밀도를 높였습니다. 콜라보(`x`) 곡은 **소유 채널 기준**으로
집계해 이중 계산을 피합니다.

## 산출물

| 경로 | 내용 |
|------|------|
| `data/covers.csv` | 커버곡별 지표(조회·좋아요·댓글·게시일·콜라보 여부) |
| `data/cover_metrics.csv` | 멤버별 집계(곡수·총조회·평균·최고·참여율·콜라보비중) |
| `sql/schema.sql` · `*.sql` | `covers` / `cover_metrics` 스키마·INSERT |
| `sql/analysis_queries.sql` · `query_results.md` | 분석 쿼리 + 실행 결과 |
| `sql/covers.db` | SQLite DB |
| `charts/*.png` | 차트 7종(TOP15·커버수·총조회수·평균조회수·참여율·산점도·분포) |
| `site/index.html` | 인터랙티브 대시보드 |
| `REPORT.md` | 핵심 요약 |

## 주요 결과 (수집 시점 스냅샷)

- **커버 총 조회수 1위**: 아카네 리제 — 약 98.0M(37곡). 곡당 평균 조회수도 2.65M로 최상위권.
- **최다 업로드**: 아오쿠모 린 — 48곡(총 77.6M).
- **역대 최고 조회 커버**: 강지 「내가 죽으려고 생각한 것은(한국어 커버)」 약 14.0M.
- 커버 수(다작)와 곡당 평균 조회수(파괴력)는 별개 축 — 산점도에서 아카네 리제는 두 축 모두 상위,
  아오쿠모 린은 다작형, 강지는 소수정예 고조회형으로 분화됩니다.

## 조회수를 세는 법 — 한 곡은 한 곡으로 (2026-09-19)

한 곡이 본편 MV·[4K]·3D 라이브·쇼츠·티저로 여러 번 올라온다(2026-09 기준 12곡). 여기에
유튜브가 음원 유통사 배급분으로 자동 생성하는 **"<이름> - Topic" 채널**의 음원 판이 따로 있다
— 네네코 마시로 '봄꿈' MV(멤버 채널) ↔ Neneko Mashiro - Topic 'Springdream'. 멤버 채널만
세면 이 조회수가 통째로 빠진다.

| 지표 | 무엇을 더한 값인가 |
|---|---|
| `cover_count` | 커버 **영상** 수 (history.csv 연속성 때문에 이름을 유지) |
| `song_count` | 여러 판을 한 곡으로 묶은 **곡** 수 (`common/songs.song_key`) |
| `total_views` | 멤버 채널 커버 영상 조회수 합 — 여러 판이면 전부 더한다 |
| `topic_views` | 같은 멤버·발매일 ±3일로 짝지은 Topic 음원 판 조회수 합 |
| `total_views_incl_topic` | 위 둘의 합 — "MV + 음원" 총계 |

Topic 트랙 제목은 유통 메타데이터라 영문인 경우가 많아 제목으로는 못 잇는다. 그래서 날짜로
잇고, 후보가 둘 이상이면 붙이지 않는다(`topic_pairs.csv` 의 `pair_reason`). 사람이 확정한
짝은 `data/topic_pairs_manual.csv`(`topic_video_id,member_video_id`)가 우선한다.
Topic 채널 ID 는 `search.list` 로 한 번 찾아 `data/topic_channels.json` 에 캐시한다.

커버로 짝지어지지 않은 Topic 트랙은 대부분 오리지널곡 음원이고, 프로젝트 12 의 오리지널곡
효과에서 MV 조회수에 더해진다.
