"""
프로젝트2 · 수집 단계
StelLive 멤버 채널에서 커버곡 영상을 검색·수집한다.
채널 검색(cover / 커버 / 歌ってみた) → 제목 필터로 커버 확정 → 영상 상세 지표.

  export YOUTUBE_API_KEY=...
  python 02_cover_song_ranking/collect.py [--per-query 40]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config
from common.youtube import YouTube

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

QUERIES = ["cover", "커버", "歌ってみた"]
# 제목에 아래 토큰이 있으면 커버로 확정 (검색 노이즈 제거)
COVER_TOKEN = re.compile(r"cover|커버|歌ってみた|うたってみた|불러[봤본]", re.IGNORECASE)


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def collect(per_query: int = 40) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    yt = YouTube(config.get_api_key())
    roster = config.member_rows()

    rows = []
    seen = set()
    for r in roster:
        cand_ids = []
        for q in QUERIES:
            items = yt.search(q, type_="video", max_results=per_query,
                              channel_id=r["channel_id"], order="relevance")
            for it in items:
                vid = it["id"]["videoId"]
                title = it["snippet"]["title"]
                if COVER_TOKEN.search(title) and vid not in seen:
                    cand_ids.append(vid)
        cand_ids = list(dict.fromkeys(cand_ids))
        seen.update(cand_ids)
        details = yt.videos(cand_ids)
        print(f"  {r['name_ko']:12} 커버 후보 {len(details)}개")
        for v in details:
            vs = v.get("statistics", {})
            sn = v.get("snippet", {})
            rows.append(dict(
                video_id=v["id"], channel_id=r["channel_id"],
                name_ko=r["name_ko"], name_en=r["name_en"], unit=r["unit"],
                title=sn.get("title"),
                published_at=sn.get("publishedAt"),
                views=to_int(vs.get("viewCount")),
                likes=to_int(vs.get("likeCount")),
                comments=to_int(vs.get("commentCount")),
                is_collab="x " in (sn.get("title") or "").lower() or " x" in (sn.get("title") or "").lower(),
            ))

    df = pd.DataFrame(rows).drop_duplicates("video_id").reset_index(drop=True)
    df.to_csv(DATA / "covers.csv", index=False)
    meta = dict(fetched_at=datetime.now(timezone.utc).isoformat(),
                n_covers=len(df), n_members=df["name_en"].nunique(),
                queries=QUERIES, source="YouTube Data API v3 (search+videos)")
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: 커버 {len(df)}개 / 멤버 {df['name_en'].nunique()}명 -> {DATA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-query", type=int, default=40)
    collect(ap.parse_args().per_query)
