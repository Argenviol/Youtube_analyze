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
|    1 | 아라하시 타비 |   5.24 |   7.44 |   39   |
|    2 | 시라유키 히나 |   5.9  |   6.15 |   36.3 |
|    3 | 아야츠노 유니 |   5.71 |   6.34 |   36.2 |
|    4 | 텐코 시부키  |   5    |   7.08 |   35.4 |
|    5 | 유즈하 리코  |   4.91 |   6.98 |   34.3 |
|    6 | 사키하네 후야 |   5.21 |   5    |   26.1 |
|    7 | 네네코 마시로 |   5.21 |   4.83 |   25.2 |
|    8 | 아카네 리제  |   4.71 |   4.96 |   23.3 |
|    9 | 하나코 나나  |   4.29 |   5.29 |   22.7 |
|   10 | 아오쿠모 린  |   4.55 |   4.72 |   21.4 |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 텐코 시부키  |         81 |     4.8 |
| 시라유키 히나 |         71 |     6.6 |
| 유즈하 리코  |         67 |     7.8 |
| 아라하시 타비 |         67 |     6.5 |
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
| 텐코 시부키  |       72 |       25 | talk     |
| 아카네 리제  |       52 |       45 | talk     |
| 아라하시 타비 |       51 |       47 | talk     |
| 네네코 마시로 |       42 |       48 | talk     |
| 시라유키 히나 |       39 |       55 | talk     |
| 유즈하 리코  |       38 |       58 | talk     |
| 사키하네 후야 |       31 |       68 | talk     |
| 아야츠노 유니 |       27 |       53 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리               |   방송수 |
|:-------------------|------:|
| talk               |  1270 |
| 마인크래프트             |   385 |
| 리그 오브 레전드          |   135 |
| 이터널 리턴             |   109 |
| 오버워치               |   100 |
| 음악/노래              |    90 |
| 2026 FIFA 북중미 월드컵  |    57 |
| Grand Theft Auto V |    52 |
| 종합 게임              |    48 |
| 팰월드                |    41 |


## 시작 시간대별 방송 수

```sql
SELECT CAST(substr(publish_date,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;
```

|   시작시 |   방송수 |
|------:|------:|
|     1 |   482 |
|     0 |   460 |
|    23 |   357 |
|     2 |   307 |
|     3 |   256 |
|    22 |   225 |
|    21 |   148 |
|     4 |   135 |

