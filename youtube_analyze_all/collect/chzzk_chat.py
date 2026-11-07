"""
치지직 다시보기(VOD) 채팅 다시보기 수집 — 분당 채팅 수 · 후원 건수 · 채팅 참여자.

엔드포인트: /service/v1/videos/{videoNo}/chats?playerMessageTime=<ms>
  - 한 번에 200건, nextPlayerMessageTime 으로 이어 받는다(끝이면 null).
  - messageTypeCode: 1 일반 채팅 · 10 후원 · 11 구독 · 그 외(30 모드 안내 등)는 기타.
  - 후원 금액(payAmount)은 다시보기에서 **항상 0** 으로 온다(2026-11-06 Mary 데뷔 VOD 885건 전부 0).
    그래서 금액은 구할 수 없고 건수만 센다. weeklyRankList 의 donationAmount 는 주간 누적이라 한 건의 금액이 아니다.
  - ⚠ 포화: 다시보기에는 채팅이 **초당 약 20건(분당 ~1,240)까지만** 저장된다. 4기 데뷔 방송 5개가 모두 분당 ~1,200건에 붙어 있다
    (분의 91~97% 가 1,150 이상, 최대 1,244). 그런 방송의 채팅 수·참여자 수는 하한이다.
  - 닉네임·채팅 본문은 저장하지 않는다. 참여자는 userIdHash(익명 해시)만 남긴다.

산출물(collect/data/):
  chat_minutes.csv   video_no, minute, chats, donations, subs, unique_chatters
  chat_videos.csv    video_no, name_ko, title, publish_date, duration_sec, chats, donations, subs, unique_chatters, collected_at
  chatters/<video_no>.txt   그 방송에서 채팅·후원한 userIdHash (한 줄에 하나)
  chat_user_hours.csv       video_no, hour, user, chats, donations — **시청자(고유 id)별로 방송 한 시간 동안 친 채팅 수·후원 건수**
                            (hour = 방송 시작 후 몇 번째 시간인가, 0부터. 내용은 저장하지 않고 개수만 합한다)

사용:
  python collect/chzzk_chat.py --abyss-debut          # 4기 데뷔 방송 4개 + 첫 단체 합방
  python collect/chzzk_chat.py --video 15741625
  python collect/chzzk_chat.py --member "토키노 메리" --first 20   # 그 멤버의 가장 오래된 N개
  python collect/chzzk_chat.py --control 2026-10-17 --per-member 2  # 비교군: 기존 멤버의 데뷔 전 한 달 인기 방송
  python collect/chzzk_chat.py --recent 8 --unit ABYSS --max 12     # 최근 8일 4기 방송 중 아직 안 받은 것(주간 자동 실행)
이미 받은 영상은 건너뛴다(--force 로 다시 받기).
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common.chzzk import Chzzk  # noqa: E402

DATA = HERE / "data"
STREAMS = ROOT / "03_chzzk_stream_pattern" / "data" / "streams.csv"
MINUTES = DATA / "chat_minutes.csv"
USER_HOURS = DATA / "chat_user_hours.csv"
VIDEOS = DATA / "chat_videos.csv"
CHAT, DONATION, SUB = 1, 10, 11
PAUSE = 0.15          # 호출 사이 대기(초) — 치지직 비공식 API 를 몰아치지 않는다


def fetch_video(api: Chzzk, video_no: int) -> tuple[pd.DataFrame, set[str], dict, pd.DataFrame]:
    """한 VOD 의 채팅 전량을 받아 분 단위로 집계한다. 끝나면 (분표, 참여자 집합, 합계)."""
    minutes: dict[int, dict] = defaultdict(lambda: {"chats": 0, "donations": 0, "subs": 0, "users": set()})
    uh: dict[tuple[int, str], list[int]] = defaultdict(lambda: [0, 0])      # (시간, 시청자 해시) → [채팅, 후원]
    t, calls, last_t = 0, 0, -1
    while True:
        c = api._get(f"/service/v1/videos/{video_no}/chats", {"playerMessageTime": t})
        calls += 1
        for m in c.get("videoChats", []):
            row = minutes[int(m.get("playerMessageTime", 0)) // 60000]
            code = m.get("messageTypeCode")
            if code == CHAT:
                row["chats"] += 1
            elif code == DONATION:
                row["donations"] += 1
            elif code == SUB:
                row["subs"] += 1
            else:
                continue
            if m.get("userIdHash"):
                row["users"].add(m["userIdHash"])
                cell = uh[(int(m.get("playerMessageTime", 0)) // 3600000, m["userIdHash"])]
                if code == DONATION:
                    cell[1] += 1
                elif code == CHAT:
                    cell[0] += 1
        nxt = c.get("nextPlayerMessageTime")
        if nxt is None or nxt <= last_t:       # 끝이거나 커서가 멈췄다
            break
        last_t, t = t, nxt
        time.sleep(PAUSE)
    rows = [{"video_no": video_no, "minute": m, "chats": v["chats"], "donations": v["donations"],
             "subs": v["subs"], "unique_chatters": len(v["users"])} for m, v in sorted(minutes.items())]
    users = set().union(*[v["users"] for v in minutes.values()]) if minutes else set()
    total = {"chats": sum(r["chats"] for r in rows), "donations": sum(r["donations"] for r in rows),
             "subs": sum(r["subs"] for r in rows), "unique_chatters": len(users), "calls": calls}
    uhdf = pd.DataFrame([{"video_no": video_no, "hour": h, "user": u, "chats": c[0], "donations": c[1]}
                         for (h, u), c in sorted(uh.items())])
    return pd.DataFrame(rows), users, total, uhdf


def pick(streams: pd.DataFrame, a: argparse.Namespace) -> pd.DataFrame:
    if a.video:
        return streams[streams["video_no"].isin(a.video)]
    if a.abyss_debut:
        ab = streams[(streams["unit"] == "ABYSS") & (streams["publish_date"] < "2026-10-19")]
        return ab.sort_values("publish_date")
    if a.recent:
        lo = (pd.Timestamp.now() - pd.Timedelta(days=a.recent)).strftime("%Y-%m-%d")
        s = streams[(streams["publish_date"] >= lo) & (streams["duration_sec"] <= 8 * 3600)]
        if a.unit:
            s = s[s["unit"] == a.unit]
        return s.sort_values("publish_date")
    if a.control:
        lo = (pd.Timestamp(a.control) - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
        s = streams[(streams["unit"] != "ABYSS") & (streams["publish_date"] >= lo) & (streams["publish_date"] < a.control)
                    & (streams["duration_sec"] <= 8 * 3600)]
        s = s.sort_values("read_count", ascending=False).groupby("name_ko").head(a.per_member)
        return s.sort_values("publish_date")
    if a.member:
        s = streams[streams["name_ko"] == a.member].sort_values("publish_date")
        return s.head(a.first)
    raise SystemExit("--video / --abyss-debut / --member / --control / --recent 중 하나가 필요하다")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", type=int, nargs="+")
    ap.add_argument("--abyss-debut", action="store_true")
    ap.add_argument("--member")
    ap.add_argument("--first", type=int, default=10)
    ap.add_argument("--control", help="이 날짜(YYYY-MM-DD) 전 30일의 기존 멤버 방송 중 조회수 상위 --per-member 개")
    ap.add_argument("--per-member", type=int, default=2)
    ap.add_argument("--recent", type=int, help="최근 N일에 게시된 방송")
    ap.add_argument("--unit", help="--recent 와 함께: 소속(예: ABYSS)")
    ap.add_argument("--max", type=int, help="이번 실행에서 새로 받을 최대 방송 수")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    streams = pd.read_csv(STREAMS)
    todo = pick(streams, a)
    DATA.mkdir(exist_ok=True)
    (DATA / "chatters").mkdir(exist_ok=True)
    done = pd.read_csv(VIDEOS) if VIDEOS.exists() else pd.DataFrame()
    minutes_all = pd.read_csv(MINUTES) if MINUTES.exists() else pd.DataFrame()
    uh_all = pd.read_csv(USER_HOURS) if USER_HOURS.exists() else pd.DataFrame()
    have_uh = set(uh_all["video_no"]) if len(uh_all) else set()       # 시청자별 시간 집계가 있는 방송
    api = Chzzk()
    fetched = 0
    for r in todo.itertuples():
        if a.max and fetched >= a.max:
            print(f"  --max {a.max} 도달 — 나머지는 다음 실행에서")
            break
        if not a.force and len(done) and r.video_no in set(done["video_no"]) and r.video_no in have_uh:
            print(f"  건너뜀 {r.video_no} (이미 있음)")
            continue
        try:
            mdf, users, tot, uhdf = fetch_video(api, int(r.video_no))
        except RuntimeError as e:        # 삭제·비공개 VOD 등 — 삼키지 않고 기록하고 다음으로
            print(f"  실패 {r.video_no} {r.name_ko}: {e}")
            continue
        fetched += 1
        (DATA / "chatters" / f"{r.video_no}.txt").write_text("\n".join(sorted(users)) + "\n", encoding="utf-8")
        minutes_all = pd.concat([minutes_all[minutes_all["video_no"] != r.video_no] if len(minutes_all) else minutes_all, mdf],
                                ignore_index=True)
        rec = {"video_no": r.video_no, "name_ko": r.name_ko, "title": r.title, "publish_date": r.publish_date,
               "duration_sec": r.duration_sec, **{k: tot[k] for k in ("chats", "donations", "subs", "unique_chatters")},
               "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        done = pd.concat([done[done["video_no"] != r.video_no] if len(done) else done, pd.DataFrame([rec])], ignore_index=True)
        uh_all = pd.concat([uh_all[uh_all["video_no"] != r.video_no] if len(uh_all) else uh_all, uhdf], ignore_index=True)
        have_uh.add(r.video_no)
        uh_all.to_csv(USER_HOURS, index=False, encoding="utf-8-sig")
        minutes_all.to_csv(MINUTES, index=False, encoding="utf-8-sig")   # 영상마다 저장 — 중간에 끊겨도 남는다
        done.to_csv(VIDEOS, index=False, encoding="utf-8-sig")
        print(f"  {r.video_no} {r.name_ko} 채팅 {tot['chats']:,} · 후원 {tot['donations']:,} · "
              f"참여자 {tot['unique_chatters']:,} ({tot['calls']}회 호출)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
