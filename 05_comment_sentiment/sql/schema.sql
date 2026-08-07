-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
    comment_id TEXT PRIMARY KEY,
    video_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    author TEXT,
    text TEXT,
    like_count INTEGER,
    published_at TEXT,
    sid INTEGER,
    sentiment TEXT,
    topic TEXT,
    topic_ko TEXT,
    sentiment_ko TEXT
);

DROP TABLE IF EXISTS sentiment_metrics;
CREATE TABLE sentiment_metrics (
    rank INTEGER,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    n_comments INTEGER,
    positive_share REAL,
    negative_share REAL,
    neutral_share REAL,
    sentiment_score REAL,
    top_topic TEXT,
    avg_likes REAL
);
