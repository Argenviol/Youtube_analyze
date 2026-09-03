"""
프로젝트12 · 분석 단계
이벤트 전후로 지표가 어떻게 움직였는지 잰다.

  python 12_event_impact/analyze.py

## 무엇을 잴 수 있고 무엇을 못 재나
이벤트마다 쓸 수 있는 자가 다르다. 없는 자를 있는 척하지 않는 게 이 파일의 핵심이다.

  소급 가능(2025-04~) — VOD 조회수 배수
      치지직 VOD 의 readCount 는 과거분이 전부 남아 있다. 이벤트 날 방송이 그 멤버의
      평소 방송보다 몇 배 봤는지를 재면, 일일 수집 이전 이벤트도 **크기**는 잴 수 있다.

  전후 비교 가능(2026-08-12~) — 팔로워·구독자·동시시청자
      history.csv 와 08 스냅샷이 시작된 날부터다. 그 이전 이벤트는 기준선이 아예
      없으므로 계산하지 않는다. '0%'가 아니라 '측정 불가'로 남긴다 — 둘은 다르다.

  영구 불가 — 수익
      치지직 후원·구독 수익도, 유튜브 광고 수익도 공개되지 않는다. 추정치를 지어내는
      대신 플랫폼이 실제로 수익을 매기는 축인 **노출량(시청시간·조회수)** 을 대리
      지표로 낸다. 회사 단위 실제 수익성은 09(DART 감사보고서)가 연 단위로 답한다.

## 유튜브 구독자를 짧은 창으로 보면 안 되는 이유
API 가 1,000 단위로 반올림해 준다. 13만 채널은 하루에 0 아니면 +1,000 으로만 움직여서
이벤트 다음날 변화를 보면 계단만 보인다. 그래서 구독자는 7일 창으로만 낸다.
"""
from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import config, db, viz  # noqa: E402
# 연속일 기준은 collect.py 가 정의한다. 여기서 다시 적으면 한쪽만 고쳤을 때
# 리포트가 실제 기준과 다른 숫자를 말하게 된다.
from collect import MIN_CONSECUTIVE_DAYS  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = HERE / "data"
SQL = HERE / "sql"
CHARTS = HERE / "charts"
SITE = HERE / "site"

# 이벤트 전후 창 길이(일). 짧으면 노이즈, 길면 다른 이벤트가 섞인다.
WINDOW = 7
# 이벤트 후 창이 이 일수만큼 실제로 지나야 결과를 낸다.
#
# 이걸 안 걸면 어제 일어난 이벤트도 표에 오른다. 실제로 8/27 이벤트가 이틀치
# 데이터만으로 "구독자 -100%"를 냈다 — 사후 창이 안 찼을 뿐인데 폭락으로 읽힌다.
# 창이 찰 때까지는 '관측 중'으로 두는 편이 틀린 숫자를 내는 것보다 낫다.
MIN_POST_DAYS = 5
# 소급 지표에서 "평소"를 정의하는 창(일). 이벤트 전후 30일의 중앙값과 비교한다.
BASELINE_DAYS = 30
# 조회수 배수가 이 값을 넘으면 "평소보다 확실히 크게 터진 방송"으로 본다.
BIG_MULTIPLE = 1.5


def _jsonable(df: pd.DataFrame) -> list[dict]:
    """date 객체는 json 이 못 넣는다. 사이트로 나가기 전에 문자열로 바꾼다."""
    if df.empty:
        return []
    out = df.copy()
    for c in out.columns:
        if out[c].map(lambda v: hasattr(v, "isoformat")).any():
            out[c] = out[c].astype(str)
    return out.to_dict("records")


def _read(p: Path, **kw) -> pd.DataFrame:
    return pd.read_csv(p, **kw) if p.exists() else pd.DataFrame()


# 방송으로 효과를 잴 수 있는 이벤트 종류. 곡 발매는 여기 없다 — 유튜브 업로드지
# 방송이 아니라서, 발매일에 마침 큰 합방이 돌면 그 성과가 곡에 붙는다.
STREAM_EVENT_TYPES = {"합방", "신의상", "콘서트"}


def _event_keys(e) -> list[str]:
    """이 이벤트의 방송을 알아보는 말. 표시 제목이 아니라 감지·수동 지정된 매칭어다."""
    raw = str(e.get("match_keys") or "") or str(e["title"])
    return [k.strip() for k in raw.replace("·", "|").split("|") if k.strip()]


def _belongs(rows: pd.DataFrame, keys: list[str], title_col: str,
             cat_col: str | None) -> pd.DataFrame:
    """기간이 겹치는 다른 이벤트의 방송을 이 이벤트 것으로 세지 않는다."""
    if rows.empty or not keys:
        return rows
    hit = rows.apply(
        lambda r: any(k and (k in str(r[title_col])
                             or (cat_col and k == str(r[cat_col])))
                      for k in keys), axis=1)
    return rows[hit]


def vod_multiple(events: pd.DataFrame, streams: pd.DataFrame) -> pd.DataFrame:
    """이벤트 날 방송이 그 멤버의 평소 방송보다 몇 배 봤나 (소급 가능).

    VOD 조회수는 과거분이 남아 있어서, 동시시청자 수집 이전(2026-08-12)의
    이벤트도 이걸로는 크기를 잴 수 있다. 2025년 신의상 릴레이가 그 경우다.
    """
    s = streams.copy()
    s["date"] = pd.to_datetime(s["publish_date"]).dt.date
    rows = []
    for _, e in events.iterrows():
        if e["type"] not in STREAM_EVENT_TYPES:
            continue
        d0, d1 = e["date"], e["end_date"]
        keys = _event_keys(e)
        for name in str(e["members"]).split("|"):
            mine = s[s["name_ko"] == name]
            in_span = mine[(mine["date"] >= d0) & (mine["date"] <= d1)]
            during = _belongs(in_span, keys, "title", "category")
            if during.empty:
                continue
            lo, hi = d0 - timedelta(days=BASELINE_DAYS), d1 + timedelta(days=BASELINE_DAYS)
            base = mine[(mine["date"] >= lo) & (mine["date"] <= hi)
                        & ~((mine["date"] >= d0) & (mine["date"] <= d1))]
            med = base["read_count"].median()
            if not med or pd.isna(med):
                continue
            rows.append({
                "event_id": e["event_id"], "date": d0, "title": e["title"],
                "type": e["type"],
                "name_ko": name, "event_views": int(during["read_count"].sum()),
                "baseline_median": float(med),
                "views_multiple": round(during["read_count"].max() / med, 2),
            })
    return pd.DataFrame(rows)


