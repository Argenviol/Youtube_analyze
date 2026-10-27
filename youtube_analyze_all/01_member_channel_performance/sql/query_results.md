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
|    1 | 아야츠노 유니 | EVERYS   | 374000 |    168780 |
|    2 | 아카네 리제  | UNIVERSE | 373000 |    336121 |
|    3 | 시라유키 히나 | UNIVERSE | 332000 |    169878 |
|    4 | 아오쿠모 린  | CLICHE   | 301000 |    212750 |
|    5 | 아라하시 타비 | UNIVERSE | 276000 |    253506 |
|    6 | 텐코 시부키  | CLICHE   | 244000 |    271578 |
|    7 | 유즈하 리코  | CLICHE   | 238000 |    280747 |
|    8 | 하나코 나나  | CLICHE   | 224000 |    253176 |
|    9 | 네네코 마시로 | UNIVERSE | 198000 |    147053 |
|   10 | 사키하네 후야 | EVERYS   | 152000 |    126296 |


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
| 유즈하 리코  | 238000 |  280747 |      118   |
| 하나코 나나  | 224000 |  253176 |      113   |
| 텐코 시부키  | 244000 |  271578 |      111.3 |
| 아라하시 타비 | 276000 |  253506 |       91.8 |
| 아카네 리제  | 373000 |  336121 |       90.1 |
| 사키하네 후야 | 152000 |  126296 |       83.1 |
| 네네코 마시로 | 198000 |  147053 |       74.3 |
| 아오쿠모 린  | 301000 |  212750 |       70.7 |
| 시라유키 히나 | 332000 |  169878 |       51.2 |
| 아야츠노 유니 | 374000 |  168780 |       45.1 |


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
| UNIVERSE |    4 |  294750 |  226639 |        2.86 |
| EVERYS   |    2 |  263000 |  147538 |        3.34 |
| CLICHE   |    4 |  251750 |  254562 |        2.7  |


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
| 사키하네 후야 |      4.02 |       3.86 |
| 네네코 마시로 |      3.57 |       3.38 |
| 시라유키 히나 |      3.21 |       3.04 |
| 유즈하 리코  |      3.03 |       2.92 |
| 하나코 나나  |      2.68 |       2.59 |
| 아야츠노 유니 |      2.66 |       2.49 |
| 아오쿠모 린  |      2.66 |       2.54 |
| 텐코 시부키  |      2.45 |       2.38 |
| 아라하시 타비 |      2.39 |       2.28 |
| 아카네 리제  |      2.29 |       2.23 |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.46 |         38 |
| 텐코 시부키  |    6.6  |         36 |
| 유즈하 리코  |    5.28 |         42 |
| 아카네 리제  |    5.12 |         40 |
| 아라하시 타비 |    4.57 |         14 |
| 아오쿠모 린  |    4.18 |         18 |
| 사키하네 후야 |    3.77 |         22 |
| 시라유키 히나 |    3.69 |         36 |
| 아야츠노 유니 |    2.79 |         14 |
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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1248540 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1134313 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1088802 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     | 1005267 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  772843 |
| 텐코 시부키  | (소리주의) 붘몽가입니다 #vtuber #shorts #치이카와 #ちいかわ                             |  714527 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  709889 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  706639 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  627153 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  544366 |

