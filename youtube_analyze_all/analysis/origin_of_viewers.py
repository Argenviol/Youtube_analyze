"""
질문: 4기(특히 메리·히요리) 데뷔 시청자는 어디서 왔나?

쓰는 자료(전부 이 저장소 안, 새 호출 없음):
  08 snapshots.csv     팔로워·동시시청자 (10분 간격, 2026-08-12~)
  08 sessions.csv      방송 세션별 피크
  collect/data/chatters/<video_no>.txt   방송별 채팅·후원 참여자 해시 (collect/chzzk_chat.py)
  collect/data/chat_videos.csv           방송별 채팅·후원 합계

방법 — 채팅 참여자 겹침(overlap)으로 세 덩어리를 가른다.
  ① 4기 사전 팔로워 이동 : 다른 4기 멤버의 데뷔 방송에도 채팅한 사람
  ② 기존 스텔라이브 팬   : 비교군(기존 멤버의 데뷔 전 한 달 인기 방송)에서 채팅한 적 있는 사람
  ③ 처음 보이는 사람     : 위 둘 어디서도 안 보인 사람
한계(결론에 그대로 적는다):
  - 참여자는 채팅한 사람이지 시청자 전체가 아니다. 눈팅 시청자는 못 잰다.
  - 비교군은 멤버당 방송 N개 표본이라 ②는 하한, ③은 상한이다.
  - 다시보기 채팅은 초당 ~20건까지만 저장돼 데뷔 방송 5개가 모두 저장 한도에 붙어 있다. 참여자 수도 하한이고,
    비율은 저장된 채팅 안에서의 값이다.
  - ③ 은 "스텔라이브 밖에서 왔다"가 아니라 "표본 밖에서 처음 보였다"이다. 치지직 안의 다른 방송에서 넘어왔는지,
    치지직 밖(유튜브·트위터 유입)인지는 이 자료로 가를 수 없다.
산출: analysis/out/origin_of_viewers.md · origin_of_viewers.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
OUT = HERE / "out"
CHAT = ROOT / "collect" / "data"
LIVE = ROOT / "08_live_viewership" / "data"
DEBUT_END = "2026-10-19"          # 이 날짜 전에 게시된 4기 VOD = 데뷔 방송
CONTROL_BEFORE = "2026-10-17"


def users(video_no: int) -> set[str]:
    p = CHAT / "chatters" / f"{video_no}.txt"
    return set(p.read_text(encoding="utf-8").split()) if p.exists() else set()


def follower_table(snap: pd.DataFrame, debut_start: dict[str, pd.Timestamp]) -> pd.DataFrame:
    rows = []
    for name, g in snap.groupby("name_ko"):
        g = g.sort_values("t")
        d0 = debut_start[name]

        def at(days: float):
            x = g[g["t"] <= d0 + pd.Timedelta(days=days)]
            return int(x["followers"].iloc[-1]) if len(x) else None
        rows.append({"name_ko": name, "first_seen": int(g["followers"].iloc[0]), "debut_start": at(0),
                     "d1": at(1), "d3": at(3), "d7": at(7), "d14": at(14), "latest": int(g["followers"].iloc[-1])})
    return pd.DataFrame(rows)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    vids = pd.read_csv(CHAT / "chat_videos.csv")
    streams = pd.read_csv(ROOT / "03_chzzk_stream_pattern" / "data" / "streams.csv")
    meta = streams.set_index("video_no")
    vids["unit"] = vids["video_no"].map(meta["unit"])
    debut = vids[(vids["unit"] == "ABYSS") & (vids["publish_date"] < DEBUT_END)]
    control = vids[(vids["unit"] != "ABYSS") & (vids["publish_date"] < CONTROL_BEFORE)]
    if debut.empty or control.empty:
        print("데뷔 방송 또는 비교군 채팅이 아직 수집되지 않았다 — collect/chzzk_chat.py --abyss-debut / --control 먼저")
        return 1

    ctrl_users = set().union(*[users(v) for v in control["video_no"]])
    rows = []
    for r in debut.itertuples():
        me = users(r.video_no)
        others4 = set().union(*[users(v) for v in debut["video_no"] if v != r.video_no])
        a = me & others4
        b = (me - a) & ctrl_users
        c = me - a - b
        n = max(len(me), 1)
        rows.append({"name_ko": f"{r.name_ko} · {r.title[:14]}", "title": r.title, "chat_participants": len(me), "chats": r.chats,
                     "donations": r.donations, "from_other_abyss": len(a), "existing_fans": len(b), "not_seen_elsewhere": len(c),
                     "share_other_abyss": len(a) / n, "share_existing": len(b) / n, "share_new": len(c) / n})
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "origin_of_viewers.csv", index=False, encoding="utf-8-sig")

    snap = pd.read_csv(LIVE / "snapshots.csv", usecols=["collected_at", "name_ko", "unit", "followers"])
    snap = snap[snap["unit"] == "ABYSS"].assign(t=lambda d: pd.to_datetime(d["collected_at"], utc=True, format="ISO8601"))
    sess = pd.read_csv(LIVE / "sessions.csv")
    sess = sess[sess["unit"] == "ABYSS"].sort_values("start_kst")
    first = sess.groupby("name_ko").head(1).set_index("name_ko")
    starts = {n: pd.Timestamp(first.loc[n, "start_kst"], tz="Asia/Seoul").tz_convert("UTC") for n in first.index}
    ft = follower_table(snap, starts)
    prev_peak = pd.read_csv(LIVE / "sessions.csv")
    prev_peak = prev_peak[(prev_peak["unit"] != "ABYSS") & (prev_peak["start_kst"] < "2026-10-17")]["peak_ccu"].max()

    L = ["# 4기 데뷔 시청자는 어디서 왔나", "",
         f"기준: 채팅 다시보기 수집분. 데뷔 방송 {len(debut)}개, 비교군 방송 {len(control)}개"
         f"(기존 멤버 {control['name_ko'].nunique()}명). 숫자는 모두 스크립트가 계산했다.", "",
         "## 1. 데뷔 전에 이미 있던 팔로워", "",
         "| 멤버 | 수집 첫 시점 | 데뷔 방송 시작 | +1일 | +3일 | +7일 | +14일 | 지금 |", "|---|---|---|---|---|---|---|---|"]
    for r in ft.itertuples():
        L.append(f"| {r.name_ko} | {r.first_seen:,} | {r.debut_start:,} | {r.d1:,} | {r.d3:,} | {r.d7:,} | {r.d14:,} | {r.latest:,} |"
                 if all(x is not None for x in (r.debut_start, r.d1, r.d3, r.d7, r.d14)) else
                 f"| {r.name_ko} | {r.first_seen:,} | {r.debut_start or '—'} | {r.d1 or '—'} | {r.d3 or '—'} | {r.d7 or '—'} | {r.d14 or '—'} | {r.latest:,} |")
    L += ["", f"4기 데뷔 전 기존 멤버 방송의 최고 피크는 {int(prev_peak):,}명이다(08 수집 기간).", "",
          "## 2. 채팅 참여자 겹침", "",
          "| 방송 | 채팅 참여자 | 채팅 | 후원(건) | 다른 4기 방송에도 | 기존 스텔라이브 방송에도 | 표본 어디서도 처음 |", "|---|---|---|---|---|---|---|"]
    for r in res.itertuples():
        L.append(f"| {r.name_ko} | {r.chat_participants:,} | {r.chats:,} | {r.donations:,} | "
                 f"{r.from_other_abyss:,} ({r.share_other_abyss:.0%}) | {r.existing_fans:,} ({r.share_existing:.0%}) | "
                 f"**{r.not_seen_elsewhere:,} ({r.share_new:.0%})** |")
    solo = res[~res["title"].str.contains("단체")]
    gr = ft.assign(x=lambda d: d["debut_start"] / d["first_seen"])
    L += ["", "## 3. 숫자가 말하는 것", "",
          f"- 데뷔 방송 {len(solo)}개의 채팅 참여자 중 **{solo['share_other_abyss'].min():.0%}~{solo['share_other_abyss'].max():.0%}** 가 "
          "다른 4기 데뷔 방송에도 채팅했다 — 4기 네 명을 같이 보러 온 하나의 관객층이다.",
          f"- 기존 스텔라이브 방송(비교군)에서도 보인 사람은 **{solo['share_existing'].min():.0%}~{solo['share_existing'].max():.0%}** 뿐이다"
          "(하한 — 비교군이 표본이라 실제는 더 클 수 있다).",
          f"- 4기 방송에만 보이는 사람은 {solo['share_new'].min():.0%}~{solo['share_new'].max():.0%} 이다.",
          f"- 데뷔 방송이 시작될 때 이미 팔로워가 수집 첫 시점의 {gr['x'].min():.1f}~{gr['x'].max():.1f}배였다 — 방송 전 티저 단계에서 쌓였다."]
    L += ["", "## 읽는 법과 한계", "",
          "- 참여자는 채팅·후원한 사람만이다. 눈팅 시청자는 이 자료로 못 잰다.",
          "- 비교군은 멤버당 방송 일부라 '기존 팬'은 하한, '처음 보임'은 상한이다.",
          "- 다시보기 채팅은 초당 약 20건까지만 저장된다. 4기 데뷔 방송은 모두 이 한도에 붙어 있어 참여자·채팅 수는 하한이고, 비율은 저장된 채팅 안에서의 값이다.",
          "- '처음 보임'은 스텔라이브 밖에서 왔다는 뜻이 아니다. 치지직의 다른 방송에서 넘어왔는지, 치지직 밖(유튜브·트위터·커뮤니티)에서 "
          "왔는지는 가를 수 없다 — 치지직 전체 방송 시청자 시계열이 없고(수집 시작 전), 유입 경로는 치지직이 공개하지 않는다.",
          "- 팔로워 표의 '수집 첫 시점'은 데뷔 전 티저로 쌓인 사전 팔로워다."]
    (OUT / "origin_of_viewers.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
