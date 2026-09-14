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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    132358 |
|    2 | 아카네 리제  | UNIVERSE | 355000 |    304025 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    204526 |
|    4 | 아오쿠모 린  | CLICHE   | 283000 |    193417 |
|    5 | 아라하시 타비 | UNIVERSE | 261000 |    211907 |
|    6 | 텐코 시부키  | CLICHE   | 230000 |    210109 |
|    7 | 유즈하 리코  | CLICHE   | 221000 |    292365 |
|    8 | 하나코 나나  | CLICHE   | 206000 |    187478 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    114205 |
|   10 | 사키하네 후야 | EVERYS   | 135000 |    115923 |


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
| 유즈하 리코  | 221000 |  292365 |      132.3 |
| 텐코 시부키  | 230000 |  210109 |       91.4 |
| 하나코 나나  | 206000 |  187478 |       91   |
| 사키하네 후야 | 135000 |  115923 |       85.9 |
| 아카네 리제  | 355000 |  304025 |       85.6 |
| 아라하시 타비 | 261000 |  211907 |       81.2 |
| 아오쿠모 린  | 283000 |  193417 |       68.3 |
| 시라유키 히나 | 320000 |  204526 |       63.9 |
| 네네코 마시로 | 184000 |  114205 |       62.1 |
| 아야츠노 유니 | 361000 |  132358 |       36.7 |


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
| UNIVERSE |    4 |  280000 |  208665 |        3.62 |
| EVERYS   |    2 |  248000 |  124140 |        3.79 |
| CLICHE   |    4 |  235000 |  220842 |        3.85 |


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
| 네네코 마시로 |      4.46 |       4.2  |
| 하나코 나나  |      4.3  |       4.13 |
| 사키하네 후야 |      4.06 |       3.88 |
| 텐코 시부키  |      4    |       3.88 |
| 유즈하 리코  |      3.62 |       3.46 |
| 아야츠노 유니 |      3.52 |       3.28 |
| 시라유키 히나 |      3.5  |       3.31 |
| 아오쿠모 린  |      3.49 |       3.33 |
| 아라하시 타비 |      3.29 |       3.11 |
| 아카네 리제  |      3.22 |       3.1  |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.47 |         48 |
| 하나코 나나  |    6.02 |         50 |
| 유즈하 리코  |    5.62 |         40 |
| 아카네 리제  |    5.2  |         40 |
| 아오쿠모 린  |    4.29 |         22 |
| 아라하시 타비 |    4.08 |         18 |
| 시라유키 히나 |    3.54 |         38 |
| 사키하네 후야 |    3.5  |         26 |
| 아야츠노 유니 |    2.91 |         18 |
| 네네코 마시로 |    1.96 |          8 |


## 멤버별 최고 조회수 영상

```sql
SELECT m.name_ko AS 멤버, v.title AS 영상, v.views AS 조회수
FROM videos v
JOIN (SELECT channel_id, MAX(views) AS mx FROM videos GROUP BY channel_id) t
  ON v.channel_id=t.channel_id AND v.views=t.mx
JOIN channel_metrics m ON m.channel_id=v.channel_id
ORDER BY v.views DESC;
```

| 멤버      | 영상                                                         |     조회수 |
|:--------|:-----------------------------------------------------------|--------:|
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1938763 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                 | 1750555 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1493811 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1407972 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts             | 1189577 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1111810 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          | 1008593 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  766390 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  685427 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  404887 |

