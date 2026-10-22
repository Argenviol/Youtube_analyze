# 데이터 계약

앱이 읽는 `data.json` 의 인터페이스 명세입니다. 소스는 `youtube_analyze_all/<project>/site/data.json`
(Python `analyze.py` 가 생성) → `scripts/sync-data.mjs` 가 `app/src/data/<id>.json` 으로 복사. 앱은 읽기만 하고,
부족한 필드는 Python 쪽 `analyze.py` 에서 채운다(앱에서 억지로 맞추지 않는다). TypeScript 타입은 `types.ts`.

## 바로 보기

| 규칙 | 내용 |
|---|---|
| 공통 `meta` | 모든 파일에 `fetched_at`(ISO8601)·`source`. 신선도 배지(`refresh.ts`)가 `fetched_at` 을 본다 |
| 멤버 단위 파일 | `members[]` 에 `name_ko`·`name_en`·`unit`. **조인 키는 `name_en`**. 로스터 정본은 `common/config.py` `MEMBERS`(15명 = 창립자 + EVERYS 2 · UNIVERSE 4 · CLICHE 4 · ABYSS 4), 앱은 `roster.ts` 가 미러 |
| 방법 변경 | 수집 방식이 바뀐 파일은 `meta.method_changed_at`·`method_note`(02·06·10). 그 경계를 넘는 비교는 하지 않는다 |
| 행 수 | 멤버 행 수는 각 프로젝트의 표본 기준(01 최근 영상 5개, 03 방송 10회, 05 영상 3개)에 따라 달라진다 — 고정값으로 두지 않는다 |
| 조인 주의 | 05 `heatmap.members` 는 `name_ko` 배열이라 `members[]` 로 `name_ko → name_en` 을 거친다. 03·08 은 치지직 데이터라 `channel_id` 가 없다 |

## 멤버 단위 (전역 필터·드릴다운 대상)

| id | 갱신 | `meta` 추가 필드 | `members[]` 주요 필드 | 보조 필드 |
|---|---|---|---|---|
| 01 | daily | `recent_per_channel`·`n_channels`·`n_videos` | `channel_id`·`role`·`handle`·`subscribers`·`total_views`·`video_count`·`recent_avg_views`·`recent_avg_engagement_rate`·`uploads_per_week`·`shorts_share`·`reach_ratio`·`rank_subs` | `correlations{}`(상관 스칼라 5개) · `top_videos[]` |
| 02 | daily | `n_covers`·`n_members`·`topic`·`title_filter`·`songs`·`method_*` | `cover_count`(영상)·`song_count`(곡)·`total_views`·`topic_views`·`total_views_incl_topic`·`avg_views_per_song`·`median_views`·`max_views`·`best_cover`·`avg_engagement_rate`·`collab_share` | `top_covers[]` · `songs[]`(곡 단위: `song_key`·`n_versions`·`is_collab`·`views_incl_topic`) |
| 03 | daily | `n_members`·`n_no_broadcast`·`n_streams`·`max_items`·`tz` | `followers`·`stream_count`·`span_days`·`streams_per_week`·`avg_duration_h`·`hours_per_week`·`avg_start_hour`·`night_share`·`game_share`·`talk_share`·`top_category`·`avg_vod_views` | `heatmap{}`(요일×시각) · `top_categories[]` · `hour_dist{}` |
| 04 | weekly | `n_clips`·`n_clip_channels`·`queries` | `clip_count`·`total_clip_views`·`avg_clip_views`·`fan_channels`·`top_clip`·`top_clip_views`·`top_channel` | `channels[]`(팬채널 랭킹) · `specialization[]`(다루는 멤버 수 × 채널 수 히스토그램) |
| 05 | weekly | `n_videos`·`n_comments`·`videos_per_member`·`comments_per_video` | `n_comments`·`n_videos`·`positive_share`·`negative_share`·`neutral_share`·`sentiment_score`·`top_topic`·`avg_likes` | `topic_totals[]` · `heatmap{members,topics,values}` · `top_liked[]` · `overall_sentiment{}` · `reference_members[]`(표본 기준 미달 멤버 — 순위 밖, 참고용) |
| 06 | daily | `cohorts`·`cohort_composition`·`missing_channels`·`sampling`·`method_*` | `group`·`cohort`·`generation`·`debut_date`·`months_since_debut`·`rank_in_cohort`·`subscribers`·`subs_per_month`·`recent_avg_views`·`recent_avg_engagement_rate`·`uploads_per_week`·`reach_ratio` | `cohorts[]`(코호트 × 그룹 집계) |
| 08 | 10분 | `n_snapshots`·`n_members`·`span`·`interval_min` | `followers`·`follower_delta`·`follower_per_day`·`n_sessions`·`n_live_points`·`peak_ccu`·`avg_ccu`·`ccu_per_1k_followers` | `coverage{}`(`observed_hours`·`coverage_ratio`·`largest_gap_hours`) · **`enough_coverage`**(bool) · `sessions[]` · `ccu_series{name_en: […]}` |

