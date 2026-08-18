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
|    1 | 강지      | STELLIVE | 762000 |  250347   |
|    2 | 아야츠노 유니 | EVERYS   | 359000 |  127797   |
|    3 | 아카네 리제  | UNIVERSE | 349000 |  287155   |
|    4 | 시라유키 히나 | UNIVERSE | 320000 |  211766   |
|    5 | 아오쿠모 린  | CLICHE   | 278000 |  192254   |
|    6 | 아라하시 타비 | UNIVERSE | 256000 |  182472   |
|    7 | 텐코 시부키  | CLICHE   | 226000 |  235347   |
|    8 | 유즈하 리코  | CLICHE   | 216000 |  275241   |
|    9 | 하나코 나나  | CLICHE   | 202000 |  173064   |
|   10 | 네네코 마시로 | UNIVERSE | 181000 |   84092.8 |
|   11 | 사키하네 후야 | EVERYS   | 131000 |  118652   |


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
| 유즈하 리코  | 216000 | 275241   |      127.4 |
| 텐코 시부키  | 226000 | 235347   |      104.1 |
| 사키하네 후야 | 131000 | 118652   |       90.6 |
| 하나코 나나  | 202000 | 173064   |       85.7 |
| 아카네 리제  | 349000 | 287155   |       82.3 |
| 아라하시 타비 | 256000 | 182472   |       71.3 |
| 아오쿠모 린  | 278000 | 192254   |       69.2 |
| 시라유키 히나 | 320000 | 211766   |       66.2 |
| 네네코 마시로 | 181000 |  84092.8 |       46.5 |
| 아야츠노 유니 | 359000 | 127797   |       35.6 |


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
| UNIVERSE |    4 |  276500 |  191371 |        4.07 |
| EVERYS   |    2 |  245000 |  123224 |        4.1  |
| CLICHE   |    4 |  230500 |  218976 |        4.19 |


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
| 네네코 마시로 |      4.98 |       4.69 |
| 하나코 나나  |      4.7  |       4.49 |
| 사키하네 후야 |      4.33 |       4.14 |
| 텐코 시부키  |      4.12 |       3.99 |
| 아오쿠모 린  |      3.98 |       3.79 |
| 유즈하 리코  |      3.97 |       3.77 |
| 아야츠노 유니 |      3.88 |       3.62 |
| 아라하시 타비 |      3.85 |       3.63 |
| 아카네 리제  |      3.81 |       3.66 |
| 시라유키 히나 |      3.63 |       3.41 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.86 |         52 |
| 유즈하 리코  |    6.12 |         38 |
| 아카네 리제  |    5.53 |         42 |
| 하나코 나나  |    4.97 |         48 |
| 아오쿠모 린  |    4.76 |         24 |
| 아라하시 타비 |    4.23 |         20 |
| 사키하네 후야 |    3.99 |         36 |
| 시라유키 히나 |    3.73 |         34 |
| 아야츠노 유니 |    2.77 |         22 |
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
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰          | 2374338 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                  | 1585153 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                          | 1404313 |
| 시라유키 히나 | 스텔라이브 삼색 볼펜들의 오도루프!🎵 #오도루프 #oddoloop #オドループ #vtuber #shorts | 1327992 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                               | 1162111 |
| 텐코 시부키  | 143cm #shorts #vtuber                                       | 1050599 |
| 강지      | 신호등 자매의 윙크 (｡•̀ ᴗ -)✧ #강지 #쇼츠 #밈                            |  926132 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                           |  890753 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts              |  653444 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                   |  613625 |
| 사키하네 후야 | 수수께끼를 풀...엇? #shorts #vtuber                                |  431419 |

