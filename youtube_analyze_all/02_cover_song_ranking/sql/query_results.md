# 커버곡 분석 쿼리 실행 결과

`sql/covers.db`(SQLite) 실행 결과입니다.

## 커버곡 조회수 TOP 15

```sql
SELECT name_ko AS 멤버, title AS 곡, views AS 조회수, likes AS 좋아요
FROM covers ORDER BY views DESC LIMIT 15;
```

| 멤버      | 곡                                                                  |      조회수 |    좋아요 |
|:--------|:-------------------------------------------------------------------|---------:|-------:|
| 아카네 리제  | 출항 [抜錨(발묘) / 나나호시 관현악단 ナナホシ管弦楽団] ㅣ아카네 리제(Akane Lize) 【COVER】       | 15998391 | 115264 |
| 아카네 리제  | Drowning (WOODZ)ㅣ아카네 리제 (Akane Lize) 【Cover】                       | 12278463 |  73670 |
| 아카네 리제  | 내일의 밤하늘 초계반(アスノヨゾラ哨戒班)ㅣ아카네 리제(Akane Lize) 【COVER】                  | 11056864 |  60659 |
| 시라유키 히나 | 낙향(都落ち) / 시라유키 히나 Cover                                            |  8199763 |  45161 |
| 아카네 리제  | 괴물 (怪物) / 아카네 리제 Cover                                             |  7741737 |  42655 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                          |  7614395 |  45116 |
| 아카네 리제  | 선잠 (Leina) / 아카네 리제 Cover                                          |  6456824 |  36432 |
| 하나코 나나  | 비행정 [飛行艇 - King Gnu] / 하나코 나나 COVER                                |  5909486 |  39341 |
| 아오쿠모 린  | 유령도쿄(Ayase) / 아오쿠모 린(Aokumo Rin) Cover                             |  5369027 |  33497 |
| 아오쿠모 린  | W/X/Y (Tani Yuuki) / 아오쿠모 린(Aokumo Rin) Cover                      |  5341001 |  33512 |
| 시라유키 히나 | I Really Want to Stay At Your House (Arrange ver.) | 시라유키 히나 Cover |  5183471 |  49535 |
| 시라유키 히나 | 피날레(フィナーレ。) / 시라유키 히나 Cover                                        |  5017022 |  31642 |
| 텐코 시부키  | 여우비 / 텐코 시부키(Tenko Shibuki) cover                                  |  5014731 |  32489 |
| 아카네 리제  | Surges (Orangestar)ㅣ아카네 리제(Akane Lize) 【COVER】                     |  4914492 |  34865 |
| 아오쿠모 린  | TAEYEON (태연) 'To. X' / 아오쿠모 린(Aokumo Rin) Cover                    |  4788715 |  33515 |


## 멤버별 커버 성과 랭킹

```sql
SELECT rank AS 순위, name_ko AS 멤버, song_count AS 곡수, cover_count AS 영상수,
       total_views AS 총조회수, total_views_incl_topic AS 음원포함, CAST(avg_views AS INT) AS 영상당평균
FROM cover_metrics ORDER BY total_views DESC;
```

|   순위 | 멤버      |   곡수 |   영상수 |      총조회수 |      음원포함 |   영상당평균 |
|-----:|:--------|-----:|------:|----------:|----------:|--------:|
|    1 | 아카네 리제  |   39 |    41 | 118822617 | 118822617 | 2898112 |
|    2 | 아오쿠모 린  |   54 |    58 |  96417473 |  96417473 | 1662370 |
|    3 | 시라유키 히나 |   46 |    51 |  68583268 |  68583268 | 1344770 |
|    4 | 유즈하 리코  |   57 |    62 |  68011299 |  68011299 | 1096956 |
|    5 | 하나코 나나  |   42 |    49 |  63623422 |  63623422 | 1298437 |
|    6 | 텐코 시부키  |   35 |    38 |  46733312 |  46733312 | 1229824 |
|    7 | 아라하시 타비 |   24 |    25 |  31132467 |  31132467 | 1245298 |
|    8 | 아야츠노 유니 |   16 |    16 |  16158066 |  16158066 | 1009879 |
|    9 | 네네코 마시로 |   21 |    21 |  15525792 |  15525792 |  739323 |
|   10 | 사키하네 후야 |    8 |     8 |   4401877 |   4401877 |  550234 |
|   11 | 토키노 메리  |    1 |     1 |   2273823 |   2273823 | 2273823 |
|   12 | 시즈키 토아  |    1 |     1 |   1137326 |   1137326 | 1137326 |
|   13 | 코가네 랑   |    1 |     1 |   1097429 |   1097429 | 1097429 |
|   14 | 하나요 히요리 |    1 |     1 |    949763 |    949763 |  949763 |


## 여러 판으로 올라온 곡

