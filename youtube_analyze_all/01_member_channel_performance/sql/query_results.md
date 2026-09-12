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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    130261 |
|    2 | 아카네 리제  | UNIVERSE | 355000 |    307103 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    201417 |
|    4 | 아오쿠모 린  | CLICHE   | 283000 |    190314 |
|    5 | 아라하시 타비 | UNIVERSE | 261000 |    205858 |
|    6 | 텐코 시부키  | CLICHE   | 229000 |    203416 |
|    7 | 유즈하 리코  | CLICHE   | 221000 |    282542 |
|    8 | 하나코 나나  | CLICHE   | 206000 |    186759 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    111916 |
|   10 | 사키하네 후야 | EVERYS   | 134000 |    115357 |


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
| 유즈하 리코  | 221000 |  282542 |      127.8 |
| 하나코 나나  | 206000 |  186759 |       90.7 |
| 텐코 시부키  | 229000 |  203416 |       88.8 |
| 아카네 리제  | 355000 |  307103 |       86.5 |
| 사키하네 후야 | 134000 |  115357 |       86.1 |
| 아라하시 타비 | 261000 |  205858 |       78.9 |
| 아오쿠모 린  | 283000 |  190314 |       67.2 |
| 시라유키 히나 | 320000 |  201417 |       62.9 |
| 네네코 마시로 | 184000 |  111916 |       60.8 |
| 아야츠노 유니 | 361000 |  130261 |       36.1 |


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
| UNIVERSE |    4 |  280000 |  206573 |        3.67 |
| EVERYS   |    2 |  247500 |  122808 |        3.86 |
| CLICHE   |    4 |  234750 |  215757 |        3.94 |


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
| 네네코 마시로 |      4.48 |       4.22 |
| 하나코 나나  |      4.42 |       4.24 |
| 텐코 시부키  |      4.15 |       4.01 |
| 사키하네 후야 |      4.12 |       3.93 |
| 유즈하 리코  |      3.68 |       3.51 |
| 아야츠노 유니 |      3.6  |       3.36 |
| 시라유키 히나 |      3.56 |       3.37 |
| 아오쿠모 린  |      3.51 |       3.35 |
| 아라하시 타비 |      3.35 |       3.17 |
| 아카네 리제  |      3.3  |       3.17 |


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
| 하나코 나나  |    5.91 |         52 |
| 유즈하 리코  |    5.72 |         40 |
| 아카네 리제  |    5.2  |         42 |
| 아오쿠모 린  |    4.29 |         22 |
| 아라하시 타비 |    4.04 |         18 |
| 사키하네 후야 |    3.61 |         26 |
| 시라유키 히나 |    3.54 |         38 |
| 아야츠노 유니 |    2.93 |         18 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1911165 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                 | 1746357 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1475045 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1398971 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts             | 1187250 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1099187 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          | 1002964 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  738341 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  684339 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  403608 |

