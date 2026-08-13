"""
프로젝트8 · 수집 단계
치지직 멤버 채널의 **동시시청자 스냅샷**을 주기적으로 찍어 시계열을 만든다.

  python 08_live_viewership/collect.py --once          # 1회 스냅샷
  python 08_live_viewership/collect.py --daemon         # 10분 간격 상시 수집

왜 별도 프로젝트인가:
  프로젝트3(방송 패턴)은 VOD 다시보기 목록으로 과거 방송 이력을 소급 수집할 수 있다.
  하지만 **동시시청자는 소급이 불가능하다.** VOD는 readCount(누적 조회수)만 주고,
  치지직에는 동시시청자 히스토리 API가 없다. 지금부터 찍어 쌓는 것 말고는 방법이 없다.
  그래서 이 수집기는 파이프라인에서 가장 먼저, 그리고 계속 돌아야 한다.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config
from common.chzzk import Chzzk, normalize_live_status

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SNAPSHOTS = DATA / "snapshots.csv"

FIELDS = [
    "collected_at", "chzzk_id", "name_ko", "name_en", "unit", "role",
    "followers", "status", "is_live", "concurrent_users", "accumulate_count",
    "live_title", "category", "tags", "last_concurrent_users",
]


def _append_rows(rows: list[dict]) -> None:
    """append-only. 원본 스냅샷은 절대 덮어쓰지 않는다."""
    DATA.mkdir(parents=True, exist_ok=True)
    is_new = not SNAPSHOTS.exists()
    with SNAPSHOTS.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if is_new:
            w.writeheader()
        w.writerows(rows)


def snapshot(quiet: bool = False) -> list[dict]:
    cz = Chzzk()
    collected_at = datetime.now(timezone.utc).isoformat()
    rows, failed = [], 0

    for m in config.member_rows():
        cid = config.CHZZK_IDS.get(m["name_en"])
        if not cid:
            continue
        try:
            ch = cz.channel(cid)
            live = normalize_live_status(cz.live_status(cid))
        except Exception as e:
            # 채널 하나가 실패해도 나머지 수집은 계속한다.
            failed += 1
            if not quiet:
                print(f"  ✗ {m['name_ko']}: {e}")
            continue

        rows.append(dict(
            collected_at=collected_at, chzzk_id=cid,
            name_ko=m["name_ko"], name_en=m["name_en"],
            unit=m["unit"], role=m["role"],
            followers=ch.get("followerCount"), **live,
        ))
        time.sleep(0.4)  # 비공식 API에 대한 최소한의 예의

    _append_rows(rows)

    live_now = [r for r in rows if r["is_live"]]
    if not quiet:
        for r in rows:
            state = (f"LIVE {r['concurrent_users']:,}명" if r["is_live"] else "offline")
            print(f"  ✓ {r['name_ko']:<8} 팔로워 {r['followers']:>9,}  {state}")
        print(f"[08] {collected_at} — 수집 {len(rows)} / 실패 {failed} / 방송중 {len(live_now)}")

    _write_meta(collected_at)
    return rows


def _write_meta(last_at: str) -> None:
    n = 0
    if SNAPSHOTS.exists():
        with SNAPSHOTS.open(encoding="utf-8") as f:
            n = max(0, sum(1 for _ in f) - 1)
    span = None
    if SNAPSHOTS.exists():
        with SNAPSHOTS.open(encoding="utf-8") as f:
            rd = list(csv.DictReader(f))
        if rd:
            span = [rd[0]["collected_at"], rd[-1]["collected_at"]]
    (DATA / "_meta.json").write_text(json.dumps(dict(
        fetched_at=last_at, n_snapshots=n, n_members=len(config.member_rows()),
        span=span, interval_min=10,
        source="Chzzk 비공식 API (channels + polling live-status)",
        note="동시시청자는 소급 수집 불가. 이 파일은 계속 자라는 시계열이다.",
    ), ensure_ascii=False, indent=2), encoding="utf-8")


def daemon(interval_min: int = 10) -> None:
    print(f"[08] 수집 데몬 시작 — {interval_min}분 간격 (Ctrl+C로 종료)")
    while True:
        try:
            snapshot()
        except Exception as e:
            # 한 번의 실패로 데몬이 죽으면 시계열에 구멍이 난다.
            print(f"[08] 스냅샷 실패: {e}")
        time.sleep(interval_min * 60)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="1회 스냅샷 (기본 동작)")
    ap.add_argument("--daemon", action="store_true", help="상시 수집 모드")
    ap.add_argument("--interval", type=int, default=10, help="수집 간격(분)")
    a = ap.parse_args()
    daemon(a.interval) if a.daemon else snapshot()
