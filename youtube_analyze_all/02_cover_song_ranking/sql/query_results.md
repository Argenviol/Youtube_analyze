# 커버곡 분석 쿼리 실행 결과

`sql/covers.db`(SQLite) 실행 결과입니다.

## 커버곡 조회수 TOP 15

```sql
SELECT name_ko AS 멤버, title AS 곡, views AS 조회수, likes AS 좋아요
FROM covers ORDER BY views DESC LIMIT 15;
```

| 멤버      | 곡                                                                  |      조회수 |    좋아요 |
|:--------|:-------------------------------------------------------------------|---------:|-------:|
| 아카네 리제  | 출항 [抜錨(발묘) / 나나호시 관현악단 ナナホシ管弦楽団] ㅣ아카네 리제(Akane Lize) 【COVER】       | 16510948 | 117389 |
| 아카네 리제  | Drowning (WOODZ)ㅣ아카네 리제 (Akane Lize) 【Cover】                       | 12387589 |  73990 |
| 아카네 리제  | 내일의 밤하늘 초계반(アスノヨゾラ哨戒班)ㅣ아카네 리제(Akane Lize) 【COVER】                  | 11271818 |  61419 |
| 시라유키 히나 | 낙향(都落ち) / 시라유키 히나 Cover                                            |  8248043 |  45383 |
| 아카네 리제  | 괴물 (怪物) / 아카네 리제 Cover                                             |  7810183 |  42933 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                          |  7728989 |  45582 |
| 아카네 리제  | 선잠 (Leina) / 아카네 리제 Cover                                          |  6520501 |  36665 |
| 하나코 나나  | 비행정 [飛行艇 - King Gnu] / 하나코 나나 COVER                                |  6055695 |  40021 |
| 아오쿠모 린  | W/X/Y (Tani Yuuki) / 아오쿠모 린(Aokumo Rin) Cover                      |  5445478 |  33936 |
| 아오쿠모 린  | 유령도쿄(Ayase) / 아오쿠모 린(Aokumo Rin) Cover                             |  5436298 |  33785 |
| 시라유키 히나 | I Really Want to Stay At Your House (Arrange ver.) | 시라유키 히나 Cover |  5267848 |  50001 |
| 아카네 리제  | Surges (Orangestar)ㅣ아카네 리제(Akane Lize) 【COVER】                     |  5107291 |  35590 |
| 텐코 시부키  | 여우비 / 텐코 시부키(Tenko Shibuki) cover                                  |  5056422 |  32651 |
| 시라유키 히나 | 피날레(フィナーレ。) / 시라유키 히나 Cover                                        |  5054245 |  31791 |
| 아오쿠모 린  | TAEYEON (태연) 'To. X' / 아오쿠모 린(Aokumo Rin) Cover                    |  4883159 |  33926 |


## 멤버별 커버 성과 랭킹

```sql
SELECT rank AS 순위, name_ko AS 멤버, song_count AS 곡수, cover_count AS 영상수,
       total_views AS 총조회수, total_views_incl_topic AS 음원포함, CAST(avg_views AS INT) AS 영상당평균
FROM cover_metrics ORDER BY total_views DESC;
```

|   순위 | 멤버      |   곡수 |   영상수 |      총조회수 |      음원포함 |   영상당평균 |
|-----:|:--------|-----:|------:|----------:|----------:|--------:|
|    1 | 아카네 리제  |   39 |    41 | 121332373 | 121332373 | 2959326 |
|    2 | 아오쿠모 린  |   55 |    59 |  99323704 |  99323704 | 1683452 |
|    3 | 시라유키 히나 |   46 |    51 |  69749698 |  69749698 | 1367641 |
|    4 | 유즈하 리코  |   57 |    62 |  69713555 |  69713555 | 1124412 |
|    5 | 하나코 나나  |   42 |    49 |  65290666 |  65290666 | 1332462 |
|    6 | 텐코 시부키  |   35 |    38 |  48003742 |  48003742 | 1263256 |
|    7 | 아라하시 타비 |   24 |    25 |  31864744 |  31864744 | 1274589 |
|    8 | 아야츠노 유니 |   16 |    16 |  16427049 |  16427049 | 1026690 |
|    9 | 네네코 마시로 |   21 |    21 |  15745981 |  15745981 |  749808 |
|   10 | 사키하네 후야 |    8 |     8 |   4632686 |   4632686 |  579085 |
|   11 | 토키노 메리  |    1 |     1 |   3668549 |   3668549 | 3668549 |
|   12 | 시즈키 토아  |    1 |     1 |   1741496 |   1741496 | 1741496 |
|   13 | 코가네 랑   |    1 |     1 |   1401133 |   1401133 | 1401133 |
|   14 | 하나요 히요리 |    1 |     1 |   1246948 |   1246948 | 1246948 |


