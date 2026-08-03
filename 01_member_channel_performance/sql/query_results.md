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
|    1 | 강지      | STELLIVE | 759000 |  246643   |
|    2 | 아야츠노 유니 | EVERYS   | 357000 |  138621   |
|    3 | 아카네 리제  | UNIVERSE | 343000 |  253222   |
|    4 | 시라유키 히나 | UNIVERSE | 317000 |  224252   |
|    5 | 아오쿠모 린  | CLICHE   | 273000 |  173475   |
|    6 | 아라하시 타비 | UNIVERSE | 252000 |  177316   |
|    7 | 텐코 시부키  | CLICHE   | 222000 |  202960   |
|    8 | 유즈하 리코  | CLICHE   | 210000 |  258194   |
|    9 | 하나코 나나  | CLICHE   | 199000 |  155407   |
|   10 | 네네코 마시로 | UNIVERSE | 179000 |   80354.8 |
|   11 | 사키하네 후야 | EVERYS   | 128000 |  109054   |


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
| 유즈하 리코  | 210000 | 258194   |      122.9 |
| 텐코 시부키  | 222000 | 202960   |       91.4 |
| 사키하네 후야 | 128000 | 109054   |       85.2 |
| 하나코 나나  | 199000 | 155407   |       78.1 |
| 아카네 리제  | 343000 | 253222   |       73.8 |
| 시라유키 히나 | 317000 | 224252   |       70.7 |
| 아라하시 타비 | 252000 | 177316   |       70.4 |
| 아오쿠모 린  | 273000 | 173475   |       63.5 |
| 네네코 마시로 | 179000 |  80354.8 |       44.9 |
| 아야츠노 유니 | 357000 | 138621   |       38.8 |


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
| UNIVERSE |    4 |  272750 |  183785 |        4.2  |
| EVERYS   |    2 |  242500 |  123837 |        4.22 |
| CLICHE   |    4 |  226000 |  197509 |        4.29 |


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
| 네네코 마시로 |      5.04 |       4.75 |
| 하나코 나나  |      4.81 |       4.6  |
| 사키하네 후야 |      4.48 |       4.29 |
| 아카네 리제  |      4.22 |       4.04 |
| 아오쿠모 린  |      4.15 |       3.95 |
| 유즈하 리코  |      4.11 |       3.91 |
| 텐코 시부키  |      4.07 |       3.94 |
| 아라하시 타비 |      3.96 |       3.74 |
| 아야츠노 유니 |      3.95 |       3.68 |
| 시라유키 히나 |      3.57 |       3.34 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.86 |         48 |
| 유즈하 리코  |    6.02 |         40 |
| 아카네 리제  |    5.91 |         44 |
| 아오쿠모 린  |    5.12 |         26 |
| 하나코 나나  |    4.57 |         44 |
| 아라하시 타비 |    4.45 |         24 |
| 사키하네 후야 |    4.45 |         36 |
| 시라유키 히나 |    3.85 |         32 |
| 아야츠노 유니 |    2.72 |         22 |
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

| 멤버      | 영상                                                          |     조회수 |
|:--------|:------------------------------------------------------------|--------:|
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰          | 2065569 |
| 시라유키 히나 | 스텔라이브 삼색 볼펜들의 오도루프!🎵 #오도루프 #oddoloop #オドループ #vtuber #shorts | 1272574 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                  | 1191713 |
| 텐코 시부키  | 143cm #shorts #vtuber                                       |  965158 |
| 강지      | 신호등 자매의 윙크 (｡•̀ ᴗ -)✧ #강지 #쇼츠 #밈                            |  902326 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                               |  863156 |
| 아오쿠모 린  | 물떼새(ヨルシカ - 千鳥) / 아오쿠모 린(Aokumo Rin) Cover                   |  838026 |
| 하나코 나나  | 다 같이 도수치료 받고 왔어요!🌟 #animation #shorts                       |  747300 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts              |  633655 |
| 아야츠노 유니 | 마법의 아르냥고동                                                   |  542806 |
| 사키하네 후야 | 수수께끼를 풀...엇? #shorts #vtuber                                |  415181 |

