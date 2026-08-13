/**
 * `contract.md`(M2 데이터 계약 검증 결과)에 대응하는 TypeScript 타입.
 *
 * 이 파일이 다루는 두 가지 알려진 예외:
 *  1. 06(경쟁사 비교)의 `members[].unit`은 StelLive 소속이 아닌 12명에 대해
 *     `null`이다 — 의도된 값(설계상 정상)이라 `Unit | null`로 타입을 잡고,
 *     UI는 그 행을 조용히 걸러내지 않는다(그룹 배지 등으로 다르게 표시한다).
 *  2. 05(댓글 여론)의 `heatmap.members`는 `name_ko` 기준 배열이다. 나머지 앱
 *     전체가 `name_en`으로만 조인하므로, `normalizeHeatmap05()`로 읽는 즉시
 *     `name_en`으로 바꿔서 그 이후에는 `name_ko`가 등장하지 않게 한다.
 *
 * 하나 더, contract.md에 없던 사소한 불일치도 여기 적어 둔다:
 *  - contract.md는 03의 `hour_dist`를 "object"라고 적었지만 실제
 *    `site/data.json`은 길이 24의 숫자 배열(index = 0~23시)이다. 실측값을
 *    기준으로 `number[]`로 타입을 잡았다 — contract.md 쪽이 부정확했다.
 */

// ---------------------------------------------------------------------------
// 공통
// ---------------------------------------------------------------------------

/** 로스터 정본(`youtube_analyze_all/common/config.py`의 `MEMBERS`) 기준 유닛. */
export type Unit = "STELLIVE" | "EVERYS" | "UNIVERSE" | "CLICHE";

export type Role = "founder" | "talent";

/** 모든 프로젝트의 `members[]` 행이 최소한 갖는 조인 키. */
export type MemberBase = {
  name_ko: string;
  name_en: string;
  unit: Unit | null;
};

export type ProjectId = "01" | "02" | "03" | "04" | "05" | "06" | "08";

// ---------------------------------------------------------------------------
// 01 · 멤버 채널 성과
// ---------------------------------------------------------------------------

export type Meta01 = {
  fetched_at: string;
  recent_per_channel: number;
  n_channels: number;
  n_videos: number;
  source: string;
};

export type Member01 = MemberBase & {
  rank_subs: number;
  channel_id: string;
  role: Role;
  handle: string;
  subscribers: number;
  total_views: number;
  video_count: number;
  created_at: string;
  channel_age_years: number;
  recent_n: number;
  recent_avg_views: number;
  recent_median_views: number;
  recent_max_views: number;
  recent_avg_engagement_rate: number;
  recent_avg_like_rate: number;
  uploads_per_week: number;
  uploads_per_month: number;
  shorts_share: number;
  reach_ratio: number;
  lifetime_views_per_sub: number;
  lifetime_views_per_video: number;
};

export type Correlations01 = {
  subs_vs_avgviews: number;
  cadence_vs_subs: number;
  cadence_vs_avgviews: number;
  engagement_vs_subs: number;
  reach_vs_subs: number;
};

export type TopVideo01 = {
  name_ko: string;
  title: string;
  views: number;
  likes: number;
  comments: number;
  published_at: string;
};

export type Data01 = {
  meta: Meta01;
  correlations: Correlations01;
  members: Member01[];
  top_videos: TopVideo01[];
};

// ---------------------------------------------------------------------------
// 02 · 커버곡 랭킹
// ---------------------------------------------------------------------------

/**
 * ⚠ M3 파트 2에서 발견한 추가 불일치: contract.md는 02의 `meta`에 `queries:
 * string[]`가 있다고 적었지만, 이 세션 도중(2026-08-12) 실제
 * `02_cover_song_ranking/analyze.py`가 재실행되면서 수집 방식이 바뀌었다 —
 * `search.list` relevance 상위 40건 창 대신 업로드 재생목록을 전량 열거하는
 * 방식(`method: "uploads_playlist_enumeration"`)으로 교체됐고, `meta`도
 * `queries` 대신 `title_filter`/`method`/`method_changed_at`/`method_note`를
 * 갖는다. 실제 `site/data.json`을 기준으로 타입을 맞췄다 — contract.md 쪽이
 * 이제 낡았다(갱신 필요).
 */
