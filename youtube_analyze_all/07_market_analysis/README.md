# 07 · 버추얼 크리에이터 시장

**질문** — 배경이 되는 시장은 얼마나 빨리, 어떤 구조로 자라는가. 스텔라이브는 그 안에서 어디에 있는가.

- 데이터: **출처가 명시된 공개 리서치·보도·통계**(`data/market_facts.csv`, 행마다 출처명·URL) + 스텔라이브 연표
  (`stellive_milestones.csv`) + 01·06 의 자체 수집 데이터. API 수집이 없는 유일한 프로젝트
- 갱신: daily 재분석만(수집 없음, `refresh.py` 의 `NO_COLLECT`). 06 이 매일 갱신되므로 같이 돌려야 낡지 않는다

## 실행

```bash
python analyze.py      # data/*.csv → sql/ charts/ REPORT.md site/data.json
python build_site.py
```

시장 통계를 새로 조사하면 `market_facts.csv` 에 행을 더하고(출처 필수) `analyze.py` 를 다시 돌린다.

## 데이터 원천

| 구분 | 출처 | 비고 |
|---|---|---|
| 글로벌 VTuber 시장 규모 | 리서치사 보고서(SkyQuest, Global Growth Insights) | 방법론 차이로 편차가 커서 **범위로 해석** |
| 한국 스트리밍(치지직) | 언론 보도 | MAU·시청시간 |
| 한국 크리에이터 산업 | 한국콘텐츠진흥원 실태조사 | |
| 스텔라이브 포지션 | 01·06 자체 수집 | 실측 |

## 산출물

| 경로 | 내용 |
|---|---|
| `data/market_facts.csv` · `stellive_milestones.csv` | 시장 통계(출처·URL) · 연표 |
| `sql/` | `market_facts` · `stellive_milestones` · 06 의 `cohort_summary`/`group_summary` 재사용 |
| `charts/`(5종) · `site/`(출처 링크 포함) · `REPORT.md` | 공통 산출물 |

## 읽는 법 · 한계

- 시장 매출의 절반가량이 구독·후원이라 **팬 직접 후원 기반 수익모델**이 핵심이고, 한국은 트위치 철수 뒤 치지직 중심이다.
- 스텔라이브는 규모는 작지만 도달 효율이 비교 그룹보다 높다 — 수치는 06 이 매일 갱신하므로 `REPORT.md` 를 본다.
- 12 는 시장 연평균 성장률과 스텔라이브 구독자 성장을 같은 단위(연율)로 놓는데, 짧은 기간을 연환산한 값이라 방향만 읽는다.
- 시장 규모 추정치는 절대 수치보다 성장 추세·구조 신호로 읽는다.
