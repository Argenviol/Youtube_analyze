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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    138750 |
|    2 | 아카네 리제  | UNIVERSE | 356000 |    266395 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    189329 |
|    4 | 아오쿠모 린  | CLICHE   | 284000 |    199560 |
|    5 | 아라하시 타비 | UNIVERSE | 262000 |    214878 |
|    6 | 텐코 시부키  | CLICHE   | 230000 |    204530 |
|    7 | 유즈하 리코  | CLICHE   | 222000 |    297709 |
|    8 | 하나코 나나  | CLICHE   | 207000 |    195711 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    119988 |
|   10 | 사키하네 후야 | EVERYS   | 135000 |    117906 |


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
| 유즈하 리코  | 222000 |  297709 |      134.1 |
| 하나코 나나  | 207000 |  195711 |       94.5 |
| 텐코 시부키  | 230000 |  204530 |       88.9 |
| 사키하네 후야 | 135000 |  117906 |       87.3 |
| 아라하시 타비 | 262000 |  214878 |       82   |
| 아카네 리제  | 356000 |  266395 |       74.8 |
| 아오쿠모 린  | 284000 |  199560 |       70.3 |
| 네네코 마시로 | 184000 |  119988 |       65.2 |
| 시라유키 히나 | 320000 |  189329 |       59.2 |
| 아야츠노 유니 | 361000 |  138750 |       38.4 |


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
| UNIVERSE |    4 |  280500 |  197647 |        3.54 |
| EVERYS   |    2 |  248000 |  128328 |        3.71 |
| CLICHE   |    4 |  235750 |  224377 |        3.75 |


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
| 네네코 마시로 |      4.35 |       4.1  |
| 하나코 나나  |      4.1  |       3.95 |
| 사키하네 후야 |      4    |       3.82 |
| 텐코 시부키  |      3.94 |       3.82 |
| 유즈하 리코  |      3.56 |       3.4  |
| 시라유키 히나 |      3.44 |       3.25 |
| 아야츠노 유니 |      3.42 |       3.18 |
| 아오쿠모 린  |      3.41 |       3.25 |
| 아카네 리제  |      3.24 |       3.12 |
| 아라하시 타비 |      3.14 |       2.97 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    6.47 |         50 |
| 텐코 시부키  |    6.24 |         46 |
| 유즈하 리코  |    5.62 |         42 |
| 아카네 리제  |    5.04 |         40 |
| 아오쿠모 린  |    4.23 |         22 |
| 아라하시 타비 |    4.04 |         18 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1999400 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1533855 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1418801 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1137222 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          | 1021397 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts             |  978399 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  829244 |
| 아카네 리제  | 사쵸의 리제 성대모사 #vtuber #shorts                                |  773071 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  687476 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  407370 |

