-- DART 재무 분석 쿼리 (SQLite: sql/dart.db)

-- 대상 법인 검색 결과
SELECT label AS 대상, category AS 구분, matched AS 기업코드확인, corp_name AS 법인명,
       corp_code AS 기업코드, note AS 비고
FROM corp_search ORDER BY matched DESC, category;

-- 재무제표 확보 현황 (연도별 status)
SELECT corp_name AS 법인명, bsns_year AS 사업연도, fs_div AS 재무제표구분,
       status AS 상태코드, status_msg AS 상태, n_rows AS 계정수
FROM financials_status ORDER BY corp_name, bsns_year, fs_div;

-- 연도별 매출·영업이익 (연결/별도 혼합, company_metrics)
SELECT corp_name AS 법인명, bsns_year AS 사업연도, fs_div AS 구분,
       ROUND(revenue/1e8,0) AS 매출_억원, ROUND(operating_income/1e8,0) AS 영업이익_억원,
       ROUND(operating_margin*100,1) AS 영업이익률_pct
FROM company_metrics WHERE revenue IS NOT NULL ORDER BY corp_name, bsns_year;

-- 자산 대비 매출 효율 랭킹 (연도×회사)
SELECT corp_name AS 법인명, bsns_year AS 사업연도, ROUND(asset_turnover,2) AS 자산회전율,
       ROUND(equity_ratio*100,1) AS 자기자본비율_pct
FROM company_metrics WHERE asset_turnover IS NOT NULL
ORDER BY 자산회전율 DESC LIMIT 10;

-- 013(데이터 없음) 비중 — XBRL(정기보고서) 경로의 한계 정량화
SELECT corp_name AS 법인명,
       SUM(CASE WHEN status='000' THEN 1 ELSE 0 END) AS 성공,
       SUM(CASE WHEN status='013' THEN 1 ELSE 0 END) AS 데이터없음,
       COUNT(*) AS 전체시도
FROM financials_status GROUP BY corp_name ORDER BY 성공 DESC;

-- 감사보고서 원문 파싱 경로 — 필링별 확보 현황
SELECT corp_name AS 법인명, bsns_year AS 사업연도, fs_div AS 재무제표구분,
       report_nm AS 공시명, status AS 상태코드, n_rows AS 추출계정수
FROM financials_audit_status ORDER BY corp_name, bsns_year, fs_div;

-- 비상장 팬덤 인접 기업 재무 (감사보고서 원문 파싱으로 확보, 연결 우선)
SELECT corp_name AS 법인명, bsns_year AS 사업연도, fs_div AS 구분,
       ROUND(revenue/1e8,1) AS 매출_억원, ROUND(operating_income/1e8,1) AS 영업이익_억원,
       ROUND(net_income/1e8,1) AS 당기순이익_억원, ROUND(assets/1e8,1) AS 자산총계_억원
FROM company_metrics
WHERE corp_name IN ('샌드박스네트워크','패러블엔터테인먼트') AND revenue IS NOT NULL
ORDER BY corp_name, bsns_year;
