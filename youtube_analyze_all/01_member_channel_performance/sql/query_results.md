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
|    1 | 아야츠노 유니 | EVERYS   | 362000 |    143304 |
|    2 | 아카네 리제  | UNIVERSE | 359000 |    286605 |
|    3 | 시라유키 히나 | UNIVERSE | 321000 |    178938 |
|    4 | 아오쿠모 린  | CLICHE   | 287000 |    192347 |
|    5 | 아라하시 타비 | UNIVERSE | 264000 |    213930 |
|    6 | 텐코 시부키  | CLICHE   | 232000 |    228100 |
|    7 | 유즈하 리코  | CLICHE   | 225000 |    252457 |
|    8 | 하나코 나나  | CLICHE   | 210000 |    212562 |
|    9 | 네네코 마시로 | UNIVERSE | 185000 |    133171 |
|   10 | 사키하네 후야 | EVERYS   | 137000 |    125248 |


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
| 유즈하 리코  | 225000 |  252457 |      112.2 |
| 하나코 나나  | 210000 |  212562 |      101.2 |
| 텐코 시부키  | 232000 |  228100 |       98.3 |
| 사키하네 후야 | 137000 |  125248 |       91.4 |
| 아라하시 타비 | 264000 |  213930 |       81   |
| 아카네 리제  | 359000 |  286605 |       79.8 |
| 네네코 마시로 | 185000 |  133171 |       72   |
| 아오쿠모 린  | 287000 |  192347 |       67   |
| 시라유키 히나 | 321000 |  178938 |       55.7 |
| 아야츠노 유니 | 362000 |  143304 |       39.6 |


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
| UNIVERSE |    4 |  282250 |  203161 |        3.14 |
| EVERYS   |    2 |  249500 |  134275 |        3.41 |
| CLICHE   |    4 |  238500 |  221366 |        3.15 |


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
| 네네코 마시로 |      3.87 |       3.63 |
| 사키하네 후야 |      3.73 |       3.56 |
| 유즈하 리코  |      3.37 |       3.23 |
| 아오쿠모 린  |      3.19 |       3.05 |
| 텐코 시부키  |      3.15 |       3.05 |
| 시라유키 히나 |      3.12 |       2.96 |
| 아야츠노 유니 |      3.09 |       2.89 |
| 하나코 나나  |      2.88 |       2.77 |
| 아라하시 타비 |      2.8  |       2.66 |
| 아카네 리제  |      2.76 |       2.67 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.98 |         46 |
| 텐코 시부키  |    6.24 |         40 |
| 유즈하 리코  |    5.36 |         42 |
| 아카네 리제  |    5.04 |         40 |
| 아오쿠모 린  |    4.45 |         24 |
| 아라하시 타비 |    3.9  |         12 |
| 시라유키 히나 |    3.57 |         36 |
| 사키하네 후야 |    3.36 |         24 |
| 아야츠노 유니 |    2.83 |         18 |
| 네네코 마시로 |    2.09 |          6 |


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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                                    | 2184194 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                                         | 1456230 |
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1058814 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        |  992714 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            |  962857 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  765966 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  735297 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  694937 |
| 하나코 나나  | 그게 무슨 말이에요 곰파님                                                        |  539458 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  440740 |

