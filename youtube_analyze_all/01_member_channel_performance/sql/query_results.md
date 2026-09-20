# 분석 쿼리 실행 결과

`sql/stellive.db`(SQLite)에 대해 `analysis_queries.sql`을 실행한 결과입니다.

## 구독자 상위 랭킹

```sql
SELECT rank_subs AS 순위, name_ko AS 멤버, unit AS 유닛,
       subscribers AS 구독자, recent_avg_views AS 최근평균조회수
FROM channel_metrics ORDER BY subscribers DESC;
```

|   순위 | 멤버      | 유닛       |    구독자 |   최근평균조회수 |
|-----:|:--------|:---------|-------:|----------:|
|    1 | 아야츠노 유니 | EVERYS   | 360000 |    140868 |
|    2 | 아카네 리제  | UNIVERSE | 354000 |    273591 |
|    3 | 시라유키 히나 | UNIVERSE | 319000 |    174742 |
|    4 | 아오쿠모 린  | CLICHE   | 282000 |    202548 |
|    5 | 아라하시 타비 | UNIVERSE | 260000 |    219567 |
|    6 | 텐코 시부키  | CLICHE   | 229000 |    195608 |
|    7 | 유즈하 리코  | CLICHE   | 220000 |    289066 |
|    8 | 하나코 나나  | CLICHE   | 206000 |    187322 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    122169 |
|   10 | 사키하네 후야 | EVERYS   | 134000 |    119420 |


## 도달 효율(평균조회수/구독자) 상위

```sql
SELECT name_ko AS 멤버, subscribers AS 구독자,
       recent_avg_views AS 평균조회수,
       ROUND(reach_ratio*100,1) AS 도달효율_pct
FROM channel_metrics WHERE role='talent'
ORDER BY reach_ratio DESC;
```

| 멤버      |    구독자 |   평균조회수 |   도달효율_pct |
|:--------|-------:|--------:|-----------:|
| 유즈하 리코  | 220000 |  289066 |      131.4 |
| 하나코 나나  | 206000 |  187322 |       90.9 |
| 사키하네 후야 | 134000 |  119420 |       89.1 |
| 텐코 시부키  | 229000 |  195608 |       85.4 |
| 아라하시 타비 | 260000 |  219567 |       84.4 |
| 아카네 리제  | 354000 |  273591 |       77.3 |
| 아오쿠모 린  | 282000 |  202548 |       71.8 |
| 네네코 마시로 | 184000 |  122169 |       66.4 |
| 시라유키 히나 | 319000 |  174742 |       54.8 |
| 아야츠노 유니 | 360000 |  140868 |       39.1 |


## 유닛별 요약

```sql
SELECT unit AS 유닛, COUNT(*) AS 인원,
       CAST(AVG(subscribers) AS INT) AS 평균구독자,
       CAST(AVG(recent_avg_views) AS INT) AS 평균조회수,
       ROUND(AVG(recent_avg_engagement_rate)*100,2) AS 평균참여율_pct
FROM channel_metrics WHERE role='talent'
GROUP BY unit ORDER BY 평균구독자 DESC;
```

| 유닛       |   인원 |   평균구독자 |   평균조회수 |   평균참여율_pct |
|:---------|-----:|--------:|--------:|------------:|
| UNIVERSE |    4 |  279250 |  197517 |        3.29 |
| EVERYS   |    2 |  247000 |  130144 |        3.49 |
| CLICHE   |    4 |  234250 |  218636 |        3.32 |


## 참여율 상위

```sql
SELECT name_ko AS 멤버,
       ROUND(recent_avg_engagement_rate*100,2) AS 참여율_pct,
       ROUND(recent_avg_like_rate*100,2) AS 좋아요율_pct
FROM channel_metrics WHERE role='talent'
ORDER BY recent_avg_engagement_rate DESC;
```

| 멤버      |   참여율_pct |   좋아요율_pct |
|:--------|----------:|-----------:|
| 네네코 마시로 |      4.26 |       4.01 |
| 사키하네 후야 |      3.67 |       3.5  |
| 하나코 나나  |      3.65 |       3.5  |
| 텐코 시부키  |      3.43 |       3.31 |
| 아야츠노 유니 |      3.31 |       3.08 |
| 시라유키 히나 |      3.29 |       3.1  |
| 유즈하 리코  |      3.13 |       2.98 |
| 아오쿠모 린  |      3.06 |       2.9  |
| 아라하시 타비 |      2.81 |       2.65 |
| 아카네 리제  |      2.79 |       2.68 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    6.6  |         50 |
| 텐코 시부키  |    6.47 |         46 |
| 유즈하 리코  |    5.53 |         40 |
| 아카네 리제  |    5.04 |         40 |
| 아오쿠모 린  |    4.13 |         22 |
| 아라하시 타비 |    3.9  |         18 |
| 시라유키 히나 |    3.54 |         38 |
| 사키하네 후야 |    3.5  |         22 |
| 아야츠노 유니 |    2.86 |         16 |
| 네네코 마시로 |    1.96 |          8 |


## 멤버별 최고 조회수 영상

```sql
SELECT m.name_ko AS 멤버, v.title AS 영상, v.views AS 조회수
FROM videos v
JOIN (SELECT channel_id, MAX(views) AS mx FROM videos GROUP BY channel_id) t
  ON v.channel_id=t.channel_id AND v.views=t.mx
JOIN channel_metrics m ON m.channel_id=v.channel_id
ORDER BY v.views DESC;
```

| 멤버      | 영상                                                         |     조회수 |
|:--------|:-----------------------------------------------------------|--------:|
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 2023321 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1549165 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1425572 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts             |  980304 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  851755 |
| 아카네 리제  | 사쵸의 리제 성대모사 #vtuber #shorts                                |  775358 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  688427 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD             |  670817 |
| 하나코 나나  | 논브레스 오블리주 [ノンブレス・オブリージュ / ピノキオピー ] / 하나코 나나 COVER          |  631135 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  408717 |

