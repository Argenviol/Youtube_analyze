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
|    1 | 아라하시 타비 |   5.41 |   7.68 |   41.6 |
|    2 | 아야츠노 유니 |   6.1  |   6.25 |   38.1 |
|    3 | 시라유키 히나 |   6.05 |   6.28 |   38   |
|    4 | 유즈하 리코  |   5.13 |   7.27 |   37.3 |
|    5 | 텐코 시부키  |   5.15 |   7.18 |   37   |
|    6 | 사키하네 후야 |   5.28 |   5.04 |   26.6 |
|    7 | 네네코 마시로 |   5.25 |   4.92 |   25.8 |
|    8 | 아카네 리제  |   4.7  |   5.04 |   23.7 |
|    9 | 하나코 나나  |   4.29 |   5.4  |   23.1 |
|   10 | 아오쿠모 린  |   4.56 |   5.01 |   22.8 |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 시라유키 히나 |          9 |    16.1 |
| 아야츠노 유니 |          7 |    15.2 |
| 아라하시 타비 |          3 |    15.8 |
| 아오쿠모 린  |          3 |    18.5 |
| 텐코 시부키  |          2 |    17.5 |
| 아카네 리제  |          1 |    19   |
| 하나코 나나  |          1 |    17.6 |
| 유즈하 리코  |          1 |    17.2 |
| 사키하네 후야 |          1 |    17.5 |
| 네네코 마시로 |          0 |    16.8 |


## 게임 vs 토크 성향

```sql
SELECT name_ko AS 멤버, ROUND(game_share*100,0) AS 게임_pct,
       ROUND(talk_share*100,0) AS 토크_pct, top_category AS 주력카테고리
FROM stream_metrics ORDER BY game_share DESC;
```

| 멤버      |   게임_pct |   토크_pct | 주력카테고리   |
|:--------|---------:|---------:|:---------|
| 아오쿠모 린  |       89 |        9 | 마인크래프트   |
| 텐코 시부키  |       77 |       20 | talk     |
| 하나코 나나  |       74 |       18 | talk     |
| 아카네 리제  |       53 |       44 | talk     |
| 아라하시 타비 |       53 |       45 | talk     |
| 네네코 마시로 |       41 |       50 | talk     |
| 시라유키 히나 |       41 |       56 | talk     |
| 유즈하 리코  |       40 |       58 | talk     |
| 사키하네 후야 |       32 |       67 | talk     |
| 아야츠노 유니 |       29 |       49 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리               |   방송수 |
|:-------------------|------:|
| talk               |  1248 |
| 마인크래프트             |   373 |
| Grand Theft Auto V |   156 |
| 리그 오브 레전드          |   134 |
| 오버워치               |   122 |
| 이터널 리턴             |   107 |
| 음악/노래              |    75 |
| 2026 FIFA 북중미 월드컵  |    57 |
| 종합 게임              |    51 |
| 팰월드                |    41 |


## 시작 시간대별 방송 수

```sql
SELECT CAST(substr(start_kst,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;
```

|   시작시 |   방송수 |
|------:|------:|
|    18 |   580 |
|    17 |   523 |
|    19 |   399 |
|    16 |   359 |
|    20 |   254 |
|    21 |   210 |
|    15 |   164 |
|    14 |   104 |

