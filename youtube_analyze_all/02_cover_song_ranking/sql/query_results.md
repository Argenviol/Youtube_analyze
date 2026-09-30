# 커버곡 분석 쿼리 실행 결과

`sql/covers.db`(SQLite) 실행 결과입니다.

## 커버곡 조회수 TOP 15

```sql
SELECT name_ko AS 멤버, title AS 곡, views AS 조회수, likes AS 좋아요
FROM covers ORDER BY views DESC LIMIT 15;
```

| 멤버      | 곡                                                                  |      조회수 |    좋아요 |
|:--------|:-------------------------------------------------------------------|---------:|-------:|
| 아카네 리제  | 출항 [抜錨(발묘) / 나나호시 관현악단 ナナホシ管弦楽団] ㅣ아카네 리제(Akane Lize) 【COVER】       | 14896603 | 109229 |
| 아카네 리제  | Drowning (WOODZ)ㅣ아카네 리제 (Akane Lize) 【Cover】                       | 12048621 |  72922 |
| 아카네 리제  | 내일의 밤하늘 초계반(アスノヨゾラ哨戒班)ㅣ아카네 리제(Akane Lize) 【COVER】                  | 10625491 |  59093 |
| 시라유키 히나 | 낙향(都落ち) / 시라유키 히나 Cover                                            |  8098219 |  44750 |
| 아카네 리제  | 괴물 (怪物) / 아카네 리제 Cover                                             |  7605165 |  42070 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                          |  7388385 |  44183 |
| 아카네 리제  | 선잠 (Leina) / 아카네 리제 Cover                                          |  6316219 |  35815 |
| 하나코 나나  | 비행정 [飛行艇 - King Gnu] / 하나코 나나 COVER                                |  5627024 |  38093 |
| 아오쿠모 린  | 유령도쿄(Ayase) / 아오쿠모 린(Aokumo Rin) Cover                             |  5226755 |  32752 |
| 아오쿠모 린  | W/X/Y (Tani Yuuki) / 아오쿠모 린(Aokumo Rin) Cover                      |  5124115 |  32710 |
| 시라유키 히나 | I Really Want to Stay At Your House (Arrange ver.) | 시라유키 히나 Cover |  5032895 |  48750 |
| 시라유키 히나 | 피날레(フィナーレ。) / 시라유키 히나 Cover                                        |  4934803 |  31288 |
| 텐코 시부키  | 여우비 / 텐코 시부키(Tenko Shibuki) cover                                  |  4921526 |  32031 |
| 아오쿠모 린  | TAEYEON (태연) 'To. X' / 아오쿠모 린(Aokumo Rin) Cover                    |  4590234 |  32742 |
| 아카네 리제  | Surges (Orangestar)ㅣ아카네 리제(Akane Lize) 【COVER】                     |  4571115 |  33635 |


## 멤버별 커버 성과 랭킹

```sql
SELECT rank AS 순위, name_ko AS 멤버, song_count AS 곡수, cover_count AS 영상수,
       total_views AS 총조회수, total_views_incl_topic AS 음원포함, CAST(avg_views AS INT) AS 영상당평균
FROM cover_metrics ORDER BY total_views DESC;
```

|   순위 | 멤버      |   곡수 |   영상수 |      총조회수 |      음원포함 |   영상당평균 |
|-----:|:--------|-----:|------:|----------:|----------:|--------:|
|    1 | 아카네 리제  |   39 |    41 | 113583638 | 113583638 | 2770332 |
|    2 | 아오쿠모 린  |   53 |    57 |  90440269 |  90440269 | 1586671 |
|    3 | 시라유키 히나 |   45 |    50 |  66098398 |  66098398 | 1321968 |
|    4 | 유즈하 리코  |   56 |    61 |  64206851 |  64206851 | 1052571 |
|    5 | 하나코 나나  |   42 |    49 |  60142820 |  60142820 | 1227404 |
|    6 | 텐코 시부키  |   34 |    37 |  44147672 |  44147672 | 1193180 |
|    7 | 아라하시 타비 |   23 |    24 |  29284392 |  29284392 | 1220183 |
|    8 | 아야츠노 유니 |   15 |    15 |  15342010 |  15342010 | 1022800 |
|    9 | 네네코 마시로 |   21 |    21 |  15047076 |  15047076 |  716527 |
|   10 | 사키하네 후야 |    7 |     7 |   3986377 |   3986377 |  569482 |


