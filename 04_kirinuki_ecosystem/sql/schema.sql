-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS clips;
CREATE TABLE clips (
    video_id TEXT PRIMARY KEY,
    clip_channel_id TEXT,
    clip_channel_title TEXT,
    source_member_ko TEXT,
    source_member_en TEXT,
    unit TEXT,
    title TEXT,
    published_at TEXT,
    views INTEGER,
    likes REAL,
    comments REAL,
    clip_channel_subs INTEGER
);

DROP TABLE IF EXISTS member_ecosystem;
CREATE TABLE member_ecosystem (
    rank INTEGER,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    clip_count INTEGER,
    total_clip_views INTEGER,
    avg_clip_views REAL,
    fan_channels INTEGER,
    top_clip TEXT,
    top_clip_views INTEGER,
    top_channel TEXT
);

DROP TABLE IF EXISTS channel_ecosystem;
CREATE TABLE channel_ecosystem (
    rank INTEGER,
    clip_channel_id TEXT PRIMARY KEY,
    clip_channel_title TEXT,
    subs INTEGER,
    clip_count INTEGER,
    total_views INTEGER,
    members_covered INTEGER,
    primary_member TEXT
);
