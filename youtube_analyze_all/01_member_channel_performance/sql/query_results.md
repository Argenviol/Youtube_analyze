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
|    1 | 강지      | STELLIVE | 762000 |  250242   |
|    2 | 아야츠노 유니 | EVERYS   | 359000 |  135280   |
|    3 | 아카네 리제  | UNIVERSE | 349000 |  284094   |
|    4 | 시라유키 히나 | UNIVERSE | 320000 |  210733   |
|    5 | 아오쿠모 린  | CLICHE   | 278000 |  190486   |
|    6 | 아라하시 타비 | UNIVERSE | 256000 |  181968   |
|    7 | 텐코 시부키  | CLICHE   | 225000 |  232043   |
|    8 | 유즈하 리코  | CLICHE   | 215000 |  272808   |
|    9 | 하나코 나나  | CLICHE   | 202000 |  171420   |
|   10 | 네네코 마시로 | UNIVERSE | 181000 |   83858.9 |
|   11 | 사키하네 후야 | EVERYS   | 130000 |  117652   |


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
| 유즈하 리코  | 215000 | 272808   |      126.9 |
| 텐코 시부키  | 225000 | 232043   |      103.1 |
| 사키하네 후야 | 130000 | 117652   |       90.5 |
| 하나코 나나  | 202000 | 171420   |       84.9 |
| 아카네 리제  | 349000 | 284094   |       81.4 |
| 아라하시 타비 | 256000 | 181968   |       71.1 |
| 아오쿠모 린  | 278000 | 190486   |       68.5 |
| 시라유키 히나 | 320000 | 210733   |       65.9 |
| 네네코 마시로 | 181000 |  83858.9 |       46.3 |
| 아야츠노 유니 | 359000 | 135280   |       37.7 |


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
| UNIVERSE |    4 |  276500 |  190163 |        4.08 |
| EVERYS   |    2 |  244500 |  126466 |        4.12 |
| CLICHE   |    4 |  230000 |  216689 |        4.23 |


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
| 네네코 마시로 |      4.99 |       4.69 |
| 하나코 나나  |      4.74 |       4.53 |
| 사키하네 후야 |      4.37 |       4.18 |
| 텐코 시부키  |      4.17 |       4.03 |
| 유즈하 리코  |      4    |       3.81 |
| 아오쿠모 린  |      4    |       3.82 |
| 아야츠노 유니 |      3.87 |       3.6  |
| 아카네 리제  |      3.85 |       3.69 |
| 아라하시 타비 |      3.82 |       3.61 |
| 시라유키 히나 |      3.65 |       3.43 |


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
| 아카네 리제  |    5.53 |         42 |
| 하나코 나나  |    4.9  |         48 |
| 아오쿠모 린  |    4.76 |         24 |
| 아라하시 타비 |    4.18 |         20 |
| 사키하네 후야 |    3.99 |         36 |
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
| 유즈하 리코  | 클리셰 최강의 로봇... #vtuber #shorts #스텔라이브 #리코 #용사툰 #클리셰          | 2360585 |
| 아카네 리제  | 온라인도 오프라인도 모두 야르한 콘서트 되세요~ #vtuber #shorts                  | 1570986 |
| 아오쿠모 린  | 아오쿠모 린(Aokumo Rin) | 'Maid My Way'                          | 1380539 |
| 시라유키 히나 | 스텔라이브 삼색 볼펜들의 오도루프!🎵 #오도루프 #oddoloop #オドループ #vtuber #shorts | 1325699 |
| 아라하시 타비 | 타비도 꿍싯꿍싯💕 #shorts #vtuber #타비                               | 1147993 |
| 텐코 시부키  | 143cm #shorts #vtuber                                       | 1047979 |
| 강지      | 신호등 자매의 윙크 (｡•̀ ᴗ -)✧ #강지 #쇼츠 #밈                            |  924586 |
| 하나코 나나  | 하나코 나나(Hanako Nana) | 'Hush Trap'                           |  885346 |
| 네네코 마시로 | ⬆️고양이의 점프력⬆️ #네네코마시로 #스텔라이브 #3D #점프챌린지 #shorts              |  652442 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                   |  608690 |
| 사키하네 후야 | 수수께끼를 풀...엇? #shorts #vtuber                                |  430812 |

