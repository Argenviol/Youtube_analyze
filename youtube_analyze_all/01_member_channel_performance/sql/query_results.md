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
|    1 | 아야츠노 유니 | EVERYS   | 362000 |    143851 |
|    2 | 아카네 리제  | UNIVERSE | 357000 |    278696 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    165998 |
|    4 | 아오쿠모 린  | CLICHE   | 285000 |    178847 |
|    5 | 아라하시 타비 | UNIVERSE | 263000 |    223796 |
|    6 | 텐코 시부키  | CLICHE   | 231000 |    213406 |
|    7 | 유즈하 리코  | CLICHE   | 223000 |    302239 |
|    8 | 하나코 나나  | CLICHE   | 208000 |    203323 |
|    9 | 네네코 마시로 | UNIVERSE | 185000 |    126629 |
|   10 | 사키하네 후야 | EVERYS   | 136000 |    120087 |


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
| 유즈하 리코  | 223000 |  302239 |      135.5 |
| 하나코 나나  | 208000 |  203323 |       97.8 |
| 텐코 시부키  | 231000 |  213406 |       92.4 |
| 사키하네 후야 | 136000 |  120087 |       88.3 |
| 아라하시 타비 | 263000 |  223796 |       85.1 |
| 아카네 리제  | 357000 |  278696 |       78.1 |
| 네네코 마시로 | 185000 |  126629 |       68.4 |
| 아오쿠모 린  | 285000 |  178847 |       62.8 |
| 시라유키 히나 | 320000 |  165998 |       51.9 |
| 아야츠노 유니 | 362000 |  143851 |       39.7 |


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
| UNIVERSE |    4 |  281250 |  198779 |        3.38 |
| EVERYS   |    2 |  249000 |  131968 |        3.65 |
| CLICHE   |    4 |  236750 |  224453 |        3.44 |


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
| 네네코 마시로 |      4.22 |       3.97 |
| 사키하네 후야 |      3.97 |       3.8  |
| 하나코 나나  |      3.56 |       3.42 |
| 텐코 시부키  |      3.49 |       3.38 |
| 유즈하 리코  |      3.4  |       3.25 |
| 시라유키 히나 |      3.37 |       3.18 |
| 아야츠노 유니 |      3.33 |       3.1  |
| 아오쿠모 린  |      3.32 |       3.17 |
| 아카네 리제  |      3.04 |       2.93 |
| 아라하시 타비 |      2.89 |       2.73 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.15 |         48 |
| 텐코 시부키  |    6.24 |         44 |
| 유즈하 리코  |    5.53 |         44 |
| 아카네 리제  |    5.12 |         40 |
| 아오쿠모 린  |    4.13 |         22 |
| 아라하시 타비 |    3.94 |         16 |
| 시라유키 히나 |    3.54 |         36 |
| 사키하네 후야 |    3.4  |         24 |
| 아야츠노 유니 |    2.81 |         16 |
| 네네코 마시로 |    1.97 |          8 |


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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 2075332 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1581486 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1434166 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts             |  983717 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  894094 |
| 아카네 리제  | 사쵸의 리제 성대모사 #vtuber #shorts                                |  779920 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD             |  704387 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  690372 |
| 하나코 나나  | 논브레스 오블리주 [ノンブレス・オブリージュ / ピノキオピー ] / 하나코 나나 COVER          |  673357 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover       |  416169 |

