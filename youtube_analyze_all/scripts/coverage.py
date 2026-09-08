"""
지난 N일의 수집 커버리지를 한 블록의 마크다운으로 낸다. 월요일 주간 리포트가 맨 위에 붙인다.

  python scripts/coverage.py            # 최근 7일
  python scripts/coverage.py --days 14

## 왜 따로 있나
2026-09-04~08 나흘 동안 08 동시시청자 스냅샷의 54%가 비어 있었는데 아무 알림도 없었다.
잡이 분리된 HEAD 에서 5시간을 돌다 exit 0 으로 끝나서, GitHub 은 '성공'으로 보고했다.
실패 알림은 실패한 잡에만 온다 — **조용히 아무것도 안 남기는 잡**은 커버리지로만 잡힌다.
08 은 소급 수집이 불가능하므로 이 숫자가 곧 영구 손실량이다.

간격 기준은 10분(워크플로 설계값)이다. 기대 시점 수 = N일 × 144. 실측 간격 중앙값이
10.2분이므로 정상이면 95% 안팎이 나온다. 90% 아래면 경고, 70% 아래면 한 잡 이상이
통째로 빈 것이다.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "08_live_viewership" / "data" / "snapshots.csv"

INTERVAL_MIN = 10
GAP_FACTOR = 3            # 간격의 3배(30분) 넘게 비면 '공백'으로 센다
WARN, CRIT = 0.90, 0.70


def snapshot_coverage(days: int, now: pd.Timestamp) -> dict:
    df = pd.read_csv(SNAP, usecols=["collected_at"])
    t = pd.to_datetime(df["collected_at"], utc=True).drop_duplicates().sort_values()
    start = now - pd.Timedelta(days=days)
    w = t[(t >= start) & (t <= now)].reset_index(drop=True)

    expected = days * 24 * 60 / INTERVAL_MIN
    ratio = min(1.0, len(w) / expected) if expected else 0.0

    # 공백: 창 시작→첫 시점, 시점 간, 마지막 시점→지금
    edges = pd.concat([pd.Series([start]), w, pd.Series([now])], ignore_index=True)
    diffs = edges.diff().dt.total_seconds().div(60)
    gaps = []
    for i in range(1, len(edges)):
        if diffs[i] > INTERVAL_MIN * GAP_FACTOR:
            gaps.append((edges[i - 1], edges[i], float(diffs[i])))
    lost_h = sum(g[2] for g in gaps) / 60

    # 일별 커버리지 — 어느 날이 비었는지
    daily = []
    for d in range(days):
        a = start + pd.Timedelta(days=d); b = a + pd.Timedelta(days=1)
        n = int(((w >= a) & (w < b)).sum())
        daily.append((a.strftime("%m-%d"), n, min(1.0, n / 144)))
    return dict(n=len(w), expected=int(expected), ratio=ratio, gaps=gaps,
                lost_h=lost_h, daily=daily, last=t.max() if len(t) else None)


def repo_health(now: datetime) -> dict:
    def git(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    log = git("log", "--format=%an|%ad|%s", "--date=short", "-300", "main")
    human = daily = weekly = None
    for line in log.splitlines():
        an, ad, msg = line.split("|", 2)
        if human is None and "github-actions" not in an:
            human = ad
        if daily is None and msg.startswith("chore: daily"):
            daily = ad
        if weekly is None and msg.startswith("chore: weekly"):
            weekly = ad
    def age(d):
        return (now.date() - datetime.strptime(d, "%Y-%m-%d").date()).days if d else None
    return dict(human=human, human_age=age(human), daily=daily, daily_age=age(daily),
                weekly=weekly, weekly_age=age(weekly))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    a = ap.parse_args()
    now = pd.Timestamp.now(tz="UTC")
    c = snapshot_coverage(a.days, now)
    h = repo_health(now.to_pydatetime())

    flag = "🟢" if c["ratio"] >= WARN else ("🟡" if c["ratio"] >= CRIT else "🔴")
    print(f"## 수집 커버리지 — 최근 {a.days}일\n")
    print(f"{flag} **08 동시시청자 {c['ratio']:.0%}** — 기대 {c['expected']:,}시점 중 {c['n']:,}시점 · "
          f"공백 {len(c['gaps'])}건 · **유실 {c['lost_h']:.1f}시간** (소급 불가)")
    if c["ratio"] < WARN:
        print(f"\n⚠ 커버리지가 {WARN:.0%} 아래다. 아래 공백 구간을 Actions 로그와 대조해 원인을 적을 것 "
              f"(`collect-live.yml` 머리말의 2026-09-08 메모 참고).")
    if c["gaps"]:
        print("\n| 공백 시작 (UTC) | 끝 | 길이 |\n|---|---|---|")
        for s, e, m in sorted(c["gaps"], key=lambda g: -g[2])[:8]:
            print(f"| {s:%m-%d %H:%M} | {e:%m-%d %H:%M} | {m/60:.1f}h |")
    print("\n| 날짜 | 시점 | 커버리지 |\n|---|---|---|")
    for d, n, r in c["daily"]:
        print(f"| {d} | {n} | {'🟢' if r >= WARN else ('🟡' if r >= CRIT else '🔴')} {r:.0%} |")
    print(f"\n마지막 스냅샷: {c['last']:%Y-%m-%d %H:%M} UTC ({(now - c['last']).total_seconds()/60:.0f}분 전)")

    print("\n**워크플로**: "
          f"daily 마지막 {h['daily']} ({h['daily_age']}일 전) · weekly 마지막 {h['weekly']} ({h['weekly_age']}일 전)")
    if h["daily_age"] is not None and h["daily_age"] > 2:
        print("⚠ daily 갱신이 2일 넘게 없다. collect-scheduled 워크플로를 확인할 것.")
    print(f"**사람 커밋**: 마지막 {h['human']} ({h['human_age']}일 전)"
          + (" — ⚠ 45일 초과. 60일이면 스케줄 워크플로가 자동 비활성화된다. 아무 커밋이나 하나 올릴 것."
             if h["human_age"] and h["human_age"] > 45 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