```sql
SELECT name_ko AS 멤버, title AS 대표제목, n_versions AS 판수, views AS 판합계조회수, topic_views AS 음원조회수
FROM cover_songs WHERE n_versions > 1 ORDER BY views DESC;
```

| 멤버      | 대표제목                                                                                          |   판수 |   판합계조회수 |   음원조회수 |
|:--------|:----------------------------------------------------------------------------------------------|-----:|---------:|--------:|
| 아카네 리제  | 선잠 (Leina) / 아카네 리제 Cover                                                                     |    2 |  8049053 |       0 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                                                     |    2 |  7789702 |       0 |
| 텐코 시부키  | 여우비 / 텐코 시부키(Tenko Shibuki) cover                                                             |    2 |  5234618 |       0 |
| 하나코 나나  | Enemy [Imagine Dragons x J.I.D] / 하나코 나나 COVER                                                |    2 |  5129528 |       0 |
| 아카네 리제  | Golden - HUNTR/X (KPop Demon Hunters)ㅣ아카네 리제 x 아오쿠모 린 x 하나코 나나 【COVER】                        |    2 |  4298613 |       0 |
| 유즈하 리코  | Henceforth / 유즈하 리코(Yuzuha Riko) cover                                                        |    3 |  3645796 |       0 |
| 아오쿠모 린  | IRIS OUT (요네즈 켄시) / 아오쿠모 린(Aokumo Rin) Cover                                                  |    2 |  3024095 |       0 |
| 시라유키 히나 | LADY - KenshiYonezu(米津玄師) | 시라유키 히나 Cover                                                     |    2 |  2910735 |       0 |
| 텐코 시부키  | UNDEAD (YOASOBI) / 텐코 시부키(Tenko Shibuki) cover                                                |    2 |  2794371 |       0 |
| 시라유키 히나 | Summertime (cinnamons × evening cinema) | 시라유키 히나(Shirayuki Hina) x 하나코 나나(Hanako Nana) Cover |    2 |  2044261 |       0 |
| 유즈하 리코  | 맑은 날(ヨルシカ - 晴る)  / 유즈하 리코(Yuzuha Riko) cover                                                  |    2 |  1992534 |       0 |
| 시라유키 히나 | Melt (メルト/supercell ) | 시라유키 히나 Cover                                                         |    2 |  1452438 |       0 |
| 아오쿠모 린  | Ｗ●ＲＫ (MILLENNIUM PARADE × 시이나 링고) / 아오쿠모 린 x 하나코 나나 Cover                                     |    2 |  1352680 |       0 |
| 아오쿠모 린  | PLAY(プレイ) - Giga📸 #Live2D #shorts #cover                                                      |    2 |  1162609 |       0 |
| 하나코 나나  | [ 당신의 연인이 되고 싶어 / ChoQMay ] 하나코 나나 Short cover #vtuber #shorts                                |    2 |  1029935 |       0 |
| 유즈하 리코  | [4K] 네모네모(NEMONEMO) - YENA(최예나) / 유즈하 리코 (Yuzuha Riko) cover                                  |    2 |   950388 |       0 |
| 아오쿠모 린  | Unbreakable Sphere (승리의 여신: 니케 OST) / 아오쿠모 린(Aokumo Rin) Cover                                |    2 |   807190 |       0 |
| 시라유키 히나 | [4K] 앨리스 인 냉동고 (Alice in 冷凍庫) / 시라유키 히나 3D Live Cover                                         |    2 |   671916 |       0 |
| 하나코 나나  | [4K] 飛行艇(비행정) - King Gnu / 하나코 나나 3D Live Cover                                               |    2 |   614579 |       0 |
| 아라하시 타비 | [4K] LADY (요네즈 켄시)ㅣ아라하시 타비(Arahashi Tabi) 「Live Cover」                                        |    2 |   527241 |       0 |
| 하나코 나나  | Dynamite - BTS(방탄소년단) / 하나코 나나 3D Cover #shorts #vtuber                                       |    2 |   460806 |       0 |
| 하나코 나나  | [4K] LAST STARDUST - Aimer / 하나코 나나 3D Cover                                                  |    2 |   410869 |       0 |
| 유즈하 리코  | [4K] No title - REOL / 유즈하 리코 (Yuzuha Riko) cover                                             |    2 |   392030 |       0 |
| 시라유키 히나 | [4K] 세계는 사랑에 빠져있어 (世界は恋に落ちている) | 시라유키 히나 3D Live Cover                                        |    2 |   356986 |       0 |
| 하나코 나나  | [4K] キミに100パーセント(너에게 100퍼센트) / 하나코 나나 3D Cover                                                |    2 |   315390 |       0 |
| 하나코 나나  | Dance The Night Away - TWICE(트와이스) / 하나코 나나 3D Cover #shorts #vtuber                          |    2 |   288254 |       0 |


## 곡당 평균 조회수 상위(5곡 이상)

