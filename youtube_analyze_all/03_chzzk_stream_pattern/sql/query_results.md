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
|    1 | 아라하시 타비 |   5.3  |   7.25 |   38.5 |
|    2 | 텐코 시부키  |   5.01 |   6.96 |   34.9 |
|    3 | 아야츠노 유니 |   5.47 |   6.33 |   34.6 |
|    4 | 시라유키 히나 |   5.75 |   5.93 |   34.1 |
|    5 | 유즈하 리코  |   4.84 |   6.79 |   32.9 |
|    6 | 사키하네 후야 |   5.17 |   5.09 |   26.3 |
|    7 | 네네코 마시로 |   5.24 |   4.77 |   25   |
|    8 | 아카네 리제  |   4.71 |   4.99 |   23.5 |
|    9 | 하나코 나나  |   4.24 |   5.23 |   22.2 |
|   10 | 아오쿠모 린  |   4.58 |   4.6  |   21   |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 텐코 시부키  |         80 |     4.9 |
| 시라유키 히나 |         70 |     6.9 |
| 유즈하 리코  |         65 |     8.1 |
| 아카네 리제  |         65 |     7.9 |
| 아라하시 타비 |         65 |     6.6 |
| 아오쿠모 린  |         65 |     8.3 |
| 하나코 나나  |         51 |    10.6 |
| 아야츠노 유니 |         45 |     9.7 |
| 사키하네 후야 |         39 |    13.1 |
| 네네코 마시로 |         22 |    16.4 |


## 게임 vs 토크 성향

```sql
SELECT name_ko AS 멤버, ROUND(game_share*100,0) AS 게임_pct,
       ROUND(talk_share*100,0) AS 토크_pct, top_category AS 주력카테고리
FROM stream_metrics ORDER BY game_share DESC;
```

| 멤버      |   게임_pct |   토크_pct | 주력카테고리   |
|:--------|---------:|---------:|:---------|
| 아오쿠모 린  |       88 |       10 | 마인크래프트   |
| 하나코 나나  |       73 |       20 | talk     |
| 텐코 시부키  |       69 |       28 | talk     |
| 아카네 리제  |       53 |       45 | talk     |
| 아라하시 타비 |       49 |       49 | talk     |
| 네네코 마시로 |       42 |       48 | talk     |
| 시라유키 히나 |       37 |       57 | talk     |
| 유즈하 리코  |       36 |       61 | talk     |
| 사키하네 후야 |       30 |       69 | talk     |
| 아야츠노 유니 |       24 |       56 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리              |   방송수 |
|:------------------|------:|
| talk              |  1295 |
| 마인크래프트            |   370 |
| 리그 오브 레전드         |   140 |
| 이터널 리턴            |   111 |
| 오버워치              |    99 |
| 음악/노래             |    93 |
| 2026 FIFA 북중미 월드컵 |    57 |
| 종합 게임             |    51 |
| 팰월드               |    41 |
| 붕괴: 스타레일          |    39 |


## 시작 시간대별 방송 수

```sql
SELECT CAST(substr(publish_date,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;
```

|   시작시 |   방송수 |
|------:|------:|
|     1 |   495 |
|     0 |   469 |
|    23 |   356 |
|     2 |   305 |
|    22 |   232 |
|     3 |   217 |
|    21 |   148 |
|     4 |   129 |

