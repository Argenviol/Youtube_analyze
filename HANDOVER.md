# 인수인계서

작업을 이어받는 사람(또는 다음 세션)을 위한 운영 문서입니다. 포트폴리오 소개는 [`README.md`](README.md),
요구사항은 [`PRD.md`](PRD.md), 작업 기준은 [`CLAUDE.md`](CLAUDE.md). **최종 갱신 2026-11-06.**

이 문서만 읽고 이어서 할 수 있게 쓴다. 상태 절은 **현재 기준으로 고쳐 쓰고**(덧붙이지 않음), 맨 아래
변경 이력에는 **그날 달라진 것만** 한 줄 더한다.

## 바로 보기

| 무엇을 | 어디서 |
|---|---|
| 자동 수집이 돌고 있나 | GitHub Actions → `collect-scheduled`(daily·weekly), `collect-live`(08). 빨간색이면 로그의 `[refresh] 실패:` 줄 |
| YouTube 쿼터를 얼마나 썼나 | `youtube_analyze_all/_state/youtube_quota.json` — 날짜별 units·검색 횟수. `exhausted` 가 있으면 그날 한도가 찼다 |
| 마지막 수집 시각 | 각 프로젝트 `data/_meta.json` 의 `fetched_at` |
| 멤버별 조회수 정리 (10/25 기준, 수동) | 루트 `멤버별_조회수_2026-10-25.md` — README 맨 위에서 링크 |
| 할 일 | 아래 "다음 할 일" |
| 무엇을 어디서 고치나 | 아래 "어디를 고치나" |

## 이어받을 때 먼저 할 것

1. `CLAUDE.md` → 이 문서 → `youtube_analyze_all/scripts/refresh.py` 머리말(그룹·쿼터 실측) 순으로 읽는다.
2. `git pull origin main`. 봇이 10분마다 08 스냅샷을 커밋하므로 **작업 전·푸시 전에 꼭** 당긴다.
3. 로컬에서 수집까지 돌리려면 `YOUTUBE_API_KEY` 환경변수가 필요하다. 없으면
   `refresh.py --group daily --skip-collect` 로 분석·사이트 재생성만 할 수 있다.
4. 작업은 `main` 에 바로 올린다. 마무리는 `CLAUDE.md` 의 "최적화" 7개 기준으로 확인하고 무엇을 확인했는지 보고한다.

## 다음 할 일 (위가 먼저)

| # | 할 일 | 방법 · 완료 기준 |
|---|---|---|
| 0 | **재편 작업 마무리** — 구조·워크플로는 끝났다. 남은 것: ① 디시 수집이 끝난 뒤 `dc_reaction.md`·H3 갱신 확인 ② `collect/vtuber_roster.csv` 에 확인된 버튜버 채널 올리기(H5) ③ 4기 5주차(2026-11-22 이후) `hypotheses.md` H1 확인 ④ 아카라이브·펨코·X·인스타·스레드는 운영자가 저장해 오면 같은 틀로 합친다(막힌 곳은 우회하지 않는다) | 수집은 Actions `collect-community`(주간+수동)·`collect-vtubers`(매시간), 분석은 `analyze-community`. 설명은 `collect/README.md`·`analysis/README.md`. 알려진 한계: 다시보기 채팅은 초당 ~20건에서 잘려 4기 데뷔 방송 채팅 수는 하한 |
| 1 | 유즈하 리코 Topic 채널 확인 — 주석엔 있다는데 검색 결과는 없음 | 실제 채널이 있으면 `02_cover_song_ranking/collect.py` 의 `TOPIC_SEED` 에 채널 ID 추가 |
| 2 | ABYSS 를 01 분석·05 순위에 넣기 | 01: 최근 영상 5개(`MIN_RECENT_VIDEOS`)가 쌓이면 자동 편입 — 그 daily 뒤 리포트 "제외" 문구와 순위 확인. 05: 영상이 3개(`MIN_SAMPLE_VIDEOS`) 넘게 쌓이면 인기 영상 기준으로 다시 뽑아 라벨링하고 옛 120행(sid 331~450)을 바꾼다. 12 데뷔 이벤트의 배수는 데뷔 뒤 방송이 쌓이면 저절로 계산된다 |
| 3 | 06 에 ABYSS 코호트 추가 — 지금은 짝지을 경쟁 기수가 없어 빠져 있다 | 같은 시기 데뷔한 경쟁 그룹을 `config.COMPETITOR_ROSTER`·`COHORT_BINS` 에 넣으면 저절로 들어온다. 구독자가 쌓인 뒤에 |
| 4 | 3D 데뷔 수동 등록 보강 — 지금은 사키하네 후야(2026-09-18) 1건 | 클리셰 3D 데뷔(2025-09, 린 9/17·나나 9/19 방송 제목만 확인)·유니 새 3D(2025-11-12)의 날짜·참여 멤버를 확인해 `12_event_impact/data/events_manual.csv` 에 `3D 데뷔` 로 |
| 5 | Actions Node.js 20 경고 정리 | `actions/checkout`·`actions/setup-python` 을 Node 24 지원 버전으로. 지금은 강제 실행돼 동작엔 문제없음 |
| 6 | (선택) 멤버별 조회수 후속 — 진행 기록은 `dev/active/member-views/`(plan·context·tasks) | 계산은 `youtube_analyze_all/member_views/member_views.py`(API 키 불필요, 원본 데이터 `data/`). `summary` 출력이 루트 `멤버별_조회수_2026-10-25.md` 표와 같다. 남은 일은 `tasks.md` |

