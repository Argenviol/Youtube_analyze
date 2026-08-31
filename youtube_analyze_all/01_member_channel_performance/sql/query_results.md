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
|    1 | 아야츠노 유니 | EVERYS   | 359000 |  124941   |
|    2 | 아카네 리제  | UNIVERSE | 352000 |  306601   |
|    3 | 시라유키 히나 | UNIVERSE | 319000 |  195792   |
|    4 | 아오쿠모 린  | CLICHE   | 281000 |  197599   |
|    5 | 아라하시 타비 | UNIVERSE | 259000 |  183388   |
|    6 | 텐코 시부키  | CLICHE   | 227000 |  223093   |
|    7 | 유즈하 리코  | CLICHE   | 218000 |  317719   |
|    8 | 하나코 나나  | CLICHE   | 204000 |  190844   |
|    9 | 네네코 마시로 | UNIVERSE | 182000 |   95028.9 |
|   10 | 사키하네 후야 | EVERYS   | 132000 |  107638   |


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
| 유즈하 리코  | 218000 | 317719   |      145.7 |
| 텐코 시부키  | 227000 | 223093   |       98.3 |
| 하나코 나나  | 204000 | 190844   |       93.6 |
| 아카네 리제  | 352000 | 306601   |       87.1 |
| 사키하네 후야 | 132000 | 107638   |       81.5 |
| 아라하시 타비 | 259000 | 183388   |       70.8 |
| 아오쿠모 린  | 281000 | 197599   |       70.3 |
| 시라유키 히나 | 319000 | 195792   |       61.4 |
| 네네코 마시로 | 182000 |  95028.9 |       52.2 |
| 아야츠노 유니 | 359000 | 124941   |       34.8 |


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
| UNIVERSE |    4 |  278000 |  195202 |        3.94 |
| EVERYS   |    2 |  245500 |  116289 |        4.03 |
| CLICHE   |    4 |  232500 |  232313 |        4.07 |


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
| 네네코 마시로 |      4.81 |       4.52 |
| 하나코 나나  |      4.48 |       4.29 |
| 사키하네 후야 |      4.31 |       4.12 |
| 텐코 시부키  |      4.18 |       4.04 |
| 아오쿠모 린  |      3.91 |       3.74 |
| 아라하시 타비 |      3.87 |       3.65 |
| 아야츠노 유니 |      3.74 |       3.48 |
| 유즈하 리코  |      3.72 |       3.55 |
| 아카네 리제  |      3.57 |       3.43 |
| 시라유키 히나 |      3.52 |       3.31 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.47 |         52 |
| 유즈하 리코  |    5.62 |         40 |
| 아카네 리제  |    5.53 |         42 |
| 하나코 나나  |    5.53 |         52 |
| 아오쿠모 린  |    4.57 |         26 |
| 아라하시 타비 |    4.23 |         20 |
| 사키하네 후야 |    3.73 |         30 |
| 시라유키 히나 |    3.43 |         34 |
| 아야츠노 유니 |    2.74 |         20 |
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
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰 | 2536266 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts         | 1704511 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                 | 1688239 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                      | 1305753 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts     | 1174339 |
| 텐코 시부키  | 143cm #shorts #vtuber                              | 1072025 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                  |  948806 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts     |  669711 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람          |  654497 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                             |  391642 |

