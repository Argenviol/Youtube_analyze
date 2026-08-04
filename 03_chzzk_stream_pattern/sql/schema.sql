-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS streams;
CREATE TABLE streams (
    video_no INTEGER PRIMARY KEY,
    chzzk_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    title TEXT,
    publish_date TEXT,
    duration_sec INTEGER,
    category TEXT,
    category_type TEXT,
    read_count INTEGER
);

DROP TABLE IF EXISTS stream_metrics;
CREATE TABLE stream_metrics (
    rank INTEGER,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    followers INTEGER,
    stream_count INTEGER,
    span_days INTEGER,
    streams_per_week REAL,
    avg_duration_h REAL,
    median_duration_h REAL,
    total_hours REAL,
    hours_per_week REAL,
    avg_start_hour REAL,
    night_share REAL,
    game_share REAL,
    talk_share REAL,
    top_category TEXT,
    avg_vod_views INTEGER
);
