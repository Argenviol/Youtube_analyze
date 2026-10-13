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
|    1 | 아라하시 타비 |   5.37 |   7.6  |   40.8 |
|    2 | 아야츠노 유니 |   5.98 |   6.28 |   37.6 |
|    3 | 시라유키 히나 |   5.95 |   6.28 |   37.4 |
|    4 | 텐코 시부키  |   5.07 |   7.16 |   36.3 |
|    5 | 유즈하 리코  |   4.88 |   7.23 |   35.3 |
|    6 | 사키하네 후야 |   5.25 |   5.06 |   26.6 |
|    7 | 네네코 마시로 |   5.25 |   4.88 |   25.6 |
|    8 | 아카네 리제  |   4.74 |   5.07 |   24   |
|    9 | 하나코 나나  |   4.29 |   5.39 |   23.1 |
|   10 | 아오쿠모 린  |   4.56 |   4.96 |   22.6 |


## 심야 방송 비중(0~5시 시작)

```sql
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;
```

| 멤버      |   심야비중_pct |   평균시작시 |
|:--------|-----------:|--------:|
| 텐코 시부키  |         81 |     4.8 |
| 시라유키 히나 |         72 |     6.4 |
| 유즈하 리코  |         70 |     7.4 |
| 아라하시 타비 |         67 |     6.5 |
| 아카네 리제  |         67 |     7.6 |
| 아오쿠모 린  |         67 |     8   |
| 하나코 나나  |         53 |    10.4 |
| 아야츠노 유니 |         48 |     9.3 |
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
| 텐코 시부키  |       76 |       21 | talk     |
| 하나코 나나  |       75 |       18 | talk     |
| 아카네 리제  |       53 |       44 | talk     |
| 아라하시 타비 |       51 |       47 | talk     |
| 네네코 마시로 |       41 |       49 | talk     |
| 시라유키 히나 |       40 |       56 | talk     |
| 유즈하 리코  |       39 |       59 | talk     |
| 사키하네 후야 |       32 |       67 | talk     |
| 아야츠노 유니 |       28 |       50 | talk     |


## 인기 방송 카테고리 TOP 10

```sql
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;
```

| 카테고리               |   방송수 |
|:-------------------|------:|
| talk               |  1251 |
| 마인크래프트             |   367 |
| Grand Theft Auto V |   156 |
| 리그 오브 레전드          |   136 |
| 오버워치               |   107 |
| 이터널 리턴             |   106 |
| 음악/노래              |    78 |
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
|     1 |   477 |
|     0 |   442 |
|    23 |   347 |
|     3 |   303 |
|     2 |   303 |
|    22 |   227 |
|    21 |   154 |
|     4 |   151 |

