-- StelLive 커버곡 분석 쿼리 (SQLite: sql/covers.db)

-- 커버곡 조회수 TOP 15
SELECT name_ko AS 멤버, title AS 곡, views AS 조회수, likes AS 좋아요
FROM covers ORDER BY views DESC LIMIT 15;

-- 멤버별 커버 성과 랭킹
SELECT rank AS 순위, name_ko AS 멤버, cover_count AS 곡수,
       total_views AS 총조회수, CAST(avg_views AS INT) AS 평균조회수
FROM cover_metrics ORDER BY total_views DESC;

-- 곡당 평균 조회수 상위(5곡 이상)
SELECT name_ko AS 멤버, cover_count AS 곡수, CAST(avg_views AS INT) AS 평균조회수
FROM cover_metrics WHERE cover_count>=5 ORDER BY avg_views DESC;

-- 멤버별 최고 커버
SELECT name_ko AS 멤버, best_cover AS 최고커버, max_views AS 조회수
FROM cover_metrics ORDER BY max_views DESC;

-- 유닛별 커버 요약
SELECT unit AS 유닛, COUNT(*) AS 멤버수, SUM(cover_count) AS 총곡수,
       SUM(total_views) AS 총조회수
FROM cover_metrics GROUP BY unit ORDER BY 총조회수 DESC;

-- 솔로 vs 콜라보 비중
SELECT name_ko AS 멤버, ROUND(collab_share*100,0) AS 콜라보비중_pct, cover_count AS 곡수
FROM cover_metrics ORDER BY collab_share DESC;
