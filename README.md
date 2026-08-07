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

각 프로젝트 폴더는 `data/`(원천·정제), `sql/`(스키마·INSERT·분석쿼리·SQLite),
`charts/`(PNG 그래프), `site/`(HTML 대시보드), `README.md`/`REPORT.md`(설명·결과)로 구성됩니다.

## 공통 파이프라인 (`common/`)

| 모듈 | 역할 |
|------|------|
| `common/config.py` | 스텔라이브 로스터(검증된 채널 ID)·팔레트·유닛 설정 |
| `common/youtube.py` | YouTube Data API v3 얇은 클라이언트(채널·영상·검색·댓글, 페이지네이션·재시도) |
| `common/db.py` | pandas DataFrame ↔ SQLite / `.sql` 덤프 헬퍼 |
| `common/viz.py` | matplotlib 공통 스타일(한글 폰트·검증 팔레트) |

## 실행 준비

```bash
pip install -r requirements.txt
export YOUTUBE_API_KEY="발급받은_키"     # 키는 환경변수로만 사용, 저장소에 커밋하지 않음
```

그런 다음 각 프로젝트 폴더의 README 순서대로 `collect.py → analyze.py → build_site.py`를 실행하면 됩니다.

## 분석 대상 (11명)

창립자 **강지** + 탤런트 10명 — EVERYS(아야츠노 유니·사키하네 후야),
UNIVERSE(시라유키 히나·네네코 마시로·아카네 리제·아라하시 타비),
cliché(텐코 시부키·아오쿠모 린·하나코 나나·유즈하 리코).

> 데이터는 수집 시점의 공개 스냅샷이며, 지표는 시간에 따라 변합니다.
