# 커버곡 분석 쿼리 실행 결과

`sql/covers.db`(SQLite) 실행 결과입니다.

## 커버곡 조회수 TOP 15

```sql
SELECT name_ko AS 멤버, title AS 곡, views AS 조회수, likes AS 좋아요
FROM covers ORDER BY views DESC LIMIT 15;
```

| 멤버      | 곡                                                                  |      조회수 |    좋아요 |
|:--------|:-------------------------------------------------------------------|---------:|-------:|
| 아카네 리제  | 출항 [抜錨(발묘) / 나나호시 관현악단 ナナホシ管弦楽団] ㅣ아카네 리제(Akane Lize) 【COVER】       | 14702127 | 108603 |
| 아카네 리제  | Drowning (WOODZ)ㅣ아카네 리제 (Akane Lize) 【Cover】                       | 12009969 |  72827 |
| 아카네 리제  | 내일의 밤하늘 초계반(アスノヨゾラ哨戒班)ㅣ아카네 리제(Akane Lize) 【COVER】                  | 10551383 |  58936 |
| 시라유키 히나 | 낙향(都落ち) / 시라유키 히나 Cover                                            |  8083131 |  44720 |
| 아카네 리제  | 괴물 (怪物) / 아카네 리제 Cover                                             |  7584097 |  41997 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                          |  7350295 |  44117 |
| 아카네 리제  | 선잠 (Leina) / 아카네 리제 Cover                                          |  6292533 |  35753 |
| 하나코 나나  | 비행정 [飛行艇 - King Gnu] / 하나코 나나 COVER                                |  5577088 |  37944 |
| 아오쿠모 린  | 유령도쿄(Ayase) / 아오쿠모 린(Aokumo Rin) Cover                             |  5206976 |  32693 |
| 아오쿠모 린  | W/X/Y (Tani Yuuki) / 아오쿠모 린(Aokumo Rin) Cover                      |  5086773 |  32588 |
| 시라유키 히나 | I Really Want to Stay At Your House (Arrange ver.) | 시라유키 히나 Cover |  5010228 |  48670 |
| 시라유키 히나 | 피날레(フィナーレ。) / 시라유키 히나 Cover                                        |  4923126 |  31247 |
| 텐코 시부키  | 여우비 / 텐코 시부키(Tenko Shibuki) cover                                  |  4906278 |  31978 |
| 아오쿠모 린  | TAEYEON (태연) 'To. X' / 아오쿠모 린(Aokumo Rin) Cover                    |  4558543 |  32636 |
| 아카네 리제  | Surges (Orangestar)ㅣ아카네 리제(Akane Lize) 【COVER】                     |  4508211 |  33431 |


## 멤버별 커버 성과 랭킹

```sql
SELECT rank AS 순위, name_ko AS 멤버, song_count AS 곡수, cover_count AS 영상수,
       total_views AS 총조회수, total_views_incl_topic AS 음원포함, CAST(avg_views AS INT) AS 영상당평균
FROM cover_metrics ORDER BY total_views DESC;
```

|   순위 | 멤버      |   곡수 |   영상수 |      총조회수 |      음원포함 |   영상당평균 |
|-----:|:--------|-----:|------:|----------:|----------:|--------:|
|    1 | 아카네 리제  |   39 |    41 | 112514749 | 112514749 | 2744262 |
|    2 | 아오쿠모 린  |   52 |    56 |  89532714 |  89532714 | 1598798 |
|    3 | 시라유키 히나 |   44 |    49 |  65559003 |  65559003 | 1337938 |
|    4 | 유즈하 리코  |   56 |    61 |  63587855 |  63587855 | 1042423 |
|    5 | 하나코 나나  |   42 |    49 |  59482946 |  59482946 | 1213937 |
|    6 | 텐코 시부키  |   34 |    37 |  43770940 |  43770940 | 1182998 |
|    7 | 아라하시 타비 |   23 |    24 |  29000391 |  29000391 | 1208349 |
|    8 | 아야츠노 유니 |   15 |    15 |  15282921 |  15282921 | 1018861 |
|    9 | 네네코 마시로 |   21 |    21 |  14953843 |  14953843 |  712087 |
|   10 | 사키하네 후야 |    7 |     7 |   3934774 |   3934774 |  562110 |


## 여러 판으로 올라온 곡

