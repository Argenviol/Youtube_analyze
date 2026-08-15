# 경쟁사 비교 분석 쿼리 결과

`sql/competitors.db`(SQLite) 실행 결과.

## 그룹별 요약 비교

```sql
SELECT "group" AS 그룹, n_members AS 인원, CAST(avg_subscribers AS INT) AS 평균구독자,
       CAST(avg_recent_views AS INT) AS 평균조회수,
       ROUND(avg_engagement_rate*100,2) AS 참여율_pct,
       ROUND(avg_reach_ratio*100,1) AS 도달효율_pct
FROM group_summary ORDER BY 평균구독자 DESC;
```

| 그룹       |   인원 |   평균구독자 |   평균조회수 |   참여율_pct |   도달효율_pct |
|:---------|-----:|--------:|--------:|----------:|-----------:|
| 홀로라이브    |    6 | 3005000 |  462480 |      7.15 |       13.1 |
| 이세계아이돌   |    6 |  413666 |   97012 |      6.16 |       23.6 |
| StelLive |    6 |  265333 |  151786 |      4.19 |       59.9 |


## 전체 멤버 구독자 랭킹

```sql
SELECT rank AS 순위, "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자
FROM member_metrics ORDER BY subscribers DESC;
```

|   순위 | 그룹       | 멤버       |     구독자 |
|-----:|:---------|:---------|--------:|
|    1 | 홀로라이브    | 가우르 구라   | 4610000 |
|    2 | 홀로라이브    | 호쇼 마린    | 4400000 |
|    3 | 홀로라이브    | 우사다 페코라  | 2790000 |
|    4 | 홀로라이브    | 모리 캘리오프  | 2620000 |
|    5 | 홀로라이브    | 이누가미 코로네 | 2280000 |
|    6 | 홀로라이브    | 모모스즈 네네  | 1330000 |
|    7 | 이세계아이돌   | 고세구      |  537000 |
|    8 | 이세계아이돌   | 릴파       |  428000 |
|    9 | 이세계아이돌   | 징버거      |  421000 |
|   10 | 이세계아이돌   | 주르르      |  411000 |
|   11 | 이세계아이돌   | 아이네      |  359000 |
|   12 | StelLive | 아야츠노 유니  |  359000 |
|   13 | StelLive | 아카네 리제   |  348000 |
|   14 | 이세계아이돌   | 비챤       |  326000 |
|   15 | StelLive | 시라유키 히나  |  319000 |
|   16 | StelLive | 아라하시 타비  |  256000 |
|   17 | StelLive | 네네코 마시로  |  180000 |
|   18 | StelLive | 사키하네 후야  |  130000 |


## 참여율 상위 10명

```sql
SELECT "group" AS 그룹, name_ko AS 멤버,
       ROUND(recent_avg_engagement_rate*100,2) AS 참여율_pct
FROM member_metrics ORDER BY recent_avg_engagement_rate DESC LIMIT 10;
```

| 그룹     | 멤버       |   참여율_pct |
|:-------|:---------|----------:|
| 홀로라이브  | 모리 캘리오프  |      9.33 |
| 이세계아이돌 | 비챤       |      9.02 |
| 홀로라이브  | 모모스즈 네네  |      8.28 |
| 홀로라이브  | 가우르 구라   |      7.28 |
| 홀로라이브  | 호쇼 마린    |      7.05 |
| 이세계아이돌 | 릴파       |      6.5  |
| 홀로라이브  | 이누가미 코로네 |      5.97 |
| 이세계아이돌 | 주르르      |      5.63 |
| 이세계아이돌 | 고세구      |      5.51 |
| 이세계아이돌 | 징버거      |      5.41 |


## 도달 효율 상위 10명

```sql
SELECT "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자,
       ROUND(reach_ratio*100,0) AS 도달효율_pct
FROM member_metrics ORDER BY reach_ratio DESC LIMIT 10;
```

| 그룹       | 멤버      |     구독자 |   도달효율_pct |
|:---------|:--------|--------:|-----------:|
| StelLive | 사키하네 후야 |  130000 |         83 |
| StelLive | 아카네 리제  |  348000 |         77 |
| StelLive | 아라하시 타비 |  256000 |         71 |
| StelLive | 네네코 마시로 |  180000 |         51 |
| StelLive | 시라유키 히나 |  319000 |         44 |
| 이세계아이돌   | 아이네     |  359000 |         38 |
| StelLive | 아야츠노 유니 |  359000 |         35 |
| 이세계아이돌   | 징버거     |  421000 |         30 |
| 홀로라이브    | 가우르 구라  | 4610000 |         27 |
| 이세계아이돌   | 주르르     |  411000 |         21 |

