"""
프로젝트6 · 수집 단계 — 데뷔 코호트 매칭 비교

StelLive 탤런트 전원 + 데뷔 시기가 겹치는 홀로라이브 기수 + 이세계아이돌을
같은 규격으로 수집한다. 누구를 넣을지는 common/config.py 의 COMPETITOR_ROSTER 가
정본이고, 여기서는 "기수 전원"이라는 원칙만 지킨다 — 유명한 사람만 골라 담으면
그 표본 자체가 생존편향이 된다.

이전 버전과 달라진 점:
  · StelLive 를 앞에서 6명만 자르지 않는다(로스터 순서대로 잘려서 CLICHE 4명이
    통째로 빠져 있었다). 탤런트 10명 전원을 넣는다.
  · 홀로라이브 표본을 인지도 기준(페코라·구라·마린…)에서 데뷔 시기 기준으로 바꿨다.
  · 채널 행에 debut_date/generation/cohort 를 같이 저장한다 — 분석 단계에서
    데뷔일을 다시 추측하지 않게 하기 위해서다.

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
    """비교 대상 전원. StelLive 는 탤런트 전원(창립자 제외)."""
    rows = [dict(group="StelLive", name_ko=m["name_ko"], name_en=m["name_en"],
                 channel_id=m["channel_id"], debut_date=m["debut_date"],
                 generation=m["generation"], cohort=m["cohort"])
            for m in config.member_rows() if m["role"] == "talent"]
    rows += config.competitor_rows()
    return rows


def collect(recent: int = 30) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    yt = YouTube(config.get_api_key())
    people = roster()
    ch_items = {c["id"]: c for c in yt.channels([p["channel_id"] for p in people])}

    ch_rows, vid_rows, missing = [], [], []
    for p in people:
        c = ch_items.get(p["channel_id"])
        if not c:
            # 조용히 건너뛰면 표본이 줄어든 걸 아무도 모른다. 메타에 남긴다.
            missing.append(p["name_ko"])
            print(f"  ! {p['name_ko']} 채널 응답 없음")
            continue
        stats, snip = c.get("statistics", {}), c.get("snippet", {})
        uploads = c["contentDetails"]["relatedPlaylists"]["uploads"]
        ch_rows.append(dict(
            group=p["group"], cohort=p["cohort"], generation=p["generation"],
            debut_date=p["debut_date"],
            channel_id=p["channel_id"], name_ko=p["name_ko"], name_en=p["name_en"],
            subscribers=to_int(stats.get("subscriberCount")),
            total_views=to_int(stats.get("viewCount")),
            video_count=to_int(stats.get("videoCount")),
            created_at=snip.get("publishedAt"),
        ))
        vids = yt.playlist_video_ids(uploads, limit=recent)
        details = yt.videos(vids)
        print(f"  [{p['group']:8}|{str(p['cohort']):14}] {p['name_ko']:14} "
              f"구독 {str(stats.get('subscriberCount')):>10} · 영상 {len(details)}개")
        for v in details:
            vs, vsnip = v.get("statistics", {}), v.get("snippet", {})
            vid_rows.append(dict(
                video_id=v["id"], channel_id=p["channel_id"], group=p["group"],
                cohort=p["cohort"], name_ko=p["name_ko"], name_en=p["name_en"],
                title=vsnip.get("title"), published_at=vsnip.get("publishedAt"),
                views=to_int(vs.get("viewCount")), likes=to_int(vs.get("likeCount")),
                comments=to_int(vs.get("commentCount")),
            ))

    ch_df, vid_df = pd.DataFrame(ch_rows), pd.DataFrame(vid_rows)
    ch_df.to_csv(DATA / "channels.csv", index=False)
    vid_df.to_csv(DATA / "videos.csv", index=False)

    by_cohort = (ch_df.groupby(["cohort", "group"]).size()
                 .reset_index(name="n").to_dict(orient="records"))
    meta = dict(
        fetched_at=datetime.now(timezone.utc).isoformat(),
        n_channels=len(ch_df), n_videos=len(vid_df), recent_per_channel=recent,
        groups=sorted(ch_df["group"].unique().tolist()),
        cohorts=sorted(x for x in ch_df["cohort"].dropna().unique().tolist()),
        cohort_composition=by_cohort,
        missing_channels=missing,
        source="YouTube Data API v3",
        sampling="데뷔 코호트 매칭 — 기수 전원 수집(개인 인지도로 고르지 않음)",
        method="debut_cohort_matched",
        method_changed_at="2026-09-18",
        method_note=("이전에는 홀로라이브 대표 6명(2019~2020 데뷔)과 StelLive 6명"
                     "(2023~2025 데뷔)을 비교했다. 구독자 격차의 대부분이 데뷔 시기 "
                     "차이로 설명되는 구조라 그룹 비교로 쓸 수 없었다. 이 시점 이전 "
                     "스냅샷과 그룹 평균을 직접 비교하지 말 것."),
    )
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    print(f"\n완료: 채널 {len(ch_df)}개 / 영상 {len(vid_df)}개 -> {DATA}")
    if missing:
        print(f"  ! 응답 없는 채널 {len(missing)}개: {', '.join(missing)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--recent", type=int, default=30)
    collect(ap.parse_args().recent)
