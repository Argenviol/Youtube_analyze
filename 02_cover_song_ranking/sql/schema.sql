-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS covers;
CREATE TABLE covers (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    title TEXT,
    published_at TEXT,
    views INTEGER,
    likes REAL,
    comments REAL,
    is_collab INTEGER,
    engagement_rate REAL
);

DROP TABLE IF EXISTS cover_metrics;
CREATE TABLE cover_metrics (
    rank INTEGER,
    channel_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    cover_count INTEGER,
    total_views INTEGER,
    avg_views REAL,
    median_views REAL,
    max_views INTEGER,
    best_cover TEXT,
    total_likes INTEGER,
    avg_engagement_rate REAL,
    collab_share REAL
);
