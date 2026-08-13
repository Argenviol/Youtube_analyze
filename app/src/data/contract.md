# 데이터 계약 요약 (M2)

PRD 섹션 7(데이터 계약) 검증 결과. Next.js 구현자는 이 문서를 인터페이스 스펙으로 사용한다.
소스는 `youtube_analyze_all/<project>/site/data.json` (Python `analyze.py`가 생성, Next.js는 읽기 전용).

공통 규칙: `name_en`이 조인 키. 정본 로스터는 `youtube_analyze_all/common/config.py`의 `MEMBERS`
(11명: 창립자 강지 STELLIVE + 탤런트 10명 — EVERYS 2 / UNIVERSE 4 / CLICHE 4).

검증 방법: 각 프로젝트 `site/data.json`을 로드해 top-level 키, `meta` 필드, 배열형 필드의 레코드
스키마(샘플 3건 기준 키 목록)를 덤프. 06·07은 갭 발견 후 `analyze.py`를 수정, 재실행하여
재검증(아래 "M2에서 수정" 항목 참고).

---

## 01_member_channel_performance

- 파일: `youtube_analyze_all/01_member_channel_performance/site/data.json`
- 갱신 주기(PRD): 일 1회
- `meta`: `fetched_at`(ISO8601), `recent_per_channel`, `n_channels`, `n_videos`, `source`
- `members[]` (11행, 1행=1멤버, 조인 키 `name_en`):
  `rank_subs`, `channel_id`, `name_ko`, `name_en`, `unit`, `role`, `handle`,
  `subscribers`, `total_views`, `video_count`, `created_at`, `channel_age_years`,
  `recent_n`, `recent_avg_views`, `recent_median_views`, `recent_max_views`,
  `recent_avg_engagement_rate`, `recent_avg_like_rate`, `uploads_per_week`,
  `uploads_per_month`, `shorts_share`, `reach_ratio`, `lifetime_views_per_sub`,
  `lifetime_views_per_video`
- 보조 필드:
  - `correlations` (object): `subs_vs_avgviews`, `cadence_vs_subs`, `cadence_vs_avgviews`,
    `engagement_vs_subs`, `reach_vs_subs` — 상관계수 스칼라
  - `top_videos[]` (15건, 멤버 아님): `name_ko`, `title`, `views`, `likes`, `comments`, `published_at`
- 대표 지표(카드용): `subscribers`, `recent_avg_views`, `reach_ratio`
- 계약 상태: 최초부터 충족. 수정 없음.

## 02_cover_song_ranking

- 파일: `youtube_analyze_all/02_cover_song_ranking/site/data.json`
- 갱신 주기(PRD): 주 1회
- `meta`: `fetched_at`, `n_covers`, `n_members`, `queries`, `source`
- `members[]` (11행): `rank`, `channel_id`, `name_ko`, `name_en`, `unit`, `cover_count`,
  `total_views`, `avg_views`, `median_views`, `max_views`, `best_cover`, `total_likes`,
  `avg_engagement_rate`, `collab_share`
- 보조 필드: `top_covers[]` (20건, 멤버 아님): `name_ko`, `title`, `views`, `likes`, `comments`,
  `published_at`
- 대표 지표: `cover_count`, `total_views`, `avg_engagement_rate`
- 계약 상태: 최초부터 충족. 수정 없음.

## 03_chzzk_stream_pattern

- 파일: `youtube_analyze_all/03_chzzk_stream_pattern/site/data.json`
- 갱신 주기(PRD): 일 1회
- `meta`: `fetched_at`, `n_members`, `n_streams`, `max_items`, `source`, `tz`(Asia/Seoul)
- `members[]` (11행): `rank`, `name_ko`, `name_en`, `unit`, `followers`, `stream_count`,
  `span_days`, `streams_per_week`, `avg_duration_h`, `median_duration_h`, `total_hours`,
  `hours_per_week`, `avg_start_hour`, `night_share`, `game_share`, `talk_share`,
  `top_category`, `avg_vod_views`
- 보조 필드: `heatmap`(object, 요일×시간 방송빈도), `top_categories[]`(12건: `name`, `count`),
  `hour_dist`(object)
- 대표 지표: `stream_count`, `hours_per_week`, `avg_start_hour`
- 계약 상태: 최초부터 충족. 수정 없음.
- 주의: `channel_id`가 없음 — 유튜브가 아닌 치지직(비공식 API) 데이터이므로 채널 조인은
  `name_en` 기준으로만 가능.

## 04_kirinuki_ecosystem

- 파일: `youtube_analyze_all/04_kirinuki_ecosystem/site/data.json`
- 갱신 주기(PRD): 주 1회
- `meta`: `fetched_at`, `n_clips`, `n_clip_channels`, `queries`, `source`, `filter`
- `members[]` (11행): `rank`, `name_ko`, `name_en`, `unit`, `clip_count`, `total_clip_views`,
  `avg_clip_views`, `fan_channels`, `top_clip`, `top_clip_views`, `top_channel`
