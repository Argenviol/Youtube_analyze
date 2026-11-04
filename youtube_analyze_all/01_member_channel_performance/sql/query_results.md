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
|    1 | 아야츠노 유니 | EVERYS   | 375000 |    170844 |
|    2 | 아카네 리제  | UNIVERSE | 375000 |    351623 |
|    3 | 시라유키 히나 | UNIVERSE | 333000 |    177961 |
|    4 | 아오쿠모 린  | CLICHE   | 303000 |    230395 |
|    5 | 아라하시 타비 | UNIVERSE | 278000 |    271105 |
|    6 | 텐코 시부키  | CLICHE   | 246000 |    293083 |
|    7 | 유즈하 리코  | CLICHE   | 240000 |    295208 |
|    8 | 하나코 나나  | CLICHE   | 225000 |    280788 |
|    9 | 네네코 마시로 | UNIVERSE | 199000 |    137772 |
|   10 | 사키하네 후야 | EVERYS   | 153000 |    131182 |


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
| 하나코 나나  | 225000 |  280788 |      124.8 |
| 유즈하 리코  | 240000 |  295208 |      123   |
| 텐코 시부키  | 246000 |  293083 |      119.1 |
| 아라하시 타비 | 278000 |  271105 |       97.5 |
| 아카네 리제  | 375000 |  351623 |       93.8 |
| 사키하네 후야 | 153000 |  131182 |       85.7 |
| 아오쿠모 린  | 303000 |  230395 |       76   |
| 네네코 마시로 | 199000 |  137772 |       69.2 |
| 시라유키 히나 | 333000 |  177961 |       53.4 |
| 아야츠노 유니 | 375000 |  170844 |       45.6 |


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
| UNIVERSE |    4 |  296250 |  234615 |        2.77 |
| EVERYS   |    2 |  264000 |  151012 |        3.17 |
| CLICHE   |    4 |  253500 |  274868 |        2.55 |


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
| 사키하네 후야 |      3.75 |       3.6  |
| 네네코 마시로 |      3.46 |       3.27 |
| 시라유키 히나 |      3.1  |       2.94 |
| 유즈하 리코  |      2.9  |       2.8  |
| 아야츠노 유니 |      2.59 |       2.43 |
| 하나코 나나  |      2.53 |       2.45 |
| 아오쿠모 린  |      2.48 |       2.36 |
| 텐코 시부키  |      2.28 |       2.21 |
| 아카네 리제  |      2.27 |       2.21 |
| 아라하시 타비 |      2.27 |       2.16 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.15 |         40 |
| 텐코 시부키  |    6.24 |         34 |
| 유즈하 리코  |    5.44 |         44 |
| 아카네 리제  |    5.2  |         40 |
| 아라하시 타비 |    4.64 |         14 |
| 아오쿠모 린  |    4.13 |         16 |
| 사키하네 후야 |    3.73 |         24 |
| 시라유키 히나 |    3.61 |         36 |
| 아야츠노 유니 |    2.83 |         14 |
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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1274542 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1175178 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1120529 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     | 1101234 |
| 텐코 시부키  | (소리주의) 붘몽가입니다 #vtuber #shorts #치이카와 #ちいかわ                             |  896932 |
| 하나코 나나  | 오늘이 무슨 날이죠? #animation #shorts                                        |  813494 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  798889 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  709412 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  651725 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  578431 |