## 지금 상태

| 워크플로 | 주기 (KST) | 하는 일 |
|---|---|---|
| `collect-live` | 매시 깨어나 잡 안에서 10분 간격(최대 5.5시간) | 08 동시시청자 — 소급 불가, 놓치면 영구 공백 |
| `collect-scheduled` daily | 매일 05:00 | 01·02·03·06·07·12 → 지표 축적 → `결과물/` 재생성 |
| `collect-scheduled` weekly | 일요일 05:30 | 04·05 |
| `collect-community` | 일요일 06:30 + 수동 | 디시 3곳 증분·4기 새 방송 채팅·(수동) 데뷔/비교군 채팅·애니 일정 |
| `collect-vtubers` | 매시 7분 | 치지직 상위 500 합계·버튜버 후보·명단 시청자 |
| `analyze-community` | `collect-community` 뒤 + 일요일 09:00 | `analysis/` 3종 재실행 → `analysis/out/` |
| `probe-sources` | 수동 | 외부 소스 응답만 확인, 저장소는 안 바꿈 |

- **CI** — `collect-scheduled` #87~#95(10/15~10/22) 전부 초록, 마지막 daily 10/23 08:08 KST. 수동 실행은 Actions → collect-scheduled → Run workflow 에서 그룹 선택.
  `refresh.py` 는 프로젝트별로 실패를 격리한다 — 하나가 죽어도 나머지는 커밋되고 잡만 빨간색이 된다.
- **지난 실패** — #56·#57(9/20, 04 검색 한도) · #65(9/26, 10 분석 오류) · #86(10/14, ABYSS 편입 직후 01·02 재생목록 404) 모두 수정.
  #709(10/5 live)는 러너 종료 신호(exit 143)로 GitHub 쪽 문제, 조치 없음.
- **리포트 PDF 4종**(`결과물/리포트/`)은 수동 산출물 — 지금 파일은 10/21 기준.
- **로스터** — 15명(창립자 + 탤런트 14명). 4기 ABYSS 4명은 10/17·18 데뷔, 수집(03·04·08)은 정상이고 01·05·06 편입은 "다음 할 일" 2·3.

### YouTube 쿼터

한도 10,000 units/일 + `search.list` 100회/일, 태평양 자정(KST 16~17시) 초기화. `common/youtube.py` 가 모든 호출을
장부에 적고 **자체 예산 8,000 units · 검색 90회**를 넘길 호출은 보내지 않는다. 한도에 걸리면 즉시 멈추고 기존 데이터를 둔다.

| 구간 | 실측 | 비고 |
|---|---|---|
| daily | ~340 units | 02 Topic 채널 "없음" 재확인은 멤버마다 7일 주기라 4명씩 두 묶음으로 돈다(10/20 후야·시부키·나나·리코, 10/22 ABYSS 4명) — 그 날만 검색 8회·~1,140 units. 다음은 10/27·10/29. 정상 |
| weekly | ~4,850 units · 검색 45회 | 04 가 4,500(멤버 15명 × 3쿼리). 10 은 최근 21일 영상·새 영상만 받아 ~200~300 |
| 토요일(태평양 날짜) | ~5,200 units | daily + weekly — 10/17 실측 5,142. 02 재확인 날과 겹치면 ~6,000·검색 61회 |

