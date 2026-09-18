-- 경쟁사 비교(데뷔 코호트 매칭) 분석 쿼리 (SQLite: sql/competitors.db)

-- 코호트 × 그룹 요약
SELECT cohort AS 코호트, "group" AS 그룹, n_members AS 인원,
       ROUND(avg_months_since_debut,1) AS 경과개월,
       CAST(median_subscribers AS INT) AS 구독자중앙값,
       CAST(median_subs_per_month AS INT) AS 월평균획득,
       ROUND(avg_engagement_rate*100,2) AS 참여율_pct,
       ROUND(avg_reach_ratio*100,1) AS 도달효율_pct
FROM cohort_summary ORDER BY 코호트, 구독자중앙값 DESC;

-- 코호트 안에서의 구독자 순위
SELECT cohort AS 코호트, rank_in_cohort AS 순위, "group" AS 그룹, name_ko AS 멤버,
       subscribers AS 구독자, ROUND(months_since_debut,1) AS 경과개월
FROM member_metrics WHERE cohort IS NOT NULL
ORDER BY 코호트, 순위;

-- 월평균 구독자 획득 상위 15명
SELECT "group" AS 그룹, name_ko AS 멤버, cohort AS 코호트,
       CAST(subs_per_month AS INT) AS 월평균획득
FROM member_metrics WHERE subs_per_month IS NOT NULL
ORDER BY subs_per_month DESC LIMIT 15;

-- 도달 효율 상위 15명
SELECT "group" AS 그룹, name_ko AS 멤버, cohort AS 코호트, subscribers AS 구독자,
       ROUND(reach_ratio*100,0) AS 도달효율_pct
FROM member_metrics ORDER BY reach_ratio DESC LIMIT 15;
