-- 자동 생성된 스키마 (StelLive 분석)

DROP TABLE IF EXISTS corp_search;
CREATE TABLE corp_search (
    query TEXT,
    label TEXT,
    category TEXT,
    context TEXT,
    matched INTEGER,
    n_candidates INTEGER,
    corp_code TEXT,
    corp_name TEXT,
    corp_eng_name TEXT,
    stock_code TEXT,
    note TEXT
);

DROP TABLE IF EXISTS financials_status;
CREATE TABLE financials_status (
    corp_code TEXT,
    corp_name TEXT,
    bsns_year INTEGER,
    fs_div TEXT,
    reprt_code INTEGER,
    status INTEGER,
    status_msg TEXT,
    n_rows INTEGER
);

DROP TABLE IF EXISTS financials_audit_status;
CREATE TABLE financials_audit_status (
    corp_code TEXT,
    corp_name TEXT,
    bsns_year REAL,
    fs_div TEXT,
    rcept_no REAL,
    report_nm TEXT,
    status TEXT,
    n_rows INTEGER
);

DROP TABLE IF EXISTS financials_raw;
CREATE TABLE financials_raw (
    corp_code TEXT,
    corp_name TEXT,
    bsns_year INTEGER,
    fs_div TEXT,
    sj_div TEXT,
    sj_nm TEXT,
    account_id TEXT,
    account_nm TEXT,
    thstrm_amount REAL,
    frmtrm_amount REAL,
    ord REAL,
    currency TEXT,
    source TEXT,
    rcept_no REAL,
    is_comparative TEXT
);

DROP TABLE IF EXISTS company_metrics;
CREATE TABLE company_metrics (
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
