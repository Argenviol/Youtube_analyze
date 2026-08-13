-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS snapshots;
CREATE TABLE snapshots (
    collected_at TEXT,
    chzzk_id TEXT,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    role TEXT,
    followers INTEGER,
    status TEXT,
    is_live INTEGER,
    concurrent_users REAL,
    accumulate_count REAL,
    live_title TEXT,
    category TEXT,
    tags TEXT,
    last_concurrent_users REAL
);

DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    start_kst TEXT,
    observed_min REAL,
    n_points INTEGER,
    peak_ccu INTEGER,
    avg_ccu INTEGER,
    title TEXT,
    category TEXT
);

DROP TABLE IF EXISTS member_metrics;
CREATE TABLE member_metrics (
    rank INTEGER,
    name_ko TEXT,
    name_en TEXT,
    unit TEXT,
    followers INTEGER,
    follower_delta INTEGER,
    follower_per_day REAL,
    n_sessions INTEGER,
    n_live_points INTEGER,
    peak_ccu INTEGER,
    avg_ccu INTEGER,
    ccu_per_1k_followers REAL
);
