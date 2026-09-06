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
|    1 | 아야츠노 유니 | EVERYS   | 360000 |    130728 |
|    2 | 아카네 리제  | UNIVERSE | 354000 |    308985 |
|    3 | 시라유키 히나 | UNIVERSE | 320000 |    198175 |
|    4 | 아오쿠모 린  | CLICHE   | 282000 |    188049 |
|    5 | 아라하시 타비 | UNIVERSE | 260000 |    185845 |
|    6 | 텐코 시부키  | CLICHE   | 229000 |    193025 |
|    7 | 유즈하 리코  | CLICHE   | 220000 |    335769 |
|    8 | 하나코 나나  | CLICHE   | 205000 |    196984 |
|    9 | 네네코 마시로 | UNIVERSE | 183000 |    105586 |
|   10 | 사키하네 후야 | EVERYS   | 133000 |    116723 |


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
| 유즈하 리코  | 220000 |  335769 |      152.6 |
| 하나코 나나  | 205000 |  196984 |       96.1 |
| 사키하네 후야 | 133000 |  116723 |       87.8 |
| 아카네 리제  | 354000 |  308985 |       87.3 |
| 텐코 시부키  | 229000 |  193025 |       84.3 |
| 아라하시 타비 | 260000 |  185845 |       71.5 |
| 아오쿠모 린  | 282000 |  188049 |       66.7 |
| 시라유키 히나 | 320000 |  198175 |       61.9 |
| 네네코 마시로 | 183000 |  105586 |       57.7 |
| 아야츠노 유니 | 360000 |  130728 |       36.3 |


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
| UNIVERSE |    4 |  279250 |  199647 |        3.78 |
| EVERYS   |    2 |  246500 |  123725 |        3.85 |
| CLICHE   |    4 |  234000 |  228456 |        4.01 |


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
| 네네코 마시로 |      4.65 |       4.38 |
| 하나코 나나  |      4.4  |       4.22 |
| 텐코 시부키  |      4.3  |       4.15 |
| 사키하네 후야 |      4.1  |       3.92 |
| 아오쿠모 린  |      3.7  |       3.53 |
| 유즈하 리코  |      3.64 |       3.47 |
| 아야츠노 유니 |      3.6  |       3.35 |
| 아라하시 타비 |      3.59 |       3.4  |
| 시라유키 히나 |      3.48 |       3.28 |
| 아카네 리제  |      3.41 |       3.27 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.47 |         50 |
| 유즈하 리코  |    5.91 |         42 |
| 하나코 나나  |    5.81 |         54 |
| 아카네 리제  |    5.36 |         40 |
| 아오쿠모 린  |    4.29 |         24 |
| 아라하시 타비 |    4.23 |         22 |
| 사키하네 후야 |    3.73 |         28 |
| 시라유키 히나 |    3.43 |         34 |
| 아야츠노 유니 |    2.83 |         20 |
| 네네코 마시로 |    1.97 |          8 |


## 멤버별 최고 조회수 영상

```sql
SELECT m.name_ko AS 멤버, v.title AS 영상, v.views AS 조회수
FROM videos v
JOIN (SELECT channel_id, MAX(views) AS mx FROM videos GROUP BY channel_id) t
  ON v.channel_id=t.channel_id AND v.views=t.mx
JOIN channel_metrics m ON m.channel_id=v.channel_id
ORDER BY v.views DESC;
```

| 멤버      | 영상                                                         |     조회수 |
|:--------|:-----------------------------------------------------------|--------:|
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰         | 2586689 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                         | 1809156 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                 | 1730180 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                              | 1355513 |
| 시라유키 히나 | 오냐 어디 한 번 죽어보자 #cartoon #comic #vtuber #shorts             | 1182091 |
| 텐코 시부키  | 텐코 시부키(Tenko Shibuki) | 베리베리스트로베리 'Berry Verry Strawberry' | 1052461 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                          |  977458 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts             |  683474 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                  |  674985 |
| 사키하네 후야 | 단단비리비리 #shorts #vtuber                                     |  399623 |

