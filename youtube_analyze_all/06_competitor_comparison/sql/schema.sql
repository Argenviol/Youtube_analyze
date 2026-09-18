-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS videos;
CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT,
    group TEXT,
    cohort TEXT,
    name_ko TEXT,
    name_en TEXT,
    title TEXT,
    published_at TEXT,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    engagement_rate REAL
);

DROP TABLE IF EXISTS member_metrics;
CREATE TABLE member_metrics (
    rank_in_cohort INTEGER,
    group TEXT,
    cohort TEXT,
    generation TEXT,
    debut_date TEXT,
    channel_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    months_since_debut REAL,
    subscribers INTEGER,
    total_views INTEGER,
    video_count INTEGER,
    subs_per_month REAL,
    recent_avg_views REAL,
    recent_avg_engagement_rate REAL,
    uploads_per_week REAL,
    reach_ratio REAL
);

DROP TABLE IF EXISTS cohort_summary;
CREATE TABLE cohort_summary (
    cohort TEXT,
    group TEXT,
    n_members INTEGER,
    avg_months_since_debut REAL,
    median_subscribers REAL,
    avg_subscribers REAL,
    median_subs_per_month REAL,
    avg_recent_views REAL,
    avg_engagement_rate REAL,
    avg_uploads_per_week REAL,
    avg_reach_ratio REAL
);
