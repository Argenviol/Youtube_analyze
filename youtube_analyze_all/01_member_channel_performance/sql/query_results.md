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
|    1 | 아카네 리제  | UNIVERSE | 377000 |    358863 |
|    2 | 아야츠노 유니 | EVERYS   | 376000 |    173581 |
|    3 | 시라유키 히나 | UNIVERSE | 333000 |    179567 |
|    4 | 아오쿠모 린  | CLICHE   | 304000 |    239186 |
|    5 | 아라하시 타비 | UNIVERSE | 279000 |    281865 |
|    6 | 텐코 시부키  | CLICHE   | 246000 |    298726 |
|    7 | 유즈하 리코  | CLICHE   | 241000 |    302696 |
|    8 | 하나코 나나  | CLICHE   | 226000 |    291295 |
|    9 | 네네코 마시로 | UNIVERSE | 199000 |    139075 |
|   10 | 사키하네 후야 | EVERYS   | 154000 |    134989 |


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
| 하나코 나나  | 226000 |  291295 |      128.9 |
| 유즈하 리코  | 241000 |  302696 |      125.6 |
| 텐코 시부키  | 246000 |  298726 |      121.4 |
| 아라하시 타비 | 279000 |  281865 |      101   |
| 아카네 리제  | 377000 |  358863 |       95.2 |
| 사키하네 후야 | 154000 |  134989 |       87.7 |
| 아오쿠모 린  | 304000 |  239186 |       78.7 |
| 네네코 마시로 | 199000 |  139075 |       69.9 |
| 시라유키 히나 | 333000 |  179567 |       53.9 |
| 아야츠노 유니 | 376000 |  173581 |       46.2 |


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
| UNIVERSE |    4 |  297000 |  239842 |        2.77 |
| EVERYS   |    2 |  265000 |  154285 |        2.94 |
| CLICHE   |    4 |  254250 |  282975 |        2.5  |


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
| 네네코 마시로 |      3.4  |       3.22 |
| 사키하네 후야 |      3.36 |       3.24 |
| 시라유키 히나 |      3.04 |       2.88 |
| 유즈하 리코  |      2.86 |       2.76 |
| 아야츠노 유니 |      2.52 |       2.37 |
| 하나코 나나  |      2.46 |       2.38 |
| 아오쿠모 린  |      2.44 |       2.33 |
| 아카네 리제  |      2.42 |       2.34 |
| 텐코 시부키  |      2.25 |       2.18 |
| 아라하시 타비 |      2.23 |       2.13 |


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
| 사키하네 후야 |    3.69 |         24 |
| 시라유키 히나 |    3.61 |         34 |
| 아야츠노 유니 |    2.88 |         14 |
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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1281762 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1192460 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     | 1145293 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1133550 |
| 하나코 나나  | 오늘이 무슨 날이죠? #animation #shorts                                        |  979813 |
| 텐코 시부키  | (소리주의) 붘몽가입니다 #vtuber #shorts #치이카와 #ちいかわ                             |  947520 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  825193 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  710883 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  660690 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  591579 |