## 여러 판으로 올라온 곡

```sql
SELECT name_ko AS 멤버, title AS 대표제목, n_versions AS 판수, views AS 판합계조회수, topic_views AS 음원조회수
FROM cover_songs WHERE n_versions > 1 ORDER BY views DESC;
```

| 멤버      | 대표제목                                                                                          |   판수 |   판합계조회수 |   음원조회수 |
|:--------|:----------------------------------------------------------------------------------------------|-----:|---------:|--------:|
| 아카네 리제  | 선잠 (Leina) / 아카네 리제 Cover                                                                     |    2 |  8171680 |       0 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                                                     |    2 |  7906672 |       0 |
| 텐코 시부키  | 여우비 / 텐코 시부키(Tenko Shibuki) cover                                                             |    2 |  5284654 |       0 |
| 하나코 나나  | Enemy [Imagine Dragons x J.I.D] / 하나코 나나 COVER                                                |    2 |  5284477 |       0 |
| 아카네 리제  | Golden - HUNTR/X (KPop Demon Hunters)ㅣ아카네 리제 x 아오쿠모 린 x 하나코 나나 【COVER】                        |    2 |  4347518 |       0 |
| 유즈하 리코  | Henceforth / 유즈하 리코(Yuzuha Riko) cover                                                        |    3 |  3785435 |       0 |
| 아오쿠모 린  | IRIS OUT (요네즈 켄시) / 아오쿠모 린(Aokumo Rin) Cover                                                  |    2 |  3056818 |       0 |
| 시라유키 히나 | LADY - KenshiYonezu(米津玄師) | 시라유키 히나 Cover                                                     |    2 |  2966644 |       0 |
| 텐코 시부키  | UNDEAD (YOASOBI) / 텐코 시부키(Tenko Shibuki) cover                                                |    2 |  2831387 |       0 |
| 시라유키 히나 | Summertime (cinnamons × evening cinema) | 시라유키 히나(Shirayuki Hina) x 하나코 나나(Hanako Nana) Cover |    2 |  2072883 |       0 |
| 유즈하 리코  | 맑은 날(ヨルシカ - 晴る)  / 유즈하 리코(Yuzuha Riko) cover                                                  |    2 |  2017606 |       0 |
| 시라유키 히나 | Melt (メルト/supercell ) | 시라유키 히나 Cover                                                         |    2 |  1485797 |       0 |
| 아오쿠모 린  | Ｗ●ＲＫ (MILLENNIUM PARADE × 시이나 링고) / 아오쿠모 린 x 하나코 나나 Cover                                     |    2 |  1376344 |       0 |
| 아오쿠모 린  | PLAY(プレイ) - Giga📸 #Live2D #shorts #cover                                                      |    2 |  1168684 |       0 |
| 하나코 나나  | [ 당신의 연인이 되고 싶어 / ChoQMay ] 하나코 나나 Short cover #vtuber #shorts                                |    2 |  1039096 |       0 |
| 유즈하 리코  | [4K] 네모네모(NEMONEMO) - YENA(최예나) / 유즈하 리코 (Yuzuha Riko) cover                                  |    2 |   962761 |       0 |
| 아오쿠모 린  | Unbreakable Sphere (승리의 여신: 니케 OST) / 아오쿠모 린(Aokumo Rin) Cover                                |    2 |   817502 |       0 |
| 시라유키 히나 | [4K] 앨리스 인 냉동고 (Alice in 冷凍庫) / 시라유키 히나 3D Live Cover                                         |    2 |   686766 |       0 |
| 하나코 나나  | [4K] 飛行艇(비행정) - King Gnu / 하나코 나나 3D Live Cover                                               |    2 |   658355 |       0 |
| 아라하시 타비 | [4K] LADY (요네즈 켄시)ㅣ아라하시 타비(Arahashi Tabi) 「Live Cover」                                        |    2 |   535503 |       0 |
| 하나코 나나  | Dynamite - BTS(방탄소년단) / 하나코 나나 3D Cover #shorts #vtuber                                       |    2 |   494528 |       0 |
| 하나코 나나  | [4K] LAST STARDUST - Aimer / 하나코 나나 3D Cover                                                  |    2 |   434667 |       0 |
| 유즈하 리코  | [4K] No title - REOL / 유즈하 리코 (Yuzuha Riko) cover                                             |    2 |   398332 |       0 |
| 시라유키 히나 | [4K] 세계는 사랑에 빠져있어 (世界は恋に落ちている) | 시라유키 히나 3D Live Cover                                        |    2 |   367470 |       0 |
| 하나코 나나  | [4K] キミに100パーセント(너에게 100퍼센트) / 하나코 나나 3D Cover                                                |    2 |   342929 |       0 |
| 하나코 나나  | Dance The Night Away - TWICE(트와이스) / 하나코 나나 3D Cover #shorts #vtuber                          |    2 |   307399 |       0 |


