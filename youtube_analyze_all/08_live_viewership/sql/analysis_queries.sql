-- StelLive 동시시청자 분석 쿼리 (SQLite: sql/viewership.db)

-- 팔로워 증감 랭킹
SELECT rank AS 순위, name_ko AS 멤버, followers AS 팔로워,
       follower_delta AS 증감, follower_per_day AS 일환산
FROM member_metrics ORDER BY follower_delta DESC;

-- 피크 동시시청자 랭킹
SELECT name_ko AS 멤버, peak_ccu AS 피크동시솔, avg_ccu AS 평균동시솔,
       n_sessions AS 관측세션
FROM member_metrics WHERE peak_ccu IS NOT NULL ORDER BY peak_ccu DESC;

-- 팬덤 밀도 (팔로워 1천명당 동시시청자)
SELECT name_ko AS 멤버, followers AS 팔로워, peak_ccu AS 피크동시솔,
       ccu_per_1k_followers AS 밀도
FROM member_metrics WHERE ccu_per_1k_followers IS NOT NULL
ORDER BY ccu_per_1k_followers DESC;

-- 유닛별 팔로워 증감 합계
SELECT unit AS 유닛, COUNT(*) AS 인원, SUM(follower_delta) AS 증감합계
FROM member_metrics GROUP BY unit ORDER BY 증감합계 DESC;

-- 관측된 방송 세션 TOP 10
SELECT name_ko AS 멤버, start_kst AS 시작, observed_min AS 관측분,
       peak_ccu AS 피크, category AS 카테고리
FROM sessions ORDER BY peak_ccu DESC LIMIT 10;
