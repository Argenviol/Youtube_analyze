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