04 는 직전 수집이 6일 안쪽이면 검색하지 않으므로 같은 주에 weekly 를 다시 돌려도 안전하다(`--force` 로 강제).

## 기준

### 데이터 · 리포트

- 비교는 같은 표본·같은 기간끼리만. 수집 방식이 바뀌면 `_meta.json` 에 `method_changed_at` 을 남기고 경계를 넘어 비교하지 않는다.
- **결론 문장에 멤버 이름을 붙인 순위를 쓰지 않는다**(공개 저장소 — 서열 비교로 퍼진다, 2026-10-18 운영자). 요약은
  `common/summary.py`(`spread`·`overlap_line`, 앱은 `app/src/lib/overlap.ts`)로 분포와 "상위 3명이 겹치는가"만 쓰고
  멤버별 수치는 표·차트에 둔다.
- **리포트 산문에 손으로 적은 숫자를 두지 않는다.** 배수·상관·건수·이름은 전부 데이터에서 계산한다. 프로젝트 README 의
  "읽는 법"에도 수집마다 바뀌는 수치는 쓰지 않고 `REPORT.md` 로 넘긴다.
- 측정 못 한 것은 "측정 불가"로 남긴다. 수익은 어떤 방법으로도 재지 않는다.
- 커버곡 조회수는 공식 MV + Topic 음원 판을 곡 단위로 합산(02·12). 치지직 방송 시작 = 다시보기 게시 − 길이(`common/chzzk.vod_start`).
- 12 의 경쟁사 비교 창은 세 그룹의 **지금 로스터 전원이 있는 첫날부터**(06 은 데뷔 코호트 매칭이라 별개).
- `결과물/` 은 daily·weekly 뒤 자동 재생성. 날짜별로 쌓이는 프로젝트(01·02·03·06·08·12)는 최신 리포트 하나만 두고
  지난 날짜는 `결과물/_이전/` 으로 옮긴다(지우지 않음 — 옛 문구가 그대로 남아 있다).
- 종합 리포트는 한 권, 전체판·요약판(지금 PDF 는 10/21 기준이라 삭제한 프로젝트가 들어 있다 — 재생성 필요). PDF 는 150×210mm, Noto Sans KR 을 base64 로 내장
  (`build_unified.py` `FONT_FACE`). 만드는 법은 `결과물/리포트/README.md`.

### 확인 방법

- 느린 기기: Playwright 로 CPU 4배 감속, 폰(390px)·PC 에서 전환·스크롤·패널 열기의 long task 를 잰다. 수백 행 표는
  `Table` 의 `pageSize` 로 나눠 그린다.