## 여러 판으로 올라온 곡

```sql
SELECT name_ko AS 멤버, title AS 대표제목, n_versions AS 판수, views AS 판합계조회수, topic_views AS 음원조회수
FROM cover_songs WHERE n_versions > 1 ORDER BY views DESC;
```

| 멤버      | 대표제목                                                                                          |   판수 |   판합계조회수 |   음원조회수 |
|:--------|:----------------------------------------------------------------------------------------------|-----:|---------:|--------:|
| 아카네 리제  | 선잠 (Leina) / 아카네 리제 Cover                                                                     |    2 |  7770292 |       0 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                                                     |    2 |  7558945 |       0 |
| 텐코 시부키  | 여우비 / 텐코 시부키(Tenko Shibuki) cover                                                             |    2 |  5121811 |       0 |
| 하나코 나나  | Enemy [Imagine Dragons x J.I.D] / 하나코 나나 COVER                                                |    2 |  4905045 |       0 |
| 아카네 리제  | Golden - HUNTR/X (KPop Demon Hunters)ㅣ아카네 리제 x 아오쿠모 린 x 하나코 나나 【COVER】                        |    2 |  4188668 |       0 |
| 유즈하 리코  | Henceforth / 유즈하 리코(Yuzuha Riko) cover                                                        |    3 |  3331213 |       0 |
| 아오쿠모 린  | IRIS OUT (요네즈 켄시) / 아오쿠모 린(Aokumo Rin) Cover                                                  |    2 |  2944637 |       0 |
| 시라유키 히나 | LADY - KenshiYonezu(米津玄師) | 시라유키 히나 Cover                                                     |    2 |  2779455 |       0 |
| 텐코 시부키  | UNDEAD (YOASOBI) / 텐코 시부키(Tenko Shibuki) cover                                                |    2 |  2707710 |       0 |
| 시라유키 히나 | Summertime (cinnamons × evening cinema) | 시라유키 히나(Shirayuki Hina) x 하나코 나나(Hanako Nana) Cover |    2 |  1972795 |       0 |
| 유즈하 리코  | 맑은 날(ヨルシカ - 晴る)  / 유즈하 리코(Yuzuha Riko) cover                                                  |    2 |  1941888 |       0 |
| 시라유키 히나 | Melt (メルト/supercell ) | 시라유키 히나 Cover                                                         |    2 |  1373755 |       0 |
| 아오쿠모 린  | Ｗ●ＲＫ (MILLENNIUM PARADE × 시이나 링고) / 아오쿠모 린 x 하나코 나나 Cover                                     |    2 |  1305881 |       0 |
| 아오쿠모 린  | PLAY(プレイ) - Giga📸 #Live2D #shorts #cover                                                      |    2 |  1146575 |       0 |
| 하나코 나나  | [ 당신의 연인이 되고 싶어 / ChoQMay ] 하나코 나나 Short cover #vtuber #shorts                                |    2 |  1014054 |       0 |
| 유즈하 리코  | [4K] 네모네모(NEMONEMO) - YENA(최예나) / 유즈하 리코 (Yuzuha Riko) cover                                  |    2 |   921499 |       0 |
| 아오쿠모 린  | Unbreakable Sphere (승리의 여신: 니케 OST) / 아오쿠모 린(Aokumo Rin) Cover                                |    2 |   786959 |       0 |
| 시라유키 히나 | [4K] 앨리스 인 냉동고 (Alice in 冷凍庫) / 시라유키 히나 3D Live Cover                                         |    2 |   640441 |       0 |
| 하나코 나나  | [4K] 飛行艇(비행정) - King Gnu / 하나코 나나 3D Live Cover                                               |    2 |   527067 |       0 |
| 아라하시 타비 | 아라하시 타비 3D Cover 米津玄師 - Lady                                                                  |    2 |   505488 |       0 |
| 유즈하 리코  | [4K] No title - REOL / 유즈하 리코 (Yuzuha Riko) cover                                             |    2 |   377267 |       0 |
| 하나코 나나  | [4K] LAST STARDUST - Aimer / 하나코 나나 3D Cover                                                  |    2 |   350759 |       0 |
| 하나코 나나  | Dynamite - BTS(방탄소년단) / 하나코 나나 3D Cover #shorts #vtuber                                       |    2 |   349079 |       0 |
| 시라유키 히나 | [4K] 세계는 사랑에 빠져있어 (世界は恋に落ちている) | 시라유키 히나 3D Live Cover                                        |    2 |   332336 |       0 |
| 하나코 나나  | [4K] キミに100パーセント(너에게 100퍼센트) / 하나코 나나 3D Cover                                                |    2 |   257544 |       0 |
| 하나코 나나  | Dance The Night Away - TWICE(트와이스) / 하나코 나나 3D Cover #shorts #vtuber                          |    2 |   212862 |       0 |


