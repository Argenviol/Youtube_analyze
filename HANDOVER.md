# 인수인계서

> 작업을 이어받는 사람(또는 다음 세션)을 위한 운영 문서입니다. 포트폴리오 설명은 [`README.md`](README.md)를
> 보세요. 최종 갱신 **2026-10-04**. 이 문서만 읽으면 이어서 작업할 수 있게 쓴다. 상태 절은 **현재 기준으로
> 고쳐 쓰고**, 맨 아래 변경 이력에는 **그날 달라진 것만** 한 줄씩 더한다. 이미 적힌 내용은 반복하지 않는다(`CLAUDE.md`).

### 이어받을 때 먼저 할 것

1. **읽기** — `CLAUDE.md`(작업 기준) → 이 절 → `youtube_analyze_all/scripts/refresh.py` 머리말(그룹·쿼터 실측).
2. **최신으로** — `git pull origin main`. 봇이 10분마다 08 스냅샷을 커밋하므로 작업 전·푸시 전에 꼭 당긴다.
3. **상태 확인** — 셋만 보면 된다.
   - GitHub Actions `collect-scheduled` 최근 실행: 빨간색이면 로그의 `[refresh] 실패:` 줄.
   - `youtube_analyze_all/_state/youtube_quota.json`: 날짜별 사용량. `exhausted` 가 있으면 그날 한도가 찼다.
   - 각 프로젝트 `data/_meta.json` 의 `fetched_at`: 마지막으로 수집된 시각.
4. **키** — 로컬에서 수집까지 돌리려면 `YOUTUBE_API_KEY`·`DART_API_KEY` 환경변수가 필요하다. 없으면
   `refresh.py --skip-collect` 로 분석·사이트 재생성만 할 수 있다.

### 다음 할 일 (위가 먼저)

| # | 할 일 | 방법 · 완료 기준 |
|---|---|---|
| 1 | 리포트 PDF 4종 다시 만들기 — 지금 파일은 9/20 기준 | `결과물/리포트/README.md` 의 명령. 휴대폰 화면에서 읽히는지 확인 후 커밋 |
| 2 | 저장소 전체 "최적화" 점검 — 지금까지는 최근 변경분만 했다 | 12개 프로젝트 + `app/` 에 `CLAUDE.md` 7개 기준. `app/` 은 느린 CPU 설정으로 전환·스크롤을 재고 PC·폰 화면을 확인 |
| 3 | 유즈하 리코 Topic 채널 확인 — 주석엔 있다는데 검색 결과는 없음 | 실제 채널이 있으면 `02_cover_song_ranking/collect.py` 의 `TOPIC_SEED` 에 채널 ID 추가 |
| 4 | Actions Node.js 20 경고 정리 | `actions/checkout`·`actions/setup-python` 을 Node 24 지원 버전으로. 지금은 강제 실행돼 동작엔 문제없음 |

### 지금 상태

| 워크플로 | 주기 (KST) | 하는 일 |
|---|---|---|
| `collect-live` | 매시 깨어나 잡 안에서 10분 간격, 최대 5시간 반 | 08 동시시청자 — 소급 불가라 놓치면 영구 공백 |
| `collect-scheduled` daily | 매일 05:00 | 01·02·03·06·07·12 → 지표 축적(history) → `결과물/` 재생성 |
| `collect-scheduled` weekly | 일요일 05:30 | 04·05·10·11 |
| `collect-scheduled` monthly | 매월 5일 06:00 | 09 DART |
| `probe-sources` | 수동 | 외부 소스 응답만 확인, 저장소는 안 바꿈 |

- 수동 실행은 Actions → collect-scheduled → Run workflow 에서 그룹을 고른다(기본 daily).
- `refresh.py` 는 프로젝트별로 실패를 격리한다. 하나가 죽어도 나머지는 커밋되고 잡만 빨간색이 된다.
  실패 알림이 오면 로그의 `[refresh] 실패:` 줄부터 본다.
- 최근 실패와 조치 — #56·#57(9/20, 04 검색 한도), #65(9/26, 10 분석 오류) 모두 수정됨. #66~#73(9/27~10/3, 9/27 이후 daily 6회·weekly 1회) 정상.

### YouTube 쿼터

한도 10,000 units/일 + `search.list` 100회/일, 태평양 자정(KST 16~17시)에 초기화.
`common/youtube.py` 가 모든 호출을 `youtube_analyze_all/_state/youtube_quota.json` 에 날짜별로 적고,
**자체 예산 8,000 units · 검색 90회**를 넘길 호출은 보내지 않는다. 실사용은 이 장부를 보면 된다.

