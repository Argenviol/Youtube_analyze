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
|    1 | 아야츠노 유니 | EVERYS   | 376000 |    173453 |
|    2 | 아카네 리제  | UNIVERSE | 376000 |    359632 |
|    3 | 시라유키 히나 | UNIVERSE | 333000 |    176952 |
|    4 | 아오쿠모 린  | CLICHE   | 304000 |    236660 |
|    5 | 아라하시 타비 | UNIVERSE | 279000 |    278780 |
|    6 | 텐코 시부키  | CLICHE   | 246000 |    298924 |
|    7 | 유즈하 리코  | CLICHE   | 241000 |    300234 |
|    8 | 하나코 나나  | CLICHE   | 226000 |    287869 |
|    9 | 네네코 마시로 | UNIVERSE | 199000 |    138079 |
|   10 | 사키하네 후야 | EVERYS   | 153000 |    134481 |


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
| 하나코 나나  | 226000 |  287869 |      127.4 |
| 유즈하 리코  | 241000 |  300234 |      124.6 |
| 텐코 시부키  | 246000 |  298924 |      121.5 |
| 아라하시 타비 | 279000 |  278780 |       99.9 |
| 아카네 리제  | 376000 |  359632 |       95.6 |
| 사키하네 후야 | 153000 |  134481 |       87.9 |
| 아오쿠모 린  | 304000 |  236660 |       77.8 |
| 네네코 마시로 | 199000 |  138079 |       69.4 |
| 시라유키 히나 | 333000 |  176952 |       53.1 |
| 아야츠노 유니 | 376000 |  173453 |       46.1 |


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
| UNIVERSE |    4 |  296750 |  238360 |        2.74 |
| EVERYS   |    2 |  264500 |  153967 |        2.97 |
| CLICHE   |    4 |  254250 |  280921 |        2.51 |


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
| 네네코 마시로 |      3.42 |       3.23 |
| 사키하네 후야 |      3.4  |       3.27 |
| 시라유키 히나 |      3.06 |       2.91 |
| 유즈하 리코  |      2.88 |       2.77 |
| 아야츠노 유니 |      2.54 |       2.38 |
| 하나코 나나  |      2.48 |       2.4  |
| 아오쿠모 린  |      2.45 |       2.33 |
| 텐코 시부키  |      2.25 |       2.19 |
| 아카네 리제  |      2.25 |       2.18 |
| 아라하시 타비 |      2.25 |       2.15 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7    |         40 |
| 텐코 시부키  |    6.24 |         34 |
| 유즈하 리코  |    5.36 |         44 |
| 아카네 리제  |    5.12 |         40 |
| 아라하시 타비 |    4.76 |         16 |
| 아오쿠모 린  |    4.13 |         16 |
| 사키하네 후야 |    3.73 |         24 |
| 시라유키 히나 |    3.61 |         34 |
| 아야츠노 유니 |    2.91 |         14 |
| 네네코 마시로 |    2.35 |          8 |


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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1279717 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1186994 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     | 1131201 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1129369 |
| 하나코 나나  | 오늘이 무슨 날이죠? #animation #shorts                                        |  937190 |
| 텐코 시부키  | (소리주의) 붘몽가입니다 #vtuber #shorts #치이카와 #ちいかわ                             |  931611 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  818497 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  710358 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  657769 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  587366 |