```sql
SELECT name_ko AS 멤버, title AS 대표제목, n_versions AS 판수, views AS 판합계조회수, topic_views AS 음원조회수
FROM cover_songs WHERE n_versions > 1 ORDER BY views DESC;
```

| 멤버      | 대표제목                                                                                          |   판수 |   판합계조회수 |   음원조회수 |
|:--------|:----------------------------------------------------------------------------------------------|-----:|---------:|--------:|
| 아카네 리제  | 선잠 (Leina) / 아카네 리제 Cover                                                                     |    2 |  7721885 |       0 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                                                     |    2 |  7520467 |       0 |
| 텐코 시부키  | 여우비 / 텐코 시부키(Tenko Shibuki) cover                                                             |    2 |  5103202 |       0 |
| 하나코 나나  | Enemy [Imagine Dragons x J.I.D] / 하나코 나나 COVER                                                |    2 |  4870233 |       0 |
| 아카네 리제  | Golden - HUNTR/X (KPop Demon Hunters)ㅣ아카네 리제 x 아오쿠모 린 x 하나코 나나 【COVER】                        |    2 |  4171723 |       0 |
| 유즈하 리코  | Henceforth / 유즈하 리코(Yuzuha Riko) cover                                                        |    3 |  3276945 |       0 |
| 아오쿠모 린  | IRIS OUT (요네즈 켄시) / 아오쿠모 린(Aokumo Rin) Cover                                                  |    2 |  2932174 |       0 |
| 시라유키 히나 | LADY - KenshiYonezu(米津玄師) | 시라유키 히나 Cover                                                     |    2 |  2758215 |       0 |
| 텐코 시부키  | UNDEAD (YOASOBI) / 텐코 시부키(Tenko Shibuki) cover                                                |    2 |  2693710 |       0 |
| 시라유키 히나 | Summertime (cinnamons × evening cinema) | 시라유키 히나(Shirayuki Hina) x 하나코 나나(Hanako Nana) Cover |    2 |  1959424 |       0 |
| 유즈하 리코  | 맑은 날(ヨルシカ - 晴る)  / 유즈하 리코(Yuzuha Riko) cover                                                  |    2 |  1932521 |       0 |
| 시라유키 히나 | Melt (メルト/supercell ) | 시라유키 히나 Cover                                                         |    2 |  1359673 |       0 |
| 아오쿠모 린  | Ｗ●ＲＫ (MILLENNIUM PARADE × 시이나 링고) / 아오쿠모 린 x 하나코 나나 Cover                                     |    2 |  1298355 |       0 |
| 아오쿠모 린  | PLAY(プレイ) - Giga📸 #Live2D #shorts #cover                                                      |    2 |  1143994 |       0 |
| 하나코 나나  | [ 당신의 연인이 되고 싶어 / ChoQMay ] 하나코 나나 Short cover #vtuber #shorts                                |    2 |  1010475 |       0 |
| 유즈하 리코  | [4K] 네모네모(NEMONEMO) - YENA(최예나) / 유즈하 리코 (Yuzuha Riko) cover                                  |    2 |   916656 |       0 |
| 아오쿠모 린  | Unbreakable Sphere (승리의 여신: 니케 OST) / 아오쿠모 린(Aokumo Rin) Cover                                |    2 |   783763 |       0 |
| 시라유키 히나 | [4K] 앨리스 인 냉동고 (Alice in 冷凍庫) / 시라유키 히나 3D Live Cover                                         |    2 |   634438 |       0 |
| 하나코 나나  | [4K] 飛行艇(비행정) - King Gnu / 하나코 나나 3D Live Cover                                               |    2 |   505346 |       0 |
| 아라하시 타비 | 아라하시 타비 3D Cover 米津玄師 - Lady                                                                  |    2 |   502121 |       0 |
| 유즈하 리코  | [4K] No title - REOL / 유즈하 리코 (Yuzuha Riko) cover                                             |    2 |   374582 |       0 |
| 하나코 나나  | [4K] LAST STARDUST - Aimer / 하나코 나나 3D Cover                                                  |    2 |   336127 |       0 |
| 시라유키 히나 | [4K] 세계는 사랑에 빠져있어 (世界は恋に落ちている) | 시라유키 히나 3D Live Cover                                        |    2 |   328130 |       0 |
| 하나코 나나  | Dynamite - BTS(방탄소년단) / 하나코 나나 3D Cover #shorts #vtuber                                       |    2 |   324945 |       0 |
| 하나코 나나  | [4K] キミに100パーセント(너에게 100퍼센트) / 하나코 나나 3D Cover                                                |    2 |   244027 |       0 |
| 하나코 나나  | Dance The Night Away - TWICE(트와이스) / 하나코 나나 3D Cover #shorts #vtuber                          |    2 |   185662 |       0 |