- API 오류는 잘라 둔 메시지가 아니라 **응답 원문 전체**에서 사유(`reason`)를 찾는다. 가짜 응답 시험은 실제 응답 모양과
  실제 `_get` 경로로 한다(#86 교훈).
- `_meta.json` 의 한 dict 안에 성격이 다른 값(dict 와 합계 정수 등)을 섞지 않는다(#65 교훈).

## 어디를 고치나

| 하려는 일 | 파일 |
|---|---|
| 그룹 구성·실행 순서, 수집 생략 프로젝트 | `youtube_analyze_all/scripts/refresh.py` (`GROUPS`, `NO_COLLECT`) |
| 실행 주기 | `.github/workflows/collect-scheduled.yml`, `collect-live.yml` |
| YouTube 호출·재시도·쿼터 예산 | `youtube_analyze_all/common/youtube.py` (`DAILY_UNIT_BUDGET`, `DAILY_SEARCH_BUDGET`) |
| 멤버 로스터·채널 ID·데뷔일·생일 | `youtube_analyze_all/common/config.py` (`MEMBERS`, `CHZZK_IDS`, `DEBUTS`, `BIRTHDAYS`) + 앱 `app/src/data/roster.ts` 를 같이 고친다 |
| 이벤트 감지·측정, 수동 등록 | `12_event_impact/collect.py`(`detect_*`), `analyze.py`(`STREAM_EVENT_TYPES`, `CCU_EVENT_TYPES`), `data/events_manual.csv` |
| 커버곡 MV ↔ Topic 음원 짝짓기 | `youtube_analyze_all/common/songs.py`, Topic 채널 탐색 `02_cover_song_ranking/collect.py` |
| 10 수집(기간·소스·댓글 증분) · 지표 | `10_hoyoverse/collect.py`(`REVIEW_WINDOW_DAYS`, `COMMENT_REFRESH_DAYS`), `reactions.py`, `analyze.py`(`COMMON_SOURCES`) |
| 붕괴3rd 한글 이름·전투복 수동 보완 | `10_hoyoverse/data/hi3_names_ko.csv`, `hi3_battlesuits_manual.csv` |
| `결과물/` 생성 · 그 README | `youtube_analyze_all/scripts/build_deliverables.py` (`PROJECTS` 결론, `_index_md`) |
| 종합 리포트 HTML·PDF 디자인 | `youtube_analyze_all/scripts/build_unified.py` (CSS·`FONT_FACE`, `--digest`) |
| 통합 대시보드 | `app/`, 방법론 `app/src/app/methodology/page.tsx`, 신선도 주기 `app/src/data/refresh.ts` |
| 멤버별 조회수 정리 문서 | 루트 `멤버별_조회수_2026-10-25.md` — 숫자는 `youtube_analyze_all/member_views/member_views.py summary`, 이어서 할 것은 `dev/active/member-views/` |

## 작업 규칙

- API 키는 환경변수로만. 코드·커밋에 넣지 않는다.
- `robots.txt`·Cloudflare 로 막힌 곳은 우회하지 않고 막혔다고 기록한다.
- 멤버 정보(유튜브 핸들·치지직 ID·생일)는 `Argenviol/stel-database`(`server.py` `TRENDING_HANDLES`·`MEMBERS`, `HANDOFF.md` §10)에도
  있다 — 새 멤버를 넣을 때 먼저 참고하되 채널 ID 는 `youtube.com/channel/<id>` 의 og:title 로 확인한다.
- 커밋 메시지는 `<type>: <description>`. 문서(README·PRD·이 문서)는 바로 보기 → 본문 → 규칙 순의 같은 틀을 유지한다.

## 변경 이력

| 날짜 | 달라진 것 |
|---|---|
| 2026-11-07 | 수집·분석 분리(`collect/`·`analysis/`)와 워크플로 3개(`collect-community`·`collect-vtubers`·`analyze-community`), 디시·채팅·전체 버튜버·애니 수집기, 분석 3종(`origin_of_viewers`·`dc_reaction`·`hypotheses`) 추가. 다시보기 채팅 포화(초당 ~20건) 확인 |
| 2026-11-07 | 삭제한 호요·DART·커머스 문구가 남은 12 날짜별 리포트 60개를 `결과물/_이전/12_event_impact/` 에서 지움(이 프로젝트만 예외 — 옛 문구가 그대로 남아 있어서). 이 날까지 12 리포트는 11/06 판 |
| 2026-11-06 | 09 DART·10 게임·11 팬 커머스와 그 앱 페이지·monthly 그룹·`DART_API_KEY` 삭제, 12 이벤트 임팩트에서 호요·DART·커머스 렌즈 제거(15→12개 렌즈), 게임 리포트 폐지. `자료_점검_및_분석계획.md` 추가 |
| 2026-10-27 | 루트에 `멤버별_조회수_2026-10-25.md`(멤버 10명 영상·쇼츠·노래 조회수, 한 번 수집한 정리본 — 자동 갱신 안 됨) 추가, README 맨 위에 링크, 계산 스크립트·데이터 `youtube_analyze_all/member_views/`, 진행 기록 `dev/active/member-views/`. 순위표를 README 본문 대신 별도 문서로 둔 건 "멤버 이름 순위는 README에 쓰지 않는다" 규칙 때문 |
| 2026-10-23 | 상태 확인만 — daily #95 정상(10/22 수집). 02 Topic 재확인이 4명씩 두 묶음·7일 주기로 자리잡아 쿼터 표에 다음 날짜를 적음 |
| 2026-10-22 | 문서 전체를 같은 틀로 정리 — 루트·`youtube_analyze_all/`·`app/` README, `PRD.md`, 프로젝트 README 12개, `결과물/README.md`(생성기 `_index_md`), `결과물/리포트/README.md`, 이 문서, `CLAUDE.md`(최적화 기준을 표로, 문서·데이터 규칙 절 추가), `SETUP_KEYS.md`(키 2개 표·발급·넣는 법, Actions 시크릿 추가), `app/src/data/contract.md`(실제 `data.json` 스키마 기준으로 재작성 — 09·10·11 추가, M2 감사 서술은 이력 한 줄로). 낡은 서술(Holodex·pytrends·`.env` 파일·'PC 켜두기'·일회성 요청 목록(PDF `fonts-nanum`, ABYSS 데뷔 전, git 미사용·M1, 02 검색 수집, 08 25분 고정 간격)과 실행마다 바뀌는 수치 제거. 앱 신선도의 09 주기를 분기→월 1회로 |
| 2026-10-21 | 저장소 전체 최적화 — pyflakes·vulture 0건(`barlabels`·`UNIT_COLORS`·`SPACING`·`chzzk.search_channel`·`apply_montage_tokens.py`·루트 PDF 3개 제거). 12 리포트 산문의 손글씨 수치 20여 곳을 계산값으로, 이벤트 유형별 배수 표, 댓글 표본을 05 비교 표본으로, 경쟁사 창을 현 로스터 기준(9/18~)으로. PDF 재설계(Noto Sans KR base64 내장, Gothic A1·구글 폰트 링크·유령 CSS 제거) 후 4종 재생성. 앱 폰 내비 줄바꿈 수정, 10 캐릭터 표 60행씩(스크롤 long task 10개→1개) |
| 2026-10-19 | 치지직 다시보기 게시 시각은 방송 **종료** 시각(08 관측 460회 중 80% 가 ±20분) — 시작 = 게시 − 길이(`common/chzzk.vod_start`)로 바꿔 03 심야 비율 22~81% → 1~9%, 12 이벤트 11건 날짜 하루 앞당김. `events_seen.csv` 는 옛 ID → 새 ID 로 옮겨 first_seen 보존. 03 `MIN_STREAMS` = 10. 03 `history.csv` 의 `night_share` 는 이날 이전과 정의가 다르다 |
| 2026-10-18 | 4기 데뷔 2일차 — 히요리(피크 60,712)·메리(79,149, 기록상 최고)·첫 단체 합방(56,056) 등록, `DEBUTS` 를 `exact` 로. 12 의 고정 수치(38,402·"19배")를 계산값으로. 05 ABYSS 댓글 120개 라벨링(리포트에 따로). 앱 빌드 오류 2건 수정(10 `is_limited` 배열 문자열, 출시일 null). **멤버 순위 문구 금지** — 리포트·사이트·앱·README 의 "○○ 1위"를 분포·겹침 문장으로, 지난 리포트 296개를 `결과물/_이전/` 으로 |
| 2026-10-17 | 12 에 `데뷔` 종류, ABYSS 1일차(토아 62,637·랑 67,950) 등록. 01 `MIN_RECENT_VIDEOS` = 5(영상 1개짜리가 순위에 들던 것). #86 수정 CI 통과 |
| 2026-10-15 | #86 — 데뷔 전 채널의 재생목록 404(`playlistNotFound`) 처리가 잘린 메시지 때문에 작동하지 않던 것을 전용 예외 `PlaylistNotFound` 로 응답 원문에서 판별 |
| 2026-10-14 | 4기 ABYSS 4명 편입(치지직·유튜브, ID 는 공지·og:title 로 확인). 구독자 숨김·영상 0개 채널에서 수집기가 죽지 않게. 12 에 생일(12건)·3D 데뷔 종류, 동시시청자 표에 이벤트 열 |
| 2026-10-04 | 첫 weekly 실측(#73) 3,936 units·검색 33회, 한도 초과 없음 |
| 2026-09-30 | 02 쿼터 절감 확인 — 9/29 daily 검색 0회·210 units |
| 2026-09-29 | 인수인계서를 README 에서 `HANDOVER.md` 로 분리 |
| 2026-09-28 | 02 Topic 채널 "없음" 재확인을 7일에 한 번으로. 속도 제한을 한도 소진으로 오판하던 것 수정. `CLAUDE.md`(최적화 기준) 신설 |
| 2026-09-27 | YouTube 쿼터 장부·자체 예산 도입. 04 는 6일 안쪽이면 건너뜀. 10 댓글 증분 수집. #65 수정 |
| 2026-09-24 | #56·#57 — 04 검색 한도 소진 시 기존 데이터 유지 |
| 2026-09-20 | 10 에 블루 아카이브·한국어 반응 소스 4종·공통 표본 비교. PDF 갱신 |
| 2026-09-19 | 02 커버곡 곡 단위 + Topic 음원 합산. 요약판(`--digest`). PDF 저장소 보관 |
| 2026-09-18 | 경쟁사 비교를 데뷔 코호트 매칭으로. 리포트 2권 분리. 10 게임별 분석 + 공통 365일 창 |
