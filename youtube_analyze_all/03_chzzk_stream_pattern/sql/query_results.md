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
|    1 | 아라하시 타비 |   5.22 |   7.36 |   38.4 |
|    2 | 시라유키 히나 |   5.87 |   6.07 |   35.6 |
|    3 | 텐코 시부키  |   5.01 |   7.04 |   35.3 |
|    4 | 아야츠노 유니 |   5.5  |   6.34 |   34.8 |
|    5 | 유즈하 리코  |   4.88 |   6.92 |   33.8 |
|    6 | 사키하네 후야 |   5.17 |   5.03 |   26   |
|    7 | 네네코 마시로 |   5.21 |   4.81 |   25.1 |
|    8 | 아카네 리제  |   4.69 |   4.94 |   23.2 |
|    9 | 하나코 나나  |   4.28 |   5.27 |   22.5 |
|   10 | 아오쿠모 린  |   4.54 |   4.65 |   21.1 |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 텐코 시부키  |         80 |     4.9 |
| 시라유키 히나 |         71 |     6.7 |
| 아라하시 타비 |         66 |     6.6 |
| 유즈하 리코  |         66 |     8   |
| 아카네 리제  |         65 |     7.9 |
| 아오쿠모 린  |         65 |     8.2 |
| 하나코 나나  |         52 |    10.5 |
| 아야츠노 유니 |         46 |     9.6 |
| 사키하네 후야 |         38 |    13.3 |
| 네네코 마시로 |         22 |    16.4 |


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
| 아라하시 타비 |       50 |       48 | talk     |
| 네네코 마시로 |       42 |       48 | talk     |
| 시라유키 히나 |       38 |       56 | talk     |
| 유즈하 리코  |       38 |       59 | talk     |
| 사키하네 후야 |       31 |       68 | talk     |
| 아야츠노 유니 |       25 |       55 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리              |   방송수 |
|:------------------|------:|
| talk              |  1285 |
| 마인크래프트            |   390 |
| 리그 오브 레전드         |   136 |
| 이터널 리턴            |   109 |
| 오버워치              |   100 |
| 음악/노래             |    90 |
| 2026 FIFA 북중미 월드컵 |    57 |
| 종합 게임             |    49 |
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
|     1 |   487 |
|     0 |   469 |
|    23 |   358 |
|     2 |   313 |
|     3 |   230 |
|    22 |   225 |
|    21 |   147 |
|     4 |   132 |

