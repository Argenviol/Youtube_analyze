"""
멤버 채널 최근 업로드의 조회수 일일 스냅샷 — 쇼츠가 업로드 뒤 며칠 동안 어떻게 크는지 쌓는다(과거 소급 불가).

API 키·쿼터 없이 유튜브 웹(innertube)에서 받는다(member_views 와 같은 방법). 멤버마다 최근 업로드 N개의
조회수·업로드일·쇼츠 여부를 매일 한 줄씩 남긴다. 쌓이면 '업로드 후 N일 조회수'로 형식을 같은 조건에서 비교할 수 있다.

산출: collect/data/shorts_views.csv  (collected_at, member, video_id, title, shorts, published, views)
사용: python collect/shorts_snapshot.py --recent 30
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "member_views"))
from common import config  # noqa: E402
import member_views as mv  # noqa: E402

OUT = HERE / "data" / "shorts_views.csv"


def recent_uploads(channel_id: str, n: int) -> list[dict]:
    """업로드 재생목록 앞쪽 n개(최신순). member_views.list_uploads 와 같은 파싱, 첫 페이지들만."""
    seen, out, body = set(), [], {"browseId": "VLUU" + channel_id[2:]}

    def walk(o):
        if isinstance(o, dict):
            lv = o.get("lockupViewModel")
            if lv and lv.get("contentId") and lv["contentId"] not in seen:
                seen.add(lv["contentId"])
                title = lv.get("metadata", {}).get("lockupMetadataViewModel", {}).get("title", {}).get("content", "")
                out.append({"id": lv["contentId"], "title": title})
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    while body and len(out) < n:
        s = mv._post("browse", body)
        walk(json.loads(s))
        tok = re.findall(r'"continuationItemViewModel".{0,1500}?"token":"([^"]+)"', s)
        body = {"continuation": tok[0]} if tok else None
    return out[:n]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recent", type=int, default=30, help="멤버마다 최근 업로드 N개")
    a = ap.parse_args()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows, failed = [], 0
    with cf.ThreadPoolExecutor(6) as ex:
        for m in config.member_rows():
            if m["role"] == "founder":
                continue
            items = recent_uploads(m["channel_id"], a.recent)
            for r in ex.map(mv.video_info, items):
                if r["views"] is None:        # 일시 실패는 세어서 알린다(삼키지 않는다)
                    failed += 1
                    continue
                rows.append({"collected_at": now, "member": m["name_ko"], "video_id": r["id"], "title": r["title"],
                             "shorts": r["shorts"], "published": r["date"], "views": r["views"]})
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(exist_ok=True)
    pd.concat([pd.read_csv(OUT), df], ignore_index=True).to_csv(OUT, index=False, encoding="utf-8-sig") if OUT.exists() \
        else df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"{len(df)}개 영상 조회수 기록(쇼츠 {int((df['shorts'] == 1).sum())}개) · 실패 {failed}")
    return 0 if failed <= len(df) // 5 else 1     # 실패가 20% 넘으면 잡을 빨갛게


if __name__ == "__main__":
    sys.exit(main())