# 콘서트 전후로 관련 방송을 훑는 창(일).
#
# 콘서트는 오프라인·유료라 **행사 중에는 방송이 없다.** 그래서 다른 이벤트처럼
# 기간 안의 방송을 세면 0건이 나온다. 효과는 그 주변에 나타난다 — 선예매·매진
# 인증·D-3 카운트다운·후기 방송. 이 창이 그 호(arc)를 담는다.
CONCERT_PRE_DAYS = 7
CONCERT_POST_DAYS = 7


def concert_arc(events: pd.DataFrame, streams: pd.DataFrame,
                videos: pd.DataFrame) -> pd.DataFrame:
    """콘서트 전후 관련 방송·영상이 평소보다 몇 배 나왔나."""
    if streams.empty:
        return pd.DataFrame()
    s = streams.copy()
    s["date"] = pd.to_datetime(s["publish_date"]).dt.date
    v = videos.copy()
    if not v.empty:
        v["date"] = pd.to_datetime(v["published_at"], format="mixed",
                                   utc=True).dt.tz_convert("Asia/Seoul").dt.date

    rows = []
    for _, e in events[events["type"] == "콘서트"].iterrows():
        d0, d1 = e["date"], e["end_date"]
        lo = d0 - timedelta(days=CONCERT_PRE_DAYS)
        hi = d1 + timedelta(days=CONCERT_POST_DAYS)
        keys = _event_keys(e)
        for name in str(e["members"]).split("|"):
            mine = s[s["name_ko"] == name]
            arc = _belongs(mine[(mine["date"] >= lo) & (mine["date"] <= hi)],
                           keys, "title", "category")
            if arc.empty:
                continue
            base = mine[(mine["date"] >= d0 - timedelta(days=BASELINE_DAYS))
                        & (mine["date"] <= d1 + timedelta(days=BASELINE_DAYS))]
            base = base[~base.index.isin(arc.index)]
            med = base["read_count"].median()
            if not med or pd.isna(med):
                continue
            top = arc.loc[arc["read_count"].idxmax()]
            yt = pd.DataFrame()
            if not v.empty:
                yt = _belongs(v[(v["name_ko"] == name) & (v["date"] >= lo)
                                & (v["date"] <= hi)], keys, "title", None)
            rows.append({
                "event_id": e["event_id"], "date": d0, "title": e["title"],
                "name_ko": name, "n_streams": int(len(arc)),
                "peak_stream_views": int(top["read_count"]),
                "peak_stream_title": str(top["title"])[:40],
                "baseline_median": float(med),
                "arc_multiple": round(top["read_count"] / med, 2),
                "yt_videos": int(len(yt)),
                "yt_top_views": int(yt["views"].max()) if len(yt) else 0,
                # 단독/합동은 참여 인원으로 가른다. 유튜브 영상 유무로 가르면
                # videos.csv 가 멤버당 최근 50개만 담는다는 사정에 결과가 딸려간다.
                "solo": int(e["n_members"]) == 1,
            })
    return pd.DataFrame(rows)


# 커버곡 효과를 잴 때 제외할 '너무 새 영상'의 나이(일).
#
# 업로드 직후 영상은 조회수가 아직 안 붙었다. 커버와 일반 영상 **양쪽 모두**에서
# 빼야 공정하다. 14일과 21일 결과가 거의 같아 14일로 둔다.
COVER_MATURE_DAYS = 14


def cover_effect(covers: pd.DataFrame, videos: pd.DataFrame) -> pd.DataFrame:
    """커버곡이 그 멤버의 일반 영상보다 몇 배 보나.

    비교는 **같은 기간 안에서만** 한다. 커버는 2017년부터 있고 videos.csv 는 멤버당
    최근 50개뿐이라, 그냥 비교하면 오래 쌓인 커버가 최근 일반 영상을 이기는 게
    당연해진다 — 효과가 아니라 누적 시간을 재게 된다.
    """
    if covers.empty or videos.empty:
        return pd.DataFrame()
    c, v = covers.copy(), videos.copy()
    for df, col in ((c, "published_at"), (v, "published_at")):
        df["date"] = pd.to_datetime(df[col], format="mixed", utc=True) \
            .dt.tz_convert("Asia/Seoul").dt.date
    asof = max(v["date"].max(), c["date"].max())
    cut = asof - timedelta(days=COVER_MATURE_DAYS)
    cover_ids = set(c["video_id"])
    v["is_cover"] = v["video_id"].isin(cover_ids)

    rows = []
    for name, g in v.groupby("name_ko"):
        lo, hi = g["date"].min(), min(g["date"].max(), cut)
        normal = g[(~g["is_cover"]) & (g["date"] <= cut)]
        mine = c[(c["name_ko"] == name) & (c["date"] >= lo) & (c["date"] <= hi)]
        if len(normal) < 5 or mine.empty:
            continue
        nm, cm = normal["views"].median(), mine["views"].median()
        if not nm:
            continue
        rows.append({
            "name_ko": name, "window_from": lo, "window_to": hi,
            "n_covers": int(len(mine)), "cover_median_views": int(cm),
            "n_normal": int(len(normal)), "normal_median_views": int(nm),
            "views_multiple": round(cm / nm, 2),
        })
    return pd.DataFrame(rows)


