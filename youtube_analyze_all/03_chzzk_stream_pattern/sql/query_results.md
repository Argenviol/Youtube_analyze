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
|    2 | 텐코 시부키  |   5    |   7    |   35   |
|    3 | 아야츠노 유니 |   5.44 |   6.35 |   34.6 |
|    4 | 시라유키 히나 |   5.75 |   5.94 |   34.2 |
|    5 | 유즈하 리코  |   4.83 |   6.83 |   33   |
|    6 | 사키하네 후야 |   5.2  |   5.06 |   26.3 |
|    7 | 네네코 마시로 |   5.25 |   4.79 |   25.2 |
|    8 | 아카네 리제  |   4.72 |   4.97 |   23.4 |
|    9 | 하나코 나나  |   4.24 |   5.24 |   22.2 |
|   10 | 아오쿠모 린  |   4.58 |   4.62 |   21.1 |


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
| 아라하시 타비 |         66 |     6.5 |
| 유즈하 리코  |         65 |     8.1 |
| 아카네 리제  |         65 |     7.9 |
| 아오쿠모 린  |         65 |     8.2 |
| 하나코 나나  |         51 |    10.6 |
| 아야츠노 유니 |         46 |     9.6 |
| 사키하네 후야 |         39 |    13.2 |
| 네네코 마시로 |         23 |    16.3 |


## 게임 vs 토크 성향

```sql
SELECT name_ko AS 멤버, ROUND(game_share*100,0) AS 게임_pct,
       ROUND(talk_share*100,0) AS 토크_pct, top_category AS 주력카테고리
FROM stream_metrics ORDER BY game_share DESC;
```

| 멤버      |   게임_pct |   토크_pct | 주력카테고리   |
|:--------|---------:|---------:|:---------|
| 아오쿠모 린  |       88 |       10 | 마인크래프트   |
| 하나코 나나  |       73 |       19 | talk     |
| 텐코 시부키  |       69 |       28 | talk     |
| 아카네 리제  |       52 |       45 | talk     |
| 아라하시 타비 |       49 |       49 | talk     |
| 네네코 마시로 |       42 |       48 | talk     |
| 시라유키 히나 |       36 |       58 | talk     |
| 유즈하 리코  |       36 |       60 | talk     |
| 사키하네 후야 |       30 |       69 | talk     |
| 아야츠노 유니 |       24 |       56 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리              |   방송수 |
|:------------------|------:|
| talk              |  1298 |
| 마인크래프트            |   381 |
| 리그 오브 레전드         |   138 |
| 이터널 리턴            |   110 |
| 오버워치              |    99 |
| 음악/노래             |    92 |
| 2026 FIFA 북중미 월드컵 |    57 |
| 종합 게임             |    50 |
| 팰월드               |    41 |
| 붕괴: 스타레일          |    38 |


## 시작 시간대별 방송 수

```sql
SELECT CAST(substr(publish_date,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;
```

|   시작시 |   방송수 |
|------:|------:|
|     1 |   494 |
|     0 |   474 |
|    23 |   357 |
|     2 |   304 |
|    22 |   228 |
|     3 |   219 |
|    21 |   147 |
|     4 |   131 |