export type Meta02 = {
  fetched_at: string;
  n_covers: number;
  n_members: number;
  title_filter: string;
  source: string;
  /** 수집 방식 식별자. 현재값: "uploads_playlist_enumeration"(업로드 재생목록 전량 열거). */
  method: string;
  /** 이 방식으로 바뀐 날짜(YYYY-MM-DD). 이 시점 이전 스냅샷과 cover_count를 직접 비교하지 말 것. */
  method_changed_at: string;
  method_note: string;
};

export type Member02 = MemberBase & {
  rank: number;
  channel_id: string;
  cover_count: number;
  total_views: number;
  avg_views: number;
  median_views: number;
  max_views: number;
  best_cover: string;
  total_likes: number;
  avg_engagement_rate: number;
  collab_share: number;
};

export type TopCover02 = {
  name_ko: string;
  title: string;
  views: number;
  likes: number;
  comments: number;
  published_at: string;
};

export type Data02 = {
  meta: Meta02;
  members: Member02[];
  top_covers: TopCover02[];
};

// ---------------------------------------------------------------------------
// 03 · 치지직 방송 패턴
// ---------------------------------------------------------------------------

export type Meta03 = {
  fetched_at: string;
  n_members: number;
  n_streams: number;
  max_items: number;
  source: string;
  tz: string;
};

/** `channel_id` 없음 — 유튜브가 아니라 치지직(비공식 API) 데이터라 `name_en`으로만 조인 가능. */
export type Member03 = MemberBase & {
  rank: number;
  followers: number;
  stream_count: number;
  span_days: number;
  streams_per_week: number;
  avg_duration_h: number;
  median_duration_h: number;
  total_hours: number;
  hours_per_week: number;
  avg_start_hour: number;
  night_share: number;
  game_share: number;
  talk_share: number;
  top_category: string;
  avg_vod_views: number;
};

export type TopCategory03 = { name: string; count: number };

export type Data03 = {
  meta: Meta03;
  members: Member03[];
  /** 요일(7) × 시간(24) 방송 빈도. `heatmap[day][hour]`, day 0=일요일. */
  heatmap: number[][];
  top_categories: TopCategory03[];
  /** 실측: 길이 24 숫자 배열(index=시각). contract.md의 "object" 서술은 부정확했다. */
  hour_dist: number[];
};

// ---------------------------------------------------------------------------
// 04 · 키리누키 생태계
// ---------------------------------------------------------------------------

export type Meta04 = {
  fetched_at: string;
  n_clips: number;
  n_clip_channels: number;
  queries: string[];
  source: string;
  filter: string;
};

export type Member04 = MemberBase & {
  rank: number;
  clip_count: number;
  total_clip_views: number;
  avg_clip_views: number;
  fan_channels: number;
  top_clip: string;
  top_clip_views: number;
  top_channel: string;
};

export type ClipChannel04 = {
  rank: number;
  clip_channel_id: string;
  clip_channel_title: string;
  subs: number;
  clip_count: number;
  total_views: number;
  members_covered: number;
  primary_member: string;
};

/** 히스토그램: "N명을 다루는 클립채널이 M개" — 멤버별 데이터가 아니다. */
export type Specialization04 = { members: number; channels: number };

export type Data04 = {
  meta: Meta04;
  members: Member04[];
  channels: ClipChannel04[];
  specialization: Specialization04[];
};

// ---------------------------------------------------------------------------
// 05 · 댓글 여론
// ---------------------------------------------------------------------------

export type Meta05 = {
  fetched_at: string;
  n_videos: number;
  n_comments: number;
  videos_per_member: number;
  comments_per_video: number;
  source: string;
};

export type Member05 = MemberBase & {
  rank: number;
  n_comments: number;
  positive_share: number;
  negative_share: number;
  neutral_share: number;
  sentiment_score: number;
  top_topic: string;
  avg_likes: number;
};

export type TopicTotal05 = { topic: string; count: number };

/** 원본 그대로: `members`가 `name_ko` 배열이다 (⚠ name_en 아님). */
export type Heatmap05Raw = {
  members: string[];
  topics: string[];
  values: number[][];
};

/** `normalizeHeatmap05()`로 조인한 뒤 형태 — `members`가 `name_en`으로 바뀐다. */
export type Heatmap05Normalized = {
  members: string[];
  topics: string[];
  values: number[][];
};

export type TopLiked05 = {
  name_ko: string;
  text: string;
  like_count: number;
  sentiment: string;
  topic_ko: string;
};

export type OverallSentiment05 = { positive: number; neutral: number; negative: number };