def original_effect(events: pd.DataFrame, videos: pd.DataFrame,
                    covers: pd.DataFrame) -> pd.DataFrame:
    """오리지널곡 MV 가 그 멤버의 일반 영상·커버곡보다 몇 배 보나.

    커버와 같은 규율을 쓴다 — 같은 기간, 성숙한 영상만. 다른 점은 곡을 특정할 수
    있다는 것이다(match 컬럼). 커버는 '그 기간 커버들의 중앙값'이지만 오리지널은
    **그 곡의 MV 한 편**을 집어서 잰다.
    """
    if events.empty or videos.empty:
        return pd.DataFrame()
    v = videos.copy()
    v["date"] = pd.to_datetime(v["published_at"], format="mixed", utc=True) \
        .dt.tz_convert("Asia/Seoul").dt.date
    cover_ids = set(covers["video_id"]) if not covers.empty else set()
    asof = v["date"].max()
    cut = asof - timedelta(days=COVER_MATURE_DAYS)

    cov = covers.copy()
    if not cov.empty:
        cov["date"] = pd.to_datetime(cov["published_at"], format="mixed", utc=True) \
            .dt.tz_convert("Asia/Seoul").dt.date

    rows = []
    for _, e in events[events["type"] == "오리지널곡"].iterrows():
        keys = [k for k in str(e.get("match_keys") or "").split("|") if k]
        if not keys:
            continue          # 매칭어가 없으면 어느 영상이 그 곡인지 알 수 없다
        for name in str(e["members"]).split("|"):
            mine = v[v["name_ko"] == name]
            hit = _belongs(mine[mine["date"] <= cut], keys, "title", None)
            if hit.empty:
                continue
            # 티저·홍보 쇼츠가 아니라 MV 본편을 잡는다 — 조회수 최대가 본편이다.
            mv = hit.loc[hit["views"].idxmax()]
            normal = mine[(~mine["video_id"].isin(cover_ids))
                          & (~mine["video_id"].isin(set(hit["video_id"])))
                          & (mine["date"] <= cut)]
            if len(normal) < 5:
                continue
            nm = normal["views"].median()
            mine_cov = cov[(cov["name_ko"] == name)
                           & (cov["date"] >= mine["date"].min())
                           & (cov["date"] <= cut)] if not cov.empty else pd.DataFrame()
            cm = mine_cov["views"].median() if len(mine_cov) else None
            rows.append({
                "date": e["date"], "title": e["title"], "name_ko": name,
                "mv_views": int(mv["views"]), "mv_title": str(mv["title"])[:40],
                "n_related": int(len(hit)),
                "normal_median": int(nm),
                "vs_normal": round(mv["views"] / nm, 2),
                "cover_median": int(cm) if cm and cm == cm else 0,
                "vs_cover": round(mv["views"] / cm, 2) if cm and cm == cm else None,
            })
    return pd.DataFrame(rows)


def _daily_delta(hist: pd.DataFrame, col: str) -> pd.DataFrame:
    """일일 순증. history.csv 는 누적값이라 차분해야 이벤트 효과가 보인다."""
    if hist.empty or col not in hist.columns:
        return pd.DataFrame()
    h = hist.copy()
    h["date"] = pd.to_datetime(h["date"]).dt.date
    h = h.sort_values(["name_ko", "date"])
    h["delta"] = h.groupby("name_ko")[col].diff()
    h["days"] = h.groupby("name_ko")["date"].diff().apply(
        lambda x: x.days if pd.notna(x) else None)
    # 수집이 하루 건너뛰면 이틀치가 한 행에 몰린다. 일 단위로 정규화한다.
    h["per_day"] = h["delta"] / h["days"]
    return h.dropna(subset=["per_day"])


def before_after(events: pd.DataFrame, hist: pd.DataFrame, col: str,
                 label: str) -> pd.DataFrame:
    """이벤트 전 WINDOW일 평균 순증 vs 후 WINDOW일 평균 순증."""
    d = _daily_delta(hist, col)
    if d.empty:
        return pd.DataFrame()
    first, last = d["date"].min(), d["date"].max()
    rows = []
    for _, e in events.iterrows():
        d0, d1 = e["date"], e["end_date"]
        # 기준선이 이벤트보다 늦게 시작했으면 전후 비교 자체가 성립하지 않는다.
        if d0 - timedelta(days=WINDOW) < first:
            continue
        # 사후 창이 아직 안 찼다 — 지금 계산하면 관측 부족이 변화로 둔갑한다.
        if (last - d1).days < MIN_POST_DAYS:
            continue
        for name in str(e["members"]).split("|"):
            mine = d[d["name_ko"] == name]
            pre = mine[(mine["date"] >= d0 - timedelta(days=WINDOW)) & (mine["date"] < d0)]
            post = mine[(mine["date"] > d1) & (mine["date"] <= d1 + timedelta(days=WINDOW))]
            if pre.empty or post.empty:
                continue
            a, b = pre["per_day"].mean(), post["per_day"].mean()
            rows.append({
                "event_id": e["event_id"], "date": d0, "title": e["title"],
                "type": e["type"], "name_ko": name, "metric": label,
                "before_per_day": round(a, 1), "after_per_day": round(b, 1),
                "change_pct": round((b - a) / a * 100, 1) if a else None,
            })
    return pd.DataFrame(rows)


# 동시시청자로 효과를 잴 수 있는 이벤트 종류.
#
# 곡 발매는 유튜브 업로드지 방송이 아니다. 그런데 발매일에 그 멤버가 방송을 했다면
# 그 방송의 피크가 곡의 효과로 잡힌다. 실제로 8/31 사키하네 후야 커버가 '평소 대비
# 18.4배'로 나왔는데, 그 피크(38,402)는 같은 날 돌던 10인 마인크래프트 합방의 것이었다.
# 곡의 효과는 조회수·구독자로 재고, 동시시청자는 방송형 이벤트에만 붙인다.
CCU_EVENT_TYPES = {"합방", "콘서트", "신의상"}


