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
|    1 | 아카네 리제  | UNIVERSE | 376000 |    353932 |
|    2 | 아야츠노 유니 | EVERYS   | 375000 |    171922 |
|    3 | 시라유키 히나 | UNIVERSE | 333000 |    175424 |
|    4 | 아오쿠모 린  | CLICHE   | 303000 |    233836 |
|    5 | 아라하시 타비 | UNIVERSE | 278000 |    273478 |
|    6 | 텐코 시부키  | CLICHE   | 246000 |    296054 |
|    7 | 유즈하 리코  | CLICHE   | 240000 |    296205 |
|    8 | 하나코 나나  | CLICHE   | 226000 |    282892 |
|    9 | 네네코 마시로 | UNIVERSE | 199000 |    136666 |
|   10 | 사키하네 후야 | EVERYS   | 153000 |    133364 |


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
| 하나코 나나  | 226000 |  282892 |      125.2 |
| 유즈하 리코  | 240000 |  296205 |      123.4 |
| 텐코 시부키  | 246000 |  296054 |      120.3 |
| 아라하시 타비 | 278000 |  273478 |       98.4 |
| 아카네 리제  | 376000 |  353932 |       94.1 |
| 사키하네 후야 | 153000 |  133364 |       87.2 |
| 아오쿠모 린  | 303000 |  233836 |       77.2 |
| 네네코 마시로 | 199000 |  136666 |       68.7 |
| 시라유키 히나 | 333000 |  175424 |       52.7 |
| 아야츠노 유니 | 375000 |  171922 |       45.8 |


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
| UNIVERSE |    4 |  296500 |  234875 |        2.75 |
| EVERYS   |    2 |  264000 |  152642 |        2.99 |
| CLICHE   |    4 |  253750 |  277246 |        2.53 |


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
| 네네코 마시로 |      3.43 |       3.25 |
| 사키하네 후야 |      3.42 |       3.29 |
| 시라유키 히나 |      3.06 |       2.9  |
| 유즈하 리코  |      2.9  |       2.79 |
| 아야츠노 유니 |      2.55 |       2.39 |
| 하나코 나나  |      2.5  |       2.42 |
| 아오쿠모 린  |      2.46 |       2.35 |
| 아카네 리제  |      2.26 |       2.2  |
| 텐코 시부키  |      2.26 |       2.2  |
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
| 아라하시 타비 |    4.64 |         14 |
| 아오쿠모 린  |    4.13 |         16 |
| 사키하네 후야 |    3.73 |         24 |
| 시라유키 히나 |    3.57 |         34 |
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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1277218 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1181357 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1124965 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     | 1116550 |
| 텐코 시부키  | (소리주의) 붘몽가입니다 #vtuber #shorts #치이카와 #ちいかわ                             |  912729 |
| 하나코 나나  | 오늘이 무슨 날이죠? #animation #shorts                                        |  871028 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  810474 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  709849 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  654774 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  582934 |

