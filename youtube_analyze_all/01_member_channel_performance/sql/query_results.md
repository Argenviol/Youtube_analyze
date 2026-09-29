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
|    1 | 아야츠노 유니 | EVERYS   | 362000 |    140309 |
|    2 | 아카네 리제  | UNIVERSE | 359000 |    282604 |
|    3 | 시라유키 히나 | UNIVERSE | 321000 |    175009 |
|    4 | 아오쿠모 린  | CLICHE   | 286000 |    182337 |
|    5 | 아라하시 타비 | UNIVERSE | 264000 |    214855 |
|    6 | 텐코 시부키  | CLICHE   | 231000 |    224227 |
|    7 | 유즈하 리코  | CLICHE   | 224000 |    249733 |
|    8 | 하나코 나나  | CLICHE   | 209000 |    212440 |
|    9 | 네네코 마시로 | UNIVERSE | 185000 |    131266 |
|   10 | 사키하네 후야 | EVERYS   | 136000 |    120488 |


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
| 유즈하 리코  | 224000 |  249733 |      111.5 |
| 하나코 나나  | 209000 |  212440 |      101.6 |
| 텐코 시부키  | 231000 |  224227 |       97.1 |
| 사키하네 후야 | 136000 |  120488 |       88.6 |
| 아라하시 타비 | 264000 |  214855 |       81.4 |
| 아카네 리제  | 359000 |  282604 |       78.7 |
| 네네코 마시로 | 185000 |  131266 |       71   |
| 아오쿠모 린  | 286000 |  182337 |       63.8 |
| 시라유키 히나 | 321000 |  175009 |       54.5 |
| 아야츠노 유니 | 362000 |  140309 |       38.8 |


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
| UNIVERSE |    4 |  282250 |  200933 |        3.2  |
| EVERYS   |    2 |  249000 |  130398 |        3.56 |
| CLICHE   |    4 |  237500 |  217184 |        3.29 |


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
| 사키하네 후야 |      4.02 |       3.84 |
| 네네코 마시로 |      3.93 |       3.69 |
| 유즈하 리코  |      3.39 |       3.25 |
| 하나코 나나  |      3.29 |       3.17 |
| 텐코 시부키  |      3.26 |       3.15 |
| 아오쿠모 린  |      3.23 |       3.08 |
| 시라유키 히나 |      3.2  |       3.03 |
| 아야츠노 유니 |      3.1  |       2.89 |
| 아카네 리제  |      2.91 |       2.81 |
| 아라하시 타비 |      2.74 |       2.6  |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.46 |         48 |
| 텐코 시부키  |    6.35 |         40 |
| 유즈하 리코  |    5.44 |         42 |
| 아카네 리제  |    5.04 |         40 |
| 아오쿠모 린  |    4.23 |         22 |
| 아라하시 타비 |    3.81 |         14 |
| 시라유키 히나 |    3.61 |         36 |
| 사키하네 후야 |    3.36 |         24 |
| 아야츠노 유니 |    2.79 |         16 |
| 네네코 마시로 |    2.05 |          6 |


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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                                    | 2136719 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                                         | 1447043 |
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1021526 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        |  989229 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            |  935770 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  743627 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  729893 |
| 하나코 나나  | 논브레스 오블리주 [ノンブレス・オブリージュ / ピノキオピー ] / 하나코 나나 COVER                     |  720745 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  692538 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  430942 |

