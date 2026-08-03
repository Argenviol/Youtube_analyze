"""
프로젝트1 · 수집 단계
StelLive 11개 채널의 채널 통계 + 최근 업로드 영상 지표를 YouTube Data API로 수집.

출력:
  data/channels.csv / channels.json   채널 단위 지표
  data/videos.csv                      최근 영상 단위 지표
  data/_meta.json                      수집 시각 등 메타
사용:
  export YOUTUBE_API_KEY=...
  python 01_member_channel_performance/collect.py [--recent 50]
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


def collect(recent: int = 50) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    yt = YouTube(config.get_api_key())
    roster = config.member_rows()
    ids = [r["channel_id"] for r in roster]

    print(f"채널 {len(ids)}개 조회 중...")
    ch_items = {c["id"]: c for c in yt.channels(ids)}

    ch_rows, vid_rows = [], []
    for r in roster:
        c = ch_items.get(r["channel_id"])
        if not c:
            print(f"  ! {r['name_ko']} 채널 응답 없음")
            continue
        stats = c.get("statistics", {})
        snip = c.get("snippet", {})
        uploads = c["contentDetails"]["relatedPlaylists"]["uploads"]
        ch_rows.append(dict(
            channel_id=r["channel_id"], name_ko=r["name_ko"], name_en=r["name_en"],
            unit=r["unit"], role=r["role"], handle=r["handle"],
            subscribers=to_int(stats.get("subscriberCount")),
            total_views=to_int(stats.get("viewCount")),
            video_count=to_int(stats.get("videoCount")),
            created_at=snip.get("publishedAt"),
            country=snip.get("country"),
            uploads_playlist=uploads,
        ))
        # 최근 영상
        vids = yt.playlist_video_ids(uploads, limit=recent)
        details = yt.videos(vids)
        print(f"  {r['name_ko']:12} 구독 {stats.get('subscriberCount'):>9} · 최근영상 {len(details)}개")
        for v in details:
            vs = v.get("statistics", {})
            vsnip = v.get("snippet", {})
            vid_rows.append(dict(
                video_id=v["id"], channel_id=r["channel_id"],
                name_ko=r["name_ko"], name_en=r["name_en"], unit=r["unit"],
                title=vsnip.get("title"),
                published_at=vsnip.get("publishedAt"),
                duration=v.get("contentDetails", {}).get("duration"),
                views=to_int(vs.get("viewCount")),
                likes=to_int(vs.get("likeCount")),
                comments=to_int(vs.get("commentCount")),
            ))

    ch_df = pd.DataFrame(ch_rows)
    vid_df = pd.DataFrame(vid_rows)
    ch_df.to_csv(DATA / "channels.csv", index=False)
    vid_df.to_csv(DATA / "videos.csv", index=False)
    ch_df.to_json(DATA / "channels.json", orient="records", force_ascii=False, indent=2)

    meta = dict(
        fetched_at=datetime.now(timezone.utc).isoformat(),
        recent_per_channel=recent,
        n_channels=len(ch_df), n_videos=len(vid_df),
        source="YouTube Data API v3",
    )
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: 채널 {len(ch_df)}개 / 영상 {len(vid_df)}개  ->  {DATA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--recent", type=int, default=50, help="채널당 최근 영상 수집 개수")
    collect(ap.parse_args().recent)
