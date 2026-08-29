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
|    1 | 아야츠노 유니 | EVERYS   | 359000 |  122575   |
|    2 | 아카네 리제  | UNIVERSE | 352000 |  299917   |
|    3 | 시라유키 히나 | UNIVERSE | 319000 |  197403   |
|    4 | 아오쿠모 린  | CLICHE   | 280000 |  192605   |
|    5 | 아라하시 타비 | UNIVERSE | 258000 |  185248   |
|    6 | 텐코 시부키  | CLICHE   | 227000 |  216538   |
|    7 | 유즈하 리코  | CLICHE   | 218000 |  308799   |
|    8 | 하나코 나나  | CLICHE   | 204000 |  179041   |
|    9 | 네네코 마시로 | UNIVERSE | 182000 |   88350.2 |
|   10 | 사키하네 후야 | EVERYS   | 131000 |  106191   |


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
| 유즈하 리코  | 218000 | 308799   |      141.7 |
| 텐코 시부키  | 227000 | 216538   |       95.4 |
| 하나코 나나  | 204000 | 179041   |       87.8 |
| 아카네 리제  | 352000 | 299917   |       85.2 |
| 사키하네 후야 | 131000 | 106191   |       81.1 |
| 아라하시 타비 | 258000 | 185248   |       71.8 |
| 아오쿠모 린  | 280000 | 192605   |       68.8 |
| 시라유키 히나 | 319000 | 197403   |       61.9 |
| 네네코 마시로 | 182000 |  88350.2 |       48.5 |
| 아야츠노 유니 | 359000 | 122575   |       34.1 |


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
| UNIVERSE |    4 |  277750 |  192729 |        4    |
| EVERYS   |    2 |  245000 |  114383 |        4.04 |
| CLICHE   |    4 |  232250 |  224245 |        4.18 |


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
| 네네코 마시로 |      4.95 |       4.64 |
| 하나코 나나  |      4.63 |       4.43 |
| 사키하네 후야 |      4.29 |       4.11 |
| 텐코 시부키  |      4.29 |       4.15 |
| 아오쿠모 린  |      3.96 |       3.78 |
| 아라하시 타비 |      3.86 |       3.64 |
| 유즈하 리코  |      3.84 |       3.66 |
| 아야츠노 유니 |      3.79 |       3.53 |
| 아카네 리제  |      3.66 |       3.51 |
| 시라유키 히나 |      3.53 |       3.33 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.35 |         52 |
| 유즈하 리코  |    5.91 |         40 |
| 아카네 리제  |    5.44 |         42 |
| 하나코 나나  |    5.44 |         52 |
| 아오쿠모 린  |    4.57 |         26 |
| 아라하시 타비 |    4.4  |         22 |
| 사키하네 후야 |    3.73 |         32 |
| 시라유키 히나 |    3.5  |         34 |
| 아야츠노 유니 |    2.74 |         20 |
| 네네코 마시로 |    1.93 |          8 |


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
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰 | 2514229 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts         | 1693555 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                 | 1644203 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                      | 1289717 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts     | 1172909 |
| 텐코 시부키  | 143cm #shorts #vtuber                              | 1068869 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                  |  938961 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts     |  665038 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람          |  650020 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                             |  389639 |

