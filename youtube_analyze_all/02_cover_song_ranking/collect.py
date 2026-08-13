"""
프로젝트2 · 수집 단계
StelLive 멤버 채널의 커버곡 영상을 **전량 열거**해 수집한다.
업로드 재생목록 전체 → 제목 필터로 커버 확정 → 영상 상세 지표.

  set YOUTUBE_API_KEY=...
  python 02_cover_song_ranking/collect.py [--max-videos 3000]

## 수집 방식을 바꾼 이유 (2026-08-12)

이전에는 멤버당 3개 쿼리로 search.list 를 돌렸다. 그 방식에는 두 가지 문제가 있었다.

1. **결과가 불안정하다.** search.list 는 order="relevance" 기준 상위 N개만 준다.
   따라서 잡히는 커버곡은 "그 채널의 커버곡 전체"가 아니라 "관련도 상위 40개 창에
   들어온 커버곡"이었다. 실제로 재수집했더니 한 멤버가 34개 → 29개로 줄었는데,
   영상이 삭제된 게 아니라 검색 랭킹이 흔들려 창 밖으로 밀린 것이었다.
   즉 이 지표는 시계열 비교에 쓸 수 없는 값이었다.

2. **비싸다.** search.list 는 호출당 100 units 다. 11명 × 3쿼리 = 3,300 units 로
   일일 한도 10,000의 3분의 1을 이 프로젝트 하나가 먹었다.

업로드 재생목록을 playlistItems 로 전량 열거하면 두 문제가 동시에 해결된다.
결과는 결정적(같은 입력이면 같은 출력)이고, 비용은 페이지(50건)당 1 unit 이다.

  이전: search 33회        = 3,300 units, 상위 40개 창, 실행마다 변동
  현재: playlistItems 수십회 =   ~100 units, 전량, 결정적

⚠ 이 변경으로 커버곡 수가 이전 수치보다 늘어난다. 방법이 달라진 것이지 급증이 아니다.
   `_archive/` 의 이전 스냅샷과 커버곡 수를 직접 비교하지 말 것.
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

# 제목에 아래 토큰이 있으면 커버로 판정. 이제 이것이 유일한 판별 기준이다
# (검색 쿼리가 사라졌으므로 재현성이 이 정규식 하나에 달려 있다).
COVER_TOKEN = re.compile(r"cover|커버|歌ってみた|うたってみた|불러[봤본]", re.IGNORECASE)


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def collect(max_videos: int = 3000) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    yt = YouTube(config.get_api_key())
    roster = config.member_rows()

    rows = []
    seen = set()
    for r in roster:
        uploads = yt.uploads_playlist_id(r["channel_id"])
        if not uploads:
            print(f"  {r['name_ko']:12} 업로드 재생목록을 찾을 수 없음 — 건너뜀")
            continue

        # 채널 전체를 열거한 뒤 제목으로 거른다. videos.list 는 후보에만 호출.
        all_videos = yt.playlist_videos(uploads, limit=max_videos)
        cand_ids = [
            v["video_id"] for v in all_videos
            if COVER_TOKEN.search(v["title"] or "") and v["video_id"] not in seen
        ]
        cand_ids = list(dict.fromkeys(cand_ids))
        seen.update(cand_ids)
        details = yt.videos(cand_ids)
        print(f"  {r['name_ko']:12} 전체 {len(all_videos):>4}개 중 커버 {len(details)}개")
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
                title_filter=COVER_TOKEN.pattern,
                source="YouTube Data API v3 (playlistItems 전량 열거 + videos)",
                method="uploads_playlist_enumeration",
                method_changed_at="2026-08-12",
                method_note=("이전에는 search.list 상위 40개 창을 썼다. 결과가 실행마다 흔들리고 "
                             "커버곡 수를 과소집계해 시계열 비교가 불가능했으므로 전량 열거로 교체했다. "
                             "이 시점 이전 스냅샷과 커버곡 수를 직접 비교하지 말 것."))
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: 커버 {len(df)}개 / 멤버 {df['name_en'].nunique()}명 -> {DATA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-videos", type=int, default=3000,
                    help="멤버당 열거할 최대 영상 수 (채널 전체를 덮을 만큼 크게 잡는다)")
    collect(ap.parse_args().max_videos)
