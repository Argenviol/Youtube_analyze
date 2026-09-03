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


def vod_multiple(events: pd.DataFrame, streams: pd.DataFrame) -> pd.DataFrame:
    """이벤트 날 방송이 그 멤버의 평소 방송보다 몇 배 봤나 (소급 가능)."""
    s = streams.copy()
    s["date"] = pd.to_datetime(s["publish_date"]).dt.date
    rows = []
    for _, e in events.iterrows():
        if e["type"] != "합방":
            continue
        d0, d1 = e["date"], e["end_date"]
        for name in str(e["members"]).split("|"):
            mine = s[s["name_ko"] == name]
            during = mine[(mine["date"] >= d0) & (mine["date"] <= d1)]
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
                "name_ko": name, "event_views": int(during["read_count"].sum()),
                "baseline_median": float(med),
                "views_multiple": round(during["read_count"].max() / med, 2),
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
        # 표시 제목이 아니라 감지·수동 지정된 매칭어를 쓴다.
        raw = str(e.get("match_keys") or "") or str(e["title"])
        keys = [k.strip() for k in raw.replace("·", "|").split("|") if k.strip()]
        for name in str(e["members"]).split("|"):
            mine = s[s["name_ko"] == name]
            in_span = mine[(mine["date"] >= d0) & (mine["date"] <= d1)]
            hit = in_span.apply(
                lambda r: any(k and (k in str(r["title"]) or k == str(r["category"]))
                              for k in keys), axis=1)
            during = in_span[hit] if len(in_span) else in_span
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

    # 리포트·차트에서는 창립자를 뺀다(수집·감지는 전 로스터 그대로).
    vod, foll, subs, ccu = (config.drop_founder(x) for x in (vod, foll, subs, ccu))
    impact = pd.concat([foll, subs], ignore_index=True)

    DATA.mkdir(parents=True, exist_ok=True)
    for name, df in (("event_vod_multiple", vod), ("event_impact", impact),
                     ("event_ccu", ccu)):
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

    write_report(events, vod, impact, ccu)
    print(f"  이벤트 {len(events)}건 · 소급 측정 {vod['event_id'].nunique() if not vod.empty else 0}건 "
          f"· 전후 비교 {measurable}건 · CCU {ccu['event_id'].nunique() if not ccu.empty else 0}건")
    return 0


def write_report(events, vod, impact, ccu) -> None:
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
- **동시시청자를 가장 크게 끌어올리는 건 합방이 아니라 신의상 공개다.** 관측된
  신의상 릴레이에서 참여 멤버가 평소 피크의 **7~20배**를 찍었다(사키하네 후야 첫
  신의상 38,402명 = 평소의 20.3배). 같은 기간 나란히 돌던 10인 마인크래프트 합방은
  1.0~1.7배였다. 합방은 **조회수**를, 신의상은 **동시시청자**를 움직인다.
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
- `data/event_vod_multiple.csv` · `event_impact.csv` · `event_ccu.csv`
- `charts/` · `sql/events.db` · `site/index.html`
""", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