export type Data05 = {
  meta: Meta05;
  members: Member05[];
  topic_totals: TopicTotal05[];
  heatmap: Heatmap05Raw;
  top_liked: TopLiked05[];
  overall_sentiment: OverallSentiment05;
};

/**
 * 05의 `heatmap.members`(name_ko 배열)를 `members[]`의 name_ko→name_en 매핑으로
 * 조인해 `name_en` 배열로 정규화한다. 이후 이 앱 안에서는 `name_ko` 히트맵 키가
 * 다시 등장하지 않아야 한다 — 이 함수가 그 경계다.
 */
export function normalizeHeatmap05(data: Data05): Heatmap05Normalized {
  const koToEn = new Map(data.members.map((m) => [m.name_ko, m.name_en]));
  return {
    members: data.heatmap.members.map((nameKo) => koToEn.get(nameKo) ?? nameKo),
    topics: data.heatmap.topics,
    values: data.heatmap.values,
  };
}

// ---------------------------------------------------------------------------
// 06 · 경쟁사 비교
// ---------------------------------------------------------------------------

export type Group06 = "StelLive" | "홀로라이브" | "이세계아이돌" | string;

export type Meta06 = {
  fetched_at: string;
  n_channels: number;
  n_videos: number;
  recent_per_channel: number;
  groups: string[];
  source: string;
  note: string;
};

/**
 * 18행(StelLive 6 + 홀로라이브 6 + 이세계아이돌 6) — 표본 비교이지 전 멤버가
 * 아니다. `unit`은 StelLive 소속 6명만 채워지고, 나머지 12명은 `null`이
 * 의도된 값이다(그 대신 `group`으로 소속을 구분한다). 이 null 행을 걸러내지
 * 말 것 — 경쟁사 비교가 이 프로젝트의 핵심이다.
 */
export type Member06 = {
  rank: number;
  group: Group06;
  channel_id: string;
  name_ko: string;
  name_en: string;
  unit: Unit | null;
  subscribers: number;
  total_views: number;
  video_count: number;
  recent_avg_views: number;
  recent_avg_engagement_rate: number;
  uploads_per_week: number;
  reach_ratio: number;
};

export type GroupSummary06 = {
  group: Group06;
  n_members: number;
  avg_subscribers: number;
  median_subscribers: number;
  total_subscribers: number;
  avg_recent_views: number;
  avg_engagement_rate: number;
  avg_uploads_per_week: number;
  avg_reach_ratio: number;
};

export type Data06 = {
  meta: Meta06;
  members: Member06[];
  groups: GroupSummary06[];
};

// ---------------------------------------------------------------------------
// 08 · 동시시청자 (FR-5 커버리지 가드 대상)
// ---------------------------------------------------------------------------

export type Meta08 = {
  fetched_at: string;
  n_snapshots: number;
  n_members: number;
  span: string[];
  interval_min: number;
  source: string;
  note: string;
};

export type Coverage08 = {
  n_snapshots: number;
  n_timepoints: number;
  /**
   * 첫 스냅샷과 마지막 스냅샷 사이의 **달력 시간**. 수집이 끊긴 구간도 포함한다.
   * ⚠ 커버리지 판단에 이 값을 쓰면 안 된다 — PC를 하루 꺼두면 span 은 24시간을
   *   넘지만 실제 데이터는 몇 시간치뿐이다. 판단에는 `observed_hours` 를 쓴다.
   */
  span_hours: number;
  /** 실제로 찍은 시점 수 × 수집 간격. 꺼져 있던 시간은 포함되지 않는다. FR-5 가드 기준. */
  observed_hours: number;
  /** `n_timepoints / 기대 시점 수`. 1.0=무중단, 0.3=70%가 공백. */
  coverage_ratio: number;
  /** 가장 길게 끊겼던 구간(시간). "언제 꺼져 있었나"를 한 숫자로 보여준다. */
  largest_gap_hours: number;
  /**
   * 라이브 상태로 관측된 **스냅샷 행** 수. 세션 수가 아니다.
   * 한 방송이 10분 간격으로 6번 찍히면 여기서는 6이지만 세션은 1건이다.
   * 세션 수가 필요하면 `sessions.length` 를 쓸 것 — FR-5 가드 기준(5세션)도 그쪽이다.
   */
  n_live_rows: number;
  members: number;
  first: string;
  last: string;
};