## 곡당 평균 조회수 상위(5곡 이상)

```sql
SELECT name_ko AS 멤버, cover_count AS 곡수, CAST(avg_views AS INT) AS 평균조회수
FROM cover_metrics WHERE cover_count>=5 ORDER BY avg_views DESC;
```

| 멤버      |   곡수 |   평균조회수 |
|:--------|-----:|--------:|
| 아카네 리제  |   41 | 2959326 |
| 아오쿠모 린  |   59 | 1683452 |
| 시라유키 히나 |   51 | 1367641 |
| 하나코 나나  |   49 | 1332462 |
| 아라하시 타비 |   25 | 1274589 |
| 텐코 시부키  |   38 | 1263256 |
| 유즈하 리코  |   62 | 1124412 |
| 아야츠노 유니 |   16 | 1026690 |
| 네네코 마시로 |   21 |  749808 |
| 사키하네 후야 |    8 |  579085 |


## 멤버별 최고 커버

```sql
SELECT name_ko AS 멤버, best_cover AS 최고커버, max_views AS 조회수
FROM cover_metrics ORDER BY max_views DESC;
```

| 멤버      | 최고커버                                                         |      조회수 |
|:--------|:-------------------------------------------------------------|---------:|
| 아카네 리제  | 출항 [抜錨(발묘) / 나나호시 관현악단 ナナホシ管弦楽団] ㅣ아카네 리제(Akane Lize) 【COVER】 | 16510948 |
| 시라유키 히나 | 낙향(都落ち) / 시라유키 히나 Cover                                      |  8248043 |
| 텐코 시부키  | 너에게 메롱(一二三) / 텐코 시부키(Tenko Shibuki) cover                    |  7728989 |
| 하나코 나나  | 비행정 [飛行艇 - King Gnu] / 하나코 나나 COVER                          |  6055695 |
| 아오쿠모 린  | W/X/Y (Tani Yuuki) / 아오쿠모 린(Aokumo Rin) Cover                |  5445478 |
| 아라하시 타비 | 낮에 뜨는 달 ( 안예은 ) / 아라하시 타비 Cover                              |  4169661 |
| 토키노 메리  | 도쿄 테디베어 [東京テディベア l Neru] / 토키노 메리 (Tokino Mary) Cover        |  3668549 |
| 유즈하 리코  | 케세라세라 (Mrs. GREEN APPLE)  / 유즈하 리코(Yuzuha Riko) cover        |  3624169 |
| 아야츠노 유니 | 【아야츠노 유니 X 아이리 칸나】 점묘의 노래 (点描の唄) | Cover                     |  3091049 |
| 네네코 마시로 | Pale (MIMI) / 네네코 마시로 Cover                                  |  2359318 |
| 시즈키 토아  | 제육감 [第六感 l Reol] / 시즈키 토아(Shizuki Toa) Cover                 |  1741496 |
| 사키하네 후야 | 별자리가 될 수 있다면 (星座になれたら) l 사키하네 후야(Sakihane Huya) Cover        |  1541586 |
| 코가네 랑   | 호랑풍류가 [나와 호랑이님 OST] / 코가네 랑 (Cogane Rang) Cover              |  1401133 |
| 하나요 히요리 | 유령이 되고싶어 [ゆうれいになりたい / 유이카] / 하나요 히요리 (Hanayo Hiyori) Cover   |  1246948 |


## 유닛별 커버 요약

```sql
SELECT unit AS 유닛, COUNT(*) AS 멤버수, SUM(cover_count) AS 총곡수,
       SUM(total_views) AS 총조회수
FROM cover_metrics GROUP BY unit ORDER BY 총조회수 DESC;
```

| 유닛       |   멤버수 |   총곡수 |      총조회수 |
|:---------|------:|------:|----------:|
| CLICHE   |     4 |   208 | 282331667 |
| UNIVERSE |     4 |   138 | 238692796 |
| EVERYS   |     2 |    24 |  21059735 |
| ABYSS    |     4 |     4 |   8058126 |


## 솔로 vs 콜라보 비중

```sql
SELECT name_ko AS 멤버, ROUND(collab_share*100,0) AS 콜라보비중_pct, cover_count AS 곡수
FROM cover_metrics ORDER BY collab_share DESC;
```

| 멤버      |   콜라보비중_pct |   곡수 |
|:--------|------------:|-----:|
| 아오쿠모 린  |          20 |   59 |
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

