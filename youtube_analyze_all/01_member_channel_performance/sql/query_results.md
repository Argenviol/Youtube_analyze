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
|    1 | 아야츠노 유니 | EVERYS   | 359000 |  121703   |
|    2 | 아카네 리제  | UNIVERSE | 352000 |  295609   |
|    3 | 시라유키 히나 | UNIVERSE | 319000 |  223090   |
|    4 | 아오쿠모 린  | CLICHE   | 280000 |  190125   |
|    5 | 아라하시 타비 | UNIVERSE | 258000 |  183911   |
|    6 | 텐코 시부키  | CLICHE   | 227000 |  215290   |
|    7 | 유즈하 리코  | CLICHE   | 218000 |  305247   |
|    8 | 하나코 나나  | CLICHE   | 204000 |  174888   |
|    9 | 네네코 마시로 | UNIVERSE | 181000 |   85544.6 |
|   10 | 사키하네 후야 | EVERYS   | 131000 |  113515   |


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
| 유즈하 리코  | 218000 | 305247   |      140   |
| 텐코 시부키  | 227000 | 215290   |       94.8 |
| 사키하네 후야 | 131000 | 113515   |       86.7 |
| 하나코 나나  | 204000 | 174888   |       85.7 |
| 아카네 리제  | 352000 | 295609   |       84   |
| 아라하시 타비 | 258000 | 183911   |       71.3 |
| 시라유키 히나 | 319000 | 223090   |       69.9 |
| 아오쿠모 린  | 280000 | 190125   |       67.9 |
| 네네코 마시로 | 181000 |  85544.6 |       47.3 |
| 아야츠노 유니 | 359000 | 121703   |       33.9 |


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
| UNIVERSE |    4 |  277500 |  197038 |        4    |
| EVERYS   |    2 |  245000 |  117608 |        4.07 |
| CLICHE   |    4 |  232250 |  221387 |        4.21 |


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
| 네네코 마시로 |      4.92 |       4.62 |
| 하나코 나나  |      4.67 |       4.47 |
| 사키하네 후야 |      4.33 |       4.15 |
| 텐코 시부키  |      4.26 |       4.12 |
| 아오쿠모 린  |      4.03 |       3.84 |
| 유즈하 리코  |      3.89 |       3.71 |
| 아라하시 타비 |      3.88 |       3.67 |
| 아야츠노 유니 |      3.81 |       3.54 |
| 아카네 리제  |      3.69 |       3.54 |
| 시라유키 히나 |      3.52 |       3.32 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.6  |         52 |
| 유즈하 리코  |    5.91 |         40 |
| 아카네 리제  |    5.44 |         40 |
| 하나코 나나  |    5.28 |         50 |
| 아오쿠모 린  |    4.57 |         26 |
| 아라하시 타비 |    4.4  |         22 |
| 사키하네 후야 |    3.77 |         34 |
| 시라유키 히나 |    3.54 |         36 |
| 아야츠노 유니 |    2.74 |         20 |
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
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰          | 2503622 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                  | 1688774 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                          | 1623884 |
| 시라유키 히나 | 스텔라이브 삼색 볼펜들의 오도루프!🎵 #오도루프 #oddoloop #オドループ #vtuber #shorts | 1352850 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                               | 1282156 |
| 텐코 시부키  | 143cm #shorts #vtuber                                       | 1067364 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                           |  934079 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts              |  663542 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                   |  648066 |
| 사키하네 후야 | 수수께끼를 풀...엇? #shorts #vtuber                                |  435664 |

