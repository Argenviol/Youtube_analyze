"""4기 ABYSS 데뷔의 영향력 (루트 `4기_데뷔의_영향력.md` 의 원본 계산).

08 동시시청자 스냅샷(치지직, 10분 간격)에서 같은 시각의 시청자를 채널 전부 더한 '합계'를
데뷔 전·뒤로 나눠 비교한다. 방송 중이 아닌 채널은 0으로 센다.

- 데뷔 전: 수집이 10분 간격으로 자리잡은 2026-09-09 ~ 데뷔 전날 2026-10-16
  (8/12~9/8 은 한 시간에 한 장 안팎이라 뺀다)
- 데뷔 뒤: 2026-10-17 ~ 어제(한국 날짜). 오늘은 하루가 덜 차서 뺀다.
- 하루 단위로 평균·최고를 낸 뒤 기간 평균을 낸다 — 날마다 수집 장수가 조금 달라도 하루 무게는 같다.

  python abyss_impact.py            # 문서의 표를 그대로 출력
"""
from pathlib import Path

import pandas as pd

SNAP = Path(__file__).resolve().parents[1] / "08_live_viewership" / "data" / "snapshots.csv"
KST = "Asia/Seoul"
BEFORE_FROM, DEBUT = pd.Timestamp("2026-09-09", tz=KST), pd.Timestamp("2026-10-17", tz=KST)
UNITS = ["STELLIVE", "EVERYS", "UNIVERSE", "CLICHE", "ABYSS"]


def load():
    d = pd.read_csv(SNAP)
    d["t"] = pd.to_datetime(d.collected_at, utc=True, format="mixed").dt.tz_convert(KST)
    d["ccu"] = d.concurrent_users.where(d.is_live.astype(str) == "True", 0).fillna(0)
    today = pd.Timestamp.now(tz=KST).normalize()
    d = d[(d.t >= BEFORE_FROM) & (d.t < today)].copy()
    d["after"] = d.t >= DEBUT
    d["day"] = d.t.dt.date
    return d


def daily(x):
    """같은 시각 합계 → 하루 평균·하루 최고 → 기간(전/뒤) 평균."""
    s = x.groupby("collected_at").agg(c=("ccu", "sum"), after=("after", "first"), day=("day", "first"))
    day = s.groupby(["after", "day"]).c.agg(["mean", "max"])
    return day.groupby("after").mean().reindex([False, True]).fillna(0)


def fmt(v):
    return f"{v:,.0f}"


def ratio(a, b):
    return f"{b / a:.2f}배" if a else "새로 생김"


def main():
    d = load()
    days = d.groupby("after").day.nunique()
    span = d.groupby("after").day.agg(["min", "max"])
    print(f"데뷔 전 {span.loc[False,'min']} ~ {span.loc[False,'max']} ({days[False]}일) · "
          f"데뷔 뒤 {span.loc[True,'min']} ~ {span.loc[True,'max']} ({days[True]}일)\n")

    t = daily(d)
    print("| 지표 | 데뷔 전 | 데뷔 뒤 | 변화 |\n|---|---:|---:|---:|")
    print(f"| 평균 합계 | {fmt(t.loc[False,'mean'])}명 | {fmt(t.loc[True,'mean'])}명 | **{ratio(t.loc[False,'mean'], t.loc[True,'mean'])}** |")
    print(f"| 하루 최고 합계 | {fmt(t.loc[False,'max'])}명 | {fmt(t.loc[True,'max'])}명 | **{ratio(t.loc[False,'max'], t.loc[True,'max'])}** |")
    print(f"| 하루 시청 총량 | {t.loc[False,'mean']*24/1e4:.1f}만 시간 | {t.loc[True,'mean']*24/1e4:.1f}만 시간 | "
          f"**{ratio(t.loc[False,'mean'], t.loc[True,'mean'])}** |\n")

    print("| 묶음 | 평균 합계 (전 → 뒤) | 변화 | 하루 최고 (전 → 뒤) | 데뷔 뒤 전체 중 몫 |\n|---|---:|---:|---:|---:|")
    groups = [("기존 멤버 (강지 포함 11명)", d[d.unit != "ABYSS"])] + [(u, d[d.unit == u]) for u in UNITS]
    for name, x in groups:
        g = daily(x)
        print(f"| {name} | {fmt(g.loc[False,'mean'])} → {fmt(g.loc[True,'mean'])} | {ratio(g.loc[False,'mean'], g.loc[True,'mean'])} | "
              f"{fmt(g.loc[False,'max'])} → {fmt(g.loc[True,'max'])} | {g.loc[True,'mean']/t.loc[True,'mean']:.0%} |")

    old = d[d.unit != "ABYSS"]
    live = old[old.ccu > 0]
    on = old.groupby(["after", "collected_at"]).ccu.apply(lambda c: (c > 0).sum()).groupby("after").mean()
    avg = live.groupby("after").ccu.mean()
    print("\n| 기존 멤버 | 데뷔 전 | 데뷔 뒤 | 변화 |\n|---|---:|---:|---:|")
    print(f"| 같은 시각 방송 중인 인원 | {on[False]:.1f}명 | {on[True]:.1f}명 | {on[True]/on[False]:.2f}배 |")
    print(f"| 방송 중일 때 채널 평균 시청자 | {fmt(avg[False])}명 | {fmt(avg[True])}명 | {avg[True]/avg[False]:.2f}배 |")


if __name__ == "__main__":
    main()
