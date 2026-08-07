"""
프로젝트6 · 수집 단계
StelLive vs 홀로라이브(Hololive) vs 이세계아이돌(이세돌) 대표 멤버들의
채널 지표 + 최근 영상 성과를 비교 수집한다. (각 그룹 6명 표본)

  export YOUTUBE_API_KEY=...
  python 06_competitor_comparison/collect.py [--recent 30]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config
from common.youtube import YouTube

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def roster():
    rows = [dict(group="StelLive", name_ko=m["name_ko"], name_en=m["name_en"], channel_id=m["channel_id"])
            for m in config.member_rows() if m["role"] == "talent"][:6]
    for grp, members in config.COMPETITORS.items():
        for name_ko, name_en, cid in members:
            rows.append(dict(group=grp, name_ko=name_ko, name_en=name_en, channel_id=cid))
    return rows


def collect(recent: int = 30) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    yt = YouTube(config.get_api_key())
    people = roster()
    ids = [p["channel_id"] for p in people]
    ch_items = {c["id"]: c for c in yt.channels(ids)}

    ch_rows, vid_rows = [], []
    for p in people:
        c = ch_items.get(p["channel_id"])
        if not c:
            print(f"  ! {p['name_ko']} 채널 응답 없음"); continue
        stats, snip = c.get("statistics", {}), c.get("snippet", {})
        uploads = c["contentDetails"]["relatedPlaylists"]["uploads"]
        ch_rows.append(dict(
            group=p["group"], channel_id=p["channel_id"], name_ko=p["name_ko"], name_en=p["name_en"],
            subscribers=to_int(stats.get("subscriberCount")), total_views=to_int(stats.get("viewCount")),
            video_count=to_int(stats.get("videoCount")), created_at=snip.get("publishedAt"),
        ))
        vids = yt.playlist_video_ids(uploads, limit=recent)
        details = yt.videos(vids)
        print(f"  [{p['group']:10}] {p['name_ko']:10} 구독 {stats.get('subscriberCount'):>10} · 영상 {len(details)}개")
        for v in details:
            vs, vsnip = v.get("statistics", {}), v.get("snippet", {})
            vid_rows.append(dict(
                video_id=v["id"], channel_id=p["channel_id"], group=p["group"],
                name_ko=p["name_ko"], name_en=p["name_en"],
                title=vsnip.get("title"), published_at=vsnip.get("publishedAt"),
                views=to_int(vs.get("viewCount")), likes=to_int(vs.get("likeCount")),
                comments=to_int(vs.get("commentCount")),
            ))

    ch_df, vid_df = pd.DataFrame(ch_rows), pd.DataFrame(vid_rows)
    ch_df.to_csv(DATA / "channels.csv", index=False)
    vid_df.to_csv(DATA / "videos.csv", index=False)
    meta = dict(fetched_at=datetime.now(timezone.utc).isoformat(),
                n_channels=len(ch_df), n_videos=len(vid_df), recent_per_channel=recent,
                groups=list(ch_df["group"].unique()),
                source="YouTube Data API v3", note="각 그룹 대표 멤버 6명 표본 비교")
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: 채널 {len(ch_df)}개 / 영상 {len(vid_df)}개 -> {DATA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--recent", type=int, default=30)
    collect(ap.parse_args().recent)
