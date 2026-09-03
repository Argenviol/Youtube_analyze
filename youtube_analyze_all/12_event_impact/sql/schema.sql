-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS events;
CREATE TABLE events (
    date TEXT,
    end_date TEXT,
    type TEXT,
    title TEXT,
    members TEXT,
    n_members TEXT,
    n_days TEXT,
    signal TEXT,
    source TEXT,
    note TEXT,
    match_keys TEXT,
    event_id TEXT,
    streak_days TEXT,
    aliases TEXT,
    ongoing TEXT
);

DROP TABLE IF EXISTS vod_multiple;
CREATE TABLE vod_multiple (
    event_id TEXT,
    date TEXT,
    title TEXT,
    type TEXT,
    name_ko TEXT,
    event_views INTEGER,
    baseline_median REAL,
    views_multiple REAL
);

DROP TABLE IF EXISTS impact;
CREATE TABLE impact (
    event_id TEXT,
    date TEXT,
    title TEXT,
    type TEXT,
    name_ko TEXT,
    metric TEXT,
    before_per_day REAL,
    after_per_day REAL,
    change_pct REAL
);

DROP TABLE IF EXISTS ccu;
CREATE TABLE ccu (
    event_id TEXT,
    date TEXT,
    title TEXT,
    name_ko TEXT,
    event_peak_ccu INTEGER,
    usual_peak_ccu INTEGER,
    ccu_multiple REAL
);
