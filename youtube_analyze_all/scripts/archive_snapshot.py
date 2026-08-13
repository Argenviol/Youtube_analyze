"""
갱신 전에 현재 수집본을 날짜별로 보존한다.

  python scripts/archive_snapshot.py            # 오늘 날짜로 보존
  python scripts/archive_snapshot.py --label 2026-08-03-original
  python scripts/archive_snapshot.py --list     # 보존된 스냅샷 목록

왜 보존하는가:
  프로젝트 1~7의 데이터는 '수집 시점의 공개 스냅샷'이다. 갱신하면 이전 수치는 영영
  사라진다. 보존해두면 같은 지표를 두 시점에 걸쳐 비교할 수 있고, 그 자체가
  '성장률 분석'이라는 새로운 축이 된다. 스냅샷은 한 번 버리면 복구가 불가능하므로
  갱신 전에 반드시 이 스크립트를 먼저 돌린다.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "_archive"

# 보존 대상: 각 프로젝트의 data/ (원천·정제 CSV) 와 결과물 요약.
PROJECT_GLOB = "0*_*"
COPY_DIRS = ["data"]
COPY_FILES = ["REPORT.md"]


def projects() -> list[Path]:
    return sorted(p for p in ROOT.glob(PROJECT_GLOB) if p.is_dir())


def snapshot_label(p: Path) -> str | None:
    """프로젝트의 _meta.json에서 수집 시점을 읽어 라벨 후보로 쓴다."""
    meta = p / "data" / "_meta.json"
    if not meta.exists():
        return None
    try:
        return json.loads(meta.read_text(encoding="utf-8")).get("fetched_at", "")[:10]
    except Exception:
        return None


def archive(label: str) -> None:
    dest_root = ARCHIVE / label
    if dest_root.exists():
        raise SystemExit(
            f"이미 존재하는 보존본입니다: {dest_root}\n"
            f"덮어쓰지 않습니다. --label 로 다른 이름을 주세요."
        )

    saved = []
    for proj in projects():
        dest = dest_root / proj.name
        copied = False
        for d in COPY_DIRS:
            src = proj / d
            if src.exists():
                shutil.copytree(src, dest / d)
                copied = True
        for f in COPY_FILES:
            src = proj / f
            if src.exists():
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest / f)
                copied = True
        if copied:
            saved.append((proj.name, snapshot_label(proj)))

    if not saved:
        raise SystemExit("보존할 데이터를 찾지 못했습니다.")

    (dest_root / "_archive_meta.json").write_text(json.dumps(dict(
        archived_on=date.today().isoformat(),
        label=label,
        projects={name: fetched for name, fetched in saved},
        note="갱신 전 원본 스냅샷. 성장률 비교의 기준선으로 쓴다.",
    ), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"보존 완료 -> {dest_root}")
    for name, fetched in saved:
        print(f"  {name:<32} 수집시점 {fetched or '?'}")


def list_archives() -> None:
    if not ARCHIVE.exists():
        print("보존된 스냅샷이 없습니다.")
        return
    for d in sorted(ARCHIVE.iterdir()):
        if not d.is_dir():
            continue
        meta = d / "_archive_meta.json"
        info = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
        print(f"{d.name}  (보존일 {info.get('archived_on', '?')}, "
              f"프로젝트 {len(info.get('projects', {}))}개)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", help="보존본 이름 (기본: 수집시점 또는 오늘 날짜)")
    ap.add_argument("--list", action="store_true", help="보존본 목록")
    a = ap.parse_args()

    if a.list:
        list_archives()
    else:
        # 라벨을 안 주면 프로젝트들의 실제 수집 시점을 우선 사용한다.
        labels = {snapshot_label(p) for p in projects()} - {None, ""}
        default = min(labels) if labels else date.today().isoformat()
        archive(a.label or default)
