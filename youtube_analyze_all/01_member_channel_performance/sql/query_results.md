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
|    1 | 아야츠노 유니 | EVERYS   | 365000 |    152356 |
|    2 | 아카네 리제  | UNIVERSE | 363000 |    300727 |
|    3 | 시라유키 히나 | UNIVERSE | 324000 |    184859 |
|    4 | 아오쿠모 린  | CLICHE   | 291000 |    165068 |
|    5 | 아라하시 타비 | UNIVERSE | 267000 |    234960 |
|    6 | 텐코 시부키  | CLICHE   | 235000 |    237469 |
|    7 | 유즈하 리코  | CLICHE   | 228000 |    267418 |
|    8 | 하나코 나나  | CLICHE   | 213000 |    239702 |
|    9 | 네네코 마시로 | UNIVERSE | 188000 |    139317 |
|   10 | 사키하네 후야 | EVERYS   | 140000 |    128856 |


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
| 유즈하 리코  | 228000 |  267418 |      117.3 |
| 하나코 나나  | 213000 |  239702 |      112.5 |
| 텐코 시부키  | 235000 |  237469 |      101.1 |
| 사키하네 후야 | 140000 |  128856 |       92   |
| 아라하시 타비 | 267000 |  234960 |       88   |
| 아카네 리제  | 363000 |  300727 |       82.8 |
| 네네코 마시로 | 188000 |  139317 |       74.1 |
| 시라유키 히나 | 324000 |  184859 |       57.1 |
| 아오쿠모 린  | 291000 |  165068 |       56.7 |
| 아야츠노 유니 | 365000 |  152356 |       41.7 |


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
| UNIVERSE |    4 |  285500 |  214965 |        3.02 |
| EVERYS   |    2 |  252500 |  140606 |        3.21 |
| CLICHE   |    4 |  241750 |  227414 |        2.94 |


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
| 네네코 마시로 |      3.74 |       3.52 |
| 사키하네 후야 |      3.57 |       3.42 |
| 시라유키 히나 |      3.21 |       3.04 |
| 아오쿠모 린  |      3.17 |       3.04 |
| 유즈하 리코  |      3.16 |       3.03 |
| 아야츠노 유니 |      2.85 |       2.66 |
| 텐코 시부키  |      2.71 |       2.62 |
| 하나코 나나  |      2.71 |       2.61 |
| 아라하시 타비 |      2.65 |       2.52 |
| 아카네 리제  |      2.45 |       2.38 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.62 |         42 |
| 텐코 시부키  |    6.02 |         36 |
| 아카네 리제  |    5.2  |         38 |
| 유즈하 리코  |    5.04 |         42 |
| 아오쿠모 린  |    4.51 |         24 |
| 아라하시 타비 |    3.9  |         14 |
| 시라유키 히나 |    3.57 |         40 |
| 사키하네 후야 |    3.43 |         24 |
| 아야츠노 유니 |    2.77 |         14 |
| 네네코 마시로 |    2.14 |          6 |


## 멤버별 최고 조회수 영상

```sql
SELECT m.name_ko AS 멤버, v.title AS 영상, v.views AS 조회수
FROM videos v
JOIN (SELECT channel_id, MAX(views) AS mx FROM videos GROUP BY channel_id) t
  ON v.channel_id=t.channel_id AND v.views=t.mx
JOIN channel_metrics m ON m.channel_id=v.channel_id
ORDER BY v.views DESC;
```

| 멤버      | 영상                                                                    |     조회수 |
|:--------|:----------------------------------------------------------------------|--------:|
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                                         | 1479450 |
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1164536 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1012625 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        | 1000825 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  810654 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  748273 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  730670 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  699442 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  590371 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  462418 |

