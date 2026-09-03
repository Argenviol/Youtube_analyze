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
|    1 | 아야츠노 유니 | EVERYS   | 360000 |    127795 |
|    2 | 아카네 리제  | UNIVERSE | 353000 |    309128 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    200216 |
|    4 | 아오쿠모 린  | CLICHE   | 281000 |    181081 |
|    5 | 아라하시 타비 | UNIVERSE | 259000 |    176240 |
|    6 | 텐코 시부키  | CLICHE   | 228000 |    203310 |
|    7 | 유즈하 리코  | CLICHE   | 219000 |    322304 |
|    8 | 하나코 나나  | CLICHE   | 205000 |    196116 |
|    9 | 네네코 마시로 | UNIVERSE | 183000 |    101526 |
|   10 | 사키하네 후야 | EVERYS   | 133000 |    112320 |


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
| 유즈하 리코  | 219000 |  322304 |      147.2 |
| 하나코 나나  | 205000 |  196116 |       95.7 |
| 텐코 시부키  | 228000 |  203310 |       89.2 |
| 아카네 리제  | 353000 |  309128 |       87.6 |
| 사키하네 후야 | 133000 |  112320 |       84.5 |
| 아라하시 타비 | 259000 |  176240 |       68   |
| 아오쿠모 린  | 281000 |  181081 |       64.4 |
| 시라유키 히나 | 320000 |  200216 |       62.6 |
| 네네코 마시로 | 183000 |  101526 |       55.5 |
| 아야츠노 유니 | 360000 |  127795 |       35.5 |


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
| UNIVERSE |    4 |  278750 |  196777 |        3.87 |
| EVERYS   |    2 |  246500 |  120057 |        3.96 |
| CLICHE   |    4 |  233250 |  225703 |        4.03 |


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
| 네네코 마시로 |      4.76 |       4.48 |
| 하나코 나나  |      4.35 |       4.17 |
| 텐코 시부키  |      4.28 |       4.13 |
| 사키하네 후야 |      4.24 |       4.05 |
| 아오쿠모 린  |      3.8  |       3.62 |
| 아라하시 타비 |      3.73 |       3.52 |
| 유즈하 리코  |      3.68 |       3.51 |
| 아야츠노 유니 |      3.68 |       3.42 |
| 시라유키 히나 |      3.52 |       3.31 |
| 아카네 리제  |      3.47 |       3.33 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.35 |         50 |
| 유즈하 리코  |    5.72 |         40 |
| 아카네 리제  |    5.53 |         40 |
| 하나코 나나  |    5.44 |         52 |
| 아오쿠모 린  |    4.4  |         24 |
| 아라하시 타비 |    4.23 |         20 |
| 사키하네 후야 |    3.77 |         30 |
| 시라유키 히나 |    3.43 |         34 |
| 아야츠노 유니 |    2.74 |         20 |
| 네네코 마시로 |    2.01 |          8 |


## 멤버별 최고 조회수 영상

```sql
SELECT m.name_ko AS 멤버, v.title AS 영상, v.views AS 조회수
FROM videos v
JOIN (SELECT channel_id, MAX(views) AS mx FROM videos GROUP BY channel_id) t
  ON v.channel_id=t.channel_id AND v.views=t.mx
JOIN channel_metrics m ON m.channel_id=v.channel_id
ORDER BY v.views DESC;
```

| 멤버      | 영상                                                 |     조회수 |
|:--------|:---------------------------------------------------|--------:|
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰 | 2557478 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                 | 1751117 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts         | 1717424 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                      | 1325626 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts     | 1178117 |
| 텐코 시부키  | 나 후배 선배! #shorts #vtuber                           | 1058789 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                  |  964857 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts     |  675606 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람          |  663567 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                             |  395535 |

