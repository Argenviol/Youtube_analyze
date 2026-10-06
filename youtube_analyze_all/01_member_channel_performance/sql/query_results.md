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
|    1 | 아야츠노 유니 | EVERYS   | 362000 |    145260 |
|    2 | 아카네 리제  | UNIVERSE | 360000 |    287419 |
|    3 | 시라유키 히나 | UNIVERSE | 321000 |    180614 |
|    4 | 아오쿠모 린  | CLICHE   | 287000 |    193381 |
|    5 | 아라하시 타비 | UNIVERSE | 265000 |    221704 |
|    6 | 텐코 시부키  | CLICHE   | 232000 |    227241 |
|    7 | 유즈하 리코  | CLICHE   | 225000 |    256496 |
|    8 | 하나코 나나  | CLICHE   | 210000 |    214278 |
|    9 | 네네코 마시로 | UNIVERSE | 186000 |    135254 |
|   10 | 사키하네 후야 | EVERYS   | 137000 |    126211 |


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
| 유즈하 리코  | 225000 |  256496 |      114   |
| 하나코 나나  | 210000 |  214278 |      102   |
| 텐코 시부키  | 232000 |  227241 |       97.9 |
| 사키하네 후야 | 137000 |  126211 |       92.1 |
| 아라하시 타비 | 265000 |  221704 |       83.7 |
| 아카네 리제  | 360000 |  287419 |       79.8 |
| 네네코 마시로 | 186000 |  135254 |       72.7 |
| 아오쿠모 린  | 287000 |  193381 |       67.4 |
| 시라유키 히나 | 321000 |  180614 |       56.3 |
| 아야츠노 유니 | 362000 |  145260 |       40.1 |


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
| UNIVERSE |    4 |  283000 |  206247 |        3.1  |
| EVERYS   |    2 |  249500 |  135735 |        3.36 |
| CLICHE   |    4 |  238500 |  222849 |        3.13 |


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
| 네네코 마시로 |      3.84 |       3.61 |
| 사키하네 후야 |      3.68 |       3.52 |
| 유즈하 리코  |      3.32 |       3.18 |
| 아오쿠모 린  |      3.13 |       3    |
| 시라유키 히나 |      3.1  |       2.94 |
| 텐코 시부키  |      3.05 |       2.96 |
| 아야츠노 유니 |      3.04 |       2.85 |
| 하나코 나나  |      3.03 |       2.92 |
| 아라하시 타비 |      2.77 |       2.64 |
| 아카네 리제  |      2.69 |       2.6  |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    8.17 |         46 |
| 텐코 시부키  |    6.35 |         38 |
| 유즈하 리코  |    5.28 |         40 |
| 아카네 리제  |    5.12 |         38 |
| 아오쿠모 린  |    4.51 |         24 |
| 아라하시 타비 |    3.94 |         14 |
| 시라유키 히나 |    3.57 |         36 |
| 사키하네 후야 |    3.33 |         24 |
| 아야츠노 유니 |    2.81 |         18 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                                    | 2203730 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                                         | 1461969 |
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1092655 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        |  994263 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            |  974047 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  776790 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  737841 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  695787 |
| 하나코 나나  | 그게 무슨 말이에요 곰파님                                                        |  542249 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  445267 |

