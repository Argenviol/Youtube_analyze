-- 버추얼 크리에이터 시장 분석 쿼리 (SQLite: sql/market.db)

-- 시장 규모 전망 (리서치사별)
SELECT source_name AS 출처, year AS 연도, value AS 규모_백만달러
FROM market_facts WHERE category='market_size' ORDER BY source_name, year;

-- 매출원·지역 구조
SELECT metric AS 지표, value AS 비율_pct, source_name AS 출처
FROM market_facts WHERE category IN ('revenue_share','region_share');

-- 치지직 핵심 지표
SELECT metric AS 지표, value AS 값, unit AS 단위, note AS 비고
FROM market_facts WHERE category='platform_kpi';

-- StelLive 성장 타임라인
SELECT date AS 날짜, event AS 이벤트, category AS 구분
FROM stellive_milestones ORDER BY date;
