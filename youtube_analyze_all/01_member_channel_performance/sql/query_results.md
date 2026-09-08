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
|    1 | 아야츠노 유니 | EVERYS   | 361000 |    128619 |
|    2 | 아카네 리제  | UNIVERSE | 354000 |    311718 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    194478 |
|    4 | 아오쿠모 린  | CLICHE   | 282000 |    183953 |
|    5 | 아라하시 타비 | UNIVERSE | 260000 |    192788 |
|    6 | 텐코 시부키  | CLICHE   | 229000 |    193330 |
|    7 | 유즈하 리코  | CLICHE   | 220000 |    293325 |
|    8 | 하나코 나나  | CLICHE   | 206000 |    188428 |
|    9 | 네네코 마시로 | UNIVERSE | 183000 |    107582 |
|   10 | 사키하네 후야 | EVERYS   | 134000 |    113740 |


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
| 유즈하 리코  | 220000 |  293325 |      133.3 |
| 하나코 나나  | 206000 |  188428 |       91.5 |
| 아카네 리제  | 354000 |  311718 |       88.1 |
| 사키하네 후야 | 134000 |  113740 |       84.9 |
| 텐코 시부키  | 229000 |  193330 |       84.4 |
| 아라하시 타비 | 260000 |  192788 |       74.1 |
| 아오쿠모 린  | 282000 |  183953 |       65.2 |
| 시라유키 히나 | 320000 |  194478 |       60.8 |
| 네네코 마시로 | 183000 |  107582 |       58.8 |
| 아야츠노 유니 | 361000 |  128619 |       35.6 |


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
| UNIVERSE |    4 |  279250 |  201641 |        3.73 |
| EVERYS   |    2 |  247500 |  121179 |        3.91 |
| CLICHE   |    4 |  234250 |  214759 |        3.98 |


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
| 네네코 마시로 |      4.63 |       4.35 |
| 하나코 나나  |      4.45 |       4.28 |
| 텐코 시부키  |      4.31 |       4.17 |
| 사키하네 후야 |      4.11 |       3.92 |
| 아야츠노 유니 |      3.72 |       3.47 |
| 아오쿠모 린  |      3.59 |       3.42 |
| 유즈하 리코  |      3.57 |       3.41 |
| 아라하시 타비 |      3.5  |       3.31 |
| 시라유키 히나 |      3.45 |       3.25 |
| 아카네 리제  |      3.34 |       3.21 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.6  |         50 |
| 하나코 나나  |    5.81 |         54 |
| 유즈하 리코  |    5.72 |         40 |
| 아카네 리제  |    5.28 |         40 |
| 아오쿠모 린  |    4.18 |         22 |
| 아라하시 타비 |    4.13 |         20 |
| 사키하네 후야 |    3.65 |         26 |
| 시라유키 히나 |    3.4  |         34 |
| 아야츠노 유니 |    2.88 |         20 |
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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1843878 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                 | 1736902 |
| 유즈하 리코  | 유즈하 리코(Yuzuha Riko) | '악당주의보'                              | 1429990 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1371698 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts             | 1183749 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1067852 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          |  984923 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts             |  686705 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  680584 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  401222 |

