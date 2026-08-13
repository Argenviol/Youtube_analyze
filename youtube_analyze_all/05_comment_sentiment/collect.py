"""
프로젝트5 · 수집 단계
멤버별 인기 영상에서 상위 댓글을 수집한다.
감성/토픽 라벨링(label.py)의 원천 데이터.

  export YOUTUBE_API_KEY=...
  python 05_comment_sentiment/collect.py [--videos-per-member 4] [--comments-per-video 40]
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


def collect(videos_per_member: int = 4, comments_per_video: int = 40) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    yt = YouTube(config.get_api_key())
    roster = config.member_rows()

    video_rows, comment_rows = [], []
    for m in roster:
        uploads = yt.channels([m["channel_id"]])[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        vids = yt.playlist_video_ids(uploads, limit=30)
        details = yt.videos(vids)
        details.sort(key=lambda v: to_int(v.get("statistics", {}).get("viewCount")) or 0, reverse=True)
        top = details[:videos_per_member]
        print(f"  {m['name_ko']:12} 대상 영상 {len(top)}개")
        for v in top:
            vsnip = v["snippet"]
            video_rows.append(dict(
                video_id=v["id"], name_ko=m["name_ko"], name_en=m["name_en"], unit=m["unit"],
                title=vsnip.get("title"), views=to_int(v.get("statistics", {}).get("viewCount")),
            ))
            threads = yt.comment_threads(v["id"], limit=comments_per_video, order="relevance")
            for t in threads:
                top_c = t["snippet"]["topLevelComment"]["snippet"]
                # 작성자(authorDisplayName)는 수집하지 않는다. 감성·토픽 집계는 전부
                # 멤버 단위라 작성자가 필요 없는데, 저장하면 공개 저장소에 핸들과 댓글
                # 원문이 묶인 데이터셋이 남는다. 분석에 안 쓰는 개인 식별자는 애초에
                # 받아두지 않는 쪽이 맞다.
                comment_rows.append(dict(
                    comment_id=t["id"], video_id=v["id"],
                    name_ko=m["name_ko"], name_en=m["name_en"], unit=m["unit"],
                    text=top_c.get("textDisplay"),
                    like_count=to_int(top_c.get("likeCount")),
                    published_at=top_c.get("publishedAt"),
                ))

    vdf = pd.DataFrame(video_rows)
    cdf = pd.DataFrame(comment_rows)
    # 너무 짧은(이모지/1~2글자) 댓글 제외 - 감성 분석 신뢰도 낮음
    cdf["text_len"] = cdf["text"].fillna("").str.replace(r"<.*?>", "", regex=True).str.strip().str.len()
    cdf = cdf[cdf["text_len"] >= 4].reset_index(drop=True)

    vdf.to_csv(DATA / "target_videos.csv", index=False)
    cdf.to_csv(DATA / "comments_raw.csv", index=False)
    meta = dict(fetched_at=datetime.now(timezone.utc).isoformat(),
                n_videos=len(vdf), n_comments=len(cdf),
                videos_per_member=videos_per_member, comments_per_video=comments_per_video,
                source="YouTube Data API v3 (commentThreads, order=relevance)")
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: 영상 {len(vdf)}개 / 댓글 {len(cdf)}개 -> {DATA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos-per-member", type=int, default=4)
    ap.add_argument("--comments-per-video", type=int, default=40)
    a = ap.parse_args()
    collect(a.videos_per_member, a.comments_per_video)
