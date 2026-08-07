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
| 홀로라이브    |    6 | 3001666 |  481659 |      7.01 |       13.6 |
| 이세계아이돌   |    6 |  414166 |   93544 |      6.21 |       22.7 |
| StelLive |    6 |  263833 |  155585 |      4.24 |       59.8 |


## 전체 멤버 구독자 랭킹

```sql
SELECT rank AS 순위, "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자
FROM member_metrics ORDER BY subscribers DESC;
```

|   순위 | 그룹       | 멤버       |     구독자 |
|-----:|:---------|:---------|--------:|
|    1 | 홀로라이브    | 가우르 구라   | 4610000 |
|    2 | 홀로라이브    | 호쇼 마린    | 4390000 |
|    3 | 홀로라이브    | 우사다 페코라  | 2780000 |
|    4 | 홀로라이브    | 모리 캘리오프  | 2620000 |
|    5 | 홀로라이브    | 이누가미 코로네 | 2280000 |
|    6 | 홀로라이브    | 모모스즈 네네  | 1330000 |
|    7 | 이세계아이돌   | 고세구      |  538000 |
|    8 | 이세계아이돌   | 릴파       |  429000 |
|    9 | 이세계아이돌   | 징버거      |  421000 |
|   10 | 이세계아이돌   | 주르르      |  412000 |
|   11 | 이세계아이돌   | 아이네      |  359000 |
|   12 | StelLive | 아야츠노 유니  |  358000 |
|   13 | StelLive | 아카네 리제   |  345000 |
|   14 | 이세계아이돌   | 비챤       |  326000 |
|   15 | StelLive | 시라유키 히나  |  318000 |
|   16 | StelLive | 아라하시 타비  |  254000 |
|   17 | StelLive | 네네코 마시로  |  179000 |
|   18 | StelLive | 사키하네 후야  |  129000 |


## 참여율 상위 10명

```sql
SELECT "group" AS 그룹, name_ko AS 멤버,
       ROUND(recent_avg_engagement_rate*100,2) AS 참여율_pct
FROM member_metrics ORDER BY recent_avg_engagement_rate DESC LIMIT 10;
```

| 그룹     | 멤버       |   참여율_pct |
|:-------|:---------|----------:|
| 홀로라이브  | 모리 캘리오프  |     10.15 |
| 이세계아이돌 | 비챤       |      8.73 |
| 홀로라이브  | 모모스즈 네네  |      8.41 |
| 홀로라이브  | 가우르 구라   |      7.29 |
| 이세계아이돌 | 릴파       |      6.66 |
| 이세계아이돌 | 주르르      |      5.68 |
| 이세계아이돌 | 징버거      |      5.6  |
| 이세계아이돌 | 고세구      |      5.6  |
| 홀로라이브  | 이누가미 코로네 |      5.54 |
| 홀로라이브  | 호쇼 마린    |      5.39 |


## 도달 효율 상위 10명

```sql
SELECT "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자,
       ROUND(reach_ratio*100,0) AS 도달효율_pct
FROM member_metrics ORDER BY reach_ratio DESC LIMIT 10;
```

| 그룹       | 멤버      |     구독자 |   도달효율_pct |
|:---------|:--------|--------:|-----------:|
| StelLive | 아카네 리제  |  345000 |         86 |
| StelLive | 사키하네 후야 |  129000 |         69 |
| StelLive | 아라하시 타비 |  254000 |         68 |
| StelLive | 시라유키 히나 |  318000 |         52 |
| StelLive | 네네코 마시로 |  179000 |         50 |
| 이세계아이돌   | 아이네     |  359000 |         35 |
| StelLive | 아야츠노 유니 |  358000 |         33 |
| 이세계아이돌   | 징버거     |  421000 |         29 |
| 홀로라이브    | 가우르 구라  | 4610000 |         27 |
| 이세계아이돌   | 주르르     |  412000 |         21 |

