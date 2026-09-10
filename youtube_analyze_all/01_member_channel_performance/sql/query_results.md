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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    127828 |
|    2 | 아카네 리제  | UNIVERSE | 355000 |    299019 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    198236 |
|    4 | 아오쿠모 린  | CLICHE   | 283000 |    185975 |
|    5 | 아라하시 타비 | UNIVERSE | 261000 |    197835 |
|    6 | 텐코 시부키  | CLICHE   | 229000 |    198863 |
|    7 | 유즈하 리코  | CLICHE   | 221000 |    296333 |
|    8 | 하나코 나나  | CLICHE   | 206000 |    184151 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    110323 |
|   10 | 사키하네 후야 | EVERYS   | 134000 |    113645 |


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
| 유즈하 리코  | 221000 |  296333 |      134.1 |
| 하나코 나나  | 206000 |  184151 |       89.4 |
| 텐코 시부키  | 229000 |  198863 |       86.8 |
| 사키하네 후야 | 134000 |  113645 |       84.8 |
| 아카네 리제  | 355000 |  299019 |       84.2 |
| 아라하시 타비 | 261000 |  197835 |       75.8 |
| 아오쿠모 린  | 283000 |  185975 |       65.7 |
| 시라유키 히나 | 320000 |  198236 |       61.9 |
| 네네코 마시로 | 184000 |  110323 |       60   |
| 아야츠노 유니 | 361000 |  127828 |       35.4 |


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
| UNIVERSE |    4 |  280000 |  201353 |        3.71 |
| EVERYS   |    2 |  247500 |  120736 |        3.9  |
| CLICHE   |    4 |  234750 |  216330 |        3.91 |


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
| 네네코 마시로 |      4.53 |       4.26 |
| 하나코 나나  |      4.34 |       4.17 |
| 텐코 시부키  |      4.21 |       4.07 |
| 사키하네 후야 |      4.17 |       3.98 |
| 아야츠노 유니 |      3.63 |       3.38 |
| 시라유키 히나 |      3.62 |       3.42 |
| 아오쿠모 린  |      3.56 |       3.39 |
| 유즈하 리코  |      3.54 |       3.38 |
| 아라하시 타비 |      3.38 |       3.2  |
| 아카네 리제  |      3.3  |       3.16 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.6  |         48 |
| 하나코 나나  |    5.91 |         52 |
| 유즈하 리코  |    5.62 |         40 |
| 아카네 리제  |    5.2  |         40 |
| 아오쿠모 린  |    4.23 |         22 |
| 아라하시 타비 |    4.08 |         18 |
| 사키하네 후야 |    3.61 |         26 |
| 시라유키 히나 |    3.54 |         38 |
| 아야츠노 유니 |    2.93 |         18 |
| 네네코 마시로 |    1.97 |          8 |


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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1877716 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                 | 1741449 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1452772 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1386045 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts             | 1185079 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1083909 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          |  992989 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  704485 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  682796 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  402757 |

