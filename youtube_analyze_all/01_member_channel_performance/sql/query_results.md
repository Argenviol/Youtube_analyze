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
|    1 | 아야츠노 유니 | EVERYS   | 374000 |    169283 |
|    2 | 아카네 리제  | UNIVERSE | 372000 |    324766 |
|    3 | 시라유키 히나 | UNIVERSE | 332000 |    174741 |
|    4 | 아오쿠모 린  | CLICHE   | 301000 |    207075 |
|    5 | 아라하시 타비 | UNIVERSE | 276000 |    244102 |
|    6 | 텐코 시부키  | CLICHE   | 244000 |    263748 |
|    7 | 유즈하 리코  | CLICHE   | 237000 |    273932 |
|    8 | 하나코 나나  | CLICHE   | 223000 |    243365 |
|    9 | 네네코 마시로 | UNIVERSE | 197000 |    145673 |
|   10 | 사키하네 후야 | EVERYS   | 151000 |    132734 |


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
| 유즈하 리코  | 237000 |  273932 |      115.6 |
| 하나코 나나  | 223000 |  243365 |      109.1 |
| 텐코 시부키  | 244000 |  263748 |      108.1 |
| 아라하시 타비 | 276000 |  244102 |       88.4 |
| 사키하네 후야 | 151000 |  132734 |       87.9 |
| 아카네 리제  | 372000 |  324766 |       87.3 |
| 네네코 마시로 | 197000 |  145673 |       73.9 |
| 아오쿠모 린  | 301000 |  207075 |       68.8 |
| 시라유키 히나 | 332000 |  174741 |       52.6 |
| 아야츠노 유니 | 374000 |  169283 |       45.3 |


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
| UNIVERSE |    4 |  294250 |  222320 |        2.89 |
| EVERYS   |    2 |  262500 |  151008 |        3.1  |
| CLICHE   |    4 |  251250 |  247030 |        2.76 |


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
| 네네코 마시로 |      3.61 |       3.41 |
| 사키하네 후야 |      3.52 |       3.38 |
| 시라유키 히나 |      3.26 |       3.1  |
| 유즈하 리코  |      3.1  |       2.98 |
| 아오쿠모 린  |      2.7  |       2.58 |
| 하나코 나나  |      2.7  |       2.61 |
| 아야츠노 유니 |      2.69 |       2.52 |
| 텐코 시부키  |      2.54 |       2.46 |
| 아라하시 타비 |      2.43 |       2.32 |
| 아카네 리제  |      2.27 |       2.21 |


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
| 텐코 시부키  |    6.73 |         36 |
| 유즈하 리코  |    5.44 |         42 |
| 아카네 리제  |    5.2  |         38 |
| 아오쿠모 린  |    4.29 |         18 |
| 아라하시 타비 |    4.29 |         14 |
| 시라유키 히나 |    3.77 |         38 |
| 사키하네 후야 |    3.69 |         24 |
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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1243607 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1122062 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1078484 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  974222 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  769178 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  705916 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  693776 |
| 텐코 시부키  | (소리주의) 붘몽가입니다 #vtuber #shorts #치이카와 #ちいかわ                             |  656276 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  619048 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  531070 |

