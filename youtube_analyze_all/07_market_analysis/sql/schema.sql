-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS market_facts;
CREATE TABLE market_facts (
    metric TEXT,
    category TEXT,
    value REAL,
    unit TEXT,
    year INTEGER,
    region TEXT,
    source_name TEXT,
    source_url TEXT,
    note TEXT
);

DROP TABLE IF EXISTS stellive_milestones;
CREATE TABLE stellive_milestones (
    date TEXT,
    event TEXT,
    category TEXT
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