## 곡당 평균 조회수 상위(5곡 이상)

```sql
SELECT name_ko AS 멤버, cover_count AS 곡수, CAST(avg_views AS INT) AS 평균조회수
FROM cover_metrics WHERE cover_count>=5 ORDER BY avg_views DESC;
```

| 멤버      |   곡수 |   평균조회수 |
|:--------|-----:|--------:|
| 아카네 리제  |   41 | 2744262 |
| 아오쿠모 린  |   56 | 1598798 |
| 시라유키 히나 |   49 | 1337938 |
| 하나코 나나  |   49 | 1213937 |
| 아라하시 타비 |   24 | 1208349 |
| 텐코 시부키  |   37 | 1182998 |
| 유즈하 리코  |   61 | 1042423 |
| 아야츠노 유니 |   15 | 1018861 |
| 네네코 마시로 |   21 |  712087 |
| 사키하네 후야 |    7 |  562110 |


## 멤버별 최고 커버

```sql
SELECT name_ko AS 멤버, best_cover AS 최고커버, max_views AS 조회수
FROM cover_metrics ORDER BY max_views DESC;
```

| 멤버      | 최고커버                                                         |      조회수 |
|:--------|:-------------------------------------------------------------|---------:|
| 아카네 리제  | 출항 [抜錨(발묘) / 나나호시 관현악단 ナナホシ管弦楽団] ㅣ아카네 리제(Akane Lize) 【COVER】 | 14702127 |
| 시라유키 히나 | 낙향(都落ち) / 시라유키 히나 Cover                                      |  8083131 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                    |  7350295 |
| 하나코 나나  | 비행정 [飛行艇 - King Gnu] / 하나코 나나 COVER                          |  5577088 |
| 아오쿠모 린  | 유령도쿄(Ayase) / 아오쿠모 린(Aokumo Rin) Cover                       |  5206976 |
| 아라하시 타비 | 낮에 뜨는 달 ( 안예은 ) / 아라하시 타비 Cover                              |  4003158 |
| 유즈하 리코  | 케세라세라 (Mrs. GREEN APPLE)  / 유즈하 리코(Yuzuha Riko) cover        |  3445249 |
| 아야츠노 유니 | 【아야츠노 유니 X 아이리 칸나】 점묘의 노래 (点描の唄) | Cover                     |  2981887 |
| 네네코 마시로 | Pale (MIMI) / 네네코 마시로 Cover                                  |  2261078 |
| 사키하네 후야 | 별자리가 될 수 있다면 (星座になれたら) l 사키하네 후야(Sakihane Huya) Cover        |  1448879 |


## 유닛별 커버 요약

```sql
SELECT unit AS 유닛, COUNT(*) AS 멤버수, SUM(cover_count) AS 총곡수,
       SUM(total_views) AS 총조회수
FROM cover_metrics GROUP BY unit ORDER BY 총조회수 DESC;
```

| 유닛       |   멤버수 |   총곡수 |      총조회수 |
|:---------|------:|------:|----------:|
| CLICHE   |     4 |   203 | 256374455 |
| UNIVERSE |     4 |   135 | 222027986 |
| EVERYS   |     2 |    22 |  19217695 |


## 솔로 vs 콜라보 비중

```sql
SELECT name_ko AS 멤버, ROUND(collab_share*100,0) AS 콜라보비중_pct, cover_count AS 곡수
FROM cover_metrics ORDER BY collab_share DESC;
```

| 멤버      |   콜라보비중_pct |   곡수 |
|:--------|------------:|-----:|
| 아오쿠모 린  |          21 |   56 |
| 하나코 나나  |          14 |   49 |
| 네네코 마시로 |          14 |   21 |
| 사키하네 후야 |          14 |    7 |
| 아야츠노 유니 |          13 |   15 |
| 유즈하 리코  |          13 |   61 |
| 텐코 시부키  |          11 |   37 |
| 아라하시 타비 |           8 |   24 |
| 시라유키 히나 |           8 |   49 |
| 아카네 리제  |           7 |   41 |

