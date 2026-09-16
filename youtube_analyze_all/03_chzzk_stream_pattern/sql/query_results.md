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
|    1 | 아라하시 타비 |   5.24 |   7.4  |   38.8 |
|    2 | 시라유키 히나 |   5.92 |   6.1  |   36.1 |
|    3 | 아야츠노 유니 |   5.57 |   6.36 |   35.4 |
|    4 | 텐코 시부키  |   5.01 |   7.06 |   35.4 |
|    5 | 유즈하 리코  |   4.91 |   6.94 |   34.1 |
|    6 | 사키하네 후야 |   5.18 |   5.04 |   26.1 |
|    7 | 네네코 마시로 |   5.22 |   4.81 |   25.1 |
|    8 | 아카네 리제  |   4.7  |   4.95 |   23.3 |
|    9 | 하나코 나나  |   4.27 |   5.28 |   22.5 |
|   10 | 아오쿠모 린  |   4.56 |   4.69 |   21.4 |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 텐코 시부키  |         81 |     4.8 |
| 시라유키 히나 |         71 |     6.7 |
| 아라하시 타비 |         66 |     6.5 |
| 유즈하 리코  |         66 |     7.9 |
| 아카네 리제  |         65 |     7.9 |
| 아오쿠모 린  |         65 |     8.2 |
| 하나코 나나  |         52 |    10.5 |
| 아야츠노 유니 |         46 |     9.6 |
| 사키하네 후야 |         38 |    13.2 |
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
| 텐코 시부키  |       71 |       26 | talk     |
| 아카네 리제  |       52 |       46 | talk     |
| 아라하시 타비 |       50 |       48 | talk     |
| 네네코 마시로 |       42 |       48 | talk     |
| 시라유키 히나 |       38 |       56 | talk     |
| 유즈하 리코  |       38 |       58 | talk     |
| 사키하네 후야 |       32 |       68 | talk     |
| 아야츠노 유니 |       25 |       55 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리              |   방송수 |
|:------------------|------:|
| talk              |  1278 |
| 마인크래프트            |   387 |
| 리그 오브 레전드         |   135 |
| 이터널 리턴            |   109 |
| 오버워치              |   100 |
| 음악/노래             |    90 |
| 2026 FIFA 북중미 월드컵 |    57 |
| 종합 게임             |    48 |
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
|     1 |   484 |
|     0 |   464 |
|    23 |   357 |
|     2 |   311 |
|     3 |   244 |
|    22 |   226 |
|    21 |   147 |
|     4 |   132 |

