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
|    1 | 아야츠노 유니 | EVERYS   | 367000 |    153395 |
|    2 | 아카네 리제  | UNIVERSE | 365000 |    306206 |
|    3 | 시라유키 히나 | UNIVERSE | 325000 |    177431 |
|    4 | 아오쿠모 린  | CLICHE   | 293000 |    171538 |
|    5 | 아라하시 타비 | UNIVERSE | 269000 |    213646 |
|    6 | 텐코 시부키  | CLICHE   | 236000 |    243882 |
|    7 | 유즈하 리코  | CLICHE   | 230000 |    265138 |
|    8 | 하나코 나나  | CLICHE   | 215000 |    238636 |
|    9 | 네네코 마시로 | UNIVERSE | 190000 |    141108 |
|   10 | 사키하네 후야 | EVERYS   | 142000 |    128842 |
|   11 | 시즈키 토아  | ABYSS    |  45500 |    150801 |
|   12 | 코가네 랑   | ABYSS    |  45100 |    127335 |


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
| 시즈키 토아  |  45500 |  150801 |      331.4 |
| 코가네 랑   |  45100 |  127335 |      282.3 |
| 유즈하 리코  | 230000 |  265138 |      115.3 |
| 하나코 나나  | 215000 |  238636 |      111   |
| 텐코 시부키  | 236000 |  243882 |      103.3 |
| 사키하네 후야 | 142000 |  128842 |       90.7 |
| 아카네 리제  | 365000 |  306206 |       83.9 |
| 아라하시 타비 | 269000 |  213646 |       79.4 |
| 네네코 마시로 | 190000 |  141108 |       74.3 |
| 아오쿠모 린  | 293000 |  171538 |       58.5 |
| 시라유키 히나 | 325000 |  177431 |       54.6 |
| 아야츠노 유니 | 367000 |  153395 |       41.8 |


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
| UNIVERSE |    4 |  287250 |  209597 |        3.07 |
| EVERYS   |    2 |  254500 |  141118 |        3.35 |
| CLICHE   |    4 |  243500 |  229798 |        3.02 |
| ABYSS    |    2 |   45300 |  139068 |       12.95 |


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
| 코가네 랑   |     13.56 |      11.7  |
| 시즈키 토아  |     12.33 |      10.85 |
| 사키하네 후야 |      3.77 |       3.61 |
| 네네코 마시로 |      3.71 |       3.5  |
| 시라유키 히나 |      3.33 |       3.16 |
| 유즈하 리코  |      3.26 |       3.13 |
| 아오쿠모 린  |      3.19 |       3.06 |
| 아야츠노 유니 |      2.94 |       2.75 |
| 하나코 나나  |      2.84 |       2.75 |
| 텐코 시부키  |      2.78 |       2.69 |
| 아라하시 타비 |      2.71 |       2.58 |
| 아카네 리제  |      2.51 |       2.43 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.62 |         38 |
| 텐코 시부키  |    6.12 |         36 |
| 아카네 리제  |    5.28 |         38 |
| 유즈하 리코  |    5.12 |         42 |
| 아오쿠모 린  |    4.51 |         24 |
| 아라하시 타비 |    3.99 |         12 |
| 시라유키 히나 |    3.65 |         40 |
| 사키하네 후야 |    3.5  |         26 |
| 아야츠노 유니 |    2.81 |         14 |
| 네네코 마시로 |    2.23 |          8 |
| 시즈키 토아  |    0    |          0 |
| 코가네 랑   |    0    |          0 |


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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1180745 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1059874 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1028142 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        | 1002221 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  824066 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  804346 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  751972 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  700613 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  615814 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  472898 |
| 시즈키 토아  | 제육감 [第六感 l Reol] / 시즈키 토아(Shizuki Toa) Cover                          |  150801 |
| 코가네 랑   | 호랑풍류가 [나와 호랑이님 OST] / 코가네 랑 (Cogane Rang) Cover                       |  127335 |

