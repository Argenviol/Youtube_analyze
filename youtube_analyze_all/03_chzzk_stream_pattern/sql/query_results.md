# 치지직 방송 패턴 분석 쿼리 결과

`sql/chzzk.db`(SQLite) 실행 결과.

## 주간 방송 시간 랭킹

```sql
SELECT rank AS 순위, name_ko AS 멤버, streams_per_week AS 주간횟수,
       avg_duration_h AS 평균시간, hours_per_week AS 주간시간
FROM stream_metrics ORDER BY hours_per_week DESC;
```

|   순위 | 멤버      |   주간횟수 |   평균시간 |   주간시간 |
|-----:|:--------|-------:|-------:|-------:|
|    1 | 아라하시 타비 |   5.32 |   7.58 |   40.3 |
|    2 | 아야츠노 유니 |   6.02 |   6.21 |   37.4 |
|    3 | 시라유키 히나 |   5.93 |   6.29 |   37.3 |
|    4 | 텐코 시부키  |   5.07 |   7.15 |   36.3 |
|    5 | 유즈하 리코  |   4.9  |   7.18 |   35.1 |
|    6 | 사키하네 후야 |   5.26 |   5.09 |   26.8 |
|    7 | 네네코 마시로 |   5.25 |   4.83 |   25.4 |
|    8 | 아카네 리제  |   4.73 |   5.05 |   23.9 |
|    9 | 하나코 나나  |   4.28 |   5.36 |   22.9 |
|   10 | 아오쿠모 린  |   4.59 |   4.9  |   22.5 |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 텐코 시부키  |         81 |     4.8 |
| 시라유키 히나 |         72 |     6.5 |
| 유즈하 리코  |         69 |     7.4 |
| 아라하시 타비 |         67 |     6.5 |
| 아카네 리제  |         66 |     7.8 |
| 아오쿠모 린  |         66 |     8.1 |
| 하나코 나나  |         52 |    10.5 |
| 아야츠노 유니 |         47 |     9.5 |
| 사키하네 후야 |         39 |    13.1 |
| 네네코 마시로 |         21 |    16.7 |


## 게임 vs 토크 성향

```sql
SELECT name_ko AS 멤버, ROUND(game_share*100,0) AS 게임_pct,
       ROUND(talk_share*100,0) AS 토크_pct, top_category AS 주력카테고리
FROM stream_metrics ORDER BY game_share DESC;
```

| 멤버      |   게임_pct |   토크_pct | 주력카테고리   |
|:--------|---------:|---------:|:---------|
| 아오쿠모 린  |       89 |        9 | 마인크래프트   |
| 텐코 시부키  |       75 |       22 | talk     |
| 하나코 나나  |       75 |       18 | talk     |
| 아카네 리제  |       53 |       44 | talk     |
| 아라하시 타비 |       52 |       46 | talk     |
| 시라유키 히나 |       42 |       54 | talk     |
| 네네코 마시로 |       42 |       48 | talk     |
| 유즈하 리코  |       39 |       58 | talk     |
| 사키하네 후야 |       33 |       67 | talk     |
| 아야츠노 유니 |       29 |       49 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리               |   방송수 |
|:-------------------|------:|
| talk               |  1238 |
| 마인크래프트             |   371 |
| Grand Theft Auto V |   151 |
| 리그 오브 레전드          |   135 |
| 이터널 리턴             |   107 |
| 오버워치               |   100 |
| 음악/노래              |    82 |
| 2026 FIFA 북중미 월드컵  |    57 |
| 종합 게임              |    50 |
| 팰월드                |    41 |


## 시작 시간대별 방송 수

```sql
SELECT CAST(substr(publish_date,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;
```

|   시작시 |   방송수 |
|------:|------:|
|     1 |   466 |
|     0 |   446 |
|    23 |   351 |
|     3 |   300 |
|     2 |   299 |
|    22 |   225 |
|     4 |   151 |
|    21 |   150 |

