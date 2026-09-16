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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    134168 |
|    2 | 아카네 리제  | UNIVERSE | 356000 |    309673 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    185859 |
|    4 | 아오쿠모 린  | CLICHE   | 284000 |    195399 |
|    5 | 아라하시 타비 | UNIVERSE | 261000 |    209035 |
|    6 | 텐코 시부키  | CLICHE   | 230000 |    213535 |
|    7 | 유즈하 리코  | CLICHE   | 222000 |    289443 |
|    8 | 하나코 나나  | CLICHE   | 206000 |    183685 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    117031 |
|   10 | 사키하네 후야 | EVERYS   | 135000 |    116639 |


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
| 유즈하 리코  | 222000 |  289443 |      130.4 |
| 텐코 시부키  | 230000 |  213535 |       92.8 |
| 하나코 나나  | 206000 |  183685 |       89.2 |
| 아카네 리제  | 356000 |  309673 |       87   |
| 사키하네 후야 | 135000 |  116639 |       86.4 |
| 아라하시 타비 | 261000 |  209035 |       80.1 |
| 아오쿠모 린  | 284000 |  195399 |       68.8 |
| 네네코 마시로 | 184000 |  117031 |       63.6 |
| 시라유키 히나 | 320000 |  185859 |       58.1 |
| 아야츠노 유니 | 361000 |  134168 |       37.2 |


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
| UNIVERSE |    4 |  280250 |  205399 |        3.57 |
| EVERYS   |    2 |  248000 |  125403 |        3.78 |
| CLICHE   |    4 |  235500 |  220515 |        3.83 |


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
| 네네코 마시로 |      4.38 |       4.12 |
| 하나코 나나  |      4.26 |       4.09 |
| 사키하네 후야 |      4.12 |       3.94 |
| 텐코 시부키  |      3.95 |       3.82 |
| 유즈하 리코  |      3.67 |       3.51 |
| 시라유키 히나 |      3.47 |       3.28 |
| 아오쿠모 린  |      3.45 |       3.29 |
| 아야츠노 유니 |      3.44 |       3.2  |
| 아라하시 타비 |      3.24 |       3.07 |
| 아카네 리제  |      3.19 |       3.08 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.35 |         46 |
| 하나코 나나  |    6.24 |         50 |
| 유즈하 리코  |    5.62 |         42 |
| 아카네 리제  |    5.12 |         42 |
| 아오쿠모 린  |    4.23 |         22 |
| 아라하시 타비 |    3.99 |         18 |
| 시라유키 히나 |    3.54 |         38 |
| 사키하네 후야 |    3.54 |         24 |
| 아야츠노 유니 |    2.86 |         16 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1968798 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                 | 1755137 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1513630 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1413244 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1124184 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          | 1014905 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts             |  977186 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  796943 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  686600 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  406075 |