- 보조 필드:
  - `channels[]` (20건, 팬 클립 채널 랭킹 — 멤버 아님): `rank`, `clip_channel_id`,
    `clip_channel_title`, `subs`, `clip_count`, `total_views`, `members_covered`, `primary_member`
  - `specialization[]` (7건, 히스토그램: "N명을 다루는 클립채널이 M개") — 멤버별 데이터 아님,
    필드는 `members`(정수, 다루는 멤버 수), `channels`(그 개수에 해당하는 채널 수)
- 대표 지표: `clip_count`, `total_clip_views`, `fan_channels`
- 계약 상태: 최초부터 충족. 수정 없음.

## 05_comment_sentiment

- 파일: `youtube_analyze_all/05_comment_sentiment/site/data.json`
- 갱신 주기(PRD): 주 1회
- `meta`: `fetched_at`, `n_videos`, `n_comments`, `videos_per_member`, `comments_per_video`, `source`
- `members[]` (11행): `rank`, `name_ko`, `name_en`, `unit`, `n_comments`, `positive_share`,
  `negative_share`, `neutral_share`, `sentiment_score`, `top_topic`, `avg_likes`
- 보조 필드:
  - `topic_totals[]` (7건): `topic`, `count`
  - `heatmap` (object): `members`(name_ko 배열), `topics`(토픽명 배열), `values`(2차원 배열) —
    ⚠ `heatmap.members`는 `name_ko` 기준이라 `name_en` 조인이 필요하면 `members[]`에서
    `name_ko → name_en` 매핑을 거쳐야 함
  - `top_liked[]` (15건, 멤버 아님): `name_ko`, `text`, `like_count`, `sentiment`, `topic_ko`
  - `overall_sentiment` (object): `positive`, `neutral`, `negative` (건수)
- 대표 지표: `sentiment_score`, `positive_share`
- 계약 상태: 최초부터 충족. 수정 없음.

## 06_competitor_comparison

- 파일: `youtube_analyze_all/06_competitor_comparison/site/data.json`
- 갱신 주기(PRD): 일 1회
- `meta`: `fetched_at`, `n_channels`, `n_videos`, `recent_per_channel`, `groups`, `source`, `note`
- `members[]` (18행 — StelLive 6 + 홀로라이브 6 + 이세계아이돌 6, 표본 비교이지 전원 아님):
  `rank`, `group`, `channel_id`, `name_ko`, `name_en`, **`unit`(M2에서 추가)**, `subscribers`,
  `total_views`, `video_count`, `recent_avg_views`, `recent_avg_engagement_rate`,
  `uploads_per_week`, `reach_ratio`
  - `unit`은 StelLive 소속 6명만 채워짐(`common/config.py` 로스터 조인 결과: EVERYS/UNIVERSE/
    CLICHE). 경쟁사(홀로라이브·이세계아이돌) 12명은 StelLive 유닛 체계에 속하지 않으므로
    `unit: null` — 대신 `group` 필드로 소속 그룹(`StelLive`/`홀로라이브`/`이세계아이돌`)을 구분한다.
- 보조 필드: `groups[]` (3건, 그룹 단위 집계): `group`, `n_members`, `avg_subscribers`,
  `median_subscribers`, `total_subscribers`, `avg_recent_views`, `avg_engagement_rate`,
  `avg_uploads_per_week`, `avg_reach_ratio`
- 대표 지표: `subscribers`, `reach_ratio` (그룹별 비교는 `groups[]` 사용)
- **계약 상태: M2에서 수정.** 갭 — `members[]`에 `unit` 필드가 전혀 없었음(경쟁사 포함 18행 모두
  누락). `06_competitor_comparison/analyze.py`의 `build_metrics()`에 `common/config.py`
  `member_rows()` 기반 `name_en → unit` 조회를 추가해 StelLive 6명은 실제 유닛을, 경쟁사 12명은
  `null`을 채우도록 수정. `analyze.py` 재실행으로 `data.json` 재생성 및 검증 완료.

## 07_market_analysis (앱 미포함 — 정적 유지, 참고용)

- 파일: `youtube_analyze_all/07_market_analysis/site/data.json`
- 갱신 주기(PRD): 없음 — 외부 리서치 기반 정적 페이지. **허브에서 외부 링크로만 연결**하며
  Next.js 앱 라우트(`/projects/07-*`)에는 포함하지 않는다(PRD 4절 "앱에서 제외").
- `meta`: `built_at`(기존, 빌드 시각), **`fetched_at`(M2에서 추가, `built_at`과 동일 값)**,
  `source`, `n_facts`, `n_milestones`
- **`members[]` 없음 — 의도된 설계.** 07은 조직/시장 단위 분석(시장 규모, 인수합병 이력,
  정부 통계 등)이라 멤버별 행 자체가 존재하지 않는다. 억지로 멤버 배열을 만들지 않았다.
- 실제 데이터 배열:
  - `facts[]` (13건): `metric`, `category`, `value`, `unit`(⚠ 이 `unit`은 측정 단위=%, 명,
    억분 등이며 멤버 계약의 `unit`=유닛 소속과 의미가 다름), `year`, `region`, `source_name`,
    `source_url`, `note`
  - `milestones[]` (8건): `date`, `event`, `category`
  - `groups[]` (3건, 06의 `group_summary`를 그대로 재사용): 06과 동일 스키마
