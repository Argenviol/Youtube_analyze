-- 호요버스 캐릭터 인기도 분석 쿼리 (SQLite: sql/hoyoverse.db)

-- 공식 푸시 TOP 15 (5성·출시 최신순)
SELECT push_rank AS 순위, name_ko AS 캐릭터, name_ko_game AS 게임, release_date AS 출시일
FROM characters WHERE push_rank IS NOT NULL ORDER BY push_rank LIMIT 15;

-- 유저 반응 TOP 15 (리뷰 언급량)
SELECT audience_rank AS 순위, name_ko AS 캐릭터, name_ko_game AS 게임,
       mention_count AS 언급수, avg_mention_score AS 언급리뷰평균평점
FROM characters WHERE audience_rank IS NOT NULL ORDER BY audience_rank LIMIT 15;

-- 리뷰에서 한 번도 언급되지 않은 캐릭터 수 (게임별)
SELECT name_ko_game AS 게임, COUNT(*) AS 무언급_캐릭터수
FROM characters WHERE matchable=1 AND mention_count=0 GROUP BY name_ko_game;

-- 게임별 월간 평균 평점
SELECT game AS 게임, month AS 월, avg_score AS 평균평점, n_reviews AS 리뷰수
FROM monthly_sentiment ORDER BY game, month;

-- 언급 리뷰 평점이 게임 평균보다 높은 캐릭터 TOP 10
SELECT name_ko AS 캐릭터, name_ko_game AS 게임, mention_count AS 언급수,
       avg_mention_score AS 언급리뷰평점, sentiment_vs_baseline AS 기준선대비
FROM characters WHERE mention_count >= 5
ORDER BY sentiment_vs_baseline DESC LIMIT 10;
