"""
치지직 전체 방송 시청자 흐름 + 버튜버 명단 시청자 — 지금부터 쌓는 시계열(과거 소급 불가).

두 가지를 한 번에 잰다.
 1) 치지직 인기순 생방 상위 N개의 동시시청자 합계 — "치지직 전체"의 대리 지표(전체 목록은 받을 수 없어 상위 N 만).
    버튜버 후보(제목·태그에 버튜버/버츄얼/vtuber 가 든 방송)의 합계와 개수도 같이 남긴다.
 2) collect/vtuber_roster.csv 에 **운영자가 확인해 올린** 채널의 동시시청자.
    스텔라이브 15명은 08 이 이미 재므로 여기에 넣지 않는다(분석에서 08 과 합친다).

버튜버 기준(PRD 데이터 원칙): 제목·태그로 자동 분류한 값은 **후보**일 뿐 집계에 넣지 않는다.
  집계는 명단(roster)에 있는 사람만 센다. 후보는 data/vtuber_candidates.csv 에 쌓이고, 운영자가 확인해 명단에 옮긴다.
  이세계아이돌·홀로라이브는 치지직이 아니라 숲(SOOP)·유튜브가 주 무대라 치지직 명단에서 확인되지 않았다(2026-11-07 검색).

산출(collect/data/):
  chzzk_total.csv       collected_at, top_n, total_ccu, vtuber_candidate_n, vtuber_candidate_ccu
  vtuber_ccu.csv        collected_at, group, name, chzzk_id, is_live, ccu       (명단 채널)
  vtuber_candidates.csv channel_id, channel_name, first_seen, last_seen, last_ccu, sample_tags, sample_title
사용: python collect/chzzk_vtubers.py            (한 번 측정)   --pages 10 (상위 500개, 기본)
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common.chzzk import Chzzk, normalize_live_status  # noqa: E402

DATA = HERE / "data"
ROSTER = HERE / "vtuber_roster.csv"
CAND_RE = re.compile(r"버튜버|버츄얼|vtuber|virtual|v-?tuber", re.I)


def top_lives(api: Chzzk, pages: int) -> list[dict]:
    out, params = [], {"size": 50, "sortType": "POPULAR"}
    for _ in range(pages):
        c = api._get("/service/v1/lives", params)
        out += c.get("data", [])
        nxt = (c.get("page") or {}).get("next")
        if not nxt:
            break
        params = {"size": 50, "sortType": "POPULAR", **nxt}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pages", type=int, default=10)
    a = ap.parse_args()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.mkdir(exist_ok=True)
    api = Chzzk()

    lives = top_lives(api, a.pages)
    cand = []
    for x in lives:
        text = " ".join([x.get("liveTitle") or "", " ".join(x.get("tags") or []), x.get("liveCategoryValue") or ""])
        if CAND_RE.search(text):
            ch = x.get("channel") or {}
            cand.append({"channel_id": ch.get("channelId"), "channel_name": ch.get("channelName"), "last_ccu": x.get("concurrentUserCount", 0),
                         "sample_tags": "|".join(x.get("tags") or []), "sample_title": x.get("liveTitle")})
    total = pd.DataFrame([{"collected_at": now, "top_n": len(lives), "total_ccu": sum(x.get("concurrentUserCount", 0) for x in lives),
                           "vtuber_candidate_n": len(cand), "vtuber_candidate_ccu": sum(c["last_ccu"] for c in cand)}])
    p = DATA / "chzzk_total.csv"
    pd.concat([pd.read_csv(p), total], ignore_index=True).to_csv(p, index=False, encoding="utf-8-sig") if p.exists() \
        else total.to_csv(p, index=False, encoding="utf-8-sig")

    cp = DATA / "vtuber_candidates.csv"
    old = pd.read_csv(cp) if cp.exists() else pd.DataFrame(columns=["channel_id", "channel_name", "first_seen", "last_seen", "last_ccu", "sample_tags", "sample_title"])
    first = dict(zip(old["channel_id"], old["first_seen"]))
    new = pd.DataFrame([{**c, "first_seen": first.get(c["channel_id"], now), "last_seen": now} for c in cand],
                       columns=old.columns)
    keep = old[~old["channel_id"].isin(new["channel_id"])]
    pd.concat([keep, new], ignore_index=True).sort_values("last_ccu", ascending=False).to_csv(cp, index=False, encoding="utf-8-sig")

    roster = pd.read_csv(ROSTER) if ROSTER.exists() else pd.DataFrame(columns=["group", "name", "chzzk_id", "note"])
    rows = []
    for r in roster.itertuples():
        try:
            st = normalize_live_status(api.live_status(r.chzzk_id))
        except RuntimeError as e:        # 채널이 사라졌거나 ID 오류 — 삼키지 않고 알린다
            print(f"  명단 {r.name}({r.chzzk_id}) 실패: {e}")
            continue
        rows.append({"collected_at": now, "group": r.group, "name": r.name, "chzzk_id": r.chzzk_id,
                     "is_live": bool(st.get("is_live")), "ccu": st.get("concurrent_users")})
    if rows:
        vp = DATA / "vtuber_ccu.csv"
        df = pd.DataFrame(rows)
        pd.concat([pd.read_csv(vp), df], ignore_index=True).to_csv(vp, index=False, encoding="utf-8-sig") if vp.exists() \
            else df.to_csv(vp, index=False, encoding="utf-8-sig")
    print(f"상위 {len(lives)}개 방송 합계 {int(total['total_ccu'].iloc[0]):,}명 · 버튜버 후보 {len(cand)}개 · 명단 {len(rows)}명 측정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
