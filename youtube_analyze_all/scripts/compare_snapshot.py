"""
보존된 스냅샷과 현재 데이터를 비교해 증감을 보여준다.

  python scripts/compare_snapshot.py                       # 가장 오래된 보존본과 비교
  python scripts/compare_snapshot.py --label 2026-08-03_original

_archive/ 에 보존본을 남겨둔 덕분에 같은 지표를 두 시점에 걸쳐 볼 수 있다.
스냅샷은 한 번 덮어쓰면 복구가 불가능하므로, 갱신 전 보존이 이 비교의 전제다.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "_archive"

# (프로젝트, CSV 파일, 조인키, 비교할 컬럼들)
COMPARISONS = [
    ("01_member_channel_performance", "channel_metrics.csv", "name_en",
     ["subscribers", "recent_avg_views"]),
    ("03_chzzk_stream_pattern", "chzzk_channels.csv", "name_en", ["followers"]),
    ("02_cover_song_ranking", "cover_metrics.csv", "name_en", ["total_views", "cover_count"]),
]


def load(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


def compare(label: str) -> None:
    base = ARCHIVE / label
    if not base.exists():
        raise SystemExit(f"보존본을 찾을 수 없습니다: {base}")

    meta = json.loads((base / "_archive_meta.json").read_text(encoding="utf-8"))
    print(f"기준 스냅샷: {label} (보존일 {meta.get('archived_on')})\n")

    for proj, fname, key, cols in COMPARISONS:
        old = load(base / proj / "data" / fname)
        new = load(ROOT / proj / "data" / fname)
        if old is None or new is None:
            print(f"[{proj}] 비교 불가 ({fname} 없음)\n")
            continue

        avail = [c for c in cols if c in old.columns and c in new.columns]
        if not avail or key not in old.columns or key not in new.columns:
            print(f"[{proj}] 비교 불가 (컬럼 불일치)\n")
            continue

        m = old[[key, *avail]].merge(new[[key, *avail]], on=key, suffixes=("_old", "_new"))
        if m.empty:
            print(f"[{proj}] 비교 불가 (조인 결과 없음)\n")
            continue

        # 이름은 새 데이터에서 가져온다 (로스터가 바뀌었을 수 있다).
        if "name_ko" in new.columns:
            m = m.merge(new[[key, "name_ko"]].drop_duplicates(), on=key, how="left")

        print(f"[{proj}]")
        for c in avail:
            m[f"{c}_delta"] = m[f"{c}_new"] - m[f"{c}_old"]

        show = m.sort_values(f"{avail[0]}_delta", ascending=False)
        label_col = "name_ko" if "name_ko" in show.columns else key
        for _, r in show.iterrows():
            parts = []
            for c in avail:
                d = r[f"{c}_delta"]
                parts.append(f"{c} {r[f'{c}_old']:,.0f} → {r[f'{c}_new']:,.0f} ({d:+,.0f})")
            print(f"  {str(r[label_col]):<14} " + " | ".join(parts))
        print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", help="비교할 보존본 이름")
    a = ap.parse_args()
    labels = sorted(p.name for p in ARCHIVE.iterdir() if p.is_dir()) if ARCHIVE.exists() else []
    if not labels:
        raise SystemExit("보존본이 없습니다. scripts/archive_snapshot.py 를 먼저 실행하세요.")
    compare(a.label or labels[0])
