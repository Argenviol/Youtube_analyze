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
|    1 | 강지      | STELLIVE | 762000 |  247652   |
|    2 | 아야츠노 유니 | EVERYS   | 359000 |  128355   |
|    3 | 아카네 리제  | UNIVERSE | 350000 |  284014   |
|    4 | 시라유키 히나 | UNIVERSE | 320000 |  212520   |
|    5 | 아오쿠모 린  | CLICHE   | 278000 |  188305   |
|    6 | 아라하시 타비 | UNIVERSE | 257000 |  184088   |
|    7 | 텐코 시부키  | CLICHE   | 226000 |  233802   |
|    8 | 유즈하 리코  | CLICHE   | 216000 |  277716   |
|    9 | 하나코 나나  | CLICHE   | 202000 |  174212   |
|   10 | 네네코 마시로 | UNIVERSE | 181000 |   84302.4 |
|   11 | 사키하네 후야 | EVERYS   | 131000 |  114149   |


## 도달 효율(평균조회수/구독자) 상위

```sql
SELECT name_ko AS 멤버, subscribers AS 구독자,
       recent_avg_views AS 평균조회수,
       ROUND(reach_ratio*100,1) AS 도달효율_pct
FROM channel_metrics WHERE role='talent'
ORDER BY reach_ratio DESC;
```

| 멤버      |    구독자 |    평균조회수 |   도달효율_pct |
|:--------|-------:|---------:|-----------:|
| 유즈하 리코  | 216000 | 277716   |      128.6 |
| 텐코 시부키  | 226000 | 233802   |      103.5 |
| 사키하네 후야 | 131000 | 114149   |       87.1 |
| 하나코 나나  | 202000 | 174212   |       86.2 |
| 아카네 리제  | 350000 | 284014   |       81.1 |
| 아라하시 타비 | 257000 | 184088   |       71.6 |
| 아오쿠모 린  | 278000 | 188305   |       67.7 |
| 시라유키 히나 | 320000 | 212520   |       66.4 |
| 네네코 마시로 | 181000 |  84302.4 |       46.6 |
| 아야츠노 유니 | 359000 | 128355   |       35.8 |


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
| UNIVERSE |    4 |  277000 |  191230 |        4.06 |
| EVERYS   |    2 |  245000 |  121251 |        4.15 |
| CLICHE   |    4 |  230500 |  218508 |        4.18 |


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
| 네네코 마시로 |      4.97 |       4.68 |
| 하나코 나나  |      4.69 |       4.49 |
| 사키하네 후야 |      4.42 |       4.24 |
| 텐코 시부키  |      4.12 |       3.98 |
| 아오쿠모 린  |      4    |       3.81 |
| 유즈하 리코  |      3.92 |       3.73 |
| 아야츠노 유니 |      3.87 |       3.6  |
| 아라하시 타비 |      3.86 |       3.64 |
| 아카네 리제  |      3.81 |       3.65 |
| 시라유키 히나 |      3.62 |       3.4  |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 텐코 시부키  |    6.86 |         52 |
| 유즈하 리코  |    6.12 |         38 |
| 아카네 리제  |    5.44 |         40 |
| 하나코 나나  |    4.97 |         48 |
| 아오쿠모 린  |    4.57 |         24 |
| 아라하시 타비 |    4.23 |         22 |
| 사키하네 후야 |    4.04 |         36 |
| 시라유키 히나 |    3.73 |         34 |
| 아야츠노 유니 |    2.77 |         22 |
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

| 멤버      | 영상                                                          |     조회수 |
|:--------|:------------------------------------------------------------|--------:|
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰          | 2386765 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                  | 1599037 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                          | 1427532 |
| 시라유키 히나 | 스텔라이브 삼색 볼펜들의 오도루프!🎵 #오도루프 #oddoloop #オドループ #vtuber #shorts | 1329959 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                               | 1177463 |
| 텐코 시부키  | 143cm #shorts #vtuber                                       | 1052267 |
| 강지      | 신호등 자매의 윙크 (｡•̀ ᴗ -)✧ #강지 #쇼츠 #밈                            |  927296 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                           |  895712 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts              |  654274 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                   |  616580 |
| 사키하네 후야 | 수수께끼를 풀...엇? #shorts #vtuber                                |  432011 |

