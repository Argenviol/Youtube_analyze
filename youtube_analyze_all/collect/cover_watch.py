"""
유명 곡의 커버가 정말 인기를 끄는지 — 곡마다 유튜브 검색 상위 영상(원곡·커버)의 조회수를 쌓고, 올린 채널의 평소 조회수와 견준다.

입력: collect/cover_watch.csv (song, query, note) — 운영자가 보고 싶은 곡을 한 줄씩 올린다. 해외곡·우타이테·버튜버 곡 모두 같은 방식.
방법(API 키 불필요, 유튜브 웹 innertube):
  1. 검색어로 영상 검색 → 상위 N개의 id·제목·채널
  2. 영상마다 정확한 조회수·업로드일(member_views.video_info)
  3. 채널마다 최근 업로드 10개 조회수 중앙값 = 그 채널의 '평소' (14일마다 갱신, cover_watch_baseline.csv)
  '인기를 끌었나' = 커버 조회수 ÷ 그 채널의 평소 조회수. 채널이 큰 탓인지 곡 덕인지를 가르려는 값이다.
한계: 검색 상위 N개만 본다(검색 순위는 개인화·변동). 원곡은 '조회수 최대 영상'으로 정한다. 채널의 평소가 최근 10개라 오래된 커버와는 시기가 다르다.
산출(collect/data/): cover_watch_views.csv (collected_at, song, video_id, title, channel, channel_id, published, views) · cover_watch_baseline.csv
사용: python collect/cover_watch.py --top 20
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "member_views"))
sys.path.insert(0, str(HERE))
import member_views as mv  # noqa: E402
from shorts_snapshot import recent_uploads  # noqa: E402

SEEDS = HERE / "cover_watch.csv"
VIEWS = HERE / "data" / "cover_watch_views.csv"
BASE = HERE / "data" / "cover_watch_baseline.csv"
BASE_DAYS = 14


def search(query: str, top: int) -> list[dict]:
    j = json.loads(mv._post("search", {"query": query, "params": "EgIQAQ%3D%3D"}))      # 영상만
    out: list[dict] = []

    def walk(o):
        if isinstance(o, dict):
            v = o.get("videoRenderer")
            if v and v.get("videoId"):
                owner = (v.get("ownerText") or {}).get("runs", [{}])[0]
                out.append({"id": v["videoId"], "title": "".join(r["text"] for r in v["title"]["runs"]),
                            "channel": owner.get("text", ""),
                            "channel_id": (owner.get("navigationEndpoint") or {}).get("browseEndpoint", {}).get("browseId", "")})
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(j)
    seen, uniq = set(), []
    for x in out:
        if x["id"] not in seen:
            seen.add(x["id"])
            uniq.append(x)
    return uniq[:top]


def baseline(channel_id: str) -> float | None:
    items = recent_uploads(channel_id, 10)
    views = [r["views"] for r in map(mv.video_info, items) if r["views"] is not None]
    return float(statistics.median(views)) if views else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    rows = []
    for s in pd.read_csv(SEEDS).itertuples():
        hits = search(s.query, a.top)
        for h, info in zip(hits, map(mv.video_info, hits)):
            if info["views"] is None:
                print(f"  조회수 실패: {h['id']}")
                continue
            rows.append({"collected_at": now.isoformat(timespec="seconds"), "song": s.song, "video_id": h["id"], "title": h["title"],
                         "channel": h["channel"], "channel_id": h["channel_id"], "published": info["date"], "views": info["views"]})
        print(f"{s.song}: 영상 {len(hits)}개")
    df = pd.DataFrame(rows)
    VIEWS.parent.mkdir(exist_ok=True)
    pd.concat([pd.read_csv(VIEWS), df], ignore_index=True).to_csv(VIEWS, index=False, encoding="utf-8-sig") if VIEWS.exists() \
        else df.to_csv(VIEWS, index=False, encoding="utf-8-sig")

    old = pd.read_csv(BASE) if BASE.exists() else pd.DataFrame(columns=["channel_id", "channel", "median_views", "collected_at"])
    fresh = {r.channel_id for r in old.itertuples() if now - datetime.fromisoformat(r.collected_at) < timedelta(days=BASE_DAYS)}
    new = []
    for cid, name in df[["channel_id", "channel"]].drop_duplicates().itertuples(index=False):
        if cid and cid not in fresh:
            m = baseline(cid)
            new.append({"channel_id": cid, "channel": name, "median_views": m, "collected_at": now.isoformat(timespec="seconds")})
    if new:
        pd.concat([old[~old["channel_id"].isin([n["channel_id"] for n in new])], pd.DataFrame(new)], ignore_index=True) \
            .to_csv(BASE, index=False, encoding="utf-8-sig")
    print(f"조회수 {len(df)}건 기록 · 채널 평소 {len(new)}곳 갱신")
    return 0


if __name__ == "__main__":
    sys.exit(main())
