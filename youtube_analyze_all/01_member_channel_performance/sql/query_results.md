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
|    1 | 아야츠노 유니 | EVERYS   | 370000 |    159555 |
|    2 | 아카네 리제  | UNIVERSE | 367000 |    308616 |
|    3 | 시라유키 히나 | UNIVERSE | 328000 |    179237 |
|    4 | 아오쿠모 린  | CLICHE   | 295000 |    181083 |
|    5 | 아라하시 타비 | UNIVERSE | 271000 |    219195 |
|    6 | 텐코 시부키  | CLICHE   | 239000 |    241339 |
|    7 | 유즈하 리코  | CLICHE   | 232000 |    271681 |
|    8 | 하나코 나나  | CLICHE   | 218000 |    240539 |
|    9 | 네네코 마시로 | UNIVERSE | 193000 |    142941 |
|   10 | 사키하네 후야 | EVERYS   | 146000 |    121098 |


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
| 유즈하 리코  | 232000 |  271681 |      117.1 |
| 하나코 나나  | 218000 |  240539 |      110.3 |
| 텐코 시부키  | 239000 |  241339 |      101   |
| 아카네 리제  | 367000 |  308616 |       84.1 |
| 사키하네 후야 | 146000 |  121098 |       82.9 |
| 아라하시 타비 | 271000 |  219195 |       80.9 |
| 네네코 마시로 | 193000 |  142941 |       74.1 |
| 아오쿠모 린  | 295000 |  181083 |       61.4 |
| 시라유키 히나 | 328000 |  179237 |       54.6 |
| 아야츠노 유니 | 370000 |  159555 |       43.1 |


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
| UNIVERSE |    4 |  289750 |  212497 |        3.03 |
| EVERYS   |    2 |  258000 |  140326 |        3.27 |
| CLICHE   |    4 |  246000 |  233660 |        2.89 |


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
| 네네코 마시로 |      3.7  |       3.49 |
| 사키하네 후야 |      3.67 |       3.52 |
| 시라유키 히나 |      3.29 |       3.12 |
| 유즈하 리코  |      3.15 |       3.01 |
| 아오쿠모 린  |      3.07 |       2.94 |
| 아야츠노 유니 |      2.87 |       2.69 |
| 하나코 나나  |      2.73 |       2.64 |
| 아라하시 타비 |      2.68 |       2.55 |
| 텐코 시부키  |      2.62 |       2.54 |
| 아카네 리제  |      2.48 |       2.4  |


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
| 아카네 리제  |    5.2  |         40 |
| 유즈하 리코  |    5.12 |         42 |
| 아오쿠모 린  |    4.51 |         24 |
| 아라하시 타비 |    3.99 |         12 |
| 시라유키 히나 |    3.65 |         40 |
| 사키하네 후야 |    3.5  |         24 |
| 아야츠노 유니 |    2.83 |         14 |
| 네네코 마시로 |    2.24 |          8 |


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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1198872 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1073801 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1039156 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        | 1003364 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  846655 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  753254 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  701572 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  633839 |
| 텐코 시부키  | 대두즈 면접 #shorts #vtuber                                                |  521755 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  481604 |

