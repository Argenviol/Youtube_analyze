# 시장 분석 쿼리 결과

`sql/market.db`(SQLite) 실행 결과. 원천: Claude 웹서치 + 프로젝트1·6 자체 데이터.

## 시장 규모 전망 (리서치사별)

```sql
SELECT source_name AS 출처, year AS 연도, value AS 규모_백만달러
FROM market_facts WHERE category='market_size' ORDER BY source_name, year;
```

| 출처                            |   연도 |   규모_백만달러 |
|:------------------------------|-----:|----------:|
| Global Growth Insights        | 2026 |      3310 |
| Global Growth Insights        | 2032 |      8240 |
| SkyQuest Vtuber Market Report | 2026 |      3130 |
| SkyQuest Vtuber Market Report | 2031 |      4940 |


## 매출원·지역 구조

```sql
SELECT metric AS 지표, value AS 비율_pct, source_name AS 출처
FROM market_facts WHERE category IN ('revenue_share','region_share');
```

| 지표            |   비율_pct | 출처                            |
|:--------------|---------:|:------------------------------|
| 구독+후원 매출 비중   |    52.67 | SkyQuest Vtuber Market Report |
| 유튜브 매출 비중     |    49.73 | SkyQuest Vtuber Market Report |
| 아시아태평양 지역 점유율 |    65.14 | SkyQuest Vtuber Market Report |


## 치지직 핵심 지표

```sql
SELECT metric AS 지표, value AS 값, unit AS 단위, note AS 비고
FROM market_facts WHERE category='platform_kpi';
```

| 지표               |        값 | 단위      | 비고                                  |
|:-----------------|---------:|:--------|:------------------------------------|
| 치지직 월간활성이용자(MAU) | 2.42e+06 | users   | 2026년 7월 기준. 전년동월 대비 +17%           |
| 치지직 월간 시청시간      | 8.47e+08 | minutes | 2026년 7월 기준. 전년동월 대비 +91%           |
| 치지직 LCK 뷰어십      | 3.31e+06 | users   | SOOP(옛 아프리카TV) 125만명 대비 우위·점유율 60%+ |


## StelLive 성장 타임라인

```sql
SELECT date AS 날짜, event AS 이벤트, category AS 구분
FROM stellive_milestones ORDER BY date;
```

| 날짜      | 이벤트                                                       | 구분         |
|:--------|:----------------------------------------------------------|:-----------|
| 2014-11 | 강지 개인 스트리머로 유튜브 채널 개설                                     | origin     |
| 2021-01 | 강지 버추얼 크리에이터 기획사 스텔라이브 설립 준비 시작                           | origin     |
| 2022-12 | 1세대 EVERYS 유닛 데뷔 (아야츠노 유니 등)                              | launch     |
| 2023-06 | 2세대 UNIVERSE 유닛 데뷔 (네네코 마시로 등)                            | launch     |
| 2024-01 | 3세대 cliché 유닛 데뷔                                          | launch     |
| 2025-07 | 브레이브 그룹(Brave Group)에 인수합병 발표                             | investment |
| 2025-09 | 브레이브 그룹 투자 라운드 참여                                         | investment |
| 2025-12 | 첫 단체 콘서트 "2025 THE 1ST STELLIVE FESTIVAL [STAR TRAIL]" 개최 | milestone  |

