-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS channels;
CREATE TABLE channels (
    channel_id TEXT PRIMARY KEY,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    role TEXT,
    handle TEXT,
    subscribers INTEGER,
    total_views INTEGER,
    video_count INTEGER,
    created_at TEXT,
    country TEXT,
    uploads_playlist TEXT
);

DROP TABLE IF EXISTS videos;
CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    title TEXT,
    published_at TEXT,
    duration TEXT,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    dur_sec INTEGER,
    is_short INTEGER,
    engagement INTEGER,
    engagement_rate REAL,
    like_rate REAL
);

DROP TABLE IF EXISTS channel_metrics;
CREATE TABLE channel_metrics (
    rank_subs INTEGER,
    channel_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    role TEXT,
    handle TEXT,
    subscribers INTEGER,
    total_views INTEGER,
    video_count INTEGER,
    created_at TEXT,
    channel_age_years REAL,
    recent_n INTEGER,
    recent_avg_views REAL,
    recent_median_views REAL,
    recent_max_views INTEGER,
    recent_avg_engagement_rate REAL,
    recent_avg_like_rate REAL,
    uploads_per_week REAL,
    uploads_per_month REAL,
    shorts_share REAL,
    reach_ratio REAL,
    lifetime_views_per_sub REAL,
    lifetime_views_per_video REAL
);