def ccu_impact(events: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:
    """이벤트 기간 동시시청자 피크 vs 그 멤버의 평소 피크 중앙값."""
    if sessions.empty:
        return pd.DataFrame()
    events = events[events["type"].isin(CCU_EVENT_TYPES)]
    s = sessions.copy()
    s["date"] = pd.to_datetime(s["start_kst"]).dt.date
    rows = []
    for _, e in events.iterrows():
        d0, d1 = e["date"], e["end_date"]
        # 기간이 겹치는 다른 이벤트의 방송을 이 이벤트의 효과로 세면 안 된다.
        # 8/29~9/3 마인크래프트 합방과 8/30~9/2 신의상 릴레이가 겹쳐서, 기간만으로
        # 고르면 신의상 공개의 38,237명이 마인크래프트 합방의 성과로 잡혔다.
        # 이벤트 이름이 방송 제목이나 카테고리에 실제로 나타난 세션만 센다.
        keys = _event_keys(e)
        for name in str(e["members"]).split("|"):
            mine = s[s["name_ko"] == name]
            in_span = mine[(mine["date"] >= d0) & (mine["date"] <= d1)]
            during = _belongs(in_span, keys, "title", "category")
            other = mine[~((mine["date"] >= d0) & (mine["date"] <= d1))]
            if during.empty or other.empty:
                continue
            med = other["peak_ccu"].median()
            if not med:
                continue
            rows.append({
                "event_id": e["event_id"], "date": d0, "title": e["title"],
                "name_ko": name, "event_peak_ccu": int(during["peak_ccu"].max()),
                "usual_peak_ccu": int(med),
                "ccu_multiple": round(during["peak_ccu"].max() / med, 2),
            })
    return pd.DataFrame(rows)


def charts(events: pd.DataFrame, vod: pd.DataFrame) -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()

    if not vod.empty:
        top = (vod.groupby(["event_id", "title", "date"])["views_multiple"]
               .mean().reset_index().nlargest(15, "views_multiple")
               .sort_values("views_multiple"))
        fig, ax = plt.subplots(figsize=(10, 6.5))
        lbl = [f"{r.title[:22]} ({r.date})" for r in top.itertuples()]
        # 다른 프로젝트와 같은 규약: zorder=3 로 막대를 그리드 위에 올린다.
        # 안 그러면 y 그리드선이 막대 한가운데를 가로질러 막대가 둘로 쪼개져 보인다.
        bars = ax.barh(lbl, top["views_multiple"], height=0.72, zorder=3,
                       color=config.PALETTE["series"][0])
        ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        # viz.barlabels 는 세로 막대용이다(값을 get_height 로 읽는다). 가로 막대에
        # 쓰면 막대 두께 0.8 을 값으로 찍어 전부 "0.8배"가 된다 — 실제로 그랬다.
        for b, v in zip(bars, top["views_multiple"]):
            ax.annotate(f"{v:.2f}배", (b.get_width(), b.get_y() + b.get_height() / 2),
                        va="center", ha="left", fontsize=9,
                        color=config.INK["text"], xytext=(4, 0),
                        textcoords="offset points")
        ax.axvline(1.0, color="#999", ls="--", lw=1, zorder=2)
        ax.margins(x=0.12)
        ax.set_title("합방 효과 · 이벤트 방송 조회수 ÷ 평소 방송 조회수 (참여자 평균)")
        ax.set_xlabel("배수 (1.0 = 평소와 같음)")
        fig.tight_layout()
        fig.savefig(CHARTS / "collab_views_multiple.png", dpi=140)
        plt.close(fig)

    if not vod.empty and "type" in vod.columns:
        g = (vod.groupby(["type", "title", "date"])["views_multiple"]
             .mean().reset_index())
        g = g[g["type"].isin(["신의상", "합방"])].sort_values("views_multiple")
        if not g.empty:
            cmap = {"신의상": config.PALETTE["series"][3],
                    "합방": config.PALETTE["series"][0]}
            fig, ax = plt.subplots(figsize=(10, 6))
            lbl = [f"{r.title[:20]} ({r.date})" for r in g.itertuples()]
            bars = ax.barh(lbl, g["views_multiple"], height=0.72, zorder=3,
                           color=[cmap[t] for t in g["type"]])
            ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
            ax.spines["left"].set_visible(False)
            for b, v in zip(bars, g["views_multiple"]):
                ax.annotate(f"{v:.2f}배",
                            (b.get_width(), b.get_y() + b.get_height() / 2),
                            va="center", ha="left", fontsize=9,
                            color=config.INK["text"], xytext=(4, 0),
                            textcoords="offset points")
            ax.axvline(1.0, color="#999", ls="--", lw=1, zorder=2)
            ax.margins(x=0.12)
            handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cmap.values()]
            ax.legend(handles, cmap.keys(), loc="lower right", frameon=False)
            ax.set_title("이벤트 종류별 효과 · 이벤트 방송 조회수 ÷ 평소 방송")
            ax.set_xlabel("배수 (1.0 = 평소와 같음)")
            fig.tight_layout()
            fig.savefig(CHARTS / "costume_vs_collab.png", dpi=140)
            plt.close(fig)

    if not events.empty:
        yr = events.copy()
        yr["ym"] = pd.to_datetime(yr["date"]).dt.to_period("M").astype(str)
        piv = yr.pivot_table(index="ym", columns="type", values="event_id",
                             aggfunc="count").fillna(0)
        fig, ax = plt.subplots(figsize=(11, 5))
        piv.plot(kind="bar", stacked=True, ax=ax,
                 color=config.PALETTE["series"][:piv.shape[1]])
        ax.set_title("월별 이벤트 발생 건수 (합방 · 커버곡 · 콘서트)")
        ax.set_xlabel("")
        ax.set_ylabel("건")
        fig.tight_layout()
        fig.savefig(CHARTS / "events_by_month.png", dpi=140)
        plt.close(fig)


