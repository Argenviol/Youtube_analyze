-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS characters;
CREATE TABLE characters (
    game TEXT,
    name_ko_game TEXT,
    char_id TEXT PRIMARY KEY,
    name_ko TEXT,
    route_en TEXT,
    rank INTEGER,
    element TEXT,
    weapon_or_path TEXT,
    is_playable_avatar INTEGER,
    release_unix INTEGER,
    release_date TEXT,
    name_len INTEGER,
    name_ambiguous INTEGER,
    matchable INTEGER,
    mention_count REAL,
    avg_mention_score REAL,
    mention_rate_per_10k REAL,
    game_avg_score REAL,
    sentiment_vs_baseline REAL,
    push_rank REAL,
    audience_rank REAL
);

DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    game TEXT,
    name_ko TEXT,
    review_id TEXT PRIMARY KEY,
    content TEXT,
    score INTEGER,
    thumbs_up INTEGER,
    at TEXT,
    app_version TEXT
);

DROP TABLE IF EXISTS monthly_sentiment;
CREATE TABLE monthly_sentiment (
    game TEXT,
    month TEXT,
    avg_score REAL,
    n_reviews INTEGER
);

DROP TABLE IF EXISTS app_summary;
CREATE TABLE app_summary (
    game TEXT,
    name_ko TEXT,
    package TEXT,
    title TEXT,
    score REAL,
    ratings INTEGER,
    reviews_total INTEGER,
    installs TEXT,
    version TEXT
);
