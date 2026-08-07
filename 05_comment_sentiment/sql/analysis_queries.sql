-- StelLive 댓글 감성 분석 쿼리 (SQLite: sql/sentiment.db)

-- 멤버별 감성 점수 랭킹
SELECT rank AS 순위, name_ko AS 멤버, n_comments AS 댓글수,
       ROUND(positive_share*100,0) AS 긍정_pct, ROUND(negative_share*100,0) AS 부정_pct,
       sentiment_score AS 감성점수
FROM sentiment_metrics ORDER BY sentiment_score DESC;

-- 멤버별 주요 토픽
SELECT name_ko AS 멤버, top_topic AS 주요토픽, avg_likes AS 평균좋아요
FROM sentiment_metrics ORDER BY avg_likes DESC;

-- 전체 감성 분포
SELECT sentiment_ko AS 감성, COUNT(*) AS 댓글수
FROM comments GROUP BY sentiment_ko ORDER BY 댓글수 DESC;

-- 토픽별 댓글 수
SELECT topic_ko AS 토픽, COUNT(*) AS 댓글수
FROM comments GROUP BY topic_ko ORDER BY 댓글수 DESC;

-- 좋아요 최다 댓글 TOP 10
SELECT name_ko AS 멤버, text AS 댓글, like_count AS 좋아요, sentiment_ko AS 감성
FROM comments ORDER BY like_count DESC LIMIT 10;