- 06 `members[]` 는 세 그룹의 **기수 전원**이다. 경쟁사는 `unit: null`, 소속은 `group`. `cohort` 가 `null` 인 행은
  구간 밖이라 표에만 남고 `rank_in_cohort` 는 0. 구독자는 **같은 `cohort` 안에서만** 비교한다.
- 08 은 `enough_coverage` 가 `false` 면(관측 24시간 미만 또는 세션 5건 미만) 결론성 차트 대신 "수집 중"을 보여 준다(FR-5).
  관측 시간은 span 이 아니라 실제 시점 수 × 실측 간격이다.

## 회사·게임·커머스 단위 (`members[]` 없음 — 멤버 필터 대상 아님)

| id | 갱신 | 배열·객체 | 비고 |
|---|---|---|---|
| 09 | monthly | `target_search[]`(대상 법인 검색 결과, `matched`·`note`) · `companies[]`(회사 × 연도 × `fs_div`: `revenue`·`operating_income`·`operating_margin`·`asset_turnover`·`equity_ratio`·`revenue_yoy` …) · `status_summary{}` · `audit_status_summary{}` · `fandom_context{}` | `meta.n_matched`·`n_with_financials`·`years`. 스텔라이브·Brave group 은 `matched: false` 가 정상 |
| 10 | weekly | `app_summary[]` · `characters[]`(574, `game`·`rank`·`release_date`·`is_limited`·`matchable`·`name_ambiguous`) · `push_top[]`·`audience_top[]`·`gap_overpushed[]`·`gap_sleeper[]`(같은 스키마) · `monthly_sentiment[]` · `by_game{genshin,starrail,zzz,hi3,ba}` · `trends_status{}` | `meta.ranking_scope = "per_game"` — 순위·격차는 게임 안에서만. `release_date` 는 `null` 일 수 있다(앱이 처리) |
| 11 | weekly | `fanding{stats,creator_summary,tiers}` · `crowdfunding[]`(`goal_estimated`·`source_url`·`source_type`·`achievement_pct`·`per_backer_krw`) · `financials[]`(09 재사용) | `meta.tumblbug_blocked_by_robots` — 크라우드펀딩은 정적 큐레이션이라 재실행해도 안 바뀐다 |
| 07 | — | 앱 미포함(정적 링크). `facts[]`·`milestones[]`·`groups[]`(06 재사용). `facts[].unit` 은 측정 단위라 멤버의 `unit` 과 뜻이 다르다 | `meta.fetched_at` 은 `built_at` 과 같은 값 |

## 바뀐 이력

| 날짜 | 변경 |
|---|---|
| 2026-08-12 | 초기 감사(M2) — 06 `members[].unit` 누락, 07 `meta.fetched_at` 누락을 `analyze.py` 에서 채움 |
| 2026-09-18 | 06 표본을 데뷔 코호트 매칭(기수 전원)으로 교체 — `groups[]` → `cohorts[]`, `meta.method_changed_at` |
| 2026-09-19 | 02 곡 단위·Topic 음원 합산 — `song_count`·`topic_views`·`total_views_incl_topic`·`songs[]` 추가 |
| 2026-10-14 | 로스터 15명(ABYSS 4명). 05 `reference_members[]`, 08 `coverage.observed_hours`·`coverage_ratio` |
| 2026-10-18 | 10 `is_limited` 를 글로벌 단일 값으로(서버별 배열 문자열이던 것), `release_date` null 허용 |
