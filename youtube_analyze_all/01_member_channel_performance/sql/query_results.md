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
|    1 | 강지      | STELLIVE | 762000 |  234035   |
|    2 | 아야츠노 유니 | EVERYS   | 359000 |  127525   |
|    3 | 아카네 리제  | UNIVERSE | 350000 |  286952   |
|    4 | 시라유키 히나 | UNIVERSE | 320000 |  214972   |
|    5 | 아오쿠모 린  | CLICHE   | 279000 |  188495   |
|    6 | 아라하시 타비 | UNIVERSE | 257000 |  182900   |
|    7 | 텐코 시부키  | CLICHE   | 226000 |  225915   |
|    8 | 유즈하 리코  | CLICHE   | 216000 |  287948   |
|    9 | 하나코 나나  | CLICHE   | 203000 |  176991   |
|   10 | 네네코 마시로 | UNIVERSE | 181000 |   84654.7 |
|   11 | 사키하네 후야 | EVERYS   | 131000 |  111568   |


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
| 유즈하 리코  | 216000 | 287948   |      133.3 |
| 텐코 시부키  | 226000 | 225915   |      100   |
| 하나코 나나  | 203000 | 176991   |       87.2 |
| 사키하네 후야 | 131000 | 111568   |       85.2 |
| 아카네 리제  | 350000 | 286952   |       82   |
| 아라하시 타비 | 257000 | 182900   |       71.2 |
| 아오쿠모 린  | 279000 | 188495   |       67.6 |
| 시라유키 히나 | 320000 | 214972   |       67.2 |
| 네네코 마시로 | 181000 |  84654.7 |       46.8 |
| 아야츠노 유니 | 359000 | 127525   |       35.5 |


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
| UNIVERSE |    4 |  277000 |  192369 |        4.01 |
| EVERYS   |    2 |  245000 |  119546 |        4.15 |
| CLICHE   |    4 |  231000 |  219837 |        4.24 |


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
| 네네코 마시로 |      4.95 |       4.66 |
| 하나코 나나  |      4.64 |       4.44 |
| 사키하네 후야 |      4.43 |       4.25 |
| 텐코 시부키  |      4.31 |       4.18 |
| 아오쿠모 린  |      4.08 |       3.9  |
| 유즈하 리코  |      3.91 |       3.72 |
| 아야츠노 유니 |      3.87 |       3.61 |
| 아라하시 타비 |      3.81 |       3.6  |
| 아카네 리제  |      3.79 |       3.63 |
| 시라유키 히나 |      3.51 |       3.29 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.73 |         54 |
| 유즈하 리코  |    6.02 |         40 |
| 아카네 리제  |    5.53 |         40 |
| 하나코 나나  |    5.04 |         48 |
| 아오쿠모 린  |    4.64 |         26 |
| 아라하시 타비 |    4.29 |         20 |
| 사키하네 후야 |    3.94 |         34 |
| 시라유키 히나 |    3.73 |         34 |
| 아야츠노 유니 |    2.79 |         22 |
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

| 멤버      | 영상                                                          |     조회수 |
|:--------|:------------------------------------------------------------|--------:|
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰          | 2420500 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                  | 1627481 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                          | 1471800 |
| 시라유키 히나 | 스텔라이브 삼색 볼펜들의 오도루프!🎵 #오도루프 #oddoloop #オドループ #vtuber #shorts | 1335287 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                               | 1205697 |
| 텐코 시부키  | 143cm #shorts #vtuber                                       | 1056328 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                           |  904631 |
| 강지      | 오프 행사에서 난리 났었다는 강지의 그 복장                                    |  716572 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts              |  655785 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                   |  624334 |
| 사키하네 후야 | 수수께끼를 풀...엇? #shorts #vtuber                                |  432831 |