/**
 * `enough_coverage`가 false일 때 `peak_ccu`/`avg_ccu`/`ccu_per_1k_followers`는
 * `null`일 수 있다 — 세션이 아직 없다는 뜻이다. UI는 이 상태에서 결론성
 * 차트 대신 "데이터 수집 중" 상태를 보여줘야 한다(FR-5).
 */
export type Member08 = MemberBase & {
  rank: number;
  followers: number;
  follower_delta: number;
  follower_per_day: number;
  n_sessions: number;
  n_live_points: number;
  peak_ccu: number | null;
  avg_ccu: number | null;
  ccu_per_1k_followers: number | null;
};

export type Data08 = {
  meta: Meta08;
  coverage: Coverage08;
  /** FR-5 커버리지 가드: 관측 24시간 미만 또는 세션 5건 미만이면 false. */
  enough_coverage: boolean;
  members: Member08[];
  sessions: unknown[];
  ccu_series: Record<string, unknown>;
};

// ---------------------------------------------------------------------------
// 09 · DART 재무 — 회사 단위 (PRD Phase 2)
//
// ⚠ 01~06·08과 달리 `members[]`가 없다. 의도된 설계다: 이 프로젝트의 조인 키는
// 멤버(name_en)가 아니라 회사(corp_name)×회계연도(bsns_year)다. 그래서 이 절의
// 타입은 `MemberBase`를 확장하지 않고, 전역 멤버/유닛 필터(FR-1)도 이 프로젝트
// 페이지에는 걸지 않는다 — 대신 회사·연도 필터를 페이지 자체가 로컬로 갖는다.
//
// 스텔라이브 본체·Brave group(일본 모기업)은 DART 118,701개 법인 기업코드
// 마스터 전체에 없다. 팬딩은 기업코드는 있지만 감사보고서 제출 이력이 0건이다.
// 재무 수치를 확보한 곳은 NAVER·SOOP(XBRL 정기보고서) 2곳과, 감사보고서
// 원문(document.xml)을 직접 파싱해 확보한 샌드박스네트워크·패러블엔터테인먼트
// 2곳뿐이다 — 자세한 경위는 /methodology 05번 카드(DART XBRL 커버리지 한계).
// ---------------------------------------------------------------------------

export type Meta09 = {
  fetched_at: string;
  source: string;
  /** DART corpCode.xml 전체 법인 수(118,701) — "찾아봤지만 없더라"의 분모. */
  corp_master_total: number;
  n_targets: number;
  n_matched: number;
  n_with_financials: number;
  n_with_audit_report_financials: number;
  /** [시작연도, 끝연도] — 조회를 시도한 회계연도 범위(2016~2025). 회사마다 실제 확보 범위는 다르다. */
  years: number[];
  note: string;
};

export type TargetSearch09 = {
  query: string;
  label: string;
  category: string;
  context: string;
  matched: boolean;
  n_candidates: number;
  corp_code: string | null;
  corp_name: string | null;
  corp_eng_name: string | null;
  stock_code: string | null;
  note: string;
};

/** 회사×회계연도 1행. `fs_div`가 회사·연도마다 CFS(연결)/OFS(별도)로 섞여 있다 — 표에 그대로 노출한다. */
export type Company09 = {
  corp_name: string;
  bsns_year: number;
  fs_div: string;
  assets: number;
  liabilities: number;
  equity: number;
  revenue: number;
  operating_income: number;
  net_income: number;
  operating_margin: number;
  net_margin: number;
  asset_turnover: number;
  equity_ratio: number;
  debt_to_equity: number;
  revenue_yoy: number | null;
  operating_income_yoy: number | null;
};

export type FandomContext09 = {
  note: string;
  project01: {
    fetched_at: string;
    n_members: number;
    total_subscribers: number;
    total_recent_avg_views: number;
  };
  project08: {
    fetched_at: string;
    coverage: {
      n_snapshots: number;
      n_timepoints: number;
      span_hours: number;
      n_live_rows: number;
      members: number;
      first: string;
      last: string;
    };
    enough_coverage: boolean;
    total_follower_delta: number;
  };
};

export type Data09 = {
  meta: Meta09;
  target_search: TargetSearch09[];
  companies: Company09[];
  /** 회사명 → { DART 상태 코드: 건수 }. "013"은 XBRL 데이터 없음(정기보고서 미태깅). */
  status_summary: Record<string, Record<string, number>>;
  /** 회사명 → { 감사보고서 원문 파싱 상태: 건수 }. "NO_FILINGS"는 제출 이력 자체가 없음. */
  audit_status_summary: Record<string, Record<string, number>>;
  fandom_context: FandomContext09;
};

