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
|    1 | 아라하시 타비 |   5.26 |   7.22 |   38   |
|    2 | 텐코 시부키  |   5.02 |   6.92 |   34.8 |
|    3 | 아야츠노 유니 |   5.38 |   6.34 |   34.1 |
|    4 | 시라유키 히나 |   5.61 |   5.91 |   33.2 |
|    5 | 유즈하 리코  |   4.77 |   6.9  |   32.9 |
|    6 | 사키하네 후야 |   5.17 |   5.17 |   26.7 |
|    7 | 네네코 마시로 |   5.21 |   4.78 |   24.9 |
|    8 | 아카네 리제  |   4.72 |   5.01 |   23.7 |
|    9 | 하나코 나나  |   4.17 |   5.25 |   21.9 |
|   10 | 아오쿠모 린  |   4.52 |   4.54 |   20.5 |


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
| 유즈하 리코  |         66 |     8   |
| 아카네 리제  |         65 |     8   |
| 아오쿠모 린  |         65 |     8.2 |
| 아라하시 타비 |         65 |     6.6 |
| 하나코 나나  |         50 |    10.9 |
| 아야츠노 유니 |         46 |     9.6 |
| 사키하네 후야 |         39 |    13.1 |
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
| 네네코 마시로 |       41 |       49 | talk     |
| 시라유키 히나 |       37 |       56 | talk     |
| 유즈하 리코  |       36 |       61 | talk     |
| 사키하네 후야 |       31 |       69 | talk     |
| 아야츠노 유니 |       24 |       57 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리              |   방송수 |
|:------------------|------:|
| talk              |  1293 |
| 마인크래프트            |   343 |
| 리그 오브 레전드         |   145 |
| 이터널 리턴            |    99 |
| 음악/노래             |    99 |
| 오버워치              |    99 |
| 2026 FIFA 북중미 월드컵 |    57 |
| 종합 게임             |    52 |
| 팰월드               |    41 |
| 붕괴: 스타레일          |    40 |


## 시작 시간대별 방송 수

```sql
SELECT CAST(substr(publish_date,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;
```

|   시작시 |   방송수 |
|------:|------:|
|     1 |   502 |
|     0 |   475 |
|    23 |   360 |
|     2 |   308 |
|    22 |   235 |
|     3 |   206 |
|    21 |   143 |
|     4 |   129 |