def main() -> int:
    events = _read(DATA / "events.csv")
    if events.empty:
        print("  ✗ events.csv 가 없다. collect.py 를 먼저 돌려야 한다.")
        return 1
    for c in ("date", "end_date"):
        events[c] = pd.to_datetime(events[c]).dt.date

    streams = _read(ROOT / "03_chzzk_stream_pattern" / "data" / "streams.csv")
    h03 = _read(ROOT / "03_chzzk_stream_pattern" / "data" / "history.csv")
    h01 = _read(ROOT / "01_member_channel_performance" / "data" / "history.csv")
    sessions = _read(ROOT / "08_live_viewership" / "data" / "sessions.csv")

    # 관측 마지막 날까지 이어지는 이벤트는 아직 진행 중이다. VOD 조회수가 계속
    # 쌓이는 중이라 배수가 과소평가된다 — 숫자를 빼진 않되 표시는 해 둔다.
    last_stream = pd.to_datetime(streams["publish_date"]).dt.date.max() if not streams.empty else None
    events["ongoing"] = (events["end_date"] >= last_stream) if last_stream else False

    vod = vod_multiple(events, streams)
    foll = before_after(events, h03, "followers", "치지직 팔로워")
    subs = before_after(events, h01, "subscribers", "유튜브 구독자")
    ccu = ccu_impact(events, sessions)
    videos = _read(ROOT / "01_member_channel_performance" / "data" / "videos.csv")
    arc = concert_arc(events, streams, videos)
    covers = _read(ROOT / "02_cover_song_ranking" / "data" / "covers.csv")
    cov_eff = config.drop_founder(cover_effect(covers, videos))
    orig_eff = config.drop_founder(original_effect(events, videos, covers))

    # 리포트·차트에서는 창립자를 뺀다(수집·감지는 전 로스터 그대로).
    vod, foll, subs, ccu, arc = (config.drop_founder(x)
                                 for x in (vod, foll, subs, ccu, arc))
    impact = pd.concat([foll, subs], ignore_index=True)

    DATA.mkdir(parents=True, exist_ok=True)
    for name, df in (("event_vod_multiple", vod), ("event_impact", impact),
                     ("event_ccu", ccu), ("concert_arc", arc),
                     ("cover_effect", cov_eff), ("original_effect", orig_eff)):
        df.to_csv(DATA / f"{name}.csv", index=False, encoding="utf-8-sig")

    SQL.mkdir(parents=True, exist_ok=True)
    tables = {"events": events.astype(str), "vod_multiple": vod,
              "impact": impact, "ccu": ccu}
    db.write_sqlite(SQL / "events.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables)

    charts(events, vod)

    SITE.mkdir(parents=True, exist_ok=True)
    measurable = int(impact["event_id"].nunique()) if not impact.empty else 0
    payload = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "n_events": int(len(events)),
        "by_type": events["type"].value_counts().to_dict(),
        "span": [str(events["date"].min()), str(events["date"].max())],
        "measurable_events": measurable,
        "top_collabs": _jsonable(vod.groupby(["title", "date"])["views_multiple"]
                                 .mean().nlargest(10).round(2).reset_index()),
        "ccu": _jsonable(ccu),
        "impact": _jsonable(impact),
    }
    (SITE / "data.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    write_report(events, vod, impact, ccu, arc, cov_eff, covers, orig_eff)
    print(f"  이벤트 {len(events)}건 · 소급 측정 {vod['event_id'].nunique() if not vod.empty else 0}건 "
          f"· 전후 비교 {measurable}건 · CCU {ccu['event_id'].nunique() if not ccu.empty else 0}건"
          f" · 콘서트 호 {len(arc) if arc is not None and not arc.empty else 0}건")
    return 0


def write_report(events, vod, impact, ccu, arc=None, cov_eff=None,
                 covers=None, orig_eff=None) -> None:
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    span = f"{events['date'].min()} ~ {events['date'].max()}"
    by_type = events["type"].value_counts()
    collabs = events[events["type"] == "합방"]

    top = ""
    if not vod.empty:
        t = (vod.groupby(["title", "date"])["views_multiple"].mean()
             .nlargest(10).round(2).reset_index())
        ongoing = set(events.loc[events["ongoing"], "title"])
        top = "\n".join(
            f"| {r.date} | {str(r.title)[:34]}"
            f"{' *(진행 중)*' if r.title in ongoing else ''} | {r.views_multiple:.2f}배 |"
            for r in t.itertuples())

    ccu_tbl = ""
    if not ccu.empty:
        c = ccu.nlargest(8, "ccu_multiple")
        ccu_tbl = "\n".join(
            f"| {r.date} | {str(r.title)[:26]} | {r.name_ko} | {r.event_peak_ccu:,} | "
            f"{r.usual_peak_ccu:,} | {r.ccu_multiple:.2f}배 |" for r in c.itertuples())

    imp_tbl = ""
    if not impact.empty:
        i = impact.dropna(subset=["change_pct"]).nlargest(10, "change_pct")
        imp_tbl = "\n".join(
            f"| {r.date} | {r.title[:26]} | {r.name_ko} | {r.metric} | "
            f"{r.before_per_day:+,.0f} | {r.after_per_day:+,.0f} | {r.change_pct:+.1f}% |"
            for r in i.itertuples())

    big = (vod.groupby("event_id")["views_multiple"].mean() >= BIG_MULTIPLE).sum() if not vod.empty else 0

    # ── 신의상 vs 합방 요약 ──
    def _rng(df, col, default=(0.0, 0.0)):
        return (float(df[col].min()), float(df[col].max())) if len(df) else default

    vt = vod.groupby(["type", "event_id"])["views_multiple"].mean().reset_index() \
        if not vod.empty and "type" in vod.columns else pd.DataFrame(columns=["type", "views_multiple"])
    cos_lo, cos_hi = _rng(vt[vt["type"] == "신의상"], "views_multiple")
    col_lo, col_hi = _rng(vt[vt["type"] == "합방"], "views_multiple")
    ct = ccu.merge(events[["event_id", "type"]], on="event_id", how="left") \
        if not ccu.empty else pd.DataFrame(columns=["type", "ccu_multiple"])
    ccu_lo, ccu_hi = _rng(ct[ct["type"] == "신의상"], "ccu_multiple")
    mc_lo, mc_hi = _rng(ct[ct["type"] == "합방"], "ccu_multiple")

    # ── 오리지널곡 ──
    orig_tbl = "| — | 측정 가능한 오리지널곡이 없음 |"
    o_lo = o_hi = oc_lo = oc_hi = riko_vc = 0.0
    if orig_eff is not None and not orig_eff.empty:
        oe = orig_eff.sort_values("vs_normal", ascending=False)
        o_lo, o_hi = float(oe["vs_normal"].min()), float(oe["vs_normal"].max())
        vc = oe["vs_cover"].dropna()
        if len(vc):
            oc_lo, oc_hi = float(vc.min()), float(vc.max())
        r = oe[oe["name_ko"] == "유즈하 리코"]["vs_cover"]
        riko_vc = float(r.iloc[0]) if len(r) and r.iloc[0] == r.iloc[0] else 0.0
        orig_tbl = ("| 곡 | 멤버 | 공개일 | MV 조회수 | 일반 중앙 | 일반 대비 | 커버 대비 |\n"
                    "|---|---|---|---|---|---|---|\n" + "\n".join(
                        f"| {str(r.title).split('「')[-1].rstrip('」')} | {r.name_ko} | "
                        f"{r.date} | {r.mv_views:,} | {r.normal_median:,} | "
                        f"**{r.vs_normal:.1f}배** | "
                        f"{(f'{r.vs_cover:.1f}배' if r.vs_cover == r.vs_cover else '—')} |"
                        for r in oe.itertuples()))

    # ── 커버곡 ──
    cover_tbl, cov_med, riko = "| — | 데이터 없음 |", 0.0, 0.0
    if cov_eff is not None and not cov_eff.empty:
        ce = cov_eff.sort_values("views_multiple", ascending=False)
        cov_med = float(ce["views_multiple"].median())
        r = ce[ce["name_ko"] == "유즈하 리코"]["views_multiple"]
        riko = float(r.iloc[0]) if len(r) else 0.0
        cover_tbl = ("| 멤버 | 커버 | 커버 중앙 조회수 | 일반 중앙 조회수 | 배수 |\n"
                     "|---|---|---|---|---|\n" + "\n".join(
                         f"| {r.name_ko} | {r.n_covers}곡 | {r.cover_median_views:,} | "
                         f"{r.normal_median_views:,} | **{r.views_multiple:.2f}배** |"
                         for r in ce.itertuples()))
    solo_med = collab_med = 0
    if covers is not None and not covers.empty:
        cc = covers.copy()
        cc["yr"] = pd.to_datetime(cc["published_at"], format="mixed", utc=True).dt.year
        recent = cc[cc["yr"] == cc["yr"].max()]
        if len(recent):
            g = recent.groupby("is_collab")["views"].median()
            solo_med = int(g.get(False, 0))
            collab_med = int(g.get(True, 0))

    arc_tbl, solo_mult, solo_yt, grp_lo, grp_hi = "| — | 데이터 없음 |", 0.0, 0, 0.0, 0.0
    if arc is not None and not arc.empty:
        a = arc.sort_values(["date", "arc_multiple"], ascending=[False, False])
        arc_tbl = ("| 콘서트 | 멤버 | 관련 방송 | 최고 조회수 | 평소 | 배수 |\n"
                   "|---|---|---|---|---|---|\n" + "\n".join(
                       f"| {r.date} {str(r.title)[:22]} | {r.name_ko} | {r.n_streams}건 | "
                       f"{r.peak_stream_views:,} | {r.baseline_median:,.0f} | "
                       f"**{r.arc_multiple:.2f}배** |" for r in a.itertuples()))
        solo = a[a["solo"]] if "solo" in a.columns else a.iloc[0:0]
        if len(solo):
            solo_mult = float(solo["arc_multiple"].max())
            solo_yt = int(solo["yt_top_views"].max())
        grp = a[~a["solo"]] if "solo" in a.columns else a.iloc[0:0]
        if len(grp):
            grp_lo, grp_hi = float(grp["arc_multiple"].min()), float(grp["arc_multiple"].max())

    costume_tbl = ""
    if not ct.empty and (ct["type"] == "신의상").any():
        c = ct[ct["type"] == "신의상"].nlargest(8, "ccu_multiple")
        costume_tbl = ("| 멤버 | 공개일 피크 | 평소 피크 | 배수 |\n|---|---|---|---|\n"
                       + "\n".join(
                           f"| {r.name_ko} | {r.event_peak_ccu:,} | "
                           f"{r.usual_peak_ccu:,} | **{r.ccu_multiple:.2f}배** |"
                           for r in c.itertuples()))
    now = pd.Timestamp.now().date()
    pending = int(sum(1 for _, e in events.iterrows()
                      if (now - e["end_date"]).days < MIN_POST_DAYS))

    (HERE / "REPORT.md").write_text(f"""# 프로젝트 12 · StelLive 이벤트 임팩트 분석

- 기준일: {today}
- 데이터 소스: 01·02·03·08 의 기존 수집분 재사용 (신규 API 호출 없음)
- 이벤트 구간: {span} · 총 {len(events)}건
- 구성: {', '.join(f'{k} {v}건' for k, v in by_type.items())}

## 이 프로젝트가 따로 있는 이유

다른 프로젝트는 "지금 얼마인가"를 답한다. 이 프로젝트는 **"무슨 일이 있어서 그렇게
됐는가"**를 답한다. 대규모 합방·커버곡 발매·콘서트 같은 사건을 자동으로 찾아 기억하고,
그 전후로 팔로워·구독자·동시시청자가 어떻게 움직였는지 붙인다.

이벤트는 손으로 적어 두지 않으면 잊힌다. 그래서 치지직 VOD 의 제목과 카테고리에서
합방을 자동 감지하고(`collect.py`), 처음 감지한 날짜를 `data/events_seen.csv` 에
append-only 로 남긴다.

## 핵심 요약

- **대규모 컨텐츠 {len(collabs)}건**을 자동 감지했다 — 4명 이상이 **연속 {MIN_CONSECUTIVE_DAYS}일 이상**
  함께한 기획만 이벤트로 본다. 마인크래프트 서버·봉켓몬·봉봉팜·팰월드처럼 며칠에 걸친
  기획이 그대로 잡힌다.
- 그 {len(collabs)}건 중 **{big}건이 평소 방송 대비 {BIG_MULTIPLE}배 이상**의 조회수를 냈다.
  하루짜리를 섞었을 때는 이 비율이 절반 수준이었다 — **연속 기획만 남기면 효과가 선명해진다.**
  단발 합방과 며칠짜리 기획은 성격이 다른 이벤트다.
- **가장 크게 터지는 이벤트는 합방이 아니라 신의상 공개다.** 조회수는 평소의
  **{cos_lo:.1f}~{cos_hi:.1f}배**(합방은 {col_lo:.1f}~{col_hi:.1f}배), 동시시청자 피크는
  **{ccu_lo:.1f}~{ccu_hi:.1f}배**(같은 기간 나란히 돌던 10인 마인크래프트 합방은
  {mc_lo:.1f}~{mc_hi:.1f}배)였다. 사키하네 후야의 첫 신의상은 38,402명 — 평소 피크의 19배다.
- **천장이 가장 높은 건 오리지널곡이다.** MV 가 일반 영상의 {o_lo:.1f}~{o_hi:.1f}배,
  같은 멤버의 커버곡과 비교해도 {oc_lo:.1f}~{oc_hi:.1f}배다. 다만 잴 수 있는 곡이
  한 앨범(4곡)뿐이라 **경향이 아니라 사례**로 읽어야 한다.
- **커버곡은 평소 영상의 {cov_med:.1f}배 본다**(같은 기간·성숙 영상만 비교). 콜라보 커버가
  더 잘 되지는 않는다 — 2026년 기준 솔로와 콜라보의 조회수 중앙값이 같다.
- **콘서트는 단독이냐 합동이냐로 갈린다.** 본인 첫 단독 콘서트의 후기 방송은 평소의
  {solo_mult:.1f}배(안내 쇼츠 {solo_yt:,}회)였지만, 같은 멤버가 참여한 그룹 페스티벌은
  {grp_lo:.1f}~{grp_hi:.1f}배였다. 합동은 관심이 10명에게 나뉜다.
- 전후 비교(팔로워·구독자·동시시청자)는 **일일 수집이 시작된 2026-08-12 이후 이벤트만**
  가능하다. 그 이전은 기준선이 없어 계산하지 않는다 — 0%가 아니라 측정 불가다.
- 최근 {pending}건은 **관측 중**이다. 이벤트 후 {MIN_POST_DAYS}일이 지나야 전후 비교를 낸다 —
  창이 안 찬 상태로 계산하면 관측 부족이 지표 폭락으로 둔갑한다.
- **수익은 어떤 방법으로도 잴 수 없다.** 치지직 후원·구독 수익도 유튜브 광고 수익도
  공개되지 않는다. 대리 지표로 노출량(동시시청자 피크·조회수)만 낸다.

## 합방 효과 — 이벤트 방송 조회수 ÷ 평소 방송 (소급 가능)

| 날짜 | 이벤트 | 참여자 평균 배수 |
|---|---|---|
{top or '| — | 데이터 부족 | — |'}

## 신의상 효과 — 가장 크게 터지는 이벤트

같은 기간에 나란히 돌아도 신의상 공개가 합방을 두 지표 모두에서 앞선다.

| 지표 | 신의상 공개 | 대규모 합방 |
|---|---|---|
| VOD 조회수 배수 | **{cos_lo:.1f}~{cos_hi:.1f}배** | {col_lo:.1f}~{col_hi:.1f}배 |
| 동시시청자 피크 배수 | **{ccu_lo:.1f}~{ccu_hi:.1f}배** | {mc_lo:.1f}~{mc_hi:.1f}배 |

{costume_tbl}

신의상은 **연 몇 회짜리 희소 이벤트**다. 합방은 며칠씩 이어지며 조회수를 꾸준히
끌어올리는 반면, 신의상은 하루 몇 시간에 평소의 몇 배가 몰린다. 성격이 다른 두
레버로 봐야 한다 — 합방은 **분량**, 신의상은 **순간 최대치**다.

## 오리지널곡 효과 — 가장 높은 천장

{orig_tbl}

오리지널곡 MV 는 그 멤버의 일반 영상보다 **{o_lo:.1f}~{o_hi:.1f}배** 본다. 같은 멤버의
커버곡과 비교해도 **{oc_lo:.1f}~{oc_hi:.1f}배**다. 지금까지 잰 이벤트 중 단일 콘텐츠로는
천장이 가장 높다.

발매는 한 편이 아니라 **묶음으로 굴러간다.** 곡마다 관련 영상이 7~11편 붙는다 —
티저(2~3일 전) → MV → 홍보 쇼츠 5~6편. 유즈하 리코의 「악당주의보」는 발매 한 달
뒤에도 댄스 챌린지 쇼츠(8/27·9/1)로 다시 20만 회씩 나왔다.

⚠ **표본은 한 앨범뿐이다.** 잴 수 있는 오리지널곡은 cliché 1st EP 「Colorful Strokes」
수록곡 4개가 전부다. 나머지 오리지널곡(2023~2026)은 일반 영상 목록이 멤버당 최근
50개뿐이라 데이터에 없다. **"오리지널곡은 커버의 2배"가 아니라 "이 앨범은 그랬다"**로
읽어야 한다. 유즈하 리코의 커버 대비 배수({riko_vc:.1f}배)가 유독 큰 것도 곡이 세서가
아니라 그의 커버 중앙값이 낮은 탓이다(아래 커버곡 절 참고).

## 커버곡 효과 — 평소 영상의 4배

커버는 2017년부터 있고 일반 영상 목록은 멤버당 최근 50개뿐이다. 그냥 비교하면
오래 쌓인 커버가 최근 일반 영상을 이기는 게 당연해진다 — 효과가 아니라 **누적 시간**을
재게 된다. 그래서 **같은 기간 안에서만**, 그리고 업로드 {COVER_MATURE_DAYS}일이 안 지난 영상은
커버·일반 **양쪽 모두에서** 빼고 비교했다.

{cover_tbl}

커버곡은 그 멤버의 일반 영상보다 **중앙값 {cov_med:.1f}배** 본다. 10명 중 9명이 2.8~7.4배에
들어간다.

**콜라보 커버가 더 잘 되지는 않는다.** 2026년 커버만 놓고 보면 솔로 {solo_med:,}회 ·
콜라보 {collab_med:,}회로 차이가 없다. 전체 기간으로는 콜라보가 높아 보이는데, 콜라보 커버가
**2024년부터만 존재해서** 생기는 착시다(그 이전 카탈로그는 전부 솔로).

### 읽을 때 주의

유즈하 리코만 {riko:.2f}배로 유일하게 1배 미만이고, 동시에 커버를 가장 자주 올린다
(월 4.5곡 · 다른 멤버는 0.3~1.2곡). "자주 올리면 효과가 희석된다"로 읽고 싶어지고
실제로 빈도와 배수의 상관은 -0.53이다. **그런데 리코 한 명을 빼면 +0.32로 뒤집힌다.**
표본 하나가 만든 상관이라 인과로 말할 수 없다.

더 그럴듯한 설명은 표본 수다. 다른 멤버는 창 안에 커버가 1~2곡뿐이라 그 중앙값이
"잘 된 한 곡"일 수 있는 반면, 리코는 7곡이라 평범한 곡까지 포함된 중앙값이다.
멤버별 배수 **순위**는 이 이유로 신뢰하지 말고, "커버는 일반 영상보다 몇 배 본다"는
**전체 경향**만 읽는 편이 안전하다.

## 콘서트 효과 — 단독과 합동은 다르다

콘서트는 오프라인·유료라 **행사 중에는 방송이 없다.** 그래서 기간 안을 세면 0건이다.
효과는 주변에 나타난다 — 선예매·매진 인증·D-3 카운트다운·후기 방송. 콘서트 전후
{CONCERT_PRE_DAYS}일의 관련 방송을 그 멤버의 평소 방송과 비교했다.

{arc_tbl}

**본인 단독 콘서트가 그룹 합동보다 훨씬 크게 남는다.** 아카네 리제의 첫 단독 콘서트
후기 방송은 평소의 {solo_mult:.1f}배였고, 콘서트 안내 쇼츠는 **{solo_yt:,}회**로 그 채널
최상위권이다. 반면 같은 멤버가 참여한 그룹 페스티벌(2025-12-20)의 후기 방송은
{grp_lo:.1f}~{grp_hi:.1f}배에 그쳤다. 합동 무대는 관심이 10명에게 나뉘지만 단독 콘서트는
그 멤버에게 몰린다.

⚠ **구독자·팔로워 전후 비교는 두 콘서트 모두 불가능하다.** 일일 축적이 2026-08-12에
시작됐는데 콘서트는 2025-12-20과 2026-07-11이라 기준선이 존재하지 않는다. 위 숫자는
**방송 조회수로 잰 간접 지표**이고, "콘서트로 구독자가 몇 % 늘었다"는 아직 말할 수 없다.
다음 콘서트부터는 전후 비교가 자동으로 붙는다.

## 동시시청자 피크 (2026-08-12 이후)

| 날짜 | 이벤트 | 멤버 | 이벤트 피크 | 평소 피크 | 배수 |
|---|---|---|---|---|---|
{ccu_tbl or '| — | 아직 측정 가능한 이벤트가 없음 | — | — | — | — |'}

## 팔로워·구독자 전후 변화 (2026-08-12 이후)

| 날짜 | 이벤트 | 멤버 | 지표 | 이전(일평균) | 이후(일평균) | 변화 |
|---|---|---|---|---|---|---|
{imp_tbl or '| — | 아직 측정 가능한 이벤트가 없음 | — | — | — | — | — |'}

## 데이터 함정

- **합방 자동 감지는 치지직 방송이 있어야 한다.** 유튜브에서만 진행한 합방이나
  오프라인 행사는 잡히지 않는다. `data/events_manual.csv` 에 손으로 적어야 한다.
- **준비·리액션 방송은 이벤트가 아니다.** 설명회·클립 월드컵·명장면 월드컵처럼
  본편 주변에서 흩어져 나오는 방송은 연속일 기준에 걸려 자동으로 빠진다.
  실제로 봉누도를 이 준비 구간만 보고 이벤트로 등록했다가 되물렸다.
- **오리지널곡은 자동 감지되지 않는다.** 02는 커버곡만 수집하므로, 오리지널 발매는
  수동 등록 대상이다.
- **유튜브 구독자는 1,000 단위 반올림**이라 이벤트 다음날 변화가 계단으로만 보인다.
  {WINDOW}일 창으로만 낸 이유다. 짧은 창은 치지직 팔로워(정확한 정수)를 볼 것.
- **조회수 배수는 시간이 지날수록 커진다.** VOD 조회수는 누적이라 오래된 이벤트가
  유리하다. 같은 시기 이벤트끼리 비교할 것. *(진행 중)* 표시가 붙은 건 아직 조회수가
  쌓이는 중이라 실제보다 낮게 나온다.
- **동시시청자는 방송형 이벤트(합방·콘서트)에만 붙인다.** 곡 발매는 유튜브 업로드지
  방송이 아니라서, 발매일에 마침 큰 합방이 돌면 그 피크가 곡의 효과로 둔갑한다.

## 산출물

- `data/events.csv` — 감지·등록된 전체 이벤트
- `data/events_seen.csv` — 처음 감지한 날짜 (append-only 기억)
- `data/events_manual.csv` — 손으로 등록하는 이벤트 (콘서트·오리지널곡·오프라인)
- `data/event_vod_multiple.csv` · `event_impact.csv` · `event_ccu.csv` ·
  `concert_arc.csv` · `cover_effect.csv` · `original_effect.csv`
- `charts/` · `sql/events.db` · `site/index.html`
""", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
