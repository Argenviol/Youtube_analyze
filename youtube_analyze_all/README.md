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

각 프로젝트 폴더는 `data/`(원천·정제), `sql/`(스키마·INSERT·분석쿼리·SQLite),
`charts/`(PNG 그래프), `site/`(HTML 대시보드), `README.md`/`REPORT.md`(설명·결과)로 구성됩니다.

## 통합 대시보드

`../app/` 에 Next.js 대시보드가 있습니다. 각 프로젝트의 `site/data.json` 을 읽어
필터·드릴다운이 되는 하나의 사이트로 묶습니다. 07은 외부 리서치 기반이라 자동 갱신이
불가능해 기존 정적 페이지로 링크만 겁니다.

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
| `daily` | 일 1회 | 01·02·03·06 |
| `weekly` | 주 1회 | 04·05·10·11 |
| `monthly` | 월 1회 | 09 (DART 공시 주기가 분기·연간) |

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

## 분석 대상 (11명)

창립자 **강지** + 탤런트 10명 — EVERYS(아야츠노 유니·사키하네 후야),
UNIVERSE(시라유키 히나·네네코 마시로·아카네 리제·아라하시 타비),
cliché(텐코 시부키·아오쿠모 린·하나코 나나·유즈하 리코).

> 데이터는 수집 시점의 공개 스냅샷이며, 지표는 시간에 따라 변합니다.
