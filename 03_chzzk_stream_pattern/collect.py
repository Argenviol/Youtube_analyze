"""
프로젝트3 · 수집 단계
치지직(Chzzk) 멤버 채널의 다시보기(VOD=방송 replay) 목록을 수집해 방송 패턴 데이터를 만든다.

  python 03_chzzk_stream_pattern/collect.py [--max 300]
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
from common.chzzk import Chzzk

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def collect(max_items: int = 300) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    cz = Chzzk()
    ch_rows, vod_rows = [], []
    for m in config.member_rows():
        cid = config.CHZZK_IDS.get(m["name_en"])
        if not cid:
            continue
        ch = cz.channel(cid)
        followers = ch.get("followerCount")
        vods = cz.videos(cid, max_items=max_items)
        # REPLAY(생방송 다시보기)만 = 실제 방송
        replays = [v for v in vods if v.get("videoType") == "REPLAY"]
        print(f"  {m['name_ko']:12} 팔로워 {followers:>8,} · 방송 {len(replays)}개")
        ch_rows.append(dict(
            chzzk_id=cid, name_ko=m["name_ko"], name_en=m["name_en"], unit=m["unit"],
            followers=followers, total_vods=ch.get("channelType") and None or len(vods),
        ))
        for v in replays:
            vod_rows.append(dict(
                video_no=v.get("videoNo"), chzzk_id=cid,
                name_ko=m["name_ko"], name_en=m["name_en"], unit=m["unit"],
                title=v.get("videoTitle"),
                publish_date=v.get("publishDate"),           # KST 문자열
                duration_sec=v.get("duration"),
                category=v.get("videoCategoryValue") or "기타",
                category_type=v.get("categoryType"),
                read_count=v.get("readCount"),
            ))

    ch_df = pd.DataFrame(ch_rows)
    vod_df = pd.DataFrame(vod_rows)
    ch_df.to_csv(DATA / "chzzk_channels.csv", index=False)
    vod_df.to_csv(DATA / "streams.csv", index=False)
    meta = dict(fetched_at=datetime.now(timezone.utc).isoformat(),
                n_members=len(ch_df), n_streams=len(vod_df), max_items=max_items,
                source="Chzzk 비공식 API (channels/videos)", tz="Asia/Seoul")
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: 멤버 {len(ch_df)}명 / 방송 {len(vod_df)}개 -> {DATA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=300, help="멤버당 최대 VOD 수집 수")
    collect(ap.parse_args().max)
