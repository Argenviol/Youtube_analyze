# 08 · 동시시청자 시계열

**질문** — 라이브 동시시청자는 어떻게 움직이고, 팔로워 규모 대비 얼마나 모이는가(팬덤 밀도).

- 데이터: 치지직 라이브 상태 API 를 **10분 간격으로 직접 찍어** 쌓는 스냅샷. 치지직에는 동시시청자 히스토리 API 가 없고
  VOD 는 누적 조회수만 남기므로, **지금부터 찍는 것 말고는 만들 방법이 없는 유일한 데이터**다
- 갱신: live — GitHub Actions 가 매시 깨어나 잡 안에서 10분 간격. 놓친 구간은 영구 공백

## 실행

```bash
python collect.py --once                       # 1회 스냅샷
python collect.py --daemon --interval 10       # 상시 수집 (Windows: ../수집시작.cmd)
python analyze.py
python build_site.py
```

## 지표 정의

| 지표 | 정의 |
|---|---|
| `peak_ccu` | 관측 구간 최대 동시시청자. 10분 샘플링이라 순간 피크보다 낮게 잡힐 수 있다(과소 추정 방향이라 비교에는 안전) |
| 세션 | 연속된 라이브 스냅샷 묶음. 실측 간격 중앙값의 2.5배(`SESSION_GAP_FACTOR`)보다 길게 끊기면 다른 방송. `observed_min` 은 **관측된** 길이 |
| `ccu_per_1k_followers` | 팔로워 1,000명당 피크 동시시청자 — 규모가 아니라 밀도 |

## 커버리지 가드

관측 24시간(`MIN_OBSERVED_HOURS`) + 라이브 세션 5건(`MIN_LIVE_SESSIONS`)이 차기 전에는 라이브 결론을 내지 않는다.
관측 시간은 **첫~마지막 시각(span)이 아니라 실제로 찍은 시점 수 × 실측 간격**이다 — 수집기가 하루 꺼져 있으면 span 은
24시간을 넘지만 데이터는 몇 시간치뿐이기 때문이다. 수집 간격도 고정값이 아니라 실측 중앙값에서 유도한다
(Actions 스케줄러는 cron 을 보장하지 않아 실제 간격이 흔들린다). 팔로워 증감은 스냅샷 2개면 유효하므로 가드와 무관하게 낸다.

## 산출물

| 경로 | 내용 |
|---|---|
| `data/snapshots.csv` | 원본 스냅샷(append-only) |
| `data/sessions.csv` · `member_metrics.csv` | 재구성한 방송 세션 · 멤버별 집계 |
| `sql/viewership.db` · `charts/`(4종) · `site/`(SVG 직접 렌더) · `REPORT.md` | 공통 산출물 |

## 데이터 함정

- **치지직은 방송이 꺼져 있어도 `concurrentUserCount`·`liveTitle` 에 직전 방송 값을 돌려준다.** 첫 수집에서 11채널 전부
  `CLOSE` 인데 1,600~3,800명으로 찍혔다. `common.chzzk.normalize_live_status()` 가 `is_live=False` 면 라이브 지표를 비우고
  잔존값은 `last_*` 로 분리한다(시계열에 쓰지 않음).
- 초기 프로토타입(Node.js)에서 넘어온 가장 이른 레코드도 같은 스키마를 따른다 — 버그 수정 전 20건은 이관에서 제외했다.
- 12 는 이 세션 데이터로 이벤트 방송의 피크 배수와 "평소 요인(카테고리·시간대·요일)"의 배수를 같은 자로 잰다.
