-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS fanding_tiers;
CREATE TABLE fanding_tiers (
    creator_url TEXT,
    nickname TEXT,
    tier_index INTEGER,
    tier_title TEXT,
    price_krw INTEGER
);

DROP TABLE IF EXISTS fanding_creator_summary;
CREATE TABLE fanding_creator_summary (
    creator_url TEXT,
    nickname TEXT,
    n_tiers INTEGER,
    min_price INTEGER,
    max_price INTEGER,
    avg_price INTEGER
);

DROP TABLE IF EXISTS crowdfunding_projects;
CREATE TABLE crowdfunding_projects (
    project_name TEXT,
    org TEXT,
    category TEXT,
    platform TEXT,
    slug TEXT,
    period_start TEXT,
    period_end TEXT,
    goal_krw INTEGER,
    goal_estimated INTEGER,
    raised_krw INTEGER,
    backers INTEGER,
    achievement_pct REAL,
    per_backer_krw INTEGER
);

DROP TABLE IF EXISTS company_financials;
CREATE TABLE company_financials (
    corp_name TEXT,
    bsns_year INTEGER,
    fs_div TEXT,
    assets REAL,
    liabilities REAL,
    equity REAL,
    revenue REAL,
    operating_income REAL,
    net_income REAL,
    operating_margin REAL,
    net_margin REAL,
    asset_turnover REAL,
    equity_ratio REAL,
    debt_to_equity REAL,
    revenue_yoy REAL,
    operating_income_yoy REAL
);
