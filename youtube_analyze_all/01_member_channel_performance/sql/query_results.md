# 분석 쿼리 실행 결과

`sql/stellive.db`(SQLite)에 대해 `analysis_queries.sql`을 실행한 결과입니다.

## 구독자 상위 랭킹

```sql
SELECT rank_subs AS 순위, name_ko AS 멤버, unit AS 유닛,
       subscribers AS 구독자, recent_avg_views AS 최근평균조회수
FROM channel_metrics ORDER BY subscribers DESC;
```

|   순위 | 멤버      | 유닛       |    구독자 |   최근평균조회수 |
|-----:|:--------|:---------|-------:|----------:|
|    1 | 아야츠노 유니 | EVERYS   | 373000 |    164860 |
|    2 | 아카네 리제  | UNIVERSE | 371000 |    313990 |
|    3 | 시라유키 히나 | UNIVERSE | 330000 |    166821 |
|    4 | 아오쿠모 린  | CLICHE   | 299000 |    195916 |
|    5 | 아라하시 타비 | UNIVERSE | 274000 |    231325 |
|    6 | 텐코 시부키  | CLICHE   | 242000 |    258055 |
|    7 | 유즈하 리코  | CLICHE   | 236000 |    281165 |
|    8 | 하나코 나나  | CLICHE   | 221000 |    240026 |
|    9 | 네네코 마시로 | UNIVERSE | 196000 |    144343 |
|   10 | 사키하네 후야 | EVERYS   | 150000 |    125831 |


## 도달 효율(평균조회수/구독자) 상위

```sql
SELECT name_ko AS 멤버, subscribers AS 구독자,
       recent_avg_views AS 평균조회수,
       ROUND(reach_ratio*100,1) AS 도달효율_pct
FROM channel_metrics WHERE role='talent'
ORDER BY reach_ratio DESC;
```

| 멤버      |    구독자 |   평균조회수 |   도달효율_pct |
|:--------|-------:|--------:|-----------:|
| 유즈하 리코  | 236000 |  281165 |      119.1 |
| 하나코 나나  | 221000 |  240026 |      108.6 |
| 텐코 시부키  | 242000 |  258055 |      106.6 |
| 아카네 리제  | 371000 |  313990 |       84.6 |
| 아라하시 타비 | 274000 |  231325 |       84.4 |
| 사키하네 후야 | 150000 |  125831 |       83.9 |
| 네네코 마시로 | 196000 |  144343 |       73.6 |
| 아오쿠모 린  | 299000 |  195916 |       65.5 |
| 시라유키 히나 | 330000 |  166821 |       50.6 |
| 아야츠노 유니 | 373000 |  164860 |       44.2 |


## 유닛별 요약

```sql
SELECT unit AS 유닛, COUNT(*) AS 인원,
       CAST(AVG(subscribers) AS INT) AS 평균구독자,
       CAST(AVG(recent_avg_views) AS INT) AS 평균조회수,
       ROUND(AVG(recent_avg_engagement_rate)*100,2) AS 평균참여율_pct
FROM channel_metrics WHERE role='talent'
GROUP BY unit ORDER BY 평균구독자 DESC;
```

| 유닛       |   인원 |   평균구독자 |   평균조회수 |   평균참여율_pct |
|:---------|-----:|--------:|--------:|------------:|
| UNIVERSE |    4 |  292750 |  214119 |        2.98 |
| EVERYS   |    2 |  261500 |  145345 |        3.19 |
| CLICHE   |    4 |  249500 |  243790 |        2.82 |


## 참여율 상위

```sql
SELECT name_ko AS 멤버,
       ROUND(recent_avg_engagement_rate*100,2) AS 참여율_pct,
       ROUND(recent_avg_like_rate*100,2) AS 좋아요율_pct
FROM channel_metrics WHERE role='talent'
ORDER BY recent_avg_engagement_rate DESC;
```

| 멤버      |   참여율_pct |   좋아요율_pct |
|:--------|----------:|-----------:|
| 네네코 마시로 |      3.63 |       3.44 |
| 사키하네 후야 |      3.63 |       3.49 |
| 시라유키 히나 |      3.34 |       3.17 |
| 유즈하 리코  |      3.08 |       2.96 |
| 아오쿠모 린  |      2.84 |       2.73 |
| 아야츠노 유니 |      2.74 |       2.57 |
| 하나코 나나  |      2.73 |       2.63 |
| 텐코 시부키  |      2.62 |       2.54 |
| 아라하시 타비 |      2.55 |       2.43 |
| 아카네 리제  |      2.39 |       2.32 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.46 |         36 |
| 텐코 시부키  |    6.6  |         36 |
| 아카네 리제  |    5.2  |         40 |
| 유즈하 리코  |    5.04 |         42 |
| 아오쿠모 린  |    4.29 |         20 |
| 아라하시 타비 |    4.13 |         12 |
| 시라유키 히나 |    3.61 |         38 |
| 사키하네 후야 |    3.54 |         24 |
| 아야츠노 유니 |    2.81 |         14 |
| 네네코 마시로 |    2.35 |         10 |


## 멤버별 최고 조회수 영상

```sql
SELECT m.name_ko AS 멤버, v.title AS 영상, v.views AS 조회수
FROM videos v
JOIN (SELECT channel_id, MAX(views) AS mx FROM videos GROUP BY channel_id) t
  ON v.channel_id=t.channel_id AND v.views=t.mx
JOIN channel_metrics m ON m.channel_id=v.channel_id
ORDER BY v.views DESC;
```

| 멤버      | 영상                                                                    |     조회수 |
|:--------|:----------------------------------------------------------------------|--------:|
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1231863 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1098212 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1059251 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  914950 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  758842 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  704131 |
| 하나코 나나  | 아메와 이츠카 야무노 데쇼~카~ #animation #shorts                                  |  669629 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  605201 |
| 텐코 시부키  | 대두즈 면접 #shorts #vtuber                                                |  593783 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  503389 |

