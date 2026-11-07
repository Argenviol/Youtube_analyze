"""
가설 H1~H6 검증 — 자료가 되는 만큼만 계산하고, 안 되는 것은 이유와 함께 '측정 불가/보류'로 적는다.
정의는 ../../자료_점검_및_분석계획.md 6절. 표본이 작으면(n<5) 상관·검정을 내지 않고 값만 늘어놓는다.
숫자는 전부 이 스크립트가 계산한다. 결론 문장에 멤버 이름을 붙인 순위를 쓰지 않는다(표에만 둔다).
산출: analysis/out/hypotheses.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common import config  # noqa: E402

OUT = HERE / "out"
LIVE = ROOT / "08_live_viewership" / "data"
CHAT = ROOT / "collect" / "data"
EVENTS = ROOT / "12_event_impact" / "data" / "events.csv"
FOUNDER = config.founder_names()
MIN_N = 5
SAT_PER_MIN = 1150      # 분당 채팅이 이 값 이상인 분 = 저장 한도에 붙은 분(실측 최대 ~1,244)


def _read(p: Path) -> pd.DataFrame:
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(자료 없음)"
    h = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns)
    return h + "\n" + "\n".join("| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False))


def sessions() -> pd.DataFrame:
    s = _read(LIVE / "sessions.csv")
    s = s[~s["name_ko"].isin(FOUNDER)].copy()
    s["t"] = pd.to_datetime(s["start_kst"])
    return s


# ── H1 ────────────────────────────────────────────────────────────────────────
def h1(s: pd.DataFrame) -> list[str]:
    ab = s[s["unit"] == "ABYSS"]
    debut = ab.sort_values("t").groupby("name_ko").head(1).set_index("name_ko")
    now = s["t"].max()
    rows = []
    for name, r in debut.iterrows():
        g = ab[ab["name_ko"] == name]
        row = {"멤버": name, "데뷔 방송 피크": f"{int(r['peak_ccu']):,}"}
        for k in range(1, 6):
            lo, hi = r["t"] + pd.Timedelta(days=7 * (k - 1)), r["t"] + pd.Timedelta(days=7 * k)
            w = g[(g["t"] >= lo) & (g["t"] < hi)]
            row[f"{k}주 평균 CCU"] = f"{w['avg_ccu'].mean():,.0f}" if hi <= now and len(w) else ("관측 중" if lo <= now else "미도래")
        rows.append(row)
    return ["## H1. 데뷔방송 시청자가 크면 5주 뒤에도 평균 시청자가 높다", "",
            md_table(pd.DataFrame(rows)), "",
            f"- 4기 4명(n=4)뿐이라 상관·검정은 내지 않는다(기준 n≥{MIN_N}). 5주차는 데뷔 5주 뒤({(debut['t'].max() + pd.Timedelta(days=35)).date()} 이후)에 채워진다.",
            "- 1~3기·후야 데뷔는 수집(2026-08-12) 이전이라 측정 불가.", ""]


# ── H2 ────────────────────────────────────────────────────────────────────────
def h2(s: pd.DataFrame) -> list[str]:
    ev = _read(EVENTS)
    ev = ev[(ev["type"] == "합방") & (ev["n_members"] >= 5) & (ev["date"] >= "2026-08-19")]
    now = s["t"].max()
    rows = []
    for e in ev.itertuples():
        a, b = pd.Timestamp(e.date), pd.Timestamp(e.end_date)
        pre = s[(s["t"] >= a - pd.Timedelta(days=7)) & (s["t"] < a)]
        post = s[(s["t"] >= b + pd.Timedelta(days=1)) & (s["t"] < b + pd.Timedelta(days=8))]
        if b + pd.Timedelta(days=8) > now:
            rows.append({"이벤트": f"{e.title} ({e.date}~{e.end_date})", "비고": "사후 7일이 아직 안 지남"})
            continue
        part = set(str(e.members).split("|"))
        out = {"이벤트": f"{e.title} ({e.date}~{e.end_date})"}
        for label, grp in (("참여", True), ("비참여", False)):
            ch = []
            for name in s["name_ko"].unique():
                if (name in part) != grp or name == "":
                    continue
                p0, p1 = pre[pre["name_ko"] == name]["avg_ccu"], post[post["name_ko"] == name]["avg_ccu"]
                if len(p0) >= 2 and len(p1) >= 2 and p0.mean() > 0:
                    ch.append(p1.mean() / p0.mean() - 1)
            out[f"{label} n"] = len(ch)
            out[f"{label} 중앙 변화"] = f"{pd.Series(ch).median():+.1%}" if ch else "—"
        rows.append(out)
    return ["## H2. 대규모 합방 참여 멤버는 이후 평균 시청자가 비참여자보다 더 오른다", "",
            md_table(pd.DataFrame(rows)), "",
            "- 변화 = 합방 종료 후 7일 평균 CCU ÷ 시작 전 7일 평균 CCU − 1 (방송 2회 이상인 멤버만). 중앙값은 멤버들의 변화율 중앙값이다.",
            "- 콘서트 2건은 수집 시작 전이라 측정 불가. 비참여 n 이 작으면 비교는 참고용이다.", ""]


# ── H3 ────────────────────────────────────────────────────────────────────────
def h3() -> list[str]:
    snap = _read(LIVE / "snapshots.csv")
    L = ["## H3. 데뷔 직후 반응은 디시 → 유튜브 → 치지직 채팅 순으로 먼저 나타난다", ""]
    if snap.empty:
        return L + ["측정 불가 — 동시시청자 자료 없음", ""]
    ab = snap[snap["unit"] == "ABYSS"].copy()
    ab["t"] = pd.to_datetime(ab["collected_at"], utc=True, format="ISO8601").dt.tz_convert("Asia/Seoul")
    ab["date"] = ab["t"].dt.strftime("%Y-%m-%d")
    f = ab.groupby(["date", "name_ko"])["followers"].max().unstack().ffill()
    gain = f.diff().sum(axis=1).loc["2026-10-17":"2026-10-31"]
    dc = _read(CHAT / "dc_posts.csv")
    peak = {"4기 팔로워 일 증가 최대일(치지직)": gain.idxmax() if len(gain) else "—"}
    if not dc.empty and dc["posted_at"].min()[:10] <= "2026-10-17":
        d = dc[dc["title"].str.contains("4기|어비스|토아|히요리|메리|코가네", na=False, regex=True)]
        daily = d.groupby(d["posted_at"].str[:10]).size().loc["2026-10-17":"2026-10-31"]
        peak["디시 제목에 4기 언급 최대일"] = daily.idxmax() if len(daily) else "—"
    else:
        peak["디시 제목에 4기 언급 최대일"] = "보류 — 디시 수집이 10-17 까지 안 닿음"
    peak["유튜브"] = "보류 — 일 단위 조회수 이력 없음(쌓는 중이 아님)"
    L += [md_table(pd.DataFrame([peak]).T.reset_index().rename(columns={"index": "지표", 0: "값"})), "",
          "- 유튜브는 영상 조회수의 시점별 이력을 안 모아서 '언제 반응했나'를 못 잰다. 순서 가설 전체는 디시+치지직 두 축으로만 본다.", ""]
    return L


# ── H4 ────────────────────────────────────────────────────────────────────────
def h4() -> list[str]:
    v = _read(CHAT / "chat_videos.csv")
    L = ["## H4. 도네·채팅 밀도는 시청자 규모와 별개의 지표다", ""]
    if v.empty:
        return L + ["측정 불가 — 채팅 수집 자료 없음", ""]
    st = _read(ROOT / "03_chzzk_stream_pattern" / "data" / "streams.csv").set_index("video_no")
    v = v[~v["name_ko"].isin(FOUNDER)].copy()
    mins = _read(CHAT / "chat_minutes.csv")
    # 포화: 다시보기 채팅은 초당 약 20건(분당 ~1,240)에서 잘려 저장된다. 그 근처에 붙은 분이 90% 이상이면 채팅 밀도를 못 잰다.
    sat = (mins.assign(full=mins["chats"] >= SAT_PER_MIN).groupby("video_no")["full"].mean() >= 0.9)
    v["saturated"] = v["video_no"].map(sat).fillna(False)
    v["views"] = v["video_no"].map(st["read_count"])
    v["min"] = v["duration_sec"] / 60
    v["chats_per_min"] = v["chats"] / v["min"]
    v["donations_per_1k_chats"] = v["donations"] / v["chats"] * 1000
    v["chats_per_min_per_1k_views"] = v["chats_per_min"] / v["views"] * 1000
    def spearman(a: pd.Series, b: pd.Series) -> float:      # scipy 없이: 순위의 피어슨
        return a.rank().corr(b.rank())
    free = v[~v["saturated"]]
    rho1 = spearman(free["chats_per_min"], free["views"])
    rho2 = spearman(free["donations_per_1k_chats"], free["views"])
    show = v[["name_ko", "title", "views", "chats_per_min", "donations_per_1k_chats", "saturated"]].copy()
    show["saturated"] = show["saturated"].map({True: "포화(하한)", False: ""})
    show["title"] = show["title"].str[:16]
    show["chats_per_min"] = show["chats_per_min"].round(1)
    show["donations_per_1k_chats"] = show["donations_per_1k_chats"].round(2)
    L += [f"방송 {len(v)}개(다시보기 조회수 = 규모 대리). 후원 금액은 다시보기에서 전부 0이라 **건수만** 쓴다.", "",
          f"⚠ **채팅 포화** — 방송 {int(v['saturated'].sum())}개는 분당 채팅이 저장 한도(~{int(mins['chats'].max()):,}건/분)에 붙어 있다. "
          "이 방송들의 채팅 수·분당 채팅은 실제보다 작은 **하한**이고 서로 비교할 수 없다. 상관은 포화되지 않은 "
          f"{len(free)}개로만 낸다.", "",
          f"- 분당 채팅 ↔ 조회수 스피어만 상관(포화 제외 {len(free)}개): **{rho1:+.2f}**",
          f"- 채팅 1,000건당 후원 건수 ↔ 조회수 스피어만 상관(포화 제외): **{rho2:+.2f}**",
          f"- 포화 제외 방송의 조회수 1,000당 분당 채팅은 {free['chats_per_min_per_1k_views'].min():.2f}~{free['chats_per_min_per_1k_views'].max():.2f} 로 "
          f"{free['chats_per_min_per_1k_views'].max() / free['chats_per_min_per_1k_views'].min():.1f}배 벌어진다 — 같은 규모에서도 밀도가 다르다.", "",
          md_table(show.rename(columns={"name_ko": "멤버", "title": "방송", "views": "조회수", "chats_per_min": "분당 채팅",
                                        "donations_per_1k_chats": "채팅 1천건당 후원", "saturated": "비고"})), "",
          "- 한계: 표본은 4기 데뷔·비교군 선택 방송이라 전체 방송의 대표값이 아니다. 조회수는 누적이라 최근 방송이 낮다.", ""]
    return L


# ── H5 ────────────────────────────────────────────────────────────────────────
def h5(s: pd.DataFrame) -> list[str]:
    t = _read(CHAT / "chzzk_total.csv")
    L = ["## H5. 스텔라이브 시청자 변화는 치지직 전체 버튜버 흐름과 같이 움직인다", ""]
    if t.empty:
        return L + ["측정 불가 — `collect-vtubers` 수집이 아직 시작되지 않음(치지직 전체 시계열은 과거 소급 불가)", ""]
    t["date"] = pd.to_datetime(t["collected_at"]).dt.strftime("%Y-%m-%d")
    days = t["date"].nunique()
    L += [f"치지직 상위 {int(t['top_n'].max())}개 방송 합계(전체의 대리) · 버튜버 후보 합계 시계열 {days}일 쌓임 "
          f"({t['date'].min()} ~ {t['date'].max()}).", ""]
    if days < 14:
        return L + [f"- 보류 — 상관은 최소 14일이 필요하다(지금 {days}일). 수집은 매시간 자동으로 쌓인다.",
                    "- 한계: 상위 N 합계와 '버튜버 후보'는 제목·태그 추정이라 확정 명단이 아니다 — 후보는 집계가 아니라 참고다.", ""]
    daily = t.groupby("date")[["total_ccu", "vtuber_candidate_ccu"]].mean()
    st = s.assign(date=s["t"].dt.strftime("%Y-%m-%d")).groupby("date")["avg_ccu"].mean().rename("stellive_avg_ccu")
    j = daily.join(st, how="inner")
    return L + [f"- 겹치는 {len(j)}일의 일별 상관(피어슨): 전체 합계 {j['total_ccu'].corr(j['stellive_avg_ccu']):+.2f} · "
                f"버튜버 후보 합계 {j['vtuber_candidate_ccu'].corr(j['stellive_avg_ccu']):+.2f}", ""]


# ── H6 ────────────────────────────────────────────────────────────────────────
def h6() -> list[str]:
    c = _read(ROOT / "12_event_impact" / "data" / "competitor_effect.csv")
    L = ["## H6. 스텔라이브의 시청자 증가는 홀로라이브·이세돌과 다른 패턴이다", ""]
    if c.empty:
        return L + ["측정 불가 — 경쟁사 자료 없음", ""]
    show = c[["group", "n_members", "subs_first", "subs_last", "gain_total", "growth_total", "growth_median", "reach_ratio"]].copy()
    show["growth_total"] = show["growth_total"].map("{:+.2%}".format)
    show["growth_median"] = show["growth_median"].map("{:+.2%}".format)
    return L + ["**동시시청자는 비교할 수 없다**(경쟁사 쪽 기록 없음 — 이세돌·홀로라이브는 치지직이 아니라 숲·유튜브가 주 무대). "
                "대신 같은 기간 구독자 증감과 도달 효율(평균 조회수 ÷ 구독자)로 본다.", "",
                md_table(show.rename(columns={"group": "그룹", "n_members": "멤버", "subs_first": "구독자(처음)", "subs_last": "구독자(지금)",
                                              "gain_total": "증감", "growth_total": "성장률", "growth_median": "멤버 중앙 성장률",
                                              "reach_ratio": "도달 효율"})), "",
                "- 한계: 구독자·조회수는 '시청자 수'가 아니다. 수집 기간(2026-08 이후)이 짧다.", ""]


def main() -> int:
    OUT.mkdir(exist_ok=True)
    s = sessions()
    L = ["# 가설 H1~H6 검증", "", f"기준: 동시시청자 수집 {s['t'].min().date()} ~ {s['t'].max().date()} · 창립자 제외", ""]
    for part in (h1(s), h2(s), h3(), h4(), h5(s), h6()):
        L += part
    (OUT / "hypotheses.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
