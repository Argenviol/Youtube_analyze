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
|    1 | 아야츠노 유니 | EVERYS   | 360000 |  127787   |
|    2 | 아카네 리제  | UNIVERSE | 353000 |  306273   |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |  201640   |
|    4 | 아오쿠모 린  | CLICHE   | 281000 |  186836   |
|    5 | 아라하시 타비 | UNIVERSE | 259000 |  189299   |
|    6 | 텐코 시부키  | CLICHE   | 228000 |  226456   |
|    7 | 유즈하 리코  | CLICHE   | 219000 |  318031   |
|    8 | 하나코 나나  | CLICHE   | 205000 |  193092   |
|    9 | 네네코 마시로 | UNIVERSE | 183000 |   99886.9 |
|   10 | 사키하네 후야 | EVERYS   | 133000 |  110876   |


## 도달 효율(평균조회수/구독자) 상위

```sql
SELECT name_ko AS 멤버, subscribers AS 구독자,
       recent_avg_views AS 평균조회수,
       ROUND(reach_ratio*100,1) AS 도달효율_pct
FROM channel_metrics WHERE role='talent'
ORDER BY reach_ratio DESC;
```

| 멤버      |    구독자 |    평균조회수 |   도달효율_pct |
|:--------|-------:|---------:|-----------:|
| 유즈하 리코  | 219000 | 318031   |      145.2 |
| 텐코 시부키  | 228000 | 226456   |       99.3 |
| 하나코 나나  | 205000 | 193092   |       94.2 |
| 아카네 리제  | 353000 | 306273   |       86.8 |
| 사키하네 후야 | 133000 | 110876   |       83.4 |
| 아라하시 타비 | 259000 | 189299   |       73.1 |
| 아오쿠모 린  | 281000 | 186836   |       66.5 |
| 시라유키 히나 | 320000 | 201640   |       63   |
| 네네코 마시로 | 183000 |  99886.9 |       54.6 |
| 아야츠노 유니 | 360000 | 127787   |       35.5 |


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
| UNIVERSE |    4 |  278750 |  199274 |        3.89 |
| EVERYS   |    2 |  246500 |  119331 |        3.99 |
| CLICHE   |    4 |  233250 |  231103 |        4.06 |


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
| 네네코 마시로 |      4.79 |       4.5  |
| 하나코 나나  |      4.44 |       4.25 |
| 사키하네 후야 |      4.27 |       4.08 |
| 텐코 시부키  |      4.2  |       4.06 |
| 아오쿠모 린  |      3.84 |       3.66 |
| 아라하시 타비 |      3.76 |       3.55 |
| 유즈하 리코  |      3.74 |       3.57 |
| 아야츠노 유니 |      3.72 |       3.46 |
| 시라유키 히나 |      3.51 |       3.31 |
| 아카네 리제  |      3.49 |       3.35 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.24 |         50 |
| 유즈하 리코  |    5.62 |         40 |
| 아카네 리제  |    5.53 |         40 |
| 하나코 나나  |    5.44 |         52 |
| 아오쿠모 린  |    4.45 |         26 |
| 아라하시 타비 |    4.23 |         20 |
| 사키하네 후야 |    3.77 |         30 |
| 시라유키 히나 |    3.4  |         34 |
| 아야츠노 유니 |    2.74 |         20 |
| 네네코 마시로 |    2.01 |          8 |


## 멤버별 최고 조회수 영상

```sql
SELECT m.name_ko AS 멤버, v.title AS 영상, v.views AS 조회수
FROM videos v
JOIN (SELECT channel_id, MAX(views) AS mx FROM videos GROUP BY channel_id) t
  ON v.channel_id=t.channel_id AND v.views=t.mx
JOIN channel_metrics m ON m.channel_id=v.channel_id
ORDER BY v.views DESC;
```

| 멤버      | 영상                                                 |     조회수 |
|:--------|:---------------------------------------------------|--------:|
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰 | 2552199 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                 | 1730647 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts         | 1713954 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                      | 1320481 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts     | 1176770 |
| 텐코 시부키  | 143cm #shorts #vtuber                              | 1074037 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                  |  960470 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts     |  673971 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람          |  660973 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                             |  394023 |