- **계약 상태: M2에서 수정.** 갭 — `meta`에 `fetched_at`이 없고 `built_at`만 있었음(공통 스키마
  위반). `07_market_analysis/analyze.py`의 `build_outputs()`에서 `built_at`은 그대로 두고
  동일 시각의 `fetched_at`을 추가(기존 필드 유지, 필드 추가만). 재실행으로 검증 완료.
  이 프로젝트는 앱에 편입되지 않으므로 이 수정은 스키마 일관성을 위한 것이며 UI 동작을
  바꾸지 않는다.

## 08_live_viewership

- 파일: `youtube_analyze_all/08_live_viewership/site/data.json`
- 갱신 주기(PRD): 10분 (평균 10~20분, Actions cron 지연 감안)
- `meta`: `fetched_at`, `n_snapshots`, `n_members`, `span`(배열, [시작,끝] ISO8601),
  `interval_min`, `source`, `note`
- `members[]` (11행): `rank`, `name_ko`, `name_en`, `unit`, `followers`, `follower_delta`,
  `follower_per_day`, `n_sessions`, `n_live_points`, `peak_ccu`, `avg_ccu`, `ccu_per_1k_followers`
- 보조 필드:
  - `coverage` (object): `n_snapshots`, `n_timepoints`, `span_hours`, `n_live_rows`, `members`,
    `first`, `last` — **FR-5 커버리지 가드에 필요**
  - `enough_coverage` (boolean) — **FR-5**: 관측 24시간 미만 또는 세션 5건 미만이면 `false`.
    감사 시점 실측값은 `false`(관측 0.36시간, 세션 0건) — 수집 데몬이 이제 막 시작된 상태라
    정상. UI는 이 값이 `false`면 결론성 차트 대신 "데이터 수집 중" 상태를 보여줘야 한다.
  - `sessions[]` (세션 재구성 결과, 감사 시점 0건 — 정상, 데몬이 아직 세션을 만들 만큼 못 돎)
  - `ccu_series` (object, 감사 시점 `{}` — 시계열이 아직 비어 있음. 계속 자라는 append-only
    구조이므로 스키마가 아니라 "현재 데이터량" 이슈)
- 대표 지표: `peak_ccu`, `avg_ccu`, `ccu_per_1k_followers` (단, `enough_coverage` 확인 후 사용)
- 계약 상태: 최초부터 충족. 수정 없음.
- 주의: 수집 데몬이 `data/` CSV에 계속 append 중일 수 있음(append-only, 안전). `analyze.py`는
  매 실행마다 그 시점까지의 CSV를 읽어 `data.json`을 재생성한다.

---

## 갭 표 (수정 전 감사 결과)

| # | 프로젝트 | `meta.fetched_at` | `members[].name_en` | `members[].name_ko` | `members[].unit` | 비고 |
|---|---|---|---|---|---|---|
| 01 | 멤버 채널 성과 | 있음 | 있음 | 있음 | 있음 | 갭 없음 |
| 02 | 커버곡 랭킹 | 있음 | 있음 | 있음 | 있음 | 갭 없음 |
| 03 | 치지직 방송 패턴 | 있음 | 있음 | 있음 | 있음 | 갭 없음 |
| 04 | 키리누키 생태계 | 있음 | 있음 | 있음 | 있음 | 갭 없음 |
| 05 | 댓글 여론 | 있음 | 있음 | 있음 | 있음 | 갭 없음(단 `heatmap.members`는 name_ko 기준) |
| 06 | 경쟁사 비교 | 있음 | 있음 | 있음 | **없음 → 수정** | 18행 전체에 `unit` 누락. 경쟁사는 `unit:null`이 의도된 값 |
| 07 | 시장 분석(정적) | **없음(`built_at`만) → 수정** | 해당없음 | 해당없음 | 해당없음 | 멤버 배열 자체가 없음(설계상 정상, org-level) |
| 08 | 동시시청자 | 있음 | 있음 | 있음 | 있음 | 갭 없음 |

## M2에서 수정한 파일

| 파일 | 변경 내용 |
|---|---|
| `youtube_analyze_all/06_competitor_comparison/analyze.py` | `build_metrics()`에 `common.config.member_rows()` 기반 `name_en → unit` 조회 추가, `members` 레코드에 `unit` 필드 삽입(StelLive 6명은 실제 값, 경쟁사 12명은 `null`) |
| `youtube_analyze_all/07_market_analysis/analyze.py` | `build_outputs()`의 `meta`에 `fetched_at`(= 기존 `built_at`과 동일 값) 필드 추가. 기존 `built_at`은 유지 |

두 파일 모두 재실행(`analyze.py`)하여 `site/data.json`을 재생성했고, 위 갭 표의 "없음" 항목이
해소된 것을 재검증했다. `collect.py`는 어느 프로젝트도 수정·실행하지 않았다.
