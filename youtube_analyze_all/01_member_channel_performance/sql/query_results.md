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
|    1 | 아야츠노 유니 | EVERYS   | 373000 |    166912 |
|    2 | 아카네 리제  | UNIVERSE | 372000 |    311644 |
|    3 | 시라유키 히나 | UNIVERSE | 331000 |    171862 |
|    4 | 아오쿠모 린  | CLICHE   | 300000 |    199858 |
|    5 | 아라하시 타비 | UNIVERSE | 275000 |    234327 |
|    6 | 텐코 시부키  | CLICHE   | 243000 |    265122 |
|    7 | 유즈하 리코  | CLICHE   | 237000 |    285041 |
|    8 | 하나코 나나  | CLICHE   | 222000 |    243577 |
|    9 | 네네코 마시로 | UNIVERSE | 197000 |    146074 |
|   10 | 사키하네 후야 | EVERYS   | 151000 |    129722 |


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
| 유즈하 리코  | 237000 |  285041 |      120.3 |
| 하나코 나나  | 222000 |  243577 |      109.7 |
| 텐코 시부키  | 243000 |  265122 |      109.1 |
| 사키하네 후야 | 151000 |  129722 |       85.9 |
| 아라하시 타비 | 275000 |  234327 |       85.2 |
| 아카네 리제  | 372000 |  311644 |       83.8 |
| 네네코 마시로 | 197000 |  146074 |       74.1 |
| 아오쿠모 린  | 300000 |  199858 |       66.6 |
| 시라유키 히나 | 331000 |  171862 |       51.9 |
| 아야츠노 유니 | 373000 |  166912 |       44.7 |


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
| UNIVERSE |    4 |  293750 |  215976 |        2.95 |
| EVERYS   |    2 |  262000 |  148317 |        3.13 |
| CLICHE   |    4 |  250500 |  248399 |        2.78 |


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
| 네네코 마시로 |      3.61 |       3.41 |
| 사키하네 후야 |      3.56 |       3.42 |
| 시라유키 히나 |      3.26 |       3.09 |
| 유즈하 리코  |      3.08 |       2.96 |
| 아오쿠모 린  |      2.76 |       2.64 |
| 아야츠노 유니 |      2.7  |       2.54 |
| 하나코 나나  |      2.69 |       2.59 |
| 아라하시 타비 |      2.58 |       2.46 |
| 텐코 시부키  |      2.58 |       2.5  |
| 아카네 리제  |      2.34 |       2.27 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.46 |         36 |
| 텐코 시부키  |    6.73 |         36 |
| 유즈하 리코  |    5.36 |         42 |
| 아카네 리제  |    5.12 |         38 |
| 아오쿠모 린  |    4.23 |         18 |
| 아라하시 타비 |    4.23 |         14 |
| 사키하네 후야 |    3.69 |         24 |
| 시라유키 히나 |    3.61 |         38 |
| 아야츠노 유니 |    2.81 |         14 |
| 네네코 마시로 |    2.35 |         10 |


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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1237410 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1111118 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1069138 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  947382 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  763263 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  705006 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  679223 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  612628 |
| 텐코 시부키  | (소리주의) 붘몽가입니다 #vtuber #shorts #치이카와 #ちいかわ                             |  607594 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  518522 |

