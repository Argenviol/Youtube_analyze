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
|    1 | 아야츠노 유니 | EVERYS   | 371000 |    161696 |
|    2 | 아카네 리제  | UNIVERSE | 369000 |    302611 |
|    3 | 시라유키 히나 | UNIVERSE | 329000 |    180659 |
|    4 | 아오쿠모 린  | CLICHE   | 296000 |    184304 |
|    5 | 아라하시 타비 | UNIVERSE | 272000 |    222778 |
|    6 | 텐코 시부키  | CLICHE   | 240000 |    247249 |
|    7 | 유즈하 리코  | CLICHE   | 234000 |    265957 |
|    8 | 하나코 나나  | CLICHE   | 219000 |    246031 |
|    9 | 네네코 마시로 | UNIVERSE | 194000 |    142240 |
|   10 | 사키하네 후야 | EVERYS   | 147000 |    122133 |


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
| 유즈하 리코  | 234000 |  265957 |      113.7 |
| 하나코 나나  | 219000 |  246031 |      112.3 |
| 텐코 시부키  | 240000 |  247249 |      103   |
| 사키하네 후야 | 147000 |  122133 |       83.1 |
| 아카네 리제  | 369000 |  302611 |       82   |
| 아라하시 타비 | 272000 |  222778 |       81.9 |
| 네네코 마시로 | 194000 |  142240 |       73.3 |
| 아오쿠모 린  | 296000 |  184304 |       62.3 |
| 시라유키 히나 | 329000 |  180659 |       54.9 |
| 아야츠노 유니 | 371000 |  161696 |       43.6 |


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
| UNIVERSE |    4 |  291000 |  212072 |        3    |
| EVERYS   |    2 |  259000 |  141914 |        3.25 |
| CLICHE   |    4 |  247250 |  235885 |        2.84 |


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
| 네네코 마시로 |      3.72 |       3.52 |
| 사키하네 후야 |      3.64 |       3.49 |
| 시라유키 히나 |      3.27 |       3.1  |
| 유즈하 리코  |      3.07 |       2.94 |
| 아오쿠모 린  |      3    |       2.87 |
| 아야츠노 유니 |      2.86 |       2.68 |
| 하나코 나나  |      2.7  |       2.61 |
| 아라하시 타비 |      2.6  |       2.47 |
| 텐코 시부키  |      2.57 |       2.49 |
| 아카네 리제  |      2.42 |       2.35 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.62 |         38 |
| 텐코 시부키  |    6.35 |         36 |
| 아카네 리제  |    5.12 |         38 |
| 유즈하 리코  |    5.04 |         40 |
| 아오쿠모 린  |    4.4  |         22 |
| 아라하시 타비 |    3.9  |         12 |
| 시라유키 히나 |    3.65 |         40 |
| 사키하네 후야 |    3.5  |         24 |
| 아야츠노 유니 |    2.83 |         14 |
| 네네코 마시로 |    2.32 |         10 |


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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1211100 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1079259 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1043611 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        | 1004250 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  862910 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  752730 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  702009 |
| 하나코 나나  | 아메와 이츠카 야무노 데쇼~카~ #animation #shorts                                  |  643417 |
| 텐코 시부키  | 대두즈 면접 #shorts #vtuber                                                |  555080 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  485118 |