| 구간 | 예상 사용량 | 비고 |
|---|---|---|
| daily | ~320 units(실측 318) | 02 Topic 채널 재확인 날(7일에 한 번)만 검색 8회 +800 — 9/29 실행에서 검색 0회로 확인. **다음 재확인은 10/6 daily — 그날 02 검색 8회·+800 units 는 정상** |
| weekly | ~3,650 units, 검색 33회 | 04가 3,300. 10 은 최근 21일 영상·새 영상만 받아 ~300 — 10/3 실행 실측 3,618 (04 3,307 · 10 234 · 05 77) |
| 토요일(태평양 날짜) | ~4,000 units | daily·weekly 가 같은 날 돈다 — 10/3 실측 3,936 units · 검색 33회 |

- 04 는 직전 수집이 6일 안쪽이면 검색하지 않는다. 같은 주에 weekly 를 손으로 다시 돌려도 안전하다.
  꼭 다시 받아야 하면 `python 04_kirinuki_ecosystem/collect.py --force`.
- 한도에 걸리면 즉시 멈추고 기존 데이터를 둔다(영상마다 재시도하지 않음).

### 프로젝트 10(게임) 기준

- 다섯 게임을 **각각** 분석한다 — 원신 · 붕괴:스타레일 · 젠레스 존 제로 · 붕괴3rd · 블루 아카이브.
  캐릭터 이름은 **한국 서버 표기**(예: 붕괴3rd `송작`).
- 기간은 다섯 게임 모두 **수집 시점부터 365일**로 같다. 건수는 게임마다 다르고 리포트에 게임별로 적는다.
- 소스 — 구글 플레이 리뷰, 애플 리뷰, 공식 한국 유튜브 채널 댓글, HoYoLAB 댓글(호요버스 4개만).
  막힌 소스와 이유는 `10_hoyoverse/data/source_probe.json`.
- **게임끼리 비교는 공통 표본(플레이+애플+유튜브)의 만 건당 언급으로만** 한다. 게임 안 순위는 전체 표본.
- 댓글·리뷰는 덮어쓰지 않고 누적한다(창 밖만 떨어뜨림). 유튜브 댓글은 최근 21일 영상과 처음 보는
  영상만 다시 받으므로, 3주 넘은 영상에 새로 달린 댓글은 들어오지 않는다.
- 최신 픽업 기준(사용자 확인, **신규 픽업만 · 복각 제외**) — 젠레스 존 제로 클라렛(현재)·시그리드(직전),
  붕괴:스타레일 어벤츄린·웨이브(현재)·로빈·서머레토(직전), 원신 오데트, 붕괴3rd 제레 발레리 - 치유의 깃.

### 결과물 · 리포트

- `결과물/` 은 daily·weekly 가 끝날 때마다 자동으로 다시 만든다.
- 리포트 PDF 4종(`결과물/리포트/`)은 자동 수집으로 만들어지지 않는 **수동 산출물**이다. 만드는 법은
  `결과물/리포트/README.md`.
- 스텔라이브 리포트와 게임 리포트는 **따로** 낸다. 요약판은 측정된 숫자만 싣되, 출처가 있는 공개 자료
  (07 시장 규모, 09 DART 재무)는 그대로 둔다.
- 커버곡 조회수는 **공식 MV + Topic 채널 음원 판을 곡 단위로 합산**한다(02·12).
- PDF 는 휴대폰에 맞춘 150×210mm. 바꿀 때마다 모바일에서 읽히는지 확인한다.

### 어디를 고치나

