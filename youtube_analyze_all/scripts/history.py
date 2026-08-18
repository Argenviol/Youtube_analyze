"""덮어쓰기 지표를 날짜별로 축적한다.

01·02·03·06 은 매 수집마다 metrics CSV 를 통째로 덮어쓴다. 그래서 리포트는 항상
"지금"만 보여주고, 변화를 보려면 git 히스토리를 뒤져야 했다. 이 스크립트는 각
프로젝트에 append-only `data/history.csv` 를 만들어 (날짜 × 대상 × 지표) 를 쌓는다.
한번 쌓이면 성장률·추세를 SQL 이나 pandas 로 바로 뽑을 수 있다.

  python scripts/history.py                 # 현재 지표를 오늘 자로 append (refresh.py 가 호출)
  python scripts/history.py --backfill      # git 히스토리에서 과거분 소급 복원
  python scripts/history.py --report        # 1일/7일/28일 변화 요약 출력

## 날짜 기준
행의 날짜는 "스크립트를 돌린 날"이 아니라 **그 데이터를 수집한 날**(`_meta.json` 의
fetched_at)이다. 그래야 소급 복원과 정상 append 가 같은 기준으로 섞인다.

## 멱등성
같은 (날짜, 대상) 행이 이미 있으면 새 값으로 교체한다. 하루에 여러 번 돌아도
중복이 쌓이지 않는다 — daily 워크플로가 재실행되는 경우가 실제로 있다.

## 08 은 대상이 아니다
08 은 이미 snapshots.csv 가 append-only 라 여기서 또 쌓을 이유가 없다.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# project -> (metrics 파일, 대상을 식별하는 키 컬럼, 추적할 지표 컬럼)
TRACKED = {
    "01_member_channel_performance": (
        "channel_metrics.csv", ["name_ko", "unit"],
        ["subscribers", "total_views", "video_count", "recent_avg_views",
         "recent_avg_engagement_rate", "uploads_per_week", "reach_ratio"],
    ),
    "02_cover_song_ranking": (
        "cover_metrics.csv", ["name_ko", "unit"],
        ["cover_count", "total_views", "avg_views", "total_likes", "avg_engagement_rate"],
    ),
    "03_chzzk_stream_pattern": (
        "stream_metrics.csv", ["name_ko", "unit"],
        ["followers", "stream_count", "streams_per_week", "avg_duration_h",
         "hours_per_week", "night_share", "avg_vod_views"],
    ),
    "06_competitor_comparison": (
        "member_metrics.csv", ["name_ko", "group"],
        ["subscribers", "recent_avg_views", "recent_avg_engagement_rate",
         "uploads_per_week", "reach_ratio"],
    ),
}


def _collected_date(meta_text: str) -> str | None:
    """_meta.json 본문에서 수집 날짜(YYYY-MM-DD)를 꺼낸다."""
    try:
        m = json.loads(meta_text)
    except Exception:
        return None
    v = m.get("fetched_at") or m.get("collected_at")
    return v[:10] if isinstance(v, str) and len(v) >= 10 else None


def _merge(hist_path: Path, new: pd.DataFrame, keys: list[str]) -> int:
    """(date, *keys) 기준으로 기존 행을 교체하며 병합. 추가/갱신된 행 수를 돌려준다."""
    if hist_path.exists():
        old = pd.read_csv(hist_path)
        merged = pd.concat([old, new], ignore_index=True)
        merged = merged.drop_duplicates(subset=["date"] + keys, keep="last")
    else:
        merged = new
    merged = merged.sort_values(["date"] + keys).reset_index(drop=True)
    hist_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(hist_path, index=False)
    return len(merged)


def append_current() -> int:
    """현재 작업트리의 지표를 각 프로젝트 history.csv 에 반영한다."""
    total = 0
    for proj, (fname, keys, metrics) in TRACKED.items():
        src = ROOT / proj / "data" / fname
        meta = ROOT / proj / "data" / "_meta.json"
        if not src.exists() or not meta.exists():
            print(f"  ! {proj} 건너뜀 (파일 없음)")
            continue
        date = _collected_date(meta.read_text(encoding="utf-8"))
        if not date:
            print(f"  ! {proj} 건너뜀 (수집 날짜 없음)")
            continue
        df = pd.read_csv(src)
        cols = [c for c in keys + metrics if c in df.columns]
        new = df[cols].copy()
        new.insert(0, "date", date)
        n = _merge(ROOT / proj / "data" / "history.csv", new, keys)
        print(f"  ✓ {proj:32} {date}  누적 {n}행")
        total += 1
    return total


def backfill() -> None:
    """git 히스토리를 훑어 과거 수집분을 소급 복원한다.

    봇이 매 수집마다 커밋하므로 커밋 하나가 곧 한 시점의 스냅샷이다. 같은 날짜에
    여러 커밋이 있으면 마지막 것만 쓴다(그날의 최종 상태).
    """
    # git 은 명령마다 경로 규칙이 다르다 — `git log -- <pathspec>` 은 cwd 기준,
    # `git show <sha>:<path>` 는 저장소 루트 기준이다. 둘을 섞으면 조용히 빈 결과가
    # 나온다. 저장소 루트에서 실행하고 경로도 루트 기준으로 통일한다.
    repo = ROOT.parent
    prefix = ROOT.name
    for proj, (fname, keys, metrics) in TRACKED.items():
        rel_src = f"{prefix}/{proj}/data/{fname}"
        rel_meta = f"{prefix}/{proj}/data/_meta.json"
        shas = subprocess.run(
            ["git", "log", "--format=%H", "--", rel_src],
            cwd=repo, capture_output=True, text=True).stdout.split()
        if not shas:
            print(f"  ! {proj} 히스토리 없음")
            continue

        by_date: dict[str, str] = {}
        for sha in reversed(shas):          # 오래된 것부터 → 같은 날짜는 뒤가 이김
            meta_txt = subprocess.run(
                ["git", "show", f"{sha}:{rel_meta}"],
                cwd=repo, capture_output=True, text=True).stdout
            d = _collected_date(meta_txt)
            if d:
                by_date[d] = sha

        frames = []
        for date, sha in sorted(by_date.items()):
            csv_txt = subprocess.run(
                ["git", "show", f"{sha}:{rel_src}"],
                cwd=repo, capture_output=True, text=True).stdout
            if not csv_txt.strip():
                continue
            try:
                df = pd.read_csv(io.StringIO(csv_txt))
            except Exception:
                continue
            cols = [c for c in keys + metrics if c in df.columns]
            if not cols:
                continue
            f = df[cols].copy()
            f.insert(0, "date", date)
            frames.append(f)

        if not frames:
            print(f"  ! {proj} 복원할 시점 없음")
            continue
        n = _merge(ROOT / proj / "data" / "history.csv",
                   pd.concat(frames, ignore_index=True), keys)
        print(f"  ✓ {proj:32} 시점 {len(frames)}일  누적 {n}행")


def report() -> None:
    """1일/7일/28일 변화를 성장률로 출력한다.

    절대 증가량은 규모가 큰 대상이 항상 유리하므로 %로 정규화한다. 창(window)마다
    가장 가까운 과거 시점을 기준으로 잡는다 — 수집이 하루 빠지는 경우가 있어
    "정확히 7일 전"이 항상 존재하지는 않는다.
    """
    for proj, (fname, keys, metrics) in TRACKED.items():
        hist = ROOT / proj / "data" / "history.csv"
        if not hist.exists():
            continue
        df = pd.read_csv(hist)
        df["date"] = pd.to_datetime(df["date"])
        dates = sorted(df["date"].unique())
        if len(dates) < 2:
            print(f"\n[{proj}] 시점 {len(dates)}개 — 비교할 과거가 없다")
            continue
        latest = dates[-1]
        primary = metrics[0]                      # 프로젝트별 대표 지표
        print(f"\n[{proj}] 기준 {pd.Timestamp(latest):%Y-%m-%d} · 지표 {primary}")

        cur = df[df["date"] == latest].set_index(keys[0])[primary]
        line = {}
        for label, days in (("1일", 1), ("7일", 7), ("28일", 28)):
            past = [d for d in dates if (latest - d).days >= days]
            if not past:
                continue
            base_date = past[-1]                  # 조건을 만족하는 가장 최근 시점
            prev = df[df["date"] == base_date].set_index(keys[0])[primary]
            pct = ((cur - prev) / prev * 100).dropna()
            line[label] = (pct, (latest - base_date).days)

        if not line:
            print("  비교 가능한 창이 없다")
            continue
        names = sorted(cur.index)
        head = "  " + f"{'대상':<14}" + "".join(
            f"{lab}({d}d)".rjust(12) for lab, (_, d) in line.items())
        print(head)
        first = list(line)[0]
        for nm in sorted(names, key=lambda x: -line[first][0].get(x, -999)):
            cells = "".join(f"{line[l][0].get(nm, float('nan')):+11.2f}%" for l in line)
            print(f"  {nm:<14}{cells}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true", help="git 히스토리에서 과거분 복원")
    ap.add_argument("--report", action="store_true", help="1일/7일/28일 변화 요약")
    a = ap.parse_args()
    if a.backfill:
        print("[history] git 히스토리 소급 복원")
        backfill()
    elif a.report:
        report()
    else:
        print("[history] 현재 지표 축적")
        append_current()
    return 0


if __name__ == "__main__":
    sys.exit(main())
