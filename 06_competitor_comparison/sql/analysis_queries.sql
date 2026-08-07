-- 경쟁사 비교 분석 쿼리 (SQLite: sql/competitors.db)

-- 그룹별 요약 비교
SELECT "group" AS 그룹, n_members AS 인원, CAST(avg_subscribers AS INT) AS 평균구독자,
       CAST(avg_recent_views AS INT) AS 평균조회수,
       ROUND(avg_engagement_rate*100,2) AS 참여율_pct,
       ROUND(avg_reach_ratio*100,1) AS 도달효율_pct
FROM group_summary ORDER BY 평균구독자 DESC;

-- 전체 멤버 구독자 랭킹
SELECT rank AS 순위, "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자
FROM member_metrics ORDER BY subscribers DESC;

-- 참여율 상위 10명
SELECT "group" AS 그룹, name_ko AS 멤버,
       ROUND(recent_avg_engagement_rate*100,2) AS 참여율_pct
FROM member_metrics ORDER BY recent_avg_engagement_rate DESC LIMIT 10;

-- 도달 효율 상위 10명
SELECT "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자,
       ROUND(reach_ratio*100,0) AS 도달효율_pct
FROM member_metrics ORDER BY reach_ratio DESC LIMIT 10;
