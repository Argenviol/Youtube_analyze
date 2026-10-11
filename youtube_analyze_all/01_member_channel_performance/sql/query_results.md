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
|    1 | 아야츠노 유니 | EVERYS   | 364000 |    150950 |
|    2 | 아카네 리제  | UNIVERSE | 362000 |    296721 |
|    3 | 시라유키 히나 | UNIVERSE | 323000 |    184265 |
|    4 | 아오쿠모 린  | CLICHE   | 290000 |    202366 |
|    5 | 아라하시 타비 | UNIVERSE | 267000 |    232668 |
|    6 | 텐코 시부키  | CLICHE   | 234000 |    234985 |
|    7 | 유즈하 리코  | CLICHE   | 227000 |    262115 |
|    8 | 하나코 나나  | CLICHE   | 213000 |    235349 |
|    9 | 네네코 마시로 | UNIVERSE | 188000 |    138759 |
|   10 | 사키하네 후야 | EVERYS   | 139000 |    130618 |


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
| 유즈하 리코  | 227000 |  262115 |      115.5 |
| 하나코 나나  | 213000 |  235349 |      110.5 |
| 텐코 시부키  | 234000 |  234985 |      100.4 |
| 사키하네 후야 | 139000 |  130618 |       94   |
| 아라하시 타비 | 267000 |  232668 |       87.1 |
| 아카네 리제  | 362000 |  296721 |       82   |
| 네네코 마시로 | 188000 |  138759 |       73.8 |
| 아오쿠모 린  | 290000 |  202366 |       69.8 |
| 시라유키 히나 | 323000 |  184265 |       57   |
| 아야츠노 유니 | 364000 |  150950 |       41.5 |


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
| UNIVERSE |    4 |  285000 |  213103 |        3    |
| EVERYS   |    2 |  251500 |  140784 |        3.25 |
| CLICHE   |    4 |  241000 |  233703 |        2.96 |


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
| 네네코 마시로 |      3.75 |       3.53 |
| 사키하네 후야 |      3.64 |       3.49 |
| 유즈하 리코  |      3.15 |       3.01 |
| 아오쿠모 린  |      3.13 |       3    |
| 시라유키 히나 |      3.11 |       2.94 |
| 아야츠노 유니 |      2.86 |       2.67 |
| 텐코 시부키  |      2.8  |       2.71 |
| 하나코 나나  |      2.75 |       2.65 |
| 아라하시 타비 |      2.67 |       2.54 |
| 아카네 리제  |      2.47 |       2.39 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.62 |         42 |
| 텐코 시부키  |    6.02 |         36 |
| 아카네 리제  |    5.2  |         38 |
| 유즈하 리코  |    5.04 |         40 |
| 아오쿠모 린  |    4.57 |         24 |
| 아라하시 타비 |    3.9  |         14 |
| 시라유키 히나 |    3.54 |         38 |
| 사키하네 후야 |    3.43 |         24 |
| 아야츠노 유니 |    2.77 |         14 |
| 네네코 마시로 |    2.14 |          6 |


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
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                                    | 2262154 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                                         | 1477186 |
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1155127 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1006120 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        | 1000191 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  806162 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  746950 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  698908 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  580529 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  458199 |

