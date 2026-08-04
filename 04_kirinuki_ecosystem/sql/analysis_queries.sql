-- StelLive 키리누키 생태계 분석 쿼리 (SQLite: sql/kirinuki.db)

-- 멤버별 키리누키 생태계
SELECT rank AS 순위, name_ko AS 멤버, clip_count AS 클립수,
       total_clip_views AS 총조회수, fan_channels AS 팬채널수
FROM member_ecosystem ORDER BY total_clip_views DESC;

-- 상위 키리누키 채널 TOP 10
SELECT rank AS 순위, clip_channel_title AS 채널, subs AS 구독자,
       clip_count AS 클립수, total_views AS 총조회수, primary_member AS 주력멤버
FROM channel_ecosystem ORDER BY total_views DESC LIMIT 10;

-- 팬채널 전문성 분포(다루는 멤버 수)
SELECT members_covered AS 다루는멤버수, COUNT(*) AS 채널수
FROM channel_ecosystem GROUP BY members_covered ORDER BY members_covered;

-- 멤버별 최고 조회 클립
SELECT name_ko AS 멤버, top_clip AS 최고클립, top_clip_views AS 조회수, top_channel AS 제작채널
FROM member_ecosystem ORDER BY top_clip_views DESC;
