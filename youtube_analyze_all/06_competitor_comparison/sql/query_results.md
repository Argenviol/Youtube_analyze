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
| 홀로라이브    |    6 | 3008333 |  524673 |      6.42 |       14.9 |
| 이세계아이돌   |    6 |  412666 |   98966 |      5.85 |       24.4 |
| StelLive |    6 |  268000 |  160441 |      3.78 |       63.9 |


## 전체 멤버 구독자 랭킹

```sql
SELECT rank AS 순위, "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자
FROM member_metrics ORDER BY subscribers DESC;
```

|   순위 | 그룹       | 멤버       |     구독자 |
|-----:|:---------|:---------|--------:|
|    1 | 홀로라이브    | 가우르 구라   | 4600000 |
|    2 | 홀로라이브    | 호쇼 마린    | 4420000 |
|    3 | 홀로라이브    | 우사다 페코라  | 2790000 |
|    4 | 홀로라이브    | 모리 캘리오프  | 2630000 |
|    5 | 홀로라이브    | 이누가미 코로네 | 2280000 |
|    6 | 홀로라이브    | 모모스즈 네네  | 1330000 |
|    7 | 이세계아이돌   | 고세구      |  536000 |
|    8 | 이세계아이돌   | 릴파       |  427000 |
|    9 | 이세계아이돌   | 징버거      |  420000 |
|   10 | 이세계아이돌   | 주르르      |  410000 |
|   11 | StelLive | 아야츠노 유니  |  360000 |
|   12 | 이세계아이돌   | 아이네      |  358000 |
|   13 | StelLive | 아카네 리제   |  353000 |
|   14 | 이세계아이돌   | 비챤       |  325000 |
|   15 | StelLive | 시라유키 히나  |  320000 |
|   16 | StelLive | 아라하시 타비  |  259000 |
|   17 | StelLive | 네네코 마시로  |  183000 |
|   18 | StelLive | 사키하네 후야  |  133000 |


## 참여율 상위 10명

```sql
SELECT "group" AS 그룹, name_ko AS 멤버,
       ROUND(recent_avg_engagement_rate*100,2) AS 참여율_pct
FROM member_metrics ORDER BY recent_avg_engagement_rate DESC LIMIT 10;
```

| 그룹     | 멤버       |   참여율_pct |
|:-------|:---------|----------:|
| 홀로라이브  | 모리 캘리오프  |      7.92 |
| 이세계아이돌 | 비챤       |      7.83 |
| 홀로라이브  | 모모스즈 네네  |      7.56 |
| 홀로라이브  | 가우르 구라   |      7.27 |
| 이세계아이돌 | 주르르      |      6.14 |
| 홀로라이브  | 호쇼 마린    |      6.01 |
| 이세계아이돌 | 릴파       |      5.74 |
| 홀로라이브  | 이누가미 코로네 |      5.67 |
| 이세계아이돌 | 고세구      |      5.44 |
| 이세계아이돌 | 징버거      |      5.12 |


## 도달 효율 상위 10명

```sql
SELECT "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자,
       ROUND(reach_ratio*100,0) AS 도달효율_pct
FROM member_metrics ORDER BY reach_ratio DESC LIMIT 10;
```

| 그룹       | 멤버      |     구독자 |   도달효율_pct |
|:---------|:--------|--------:|-----------:|
| StelLive | 사키하네 후야 |  133000 |         91 |
| StelLive | 아라하시 타비 |  259000 |         67 |
| StelLive | 아카네 리제  |  353000 |         67 |
| StelLive | 네네코 마시로 |  183000 |         66 |
| StelLive | 시라유키 히나 |  320000 |         56 |
| 이세계아이돌   | 아이네     |  358000 |         39 |
| StelLive | 아야츠노 유니 |  360000 |         37 |
| 홀로라이브    | 가우르 구라  | 4600000 |         27 |
| 이세계아이돌   | 징버거     |  420000 |         26 |
| 이세계아이돌   | 릴파      |  427000 |         24 |

