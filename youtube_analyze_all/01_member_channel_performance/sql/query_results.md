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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    133428 |
|    2 | 아카네 리제  | UNIVERSE | 356000 |    306407 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    183298 |
|    4 | 아오쿠모 린  | CLICHE   | 284000 |    193724 |
|    5 | 아라하시 타비 | UNIVERSE | 262000 |    205860 |
|    6 | 텐코 시부키  | CLICHE   | 230000 |    212942 |
|    7 | 유즈하 리코  | CLICHE   | 222000 |    294195 |
|    8 | 하나코 나나  | CLICHE   | 206000 |    179523 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    114826 |
|   10 | 사키하네 후야 | EVERYS   | 135000 |    115011 |


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
| 유즈하 리코  | 222000 |  294195 |      132.5 |
| 텐코 시부키  | 230000 |  212942 |       92.6 |
| 하나코 나나  | 206000 |  179523 |       87.1 |
| 아카네 리제  | 356000 |  306407 |       86.1 |
| 사키하네 후야 | 135000 |  115011 |       85.2 |
| 아라하시 타비 | 262000 |  205860 |       78.6 |
| 아오쿠모 린  | 284000 |  193724 |       68.2 |
| 네네코 마시로 | 184000 |  114826 |       62.4 |
| 시라유키 히나 | 320000 |  183298 |       57.3 |
| 아야츠노 유니 | 361000 |  133428 |       37   |


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
| UNIVERSE |    4 |  280500 |  202597 |        3.64 |
| EVERYS   |    2 |  248000 |  124219 |        3.98 |
| CLICHE   |    4 |  235500 |  220095 |        3.85 |


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
| 네네코 마시로 |      4.45 |       4.19 |
| 사키하네 후야 |      4.44 |       4.24 |
| 하나코 나나  |      4.35 |       4.17 |
| 텐코 시부키  |      3.99 |       3.86 |
| 유즈하 리코  |      3.6  |       3.44 |
| 시라유키 히나 |      3.56 |       3.37 |
| 아야츠노 유니 |      3.51 |       3.27 |
| 아오쿠모 린  |      3.46 |       3.3  |
| 아카네 리제  |      3.28 |       3.15 |
| 아라하시 타비 |      3.27 |       3.09 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.47 |         48 |
| 하나코 나나  |    6.12 |         50 |
| 유즈하 리코  |    5.53 |         40 |
| 아카네 리제  |    5.04 |         42 |
| 아오쿠모 린  |    4.23 |         22 |
| 아라하시 타비 |    3.99 |         18 |
| 시라유키 히나 |    3.54 |         38 |
| 사키하네 후야 |    3.54 |         24 |
| 아야츠노 유니 |    2.91 |         18 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1952523 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                 | 1752746 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1502923 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1410332 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1117689 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          | 1011528 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts             |  976511 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  780417 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  685945 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  405402 |