// ---------------------------------------------------------------------------
// 10 · 호요버스 — 캐릭터 단위 (PRD Phase 2)
//
// ⚠ 09와 같은 이유로 `members[]`가 없다. 조인 키는 `char_id`(게임 내 캐릭터
// ID)다. 원신·붕괴:스타레일 두 게임을 다루고, 필터는 멤버/유닛이 아니라
// 게임·희귀도(rank)다. Zenless Zone Zero는 작동하는 데이터 소스가 없어
// 수집 대상에서 제외했다(코드/데이터에 흔적 없음 — README에만 기록).
//
// Google Trends(pytrends)는 매 실행 HTTP 429로 죽어 있어 폐기했다 — 가짜
// 데이터로 채우지 않고 `trends_status`에 실패를 그대로 남긴다
// (/methodology 06번 카드). "공식 푸시"는 실제 배너 데이터가 없어 5★
// 캐릭터의 출시 최신성(release_unix)으로 근사한 값이다 — `push_rank`는
// 프록시이지 실측 배너율이 아니다.
// ---------------------------------------------------------------------------

export type Meta10 = {
  fetched_at: string;
  source: string;
  n_characters: number;
  /** 원신 여행자·스타레일 개척자 등 플레이어 아바타 — 팬 인기 캐릭터가 아니라서 이미 제외된 수. */
  n_playable_avatars_excluded: number;
  n_reviews: number;
  games: string[];
  google_trends_ok: boolean;
  google_trends_error: string;
  n_reviews_requested_per_app: number;
};

export type TrendsStatus10 = {
  attempted_at: string;
  ok: boolean;
  library: string;
  error: string;
  note: string;
};

export type AppSummary10 = {
  game: string;
  name_ko: string;
  package: string;
  title: string;
  score: number;
  ratings: number;
  reviews_total: number;
  installs: string;
  version: string;
};

/**
 * 캐릭터 1명. `push_rank`/`audience_rank`는 전체 캐릭터 배열에서는 순위가 없는
 * 캐릭터에 `null`이 온다(리뷰에서 언급이 매칭되지 않았거나 5★가 아니라 push
 * 대상이 아닌 경우 등). `gap`은 `gap_overpushed`/`gap_sleeper` 배열에만 있는
 * 파생 필드(= push_rank - audience_rank 부호 반전 근사)다.
 */
export type Character10 = {
  game: string;
  name_ko_game: string;
  char_id: string;
  name_ko: string;
  route_en: string;
  /** 캐릭터 희귀도(4 또는 5) — "희귀도" 필터가 이 값을 쓴다. */
  rank: number;
  element: string;
  weapon_or_path: string;
  is_playable_avatar: boolean;
  release_unix: number;
  release_date: string;
  name_len: number;
  name_ambiguous: boolean;
  matchable: boolean;
  mention_count: number | null;
  avg_mention_score: number | null;
  mention_rate_per_10k: number | null;
  game_avg_score: number;
  sentiment_vs_baseline: number | null;
  push_rank?: number | null;
  audience_rank?: number | null;
  gap?: number;
};

export type MonthlySentiment10 = { game: string; month: string; avg_score: number; n_reviews: number };

export type Data10 = {
  meta: Meta10;
  trends_status: TrendsStatus10;
  app_summary: AppSummary10[];
  characters: Character10[];
  /** `characters`를 push_rank 기준 상위 15명으로 미리 뽑아둔 배열(원본 그대로). */
  push_top: Character10[];
  /** `characters`를 audience_rank 기준 상위 15명으로 미리 뽑아둔 배열(원본 그대로). */
  audience_top: Character10[];
  monthly_sentiment: MonthlySentiment10[];
  /** push_rank는 높은데(많이 밀었는데) audience_rank는 낮은(반응이 적은) 캐릭터. */
  gap_overpushed: Character10[];
  /** push_rank는 낮은데(안 밀었는데) audience_rank는 높은(반응이 큰) 캐릭터 — 숨은 인기. */
  gap_sleeper: Character10[];
  n_matchable_low_confidence: number;
};

