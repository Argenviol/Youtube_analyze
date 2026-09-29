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
|    1 | 아라하시 타비 |   5.3  |   7.5  |   39.8 |
|    2 | 아야츠노 유니 |   5.9  |   6.37 |   37.6 |
|    3 | 시라유키 히나 |   5.92 |   6.29 |   37.2 |
|    4 | 텐코 시부키  |   5.05 |   7.15 |   36.1 |
|    5 | 유즈하 리코  |   4.88 |   7.14 |   34.9 |
|    6 | 사키하네 후야 |   5.24 |   5.08 |   26.6 |
|    7 | 네네코 마시로 |   5.26 |   4.83 |   25.4 |
|    8 | 아카네 리제  |   4.72 |   5.06 |   23.9 |
|    9 | 하나코 나나  |   4.29 |   5.36 |   23   |
|   10 | 아오쿠모 린  |   4.58 |   4.86 |   22.2 |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 텐코 시부키  |         81 |     4.8 |
| 시라유키 히나 |         72 |     6.6 |
| 유즈하 리코  |         69 |     7.5 |
| 아라하시 타비 |         67 |     6.5 |
| 아카네 리제  |         66 |     7.8 |
| 아오쿠모 린  |         66 |     8.2 |
| 하나코 나나  |         52 |    10.5 |
| 아야츠노 유니 |         47 |     9.3 |
| 사키하네 후야 |         39 |    13.2 |
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
| 하나코 나나  |       75 |       18 | talk     |
| 텐코 시부키  |       74 |       23 | talk     |
| 아카네 리제  |       53 |       44 | talk     |
| 아라하시 타비 |       51 |       47 | talk     |
| 네네코 마시로 |       42 |       48 | talk     |
| 시라유키 히나 |       41 |       54 | talk     |
| 유즈하 리코  |       38 |       59 | talk     |
| 사키하네 후야 |       33 |       67 | talk     |
| 아야츠노 유니 |       29 |       51 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리               |   방송수 |
|:-------------------|------:|
| talk               |  1245 |
| 마인크래프트             |   376 |
| 리그 오브 레전드          |   135 |
| Grand Theft Auto V |   130 |
| 이터널 리턴             |   108 |
| 오버워치               |   100 |
| 음악/노래              |    84 |
| 2026 FIFA 북중미 월드컵  |    57 |
| 종합 게임              |    51 |
| 팰월드                |    41 |


## 시작 시간대별 방송 수

```sql
SELECT CAST(substr(publish_date,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;
```

|   시작시 |   방송수 |
|------:|------:|
|     1 |   467 |
|     0 |   446 |
|    23 |   355 |
|     2 |   299 |
|     3 |   295 |
|    22 |   224 |
|     4 |   152 |
|    21 |   150 |