## 곡당 평균 조회수 상위(5곡 이상)

```sql
SELECT name_ko AS 멤버, cover_count AS 곡수, CAST(avg_views AS INT) AS 평균조회수
FROM cover_metrics WHERE cover_count>=5 ORDER BY avg_views DESC;
```

| 멤버      |   곡수 |   평균조회수 |
|:--------|-----:|--------:|
| 아카네 리제  |   41 | 2770332 |
| 아오쿠모 린  |   57 | 1586671 |
| 시라유키 히나 |   50 | 1321968 |
| 하나코 나나  |   49 | 1227404 |
| 아라하시 타비 |   24 | 1220183 |
| 텐코 시부키  |   37 | 1193180 |
| 유즈하 리코  |   61 | 1052571 |
| 아야츠노 유니 |   15 | 1022800 |
| 네네코 마시로 |   21 |  716527 |
| 사키하네 후야 |    7 |  569482 |


## 멤버별 최고 커버

```sql
SELECT name_ko AS 멤버, best_cover AS 최고커버, max_views AS 조회수
FROM cover_metrics ORDER BY max_views DESC;
```

| 멤버      | 최고커버                                                         |      조회수 |
|:--------|:-------------------------------------------------------------|---------:|
| 아카네 리제  | 출항 [抜錨(발묘) / 나나호시 관현악단 ナナホシ管弦楽団] ㅣ아카네 리제(Akane Lize) 【COVER】 | 14896603 |
| 시라유키 히나 | 낙향(都落ち) / 시라유키 히나 Cover                                      |  8098219 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                    |  7388385 |
| 하나코 나나  | 비행정 [飛行艇 - King Gnu] / 하나코 나나 COVER                          |  5627024 |
| 아오쿠모 린  | 유령도쿄(Ayase) / 아오쿠모 린(Aokumo Rin) Cover                       |  5226755 |
| 아라하시 타비 | 낮에 뜨는 달 ( 안예은 ) / 아라하시 타비 Cover                              |  4020416 |
| 유즈하 리코  | 케세라세라 (Mrs. GREEN APPLE)  / 유즈하 리코(Yuzuha Riko) cover        |  3463294 |
| 아야츠노 유니 | 【아야츠노 유니 X 아이리 칸나】 점묘의 노래 (点描の唄) | Cover                     |  2992339 |
| 네네코 마시로 | Pale (MIMI) / 네네코 마시로 Cover                                  |  2270887 |
| 사키하네 후야 | 별자리가 될 수 있다면 (星座になれたら) l 사키하네 후야(Sakihane Huya) Cover        |  1457958 |


## 유닛별 커버 요약

```sql
SELECT unit AS 유닛, COUNT(*) AS 멤버수, SUM(cover_count) AS 총곡수,
       SUM(total_views) AS 총조회수
FROM cover_metrics GROUP BY unit ORDER BY 총조회수 DESC;
```

| 유닛       |   멤버수 |   총곡수 |      총조회수 |
|:---------|------:|------:|----------:|
| CLICHE   |     4 |   204 | 258937612 |
| UNIVERSE |     4 |   136 | 224013504 |
| EVERYS   |     2 |    22 |  19328387 |


## 솔로 vs 콜라보 비중

```sql
SELECT name_ko AS 멤버, ROUND(collab_share*100,0) AS 콜라보비중_pct, cover_count AS 곡수
FROM cover_metrics ORDER BY collab_share DESC;
```

| 멤버      |   콜라보비중_pct |   곡수 |
|:--------|------------:|-----:|
| 아오쿠모 린  |          21 |   57 |
| 하나코 나나  |          14 |   49 |
| 네네코 마시로 |          14 |   21 |
| 사키하네 후야 |          14 |    7 |
| 아야츠노 유니 |          13 |   15 |
| 유즈하 리코  |          13 |   61 |
| 텐코 시부키  |          11 |   37 |
| 시라유키 히나 |          10 |   50 |
| 아라하시 타비 |           8 |   24 |
| 아카네 리제  |           7 |   41 |

