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
|    1 | 아야츠노 유니 | EVERYS   | 360000 |    127798 |
|    2 | 아카네 리제  | UNIVERSE | 353000 |    311730 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    203179 |
|    4 | 아오쿠모 린  | CLICHE   | 282000 |    183121 |
|    5 | 아라하시 타비 | UNIVERSE | 260000 |    179363 |
|    6 | 텐코 시부키  | CLICHE   | 228000 |    207980 |
|    7 | 유즈하 리코  | CLICHE   | 220000 |    332665 |
|    8 | 하나코 나나  | CLICHE   | 205000 |    190930 |
|    9 | 네네코 마시로 | UNIVERSE | 183000 |    103897 |
|   10 | 사키하네 후야 | EVERYS   | 133000 |    113640 |


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
| 유즈하 리코  | 220000 |  332665 |      151.2 |
| 하나코 나나  | 205000 |  190930 |       93.1 |
| 텐코 시부키  | 228000 |  207980 |       91.2 |
| 아카네 리제  | 353000 |  311730 |       88.3 |
| 사키하네 후야 | 133000 |  113640 |       85.4 |
| 아라하시 타비 | 260000 |  179363 |       69   |
| 아오쿠모 린  | 282000 |  183121 |       64.9 |
| 시라유키 히나 | 320000 |  203179 |       63.5 |
| 네네코 마시로 | 183000 |  103897 |       56.8 |
| 아야츠노 유니 | 360000 |  127798 |       35.5 |


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
| UNIVERSE |    4 |  279000 |  199542 |        3.87 |
| EVERYS   |    2 |  246500 |  120718 |        3.88 |
| CLICHE   |    4 |  233750 |  228674 |        4.02 |


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
| 네네코 마시로 |      4.72 |       4.44 |
| 하나코 나나  |      4.41 |       4.23 |
| 텐코 시부키  |      4.22 |       4.08 |
| 사키하네 후야 |      4.14 |       3.96 |
| 아라하시 타비 |      3.8  |       3.59 |
| 아오쿠모 린  |      3.78 |       3.6  |
| 유즈하 리코  |      3.66 |       3.5  |
| 아야츠노 유니 |      3.63 |       3.38 |
| 시라유키 히나 |      3.53 |       3.33 |
| 아카네 리제  |      3.42 |       3.28 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.35 |         50 |
| 유즈하 리코  |    5.81 |         42 |
| 하나코 나나  |    5.53 |         52 |
| 아카네 리제  |    5.36 |         40 |
| 아오쿠모 린  |    4.4  |         24 |
| 아라하시 타비 |    4.29 |         22 |
| 사키하네 후야 |    3.73 |         28 |
| 시라유키 히나 |    3.43 |         36 |
| 아야츠노 유니 |    2.83 |         20 |
| 네네코 마시로 |    1.98 |          8 |


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
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰 | 2565016 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                 | 1772320 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts         | 1720669 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                      | 1335211 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts     | 1179295 |
| 텐코 시부키  | 나 후배 선배! #shorts #vtuber                           | 1060861 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                  |  969419 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts     |  677738 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람          |  666008 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                             |  396971 |

