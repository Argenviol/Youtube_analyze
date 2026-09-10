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
|    1 | 아라하시 타비 |   5.26 |   7.29 |   38.4 |
|    2 | 텐코 시부키  |   5.01 |   7.03 |   35.2 |
|    3 | 시라유키 히나 |   5.79 |   6.01 |   34.8 |
|    4 | 아야츠노 유니 |   5.48 |   6.33 |   34.7 |
|    5 | 유즈하 리코  |   4.87 |   6.89 |   33.6 |
|    6 | 사키하네 후야 |   5.18 |   5.06 |   26.2 |
|    7 | 네네코 마시로 |   5.21 |   4.81 |   25.1 |
|    8 | 아카네 리제  |   4.71 |   4.95 |   23.3 |
|    9 | 하나코 나나  |   4.25 |   5.29 |   22.5 |
|   10 | 아오쿠모 린  |   4.56 |   4.63 |   21.1 |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 텐코 시부키  |         80 |     4.9 |
| 시라유키 히나 |         70 |     6.8 |
| 유즈하 리코  |         66 |     7.9 |
| 아라하시 타비 |         66 |     6.5 |
| 아오쿠모 린  |         65 |     8.2 |
| 아카네 리제  |         65 |     7.9 |
| 하나코 나나  |         52 |    10.6 |
| 아야츠노 유니 |         46 |     9.5 |
| 사키하네 후야 |         38 |    13.2 |
| 네네코 마시로 |         23 |    16.3 |


## 게임 vs 토크 성향

```sql
SELECT name_ko AS 멤버, ROUND(game_share*100,0) AS 게임_pct,
       ROUND(talk_share*100,0) AS 토크_pct, top_category AS 주력카테고리
FROM stream_metrics ORDER BY game_share DESC;
```

| 멤버      |   게임_pct |   토크_pct | 주력카테고리   |
|:--------|---------:|---------:|:---------|
| 아오쿠모 린  |       87 |       10 | 마인크래프트   |
| 하나코 나나  |       74 |       19 | talk     |
| 텐코 시부키  |       70 |       27 | talk     |
| 아카네 리제  |       52 |       46 | talk     |
| 아라하시 타비 |       49 |       49 | talk     |
| 네네코 마시로 |       42 |       48 | talk     |
| 유즈하 리코  |       37 |       59 | talk     |
| 시라유키 히나 |       37 |       57 | talk     |
| 사키하네 후야 |       30 |       69 | talk     |
| 아야츠노 유니 |       24 |       56 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리              |   방송수 |
|:------------------|------:|
| talk              |  1294 |
| 마인크래프트            |   388 |
| 리그 오브 레전드         |   138 |
| 이터널 리턴            |   110 |
| 오버워치              |    99 |
| 음악/노래             |    91 |
| 2026 FIFA 북중미 월드컵 |    57 |
| 종합 게임             |    50 |
| 팰월드               |    41 |
| 붕괴: 스타레일          |    37 |


## 시작 시간대별 방송 수

```sql
SELECT CAST(substr(publish_date,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;
```

|   시작시 |   방송수 |
|------:|------:|
|     1 |   492 |
|     0 |   471 |
|    23 |   357 |
|     2 |   310 |
|    22 |   227 |
|     3 |   223 |
|    21 |   145 |
|     4 |   132 |

