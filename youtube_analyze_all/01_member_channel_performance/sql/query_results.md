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
|    1 | 아야츠노 유니 | EVERYS   | 374000 |    167782 |
|    2 | 아카네 리제  | UNIVERSE | 373000 |    329275 |
|    3 | 시라유키 히나 | UNIVERSE | 332000 |    176792 |
|    4 | 아오쿠모 린  | CLICHE   | 301000 |    209853 |
|    5 | 아라하시 타비 | UNIVERSE | 276000 |    246274 |
|    6 | 텐코 시부키  | CLICHE   | 244000 |    265401 |
|    7 | 유즈하 리코  | CLICHE   | 238000 |    277427 |
|    8 | 하나코 나나  | CLICHE   | 223000 |    247894 |
|    9 | 네네코 마시로 | UNIVERSE | 198000 |    146470 |
|   10 | 사키하네 후야 | EVERYS   | 152000 |    127626 |


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
| 유즈하 리코  | 238000 |  277427 |      116.6 |
| 하나코 나나  | 223000 |  247894 |      111.2 |
| 텐코 시부키  | 244000 |  265401 |      108.8 |
| 아라하시 타비 | 276000 |  246274 |       89.2 |
| 아카네 리제  | 373000 |  329275 |       88.3 |
| 사키하네 후야 | 152000 |  127626 |       84   |
| 네네코 마시로 | 198000 |  146470 |       74   |
| 아오쿠모 린  | 301000 |  209853 |       69.7 |
| 시라유키 히나 | 332000 |  176792 |       53.3 |
| 아야츠노 유니 | 374000 |  167782 |       44.9 |


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
| UNIVERSE |    4 |  294750 |  224702 |        2.89 |
| EVERYS   |    2 |  263000 |  147703 |        3.06 |
| CLICHE   |    4 |  251500 |  250143 |        2.74 |


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
| 네네코 마시로 |      3.59 |       3.39 |
| 사키하네 후야 |      3.46 |       3.32 |
| 시라유키 히나 |      3.24 |       3.08 |
| 유즈하 리코  |      3.08 |       2.96 |
| 아오쿠모 린  |      2.69 |       2.57 |
| 아야츠노 유니 |      2.66 |       2.5  |
| 하나코 나나  |      2.63 |       2.54 |
| 텐코 시부키  |      2.58 |       2.5  |
| 아라하시 타비 |      2.47 |       2.35 |
| 아카네 리제  |      2.26 |       2.2  |


## 업로드 빈도 상위

```sql
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;
```

| 멤버      |   주간업로드 |   쇼츠비중_pct |
|:--------|--------:|-----------:|
| 하나코 나나  |    7.46 |         36 |
| 텐코 시부키  |    6.6  |         38 |
| 유즈하 리코  |    5.44 |         42 |
| 아카네 리제  |    5.2  |         38 |
| 아라하시 타비 |    4.51 |         14 |
| 아오쿠모 린  |    4.29 |         18 |
| 시라유키 히나 |    3.77 |         38 |
| 사키하네 후야 |    3.65 |         22 |
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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1245786 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1128284 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1083744 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  990042 |
| 아카네 리제  | 픽셀 병약 담당 vs 스텔 병약 담당                                                  |  771020 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  706283 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  701747 |
| 텐코 시부키  | (소리주의) 붘몽가입니다 #vtuber #shorts #치이카와 #ちいかわ                             |  682062 |
| 시라유키 히나 | 아틀란티스 소녀 (Atlantis Princess) | 시라유키 히나 Cover                          |  623360 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  538133 |

