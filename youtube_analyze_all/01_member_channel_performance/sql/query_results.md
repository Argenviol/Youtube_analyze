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
|    1 | 아야츠노 유니 | EVERYS   | 362000 |    144468 |
|    2 | 아카네 리제  | UNIVERSE | 360000 |    283804 |
|    3 | 시라유키 히나 | UNIVERSE | 321000 |    179795 |
|    4 | 아오쿠모 린  | CLICHE   | 287000 |    192898 |
|    5 | 아라하시 타비 | UNIVERSE | 264000 |    218039 |
|    6 | 텐코 시부키  | CLICHE   | 232000 |    224096 |
|    7 | 유즈하 리코  | CLICHE   | 225000 |    254329 |
|    8 | 하나코 나나  | CLICHE   | 210000 |    211362 |
|    9 | 네네코 마시로 | UNIVERSE | 186000 |    134502 |
|   10 | 사키하네 후야 | EVERYS   | 137000 |    126001 |


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
| 유즈하 리코  | 225000 |  254329 |      113   |
| 하나코 나나  | 210000 |  211362 |      100.6 |
| 텐코 시부키  | 232000 |  224096 |       96.6 |
| 사키하네 후야 | 137000 |  126001 |       92   |
| 아라하시 타비 | 264000 |  218039 |       82.6 |
| 아카네 리제  | 360000 |  283804 |       78.8 |
| 네네코 마시로 | 186000 |  134502 |       72.3 |
| 아오쿠모 린  | 287000 |  192898 |       67.2 |
| 시라유키 히나 | 321000 |  179795 |       56   |
| 아야츠노 유니 | 362000 |  144468 |       39.9 |


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
| UNIVERSE |    4 |  282750 |  204035 |        3.1  |
| EVERYS   |    2 |  249500 |  135234 |        3.4  |
| CLICHE   |    4 |  238500 |  220671 |        3.15 |


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
| 네네코 마시로 |      3.85 |       3.62 |
| 사키하네 후야 |      3.72 |       3.55 |
| 유즈하 리코  |      3.29 |       3.15 |
| 아오쿠모 린  |      3.22 |       3.08 |
| 시라유키 히나 |      3.11 |       2.95 |
| 아야츠노 유니 |      3.08 |       2.88 |
| 텐코 시부키  |      3.07 |       2.97 |
| 하나코 나나  |      3.03 |       2.92 |
| 아라하시 타비 |      2.73 |       2.6  |
| 아카네 리제  |      2.7  |       2.61 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.98 |         44 |
| 텐코 시부키  |    6.35 |         38 |
| 유즈하 리코  |    5.28 |         40 |
| 아카네 리제  |    5.12 |         38 |
| 아오쿠모 린  |    4.45 |         26 |
| 아라하시 타비 |    3.85 |         12 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                                    | 2193514 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                                         | 1458648 |
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1073619 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        |  993440 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            |  968204 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  770969 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  736547 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  695385 |
| 하나코 나나  | 그게 무슨 말이에요 곰파님                                                        |  540657 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  443031 |

