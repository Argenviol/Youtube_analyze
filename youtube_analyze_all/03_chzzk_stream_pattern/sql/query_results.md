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
|    1 | 아라하시 타비 |   5.29 |   7.48 |   39.6 |
|    2 | 아야츠노 유니 |   5.87 |   6.37 |   37.3 |
|    3 | 시라유키 히나 |   5.93 |   6.22 |   36.9 |
|    4 | 텐코 시부키  |   5.04 |   7.12 |   35.9 |
|    5 | 유즈하 리코  |   4.88 |   7.09 |   34.6 |
|    6 | 사키하네 후야 |   5.23 |   5.04 |   26.3 |
|    7 | 네네코 마시로 |   5.2  |   4.84 |   25.1 |
|    8 | 아카네 리제  |   4.71 |   5.06 |   23.8 |
|    9 | 하나코 나나  |   4.28 |   5.34 |   22.9 |
|   10 | 아오쿠모 린  |   4.56 |   4.81 |   21.9 |


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
| 유즈하 리코  |         68 |     7.6 |
| 아라하시 타비 |         67 |     6.5 |
| 아카네 리제  |         66 |     7.8 |
| 아오쿠모 린  |         66 |     8.2 |
| 하나코 나나  |         52 |    10.5 |
| 아야츠노 유니 |         47 |     9.4 |
| 사키하네 후야 |         38 |    13.3 |
| 네네코 마시로 |         21 |    16.7 |


## 게임 vs 토크 성향

```sql
SELECT name_ko AS 멤버, ROUND(game_share*100,0) AS 게임_pct,
       ROUND(talk_share*100,0) AS 토크_pct, top_category AS 주력카테고리
FROM stream_metrics ORDER BY game_share DESC;
```

| 멤버      |   게임_pct |   토크_pct | 주력카테고리   |
|:--------|---------:|---------:|:---------|
| 아오쿠모 린  |       88 |        9 | 마인크래프트   |
| 하나코 나나  |       75 |       18 | talk     |
| 텐코 시부키  |       74 |       24 | talk     |
| 아카네 리제  |       53 |       45 | talk     |
| 아라하시 타비 |       51 |       47 | talk     |
| 네네코 마시로 |       42 |       47 | talk     |
| 시라유키 히나 |       41 |       54 | talk     |
| 유즈하 리코  |       38 |       59 | talk     |
| 사키하네 후야 |       32 |       67 | talk     |
| 아야츠노 유니 |       28 |       52 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리               |   방송수 |
|:-------------------|------:|
| talk               |  1250 |
| 마인크래프트             |   380 |
| 리그 오브 레전드          |   135 |
| 이터널 리턴             |   109 |
| Grand Theft Auto V |   103 |
| 오버워치               |   100 |
| 음악/노래              |    87 |
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
|     1 |   473 |
|     0 |   450 |
|    23 |   356 |
|     2 |   302 |
|     3 |   283 |
|    22 |   225 |
|    21 |   149 |
|     4 |   145 |