| 하려는 일 | 파일 |
|---|---|
| 그룹 구성·실행 순서, 수집 생략 프로젝트 | `youtube_analyze_all/scripts/refresh.py` (`GROUPS`, `NO_COLLECT`) |
| 실행 주기 | `.github/workflows/collect-scheduled.yml`, `collect-live.yml` |
| YouTube 호출·재시도·쿼터 예산 | `youtube_analyze_all/common/youtube.py` (`DAILY_UNIT_BUDGET`, `DAILY_SEARCH_BUDGET`) |
| 멤버 로스터·채널 ID | `youtube_analyze_all/common/config.py` |
| 커버곡 MV↔Topic 음원 짝짓기 | `youtube_analyze_all/common/songs.py`, Topic 채널 탐색은 `02_cover_song_ranking/collect.py` |
| 10 수집(기간·소스·댓글 증분) | `10_hoyoverse/collect.py` (`REVIEW_WINDOW_DAYS`, `COMMENT_REFRESH_DAYS`), 애플·HoYoLAB·누적은 `reactions.py` |
| 10 지표·리포트 본문 | `10_hoyoverse/analyze.py` (`COMMON_SOURCES` = 게임 간 비교 표본) |
| 붕괴3rd 한글 이름·전투복 수동 보완 | `10_hoyoverse/data/hi3_names_ko.csv`, `hi3_battlesuits_manual.csv` |
| `결과물/` 생성 | `youtube_analyze_all/scripts/build_deliverables.py` |
| 종합 리포트 HTML(전체판·`--digest` 요약판) | `youtube_analyze_all/scripts/build_unified.py` |
| 통합 대시보드 | `app/` (Next.js), 방법론 페이지 `app/src/app/methodology/page.tsx` |

### 작업 규칙

- API 키는 환경변수로만(`YOUTUBE_API_KEY`, `DART_API_KEY`). 코드·커밋에 넣지 않는다.
- `robots.txt`·Cloudflare 로 막힌 곳은 우회하지 않고, 막혔다고 기록한다.
- 비교는 같은 표본·같은 기간끼리만. 수집 방식이 바뀌면 `_meta.json` 에 `method_changed_at`.
- `_meta.json` 의 한 dict 안에 성격이 다른 값(게임별 dict 와 합계 정수 등)을 섞지 않는다 — #65 의 원인.
- 작업은 `main` 에 바로 올린다. 마무리는 `CLAUDE.md` 의 "최적화" 7개 기준으로 확인하고 보고한다.

### 변경 이력

| 날짜 | 달라진 것 |
|---|---|
| 2026-10-04 | 첫 weekly 실측 확인(10/3 PT, #73 초록) — 장부 3,936 units·검색 33회·한도 초과 없음. 04 는 7일 만에 검색해 갱신, 10 은 공식 채널 영상 1,462개 중 86개만 댓글 수집(window_complete 5/5), 분석 오류 없이 끝나 리포트 총 건수 171,994건. 인수인계서 "다음 할 일"에서 항목 제거 |
| 2026-09-30 | 02 쿼터 절감 확인됨 — 9/29 daily 실행(#68)에서 `02_cover_song_ranking` 검색 0회·210 units(전날까지 8회·1,009 units). 인수인계서 "다음 할 일"에서 항목 제거 |
| 2026-09-29 | 인수인계서를 README.md 에서 별도 `HANDOVER.md` 로 분리 — README 는 GitHub 방문자가 보는 포트폴리오 소개로 깔끔하게, 운영 내용은 여기로. 9/28(PT) daily 가 02 캐시 형식을 첫 마이그레이션하며 예정대로 한 번 더 검색한 것 확인(버그 아님) |
| 2026-09-28 | 02 Topic 채널 "없음" 재확인을 매일 → 7일에 한 번(하루 800 units 절약). 순간 속도 제한을 하루 한도 소진으로 오판하던 것, 검색 한도만 찼을 때 다른 호출까지 막던 것 수정. `CLAUDE.md`(최적화 기준)·인수인계서 신설, 이어받는 순서·다음 할 일·파일 지도 추가 |
| 2026-09-27 | YouTube 쿼터 장부·자체 예산 도입. 04 는 6일 안쪽이면 검색 전에 건너뜀. 10 유튜브 댓글을 증분 수집(주 ~3,000 → ~300 units). #65 수정 — 10 리포트 총 건수를 누적 표본에서 셈 |
| 2026-09-24 | #56·#57 수정 — 04 검색 한도 소진 시 실패 대신 기존 데이터 유지 |
| 2026-09-20 | 10 에 블루 아카이브 추가, 한국어 반응 소스 4종, 표본 명시와 공통 표본 비교, 수집을 누적 합치기로. 리포트 PDF 갱신 |
| 2026-09-19 | 02 커버곡을 곡 단위로 묶고 Topic 음원 판 합산. 요약판(`--digest`) 추가. 10 붕괴3rd 전투복 보완. 리포트 PDF 저장소 보관 |
| 2026-09-18 | 경쟁사 비교를 데뷔 코호트 매칭으로. 리포트 2권 분리. 10 을 게임별 분석 + 공통 365일 창으로 |
