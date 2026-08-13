-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS videos;
CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT,
    group TEXT,
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
    rank INTEGER,
    group TEXT,
    channel_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    subscribers INTEGER,
    total_views INTEGER,
    video_count INTEGER,
    recent_avg_views REAL,
    recent_avg_engagement_rate REAL,
    uploads_per_week REAL,
    reach_ratio REAL
);

DROP TABLE IF EXISTS group_summary;
CREATE TABLE group_summary (
    group TEXT,
    n_members INTEGER,
    avg_subscribers REAL,
    median_subscribers REAL,
    total_subscribers INTEGER,
    avg_recent_views REAL,
    avg_engagement_rate REAL,
    avg_uploads_per_week REAL,
    avg_reach_ratio REAL
);
