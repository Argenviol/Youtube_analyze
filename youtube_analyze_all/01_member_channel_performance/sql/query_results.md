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
|    1 | 아야츠노 유니 | EVERYS   | 372000 |    158876 |
|    2 | 아카네 리제  | UNIVERSE | 370000 |    306994 |
|    3 | 시라유키 히나 | UNIVERSE | 330000 |    181564 |
|    4 | 아오쿠모 린  | CLICHE   | 298000 |    188401 |
|    5 | 아라하시 타비 | UNIVERSE | 273000 |    218933 |
|    6 | 텐코 시부키  | CLICHE   | 241000 |    252125 |
|    7 | 유즈하 리코  | CLICHE   | 235000 |    271461 |
|    8 | 하나코 나나  | CLICHE   | 220000 |    241972 |
|    9 | 네네코 마시로 | UNIVERSE | 195000 |    143051 |
|   10 | 사키하네 후야 | EVERYS   | 149000 |    123689 |


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
| 유즈하 리코  | 235000 |  271461 |      115.5 |
| 하나코 나나  | 220000 |  241972 |      110   |
| 텐코 시부키  | 241000 |  252125 |      104.6 |
| 아카네 리제  | 370000 |  306994 |       83   |
| 사키하네 후야 | 149000 |  123689 |       83   |
| 아라하시 타비 | 273000 |  218933 |       80.2 |
| 네네코 마시로 | 195000 |  143051 |       73.4 |
| 아오쿠모 린  | 298000 |  188401 |       63.2 |
| 시라유키 히나 | 330000 |  181564 |       55   |
| 아야츠노 유니 | 372000 |  158876 |       42.7 |


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
| UNIVERSE |    4 |  292000 |  212635 |        3.01 |
| EVERYS   |    2 |  260500 |  141282 |        3.22 |
| CLICHE   |    4 |  248500 |  238489 |        2.83 |


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
| 네네코 마시로 |      3.69 |       3.49 |
| 사키하네 후야 |      3.6  |       3.45 |
| 시라유키 히나 |      3.26 |       3.09 |
| 유즈하 리코  |      3.12 |       2.98 |
| 아오쿠모 린  |      2.97 |       2.85 |
| 아야츠노 유니 |      2.85 |       2.67 |
| 아라하시 타비 |      2.68 |       2.55 |
| 하나코 나나  |      2.66 |       2.57 |
| 텐코 시부키  |      2.59 |       2.51 |
| 아카네 리제  |      2.4  |       2.33 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.62 |         36 |
| 텐코 시부키  |    6.24 |         38 |
| 아카네 리제  |    5.12 |         38 |
| 유즈하 리코  |    4.97 |         40 |
| 아오쿠모 린  |    4.4  |         22 |
| 아라하시 타비 |    4.04 |         12 |
| 시라유키 히나 |    3.65 |         40 |
| 사키하네 후야 |    3.57 |         24 |
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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1219136 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1086066 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1048772 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        | 1005127 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  882156 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  754806 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  702354 |
| 하나코 나나  | 아메와 이츠카 야무노 데쇼~카~ #animation #shorts                                  |  653167 |
| 텐코 시부키  | 대두즈 면접 #shorts #vtuber                                                |  574315 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  490756 |