```sql
SELECT name_ko AS 멤버, cover_count AS 곡수, CAST(avg_views AS INT) AS 평균조회수
FROM cover_metrics WHERE cover_count>=5 ORDER BY avg_views DESC;
```

| 멤버      |   곡수 |   평균조회수 |
|:--------|-----:|--------:|
| 아카네 리제  |   41 | 2898112 |
| 아오쿠모 린  |   58 | 1662370 |
| 시라유키 히나 |   51 | 1344770 |
| 하나코 나나  |   49 | 1298437 |
| 아라하시 타비 |   25 | 1245298 |
| 텐코 시부키  |   38 | 1229824 |
| 유즈하 리코  |   62 | 1096956 |
| 아야츠노 유니 |   16 | 1009879 |
| 네네코 마시로 |   21 |  739323 |
| 사키하네 후야 |    8 |  550234 |


## 멤버별 최고 커버

```sql
SELECT name_ko AS 멤버, best_cover AS 최고커버, max_views AS 조회수
FROM cover_metrics ORDER BY max_views DESC;
```

| 멤버      | 최고커버                                                         |      조회수 |
|:--------|:-------------------------------------------------------------|---------:|
| 아카네 리제  | 출항 [抜錨(발묘) / 나나호시 관현악단 ナナホシ管弦楽団] ㅣ아카네 리제(Akane Lize) 【COVER】 | 15998391 |
| 시라유키 히나 | 낙향(都落ち) / 시라유키 히나 Cover                                      |  8199763 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                    |  7614395 |
| 하나코 나나  | 비행정 [飛行艇 - King Gnu] / 하나코 나나 COVER                          |  5909486 |
| 아오쿠모 린  | 유령도쿄(Ayase) / 아오쿠모 린(Aokumo Rin) Cover                       |  5369027 |
| 아라하시 타비 | 낮에 뜨는 달 ( 안예은 ) / 아라하시 타비 Cover                              |  4121208 |
| 유즈하 리코  | 케세라세라 (Mrs. GREEN APPLE)  / 유즈하 리코(Yuzuha Riko) cover        |  3572239 |
| 아야츠노 유니 | 【아야츠노 유니 X 아이리 칸나】 점묘의 노래 (点描の唄) | Cover                     |  3058580 |
| 네네코 마시로 | Pale (MIMI) / 네네코 마시로 Cover                                  |  2328161 |
| 토키노 메리  | 도쿄 테디베어 [東京テディベア l Neru] / 토키노 메리 (Tokino Mary) Cover        |  2273823 |
| 사키하네 후야 | 별자리가 될 수 있다면 (星座になれたら) l 사키하네 후야(Sakihane Huya) Cover        |  1516128 |
| 시즈키 토아  | 제육감 [第六感 l Reol] / 시즈키 토아(Shizuki Toa) Cover                 |  1137326 |
| 코가네 랑   | 호랑풍류가 [나와 호랑이님 OST] / 코가네 랑 (Cogane Rang) Cover              |  1097429 |
| 하나요 히요리 | 유령이 되고싶어 [ゆうれいになりたい / 유이카] / 하나요 히요리 (Hanayo Hiyori) Cover   |   949763 |


## 유닛별 커버 요약

```sql
SELECT unit AS 유닛, COUNT(*) AS 멤버수, SUM(cover_count) AS 총곡수,
       SUM(total_views) AS 총조회수
FROM cover_metrics GROUP BY unit ORDER BY 총조회수 DESC;
```

| 유닛       |   멤버수 |   총곡수 |      총조회수 |
|:---------|------:|------:|----------:|
| CLICHE   |     4 |   207 | 274785506 |
| UNIVERSE |     4 |   138 | 234064144 |
| EVERYS   |     2 |    24 |  20559943 |
| ABYSS    |     4 |     4 |   5458341 |


## 솔로 vs 콜라보 비중

```sql
SELECT name_ko AS 멤버, ROUND(collab_share*100,0) AS 콜라보비중_pct, cover_count AS 곡수
FROM cover_metrics ORDER BY collab_share DESC;
```

| 멤버      |   콜라보비중_pct |   곡수 |
|:--------|------------:|-----:|
| 아오쿠모 린  |          21 |   58 |
| 하나코 나나  |          14 |   49 |
| 네네코 마시로 |          14 |   21 |
| 유즈하 리코  |          13 |   62 |
| 아야츠노 유니 |          13 |   16 |
| 사키하네 후야 |          13 |    8 |
| 시라유키 히나 |          12 |   51 |
| 텐코 시부키  |          11 |   38 |
| 아라하시 타비 |           8 |   25 |
| 아카네 리제  |           7 |   41 |
| 토키노 메리  |           0 |    1 |
| 시즈키 토아  |           0 |    1 |
| 코가네 랑   |           0 |    1 |
| 하나요 히요리 |           0 |    1 |

