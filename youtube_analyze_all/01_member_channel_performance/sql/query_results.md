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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    129207 |
|    2 | 아카네 리제  | UNIVERSE | 355000 |    302132 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    199908 |
|    4 | 아오쿠모 린  | CLICHE   | 283000 |    188086 |
|    5 | 아라하시 타비 | UNIVERSE | 261000 |    201706 |
|    6 | 텐코 시부키  | CLICHE   | 229000 |    201361 |
|    7 | 유즈하 리코  | CLICHE   | 221000 |    299375 |
|    8 | 하나코 나나  | CLICHE   | 206000 |    181705 |
|    9 | 네네코 마시로 | UNIVERSE | 184000 |    111725 |
|   10 | 사키하네 후야 | EVERYS   | 134000 |    114491 |


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
| 유즈하 리코  | 221000 |  299375 |      135.5 |
| 하나코 나나  | 206000 |  181705 |       88.2 |
| 텐코 시부키  | 229000 |  201361 |       87.9 |
| 사키하네 후야 | 134000 |  114491 |       85.4 |
| 아카네 리제  | 355000 |  302132 |       85.1 |
| 아라하시 타비 | 261000 |  201706 |       77.3 |
| 아오쿠모 린  | 283000 |  188086 |       66.5 |
| 시라유키 히나 | 320000 |  199908 |       62.5 |
| 네네코 마시로 | 184000 |  111725 |       60.7 |
| 아야츠노 유니 | 361000 |  129207 |       35.8 |


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
| UNIVERSE |    4 |  280000 |  203867 |        3.69 |
| EVERYS   |    2 |  247500 |  121849 |        3.88 |
| CLICHE   |    4 |  234750 |  217631 |        3.91 |


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
| 네네코 마시로 |      4.51 |       4.25 |
| 하나코 나나  |      4.39 |       4.22 |
| 텐코 시부키  |      4.19 |       4.05 |
| 사키하네 후야 |      4.14 |       3.95 |
| 아야츠노 유니 |      3.62 |       3.38 |
| 시라유키 히나 |      3.59 |       3.39 |
| 아오쿠모 린  |      3.55 |       3.38 |
| 유즈하 리코  |      3.52 |       3.36 |
| 아라하시 타비 |      3.36 |       3.18 |
| 아카네 리제  |      3.28 |       3.15 |


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
| 하나코 나나  |    6.02 |         52 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1894449 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                 | 1743457 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1463873 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1391262 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts             | 1185890 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1091543 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          |  997115 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover |  720991 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  683562 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  403160 |

