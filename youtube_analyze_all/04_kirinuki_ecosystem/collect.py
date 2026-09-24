"""
프로젝트4 · 수집 단계
키리누키(2차창작 클립) 생태계 매핑.
멤버별로 "키리누키/클립/切り抜き" 영상을 검색 → 공식 채널 제외(=팬 제작) →
어떤 채널이 어느 멤버를 얼마나 다루는지 수집.

  python 04_kirinuki_ecosystem/collect.py [--per-query 40]
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
from common.youtube import QuotaExceeded, YouTube

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
# search.list 는 하루 100회 한도가 따로 있고 이 수집이 한 번에 33회를 쓴다. 같은 날 weekly 를
# 손으로 몇 번 더 돌리면 막힌다. 직전 수집이 이만큼 안쪽이면 이번 주 몫은 이미 있는 것이므로
# 실패로 치지 않고 기존 데이터를 둔다. 그보다 오래됐으면 진짜 결측이라 실패로 낸다.
FRESH_DAYS = 6
SUFFIX = ["키리누키", "클립", "切り抜き"]
# 검색 노이즈(무관한 대형 쇼츠·커버 등) 제거: 제목 또는 채널명에 키리누키/클립 토큰이 있어야 팬클립으로 인정
KIRI_TOKEN = re.compile(r"키리누키|클립|切り抜き|切りぬき|キリヌキ|kirinuki|clip", re.IGNORECASE)


def is_kirinuki(title: str, channel_title: str) -> bool:
    return bool(KIRI_TOKEN.search(title or "") or KIRI_TOKEN.search(channel_title or ""))


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def collect(per_query: int = 40) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    yt = YouTube(config.get_api_key())
    official = set(config.channel_ids()) | {config.OFFICIAL_CHANNEL[2]}

    rows, seen = [], set()
    for m in config.member_rows():
        for suf in SUFFIX:
            items = yt.search(f"{m['name_ko']} {suf}", type_="video",
                              max_results=per_query, order="relevance")
            for it in items:
                vid = it["id"]["videoId"]
                ch = it["snippet"]["channelId"]
                if ch in official or vid in seen:
                    continue
                if not is_kirinuki(it["snippet"]["title"], it["snippet"]["channelTitle"]):
                    continue
                seen.add(vid)
                rows.append(dict(
                    video_id=vid, clip_channel_id=ch,
                    clip_channel_title=it["snippet"]["channelTitle"],
                    source_member_ko=m["name_ko"], source_member_en=m["name_en"], unit=m["unit"],
                    title=it["snippet"]["title"], published_at=it["snippet"]["publishedAt"],
                ))
        print(f"  {m['name_ko']:12} 클립 후보 누적 {len(rows)}")

    df = pd.DataFrame(rows).drop_duplicates("video_id").reset_index(drop=True)

    # 영상 상세 지표
    details = {v["id"]: v for v in yt.videos(df["video_id"].tolist())}
    df["views"] = df["video_id"].map(lambda i: to_int(details.get(i, {}).get("statistics", {}).get("viewCount")))
    df["likes"] = df["video_id"].map(lambda i: to_int(details.get(i, {}).get("statistics", {}).get("likeCount")))
    df["comments"] = df["video_id"].map(lambda i: to_int(details.get(i, {}).get("statistics", {}).get("commentCount")))
    df = df.dropna(subset=["views"]).reset_index(drop=True)

    # 클립 채널 규모(구독자)
    uniq = df["clip_channel_id"].unique().tolist()
    chinfo = {c["id"]: c for c in yt.channels(uniq, part="snippet,statistics")}
    df["clip_channel_subs"] = df["clip_channel_id"].map(
        lambda c: to_int(chinfo.get(c, {}).get("statistics", {}).get("subscriberCount")))

    df.to_csv(DATA / "clips.csv", index=False)
    meta = dict(fetched_at=datetime.now(timezone.utc).isoformat(),
                n_clips=len(df), n_clip_channels=df["clip_channel_id"].nunique(),
                queries=SUFFIX, source="YouTube Data API v3 (search+videos+channels)")
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: 클립 {len(df)}개 / 팬채널 {df['clip_channel_id'].nunique()}개 -> {DATA}")


def _last_fetch_age_days() -> float | None:
    try:
        meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
        at = datetime.fromisoformat(meta["fetched_at"])
    except (OSError, KeyError, ValueError):
        return None
    return (datetime.now(timezone.utc) - at).total_seconds() / 86400


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-query", type=int, default=40)
    try:
        collect(ap.parse_args().per_query)
    except QuotaExceeded as e:
        age = _last_fetch_age_days()
        if age is not None and age < FRESH_DAYS:
            print(f"::warning::04 search 한도 소진 — {age:.1f}일 전 수집분을 그대로 둔다 ({e})")
            sys.exit(0)
        raise
