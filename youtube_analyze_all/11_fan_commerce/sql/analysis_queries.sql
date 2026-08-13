-- 팬 커머스 분석 쿼리 (SQLite: sql/fan_commerce.db)

-- 팬딩 VTuber 멤버십 가격 랭킹 (크리에이터별 평균가)
SELECT nickname AS 크리에이터, n_tiers AS 티어수, min_price AS 최저가,
       max_price AS 최고가, avg_price AS 평균가
FROM fanding_creator_summary ORDER BY avg_price DESC LIMIT 15;

-- 스텔라이브 팬딩 멤버십 티어
SELECT nickname AS 크리에이터, tier_title AS 티어명, price_krw AS 가격
FROM fanding_tiers WHERE creator_url = 'stellive';

-- 텀블벅 크라우드펀딩 프로젝트 랭킹 (모금액순)
SELECT project_name AS 프로젝트, category AS 구분, goal_krw AS 목표금액,
       raised_krw AS 모인금액, backers AS 후원자수, achievement_pct AS 달성률_pct,
       per_backer_krw AS 인당후원액
FROM crowdfunding_projects ORDER BY raised_krw DESC;

-- 크라우드펀딩 구분별(공식/팬메이드) 평균 지표
SELECT category AS 구분, COUNT(*) AS 프로젝트수, ROUND(AVG(achievement_pct),0) AS 평균달성률_pct,
       ROUND(AVG(per_backer_krw),0) AS 평균인당후원액
FROM crowdfunding_projects GROUP BY category;

-- 회사별 최신 연도 매출·영업이익
SELECT corp_name AS 법인, bsns_year AS 사업연도, fs_div AS 구분,
       ROUND(revenue/1e8,1) AS 매출_억원, ROUND(operating_income/1e8,1) AS 영업이익_억원,
       ROUND(operating_margin*100,1) AS 영업이익률_pct
FROM company_financials
WHERE (corp_name, bsns_year) IN (
    SELECT corp_name, MAX(bsns_year) FROM company_financials GROUP BY corp_name
);

-- 샌드박스네트워크 영업손실 연속 연도
SELECT bsns_year AS 사업연도, ROUND(revenue/1e8,1) AS 매출_억원,
       ROUND(operating_income/1e8,1) AS 영업이익_억원
FROM company_financials WHERE corp_name = '샌드박스네트워크' ORDER BY bsns_year;