// ---------------------------------------------------------------------------
// 11 · 팬 커머스 (PRD Phase 2) — 플랫폼/회사 단위
//
// ⚠ 이 프로젝트는 다른 세션이 동시에 만들고 있었다 — 이 세션 도중 소스가
// 도착했다. `sync-data.mjs`는 소스가 없을 때만 `{ available: false, note }`
// 플레이스홀더를 쓰고, 있으면 그대로 복사한다. 그래서 `Data11`은 두 상태의
// 유니온이다: 플레이스홀더(`Data11NotReady`, `available: false`를 갖는 합성
// 객체)와 실제 데이터(`Data11Ready`, 원본에 `available` 필드 자체가 없다).
// 판별은 `available` 값이 아니라 `"fanding" in data`로 한다(`isData11Ready`).
//
// 팬딩(멤버십 티어) + 크라우드펀딩(텀블벅 굿즈·팬메이드 광고) + 09에서 이미
// 확보한 재무(샌드박스네트워크·패러블엔터테인먼트)를 재사용한다 — DART를
// 다시 수집하지 않는다(meta.source에 명시).
// ---------------------------------------------------------------------------

export type Meta11 = {
  fetched_at: string;
  source: string;
  n_fanding_creators: number;
  n_fanding_creators_with_tiers: number;
  n_fanding_tiers: number;
  n_crowdfunding_projects: number;
  n_financial_company_years: number;
  /** 텀블벅 robots.txt가 /api/(실제 모금액·후원자 수 출처)를 막는다 — 자동 수집 불가. */
  tumblbug_blocked_by_robots: boolean;
  tumblbug_robots_rule: string;
  wadiz_note: string;
};

export type FandingStats11 = {
  n_tiers: number;
  n_creators_with_tiers: number;
  min_price: number;
  max_price: number;
  median_price: number;
  mean_price: number;
  /** 스텔라이브 계열 팬딩 티어 가격(있으면). */
  stellive_prices: number[];
  /** 전체 티어 가격 분포에서 스텔라이브 계열 가격의 백분위. */
  stellive_percentile: number;
};

export type FandingCreator11 = {
  creator_url: string;
  nickname: string;
  n_tiers: number;
  min_price: number;
  max_price: number;
  avg_price: number;
};

export type FandingTier11 = {
  creator_url: string;
  nickname: string;
  tier_index: number;
  tier_title: string;
  price_krw: number;
};

export type Fanding11 = {
  stats: FandingStats11;
  creator_summary: FandingCreator11[];
  tiers: FandingTier11[];
};

/**
 * 텀블벅 크라우드펀딩 1건. 공식 굿즈 펀딩(패러블/이세계아이돌)은 언론 보도·
 * 나무위키 사후 집계, 팬메이드 광고는 텀블벅 프로젝트 페이지 직접 열람으로
 * 얻었다(robots.txt가 막는 /api/를 우회하지 않았다) — `source_type`에 그대로
 * 남아 있다. 팬메이드 광고 펀딩은 회사 매출이 아니다(각 `note` 참고).
 */
export type Crowdfunding11 = {
  project_name: string;
  org: string;
  category: string;
  platform: string;
  slug: string;
  period_start: string;
  period_end: string;
  goal_krw: number;
  /** true면 목표 금액이 원본 소스에 없어 추정한 값 — 표에 그대로 밝힌다. */
  goal_estimated: boolean;
  raised_krw: number;
  backers: number;
  source_url: string;
  source_type: string;
  note: string;
  achievement_pct: number;
  per_backer_krw: number;
};

export type Data11Ready = {
  meta: Meta11;
  fanding: Fanding11;
  crowdfunding: Crowdfunding11[];
  /** 09(DART 재무)와 같은 회사×연도 형태 — 샌드박스네트워크·패러블엔터테인먼트만 재사용. */
  financials: Company09[];
};

export type Data11NotReady = {
  available: false;
  note: string;
};

export type Data11 = Data11Ready | Data11NotReady;

/** `available` 필드가 아니라 실제 데이터에만 있는 `fanding` 키로 판별한다. */
export function isData11Ready(data: Data11): data is Data11Ready {
  return "fanding" in data;
}

// ---------------------------------------------------------------------------
// 프로젝트 id → 데이터 타입 맵 (제네릭 유틸에 사용)
// ---------------------------------------------------------------------------

export type ProjectDataMap = {
  "01": Data01;
  "02": Data02;
  "03": Data03;
  "04": Data04;
  "05": Data05;
  "06": Data06;
  "08": Data08;
};
