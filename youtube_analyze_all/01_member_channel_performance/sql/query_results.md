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
|    1 | 아야츠노 유니 | EVERYS   | 372000 |    163023 |
|    2 | 아카네 리제  | UNIVERSE | 370000 |    310120 |
|    3 | 시라유키 히나 | UNIVERSE | 330000 |    182834 |
|    4 | 아오쿠모 린  | CLICHE   | 298000 |    191555 |
|    5 | 아라하시 타비 | UNIVERSE | 274000 |    226437 |
|    6 | 텐코 시부키  | CLICHE   | 242000 |    254497 |
|    7 | 유즈하 리코  | CLICHE   | 235000 |    274128 |
|    8 | 하나코 나나  | CLICHE   | 221000 |    241862 |
|    9 | 네네코 마시로 | UNIVERSE | 196000 |    143583 |
|   10 | 사키하네 후야 | EVERYS   | 149000 |    123550 |


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
| 유즈하 리코  | 235000 |  274128 |      116.7 |
| 하나코 나나  | 221000 |  241862 |      109.4 |
| 텐코 시부키  | 242000 |  254497 |      105.2 |
| 아카네 리제  | 370000 |  310120 |       83.8 |
| 사키하네 후야 | 149000 |  123550 |       82.9 |
| 아라하시 타비 | 274000 |  226437 |       82.6 |
| 네네코 마시로 | 196000 |  143583 |       73.3 |
| 아오쿠모 린  | 298000 |  191555 |       64.3 |
| 시라유키 히나 | 330000 |  182834 |       55.4 |
| 아야츠노 유니 | 372000 |  163023 |       43.8 |


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
| UNIVERSE |    4 |  292500 |  215743 |        2.98 |
| EVERYS   |    2 |  260500 |  143286 |        3.36 |
| CLICHE   |    4 |  249000 |  240510 |        2.82 |


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
| 사키하네 후야 |      3.96 |       3.8  |
| 네네코 마시로 |      3.68 |       3.48 |
| 시라유키 히나 |      3.21 |       3.05 |
| 유즈하 리코  |      3.06 |       2.93 |
| 아오쿠모 린  |      2.87 |       2.75 |
| 하나코 나나  |      2.78 |       2.68 |
| 아야츠노 유니 |      2.76 |       2.59 |
| 아라하시 타비 |      2.58 |       2.46 |
| 텐코 시부키  |      2.58 |       2.5  |
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
| 하나코 나나  |    7.62 |         38 |
| 텐코 시부키  |    6.24 |         36 |
| 아카네 리제  |    5.2  |         40 |
| 유즈하 리코  |    4.97 |         40 |
| 아오쿠모 린  |    4.29 |         20 |
| 아라하시 타비 |    4.13 |         12 |
| 시라유키 히나 |    3.54 |         38 |
| 사키하네 후야 |    3.54 |         24 |
| 아야츠노 유니 |    2.81 |         14 |
| 네네코 마시로 |    2.32 |         10 |


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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1226750 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1092074 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1053798 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        | 1006032 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  897588 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  756915 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  703570 |
| 하나코 나나  | 아메와 이츠카 야무노 데쇼~카~ #animation #shorts                                  |  662120 |
| 텐코 시부키  | 대두즈 면접 #shorts #vtuber                                                |  585739 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  496646 |

