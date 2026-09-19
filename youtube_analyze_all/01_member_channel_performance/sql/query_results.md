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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    139996 |
|    2 | 아카네 리제  | UNIVERSE | 356000 |    270943 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    180407 |
|    4 | 아오쿠모 린  | CLICHE   | 284000 |    201337 |
|    5 | 아라하시 타비 | UNIVERSE | 262000 |    216790 |
|    6 | 텐코 시부키  | CLICHE   | 230000 |    189787 |
|    7 | 유즈하 리코  | CLICHE   | 222000 |    284394 |
|    8 | 하나코 나나  | CLICHE   | 207000 |    181668 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    121173 |
|   10 | 사키하네 후야 | EVERYS   | 135000 |    118818 |


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
| 유즈하 리코  | 222000 |  284394 |      128.1 |
| 사키하네 후야 | 135000 |  118818 |       88   |
| 하나코 나나  | 207000 |  181668 |       87.8 |
| 아라하시 타비 | 262000 |  216790 |       82.7 |
| 텐코 시부키  | 230000 |  189787 |       82.5 |
| 아카네 리제  | 356000 |  270943 |       76.1 |
| 아오쿠모 린  | 284000 |  201337 |       70.9 |
| 네네코 마시로 | 184000 |  121173 |       65.9 |
| 시라유키 히나 | 320000 |  180407 |       56.4 |
| 아야츠노 유니 | 361000 |  139996 |       38.8 |


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
| UNIVERSE |    4 |  280500 |  197328 |        3.52 |
| EVERYS   |    2 |  248000 |  129406 |        3.7  |
| CLICHE   |    4 |  235750 |  214296 |        3.73 |


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
| 네네코 마시로 |      4.33 |       4.08 |
| 하나코 나나  |      4.12 |       3.96 |
| 사키하네 후야 |      3.98 |       3.81 |
| 텐코 시부키  |      3.93 |       3.81 |
| 유즈하 리코  |      3.49 |       3.34 |
| 시라유키 히나 |      3.43 |       3.25 |
| 아야츠노 유니 |      3.41 |       3.18 |
| 아오쿠모 린  |      3.4  |       3.24 |
| 아카네 리제  |      3.17 |       3.06 |
| 아라하시 타비 |      3.13 |       2.96 |


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
| 하나코 나나  |    6.47 |         52 |
| 유즈하 리코  |    5.53 |         40 |
| 아카네 리제  |    5.04 |         40 |
| 아오쿠모 린  |    4.23 |         22 |
| 아라하시 타비 |    4.04 |         18 |
| 사키하네 후야 |    3.5  |         22 |
| 시라유키 히나 |    3.43 |         38 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 2014082 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1543008 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1421828 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts             |  979262 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  843157 |
| 아카네 리제  | 사쵸의 리제 성대모사 #vtuber #shorts                                |  774168 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  687952 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD             |  657404 |
| 하나코 나나  | 논브레스 오블리주 [ノンブレス・オブリージュ / ピノキオピー ] / 하나코 나나 COVER          |  623761 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  408024 |

