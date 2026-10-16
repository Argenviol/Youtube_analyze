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
|    1 | 아야츠노 유니 | EVERYS   | 369000 |    156758 |
|    2 | 아카네 리제  | UNIVERSE | 366000 |    308637 |
|    3 | 시라유키 히나 | UNIVERSE | 327000 |    177529 |
|    4 | 아오쿠모 린  | CLICHE   | 294000 |    176918 |
|    5 | 아라하시 타비 | UNIVERSE | 270000 |    216775 |
|    6 | 텐코 시부키  | CLICHE   | 238000 |    249287 |
|    7 | 유즈하 리코  | CLICHE   | 231000 |    268331 |
|    8 | 하나코 나나  | CLICHE   | 217000 |    244139 |
|    9 | 네네코 마시로 | UNIVERSE | 192000 |    141887 |
|   10 | 사키하네 후야 | EVERYS   | 144000 |    122938 |
|   11 | 토키노 메리  | ABYSS    |  60800 |    206704 |
|   12 | 시즈키 토아  | ABYSS    |  58900 |    303646 |
|   13 | 코가네 랑   | ABYSS    |  58400 |    259492 |
|   14 | 하나요 히요리 | ABYSS    |  56500 |    296835 |


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
| 하나요 히요리 |  56500 |  296835 |      525.4 |
| 시즈키 토아  |  58900 |  303646 |      515.5 |
| 코가네 랑   |  58400 |  259492 |      444.3 |
| 토키노 메리  |  60800 |  206704 |      340   |
| 유즈하 리코  | 231000 |  268331 |      116.2 |
| 하나코 나나  | 217000 |  244139 |      112.5 |
| 텐코 시부키  | 238000 |  249287 |      104.7 |
| 사키하네 후야 | 144000 |  122938 |       85.4 |
| 아카네 리제  | 366000 |  308637 |       84.3 |
| 아라하시 타비 | 270000 |  216775 |       80.3 |
| 네네코 마시로 | 192000 |  141887 |       73.9 |
| 아오쿠모 린  | 294000 |  176918 |       60.2 |
| 시라유키 히나 | 327000 |  177529 |       54.3 |
| 아야츠노 유니 | 369000 |  156758 |       42.5 |


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
| UNIVERSE |    4 |  288750 |  211206 |        3.04 |
| EVERYS   |    2 |  256500 |  139848 |        3.31 |
| CLICHE   |    4 |  245000 |  234668 |        2.95 |
| ABYSS    |    4 |   58650 |  266669 |        8.51 |


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
| 토키노 메리  |     10.99 |       9.72 |
| 코가네 랑   |      8.68 |       7.57 |
| 시즈키 토아  |      7.97 |       7.11 |
| 하나요 히요리 |      6.4  |       5.72 |
| 사키하네 후야 |      3.74 |       3.59 |
| 네네코 마시로 |      3.69 |       3.49 |
| 시라유키 히나 |      3.31 |       3.14 |
| 유즈하 리코  |      3.19 |       3.05 |
| 아오쿠모 린  |      3.11 |       2.99 |
| 아야츠노 유니 |      2.89 |       2.7  |
| 하나코 나나  |      2.77 |       2.67 |
| 텐코 시부키  |      2.72 |       2.63 |
| 아라하시 타비 |      2.69 |       2.56 |
| 아카네 리제  |      2.47 |       2.39 |


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
| 텐코 시부키  |    6.12 |         36 |
| 아카네 리제  |    5.2  |         38 |
| 유즈하 리코  |    5.12 |         42 |
| 아오쿠모 린  |    4.51 |         24 |
| 아라하시 타비 |    3.99 |         12 |
| 시라유키 히나 |    3.65 |         40 |
| 사키하네 후야 |    3.46 |         26 |
| 아야츠노 유니 |    2.83 |         14 |
| 네네코 마시로 |    2.23 |          8 |
| 토키노 메리  |    0    |          0 |
| 시즈키 토아  |    0    |          0 |
| 코가네 랑   |    0    |          0 |
| 하나요 히요리 |    0    |          0 |


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
| 유즈하 리코  | 오늘 나는 찌그러진 클리셰가 될 거야 #vtuber #shorts #리코 #스텔라이브 #챌린지 #meme | 1187438 |
| 아라하시 타비 | High Hopes - Panic! At The Discoㅣ아라하시 타비 Cover                        | 1067236 |
| 네네코 마시로 | 콧치노 켄토 - 네, 기꺼이 [はいよろこんで / こっちのけんと]ㅣ네네코 마시로 x 텐코 시부키 Cover            | 1034091 |
| 시라유키 히나 | 공주 언니 좋으면 멍멍해! #cartoon #comic #vtuber #shorts                        | 1002764 |
| 텐코 시부키  | 최산 BAD 챌린지를 춰보았습니다. #meme #vtuber #shorts #BAD                        |  831718 |
| 아오쿠모 린  | 불가행력 [不可幸力 / Vaundy ] / 아오쿠모 린 (Aokumo Rin) Cover                     |  827039 |
| 아카네 리제  | 제철 리제가 왔어요~ #vtuber #shorts                                           |  752497 |
| 아야츠노 유니 | 아 르 냥 일 어 나 🕗 !! #stellive #스텔라이브 #유니 #알람                             |  701087 |
| 하나코 나나  | 오츠카레summer [おつかれsummer/HALCALI] / 하나코 나나, 사키하네 후야 COVER               |  625291 |
| 사키하네 후야 | 푸른 산호초(青い珊瑚礁) - 松田 聖子 l 사키하네 후야(Sakihane Huya) Cover                  |  477352 |
| 시즈키 토아  | 제육감 [第六感 l Reol] / 시즈키 토아(Shizuki Toa) Cover                          |  303646 |
| 하나요 히요리 | 유령이 되고싶어 [ゆうれいになりたい / 유이카] / 하나요 히요리 (Hanayo Hiyori) Cover            |  296835 |
| 코가네 랑   | 호랑풍류가 [나와 호랑이님 OST] / 코가네 랑 (Cogane Rang) Cover                       |  259492 |
| 토키노 메리  | 도쿄 테디베어 [東京テディベア l Neru] / 토키노 메리 (Tokino Mary) Cover                 |  206704 |

