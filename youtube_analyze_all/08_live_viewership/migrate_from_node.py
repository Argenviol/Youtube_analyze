"""
일회성 이관 스크립트.
초기 프로토타이핑에 쓴 Node 수집기(fandom-analytics/data/raw/chzzk/*.jsonl)의
스냅샷을 프로젝트8의 snapshots.csv 로 옮긴다. 이관 후에는 Node 수집기를 쓰지 않는다.

  python 08_live_viewership/migrate_from_node.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config

HERE = Path(__file__).resolve().parent
NODE_RAW = HERE.parents[1] / "fandom-analytics" / "data" / "raw" / "chzzk"
SNAPSHOTS = HERE / "data" / "snapshots.csv"

FIELDS = [
    "collected_at", "chzzk_id", "name_ko", "name_en", "unit", "role",
    "followers", "status", "is_live", "concurrent_users", "accumulate_count",
    "live_title", "category", "tags", "last_concurrent_users",
]

# name_ko -> (name_en, unit, role) 매핑. Node 설정에는 유닛 정보가 없었다.
META = {m["name_ko"]: m for m in config.member_rows()}


def main() -> None:
    if not NODE_RAW.exists():
        print(f"이관할 Node 데이터 없음: {NODE_RAW}")
        return

    # .bak 는 stale-viewer 버그 수정 이전 스키마라 제외한다.
    files = sorted(p for p in NODE_RAW.glob("*.jsonl") if not p.name.endswith(".bak"))
    rows = []
    for p in files:
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            m = META.get(r.get("config_name"), {})
            rows.append(dict(
                collected_at=r["collected_at"],
                chzzk_id=r["channel_id"],
                name_ko=r.get("config_name"),
                name_en=m.get("name_en", ""),
                unit=m.get("unit", ""),
                role=r.get("role", m.get("role", "")),
                followers=r.get("follower_count"),
                status=r.get("status"),
                is_live=r.get("is_live"),
                concurrent_users=r.get("concurrent_users"),
                accumulate_count=r.get("accumulate_count"),
                live_title=r.get("live_title"),
                category=r.get("category"),
                tags="|".join(r.get("tags") or []),
                last_concurrent_users=r.get("last_concurrent_users"),
            ))

    if not rows:
        print("이관할 레코드 없음")
        return

    # 이미 있는 collected_at+chzzk_id 는 건너뛴다 (재실행 안전).
    existing = set()
    if SNAPSHOTS.exists():
        with SNAPSHOTS.open(encoding="utf-8") as f:
            existing = {(r["collected_at"], r["chzzk_id"]) for r in csv.DictReader(f)}

    fresh = [r for r in rows if (r["collected_at"], r["chzzk_id"]) not in existing]
    if not fresh:
        print(f"이미 모두 이관됨 (기존 {len(existing)}건)")
        return

    SNAPSHOTS.parent.mkdir(parents=True, exist_ok=True)
    is_new = not SNAPSHOTS.exists()
    with SNAPSHOTS.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if is_new:
            w.writeheader()
        w.writerows(fresh)

    stamps = sorted({r["collected_at"] for r in fresh})
    print(f"이관 완료: {len(fresh)}건 ({len(stamps)}개 시점) -> {SNAPSHOTS}")
    print(f"  {stamps[0]} ~ {stamps[-1]}")


if __name__ == "__main__":
    main()
