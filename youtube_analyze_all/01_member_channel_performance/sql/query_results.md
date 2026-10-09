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
|    1 | 아야츠노 유니 | EVERYS   | 362000 |    145180 |
|    2 | 아카네 리제  | UNIVERSE | 361000 |    295506 |
|    3 | 시라유키 히나 | UNIVERSE | 321000 |    179577 |
|    4 | 아오쿠모 린  | CLICHE   | 288000 |    200080 |
|    5 | 아라하시 타비 | UNIVERSE | 265000 |    225871 |
|    6 | 텐코 시부키  | CLICHE   | 232000 |    229877 |
|    7 | 유즈하 리코  | CLICHE   | 226000 |    254870 |
|    8 | 하나코 나나  | CLICHE   | 211000 |    222099 |
|    9 | 네네코 마시로 | UNIVERSE | 186000 |    136984 |
|   10 | 사키하네 후야 | EVERYS   | 137000 |    127182 |


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
| 유즈하 리코  | 226000 |  254870 |      112.8 |
| 하나코 나나  | 211000 |  222099 |      105.3 |
| 텐코 시부키  | 232000 |  229877 |       99.1 |
| 사키하네 후야 | 137000 |  127182 |       92.8 |
| 아라하시 타비 | 265000 |  225871 |       85.2 |
| 아카네 리제  | 361000 |  295506 |       81.9 |
| 네네코 마시로 | 186000 |  136984 |       73.6 |
| 아오쿠모 린  | 288000 |  200080 |       69.5 |
| 시라유키 히나 | 321000 |  179577 |       55.9 |
| 아야츠노 유니 | 362000 |  145180 |       40.1 |


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
| UNIVERSE |    4 |  283250 |  209484 |        3.03 |
| EVERYS   |    2 |  249500 |  136180 |        3.42 |
| CLICHE   |    4 |  239250 |  226731 |        3.06 |


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
| 사키하네 후야 |      3.91 |       3.74 |
| 네네코 마시로 |      3.79 |       3.56 |
| 유즈하 리코  |      3.28 |       3.13 |
| 아오쿠모 린  |      3.13 |       3.01 |
| 시라유키 히나 |      3.09 |       2.93 |
| 아야츠노 유니 |      2.92 |       2.73 |
| 하나코 나나  |      2.91 |       2.81 |
| 텐코 시부키  |      2.91 |       2.81 |
| 아라하시 타비 |      2.64 |       2.51 |
| 아카네 리제  |      2.61 |       2.53 |


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
| 텐코 시부키  |    6.12 |         36 |
| 아카네 리제  |    5.2  |         40 |
| 유즈하 리코  |    5.12 |         42 |
| 아오쿠모 린  |    4.57 |         26 |
| 아라하시 타비 |    3.94 |         12 |
| 시라유키 히나 |    3.43 |         36 |
| 사키하네 후야 |    3.4  |         24 |
| 아야츠노 유니 |    2.81 |         16 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                                    | 2234597 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                                         | 1467922 |
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1133255 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        |  997939 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            |  989796 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  789969 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  740337 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  696965 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  555837 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  451060 |

