"""
프로젝트8 · 분석 단계
동시시청자 스냅샷 시계열 → 방송 세션 재구성 → 지표 → SQL → 차트 → 사이트 → 리포트.

  python 08_live_viewership/analyze.py

이 프로젝트는 수집 시간이 곧 데이터다. 스냅샷이 얇으면 차트가 거짓말을 하므로,
커버리지가 기준에 못 미치면 라이브 분석은 건너뛰고 무엇이 더 필요한지 알려준다.
팔로워 증감은 스냅샷 2개만 있어도 유효하므로 먼저 낸다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config, db, viz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SQL = HERE / "sql"
CHARTS = HERE / "charts"
SITE = HERE / "site"

# 라이브 분석을 신뢰할 수 있는 최소 커버리지.
MIN_LIVE_SESSIONS = 5
# ⚠ "관측 시간"은 span(마지막-처음)이 아니라 **실제로 찍은 시점 수 × 간격**이다.
#    수집기는 PC가 켜져 있을 때만 돈다. 노트북을 하루 꺼두면 span 은 24시간을
#    넘겨버리지만 실제 데이터는 몇 시간치뿐이다. span 을 기준으로 가드를 풀면
#    "얇은 데이터로 만든 그럴듯한 차트"가 정확히 그 상황에서 통과한다.
MIN_OBSERVED_HOURS = 24
# 수집 간격은 고정값으로 둘 수 없다. GitHub Actions 스케줄러는 cron 집행을
# 보장하지 않고 고빈도일수록 자주 건너뛴다 — 워크플로에 10분으로 걸어둬도 실제로는
# 중앙값 30분 안팎으로 들어온다(실측 48시간: 중앙값 32분, 최대 107분).
#
# 이걸 고정값으로 두면 두 군데가 동시에 무너진다.
#   1) 세션 재구성: 정상 간격이 임계값(25분)을 넘겨서 연속 방송이 스냅샷 1개짜리
#      세션으로 산산조각 난다. 실측에서 365세션 중 300건(82%)이 1포인트였다.
#   2) 커버리지: 관측 시간을 "시점 수 × 간격"으로 재는데 간격을 10분으로 잡으면
#      실제의 1/3로 과소평가된다.
# 그래서 둘 다 실측 간격에서 유도한다. 스케줄러 사정이 바뀌어도 따라간다.
NOMINAL_INTERVAL_MIN = 10   # 워크플로 cron 이 의도한 간격. 하한선으로만 쓴다.
SESSION_GAP_FACTOR = 2.5    # 관측 간격의 몇 배까지 같은 방송으로 이을지


def observed_interval_min(df: pd.DataFrame) -> float:
    """실제 스냅샷 간격의 중앙값(분). 장시간 중단 구간이 섞여 있어 평균이 아니라
    중앙값을 쓴다. 데이터가 없거나 의도 간격보다 촘촘하면 의도 간격을 쓴다."""
    stamps = df["collected_at"].drop_duplicates().sort_values()
    gaps = stamps.diff().dt.total_seconds().div(60).dropna()
    if gaps.empty:
        return float(NOMINAL_INTERVAL_MIN)
    return max(float(NOMINAL_INTERVAL_MIN), float(gaps.median()))


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA / "snapshots.csv")
    df["collected_at"] = pd.to_datetime(df["collected_at"], format="ISO8601", utc=True)
    df["kst"] = df["collected_at"].dt.tz_convert("Asia/Seoul")
    df["is_live"] = df["is_live"].astype(str).str.lower().isin(["true", "1"])
    return df.sort_values("collected_at").reset_index(drop=True)


def coverage(df: pd.DataFrame, interval_min: float) -> dict:
    span_h = (df["collected_at"].max() - df["collected_at"].min()).total_seconds() / 3600
    n_timepoints = int(df["collected_at"].nunique())

    # 실제 관측 시간 = 찍은 시점 수 × 간격. PC가 꺼져 있던 구간은 여기 안 들어간다.
    observed_h = n_timepoints * interval_min / 60
    # 기대 시점 수 대비 실제 시점 수. 1.0 이면 무중단, 0.3 이면 70%가 공백이다.
    expected = max(1.0, span_h * 60 / interval_min)
    ratio = min(1.0, n_timepoints / expected)

    # 가장 큰 단절 구간 — "언제 꺼져 있었나"를 한 숫자로 보여준다.
    stamps = df["collected_at"].drop_duplicates().sort_values()
    gaps = stamps.diff().dt.total_seconds().div(3600).dropna()
    largest_gap_h = float(gaps.max()) if len(gaps) else 0.0

    return dict(
        n_snapshots=len(df),
        n_timepoints=n_timepoints,
        span_hours=round(span_h, 2),
        observed_hours=round(observed_h, 2),
        coverage_ratio=round(ratio, 3),
        largest_gap_hours=round(largest_gap_h, 2),
        n_live_rows=int(df["is_live"].sum()),
        members=df["name_ko"].nunique(),
        first=df["collected_at"].min().isoformat(),
        last=df["collected_at"].max().isoformat(),
    )


def follower_growth(df: pd.DataFrame) -> pd.DataFrame:
    """스냅샷 간 팔로워 증감. 동시시청자보다 훨씬 빨리 의미가 생긴다."""
    rows = []
    for (ko, en, unit), g in df.groupby(["name_ko", "name_en", "unit"]):
        g = g.sort_values("collected_at")
        first, last = g.iloc[0], g.iloc[-1]
        hours = (last["collected_at"] - first["collected_at"]).total_seconds() / 3600
        delta = int(last["followers"] - first["followers"])
        rows.append(dict(
            name_ko=ko, name_en=en, unit=unit,
            followers_first=int(first["followers"]), followers_last=int(last["followers"]),
            delta=delta, span_hours=round(hours, 2),
            per_day=round(delta / hours * 24, 1) if hours > 0 else None,
        ))
    out = pd.DataFrame(rows).sort_values("delta", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    return out


def sessions(df: pd.DataFrame, gap_threshold_min: float) -> pd.DataFrame:
    """연속된 is_live 스냅샷을 하나의 방송 세션으로 묶는다."""
    rows = []
    for (ko, en, unit), g in df[df["is_live"]].groupby(["name_ko", "name_en", "unit"]):
        g = g.sort_values("collected_at")
        gap = g["collected_at"].diff().dt.total_seconds().div(60)
        sid = (gap.isna() | (gap > gap_threshold_min)).cumsum()
        for _, s in g.groupby(sid):
            start, end = s["collected_at"].iloc[0], s["collected_at"].iloc[-1]
            rows.append(dict(
                name_ko=ko, name_en=en, unit=unit,
                start_kst=s["kst"].iloc[0].strftime("%Y-%m-%d %H:%M"),
                observed_min=round((end - start).total_seconds() / 60, 1),
                n_points=len(s),
                peak_ccu=int(s["concurrent_users"].max()),
                avg_ccu=int(s["concurrent_users"].mean()),
                title=s["live_title"].dropna().iloc[0] if s["live_title"].notna().any() else None,
                category=s["category"].dropna().iloc[0] if s["category"].notna().any() else None,
            ))
    if not rows:
        return pd.DataFrame(columns=[
            "name_ko", "name_en", "unit", "start_kst", "observed_min",
            "n_points", "peak_ccu", "avg_ccu", "title", "category"])
    return pd.DataFrame(rows).sort_values("peak_ccu", ascending=False).reset_index(drop=True)


def member_metrics(df: pd.DataFrame, sess: pd.DataFrame, grow: pd.DataFrame) -> pd.DataFrame:
    live = df[df["is_live"]]
    rows = []
    for _, r in grow.iterrows():
        en = r["name_en"]
        ml = live[live["name_en"] == en]
        ms = sess[sess["name_en"] == en] if len(sess) else sess
        followers = r["followers_last"]
        peak = int(ml["concurrent_users"].max()) if len(ml) else None
        rows.append(dict(
            name_ko=r["name_ko"], name_en=en, unit=r["unit"],
            followers=followers,
            follower_delta=r["delta"], follower_per_day=r["per_day"],
            n_sessions=int(len(ms)), n_live_points=int(len(ml)),
            peak_ccu=peak,
            avg_ccu=int(ml["concurrent_users"].mean()) if len(ml) else None,
            # 팔로워 대비 실제로 방송에 들어오는 비율 — 팬덤 '밀도' 지표.
            ccu_per_1k_followers=round(peak / followers * 1000, 2) if peak and followers else None,
        ))
    out = pd.DataFrame(rows)
    sort_col = "peak_ccu" if out["peak_ccu"].notna().any() else "follower_delta"
    out = out.sort_values(sort_col, ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    return out


def _mc(names):
    cmap = config.member_colors()
    return [cmap.get(n, "#888") for n in names]


def build_charts(df: pd.DataFrame, sess: pd.DataFrame, metrics: pd.DataFrame, cov: dict) -> list[str]:
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    made = []

    # 1. 팔로워 증감 (커버리지가 얇아도 유효)
    d = metrics.sort_values("follower_delta")
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(d["name_ko"], d["follower_delta"], color=_mc(d["name_en"]), height=0.72, zorder=3)
    ax.set_title(f"관측 구간 팔로워 증감 ({cov['span_hours']:.1f}시간)")
    ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    for b, v in zip(bars, d["follower_delta"]):
        ax.annotate(f"{v:+,}", (b.get_width(), b.get_y() + b.get_height() / 2), va="center",
                    ha="left" if v >= 0 else "right", fontsize=9, color=config.INK["text"],
                    xytext=(4 if v >= 0 else -4, 0), textcoords="offset points")
    ax.margins(x=0.18); fig.tight_layout()
    fig.savefig(CHARTS / "01_follower_delta.png", dpi=140); plt.close(fig)
    made.append("01_follower_delta.png")

    live = df[df["is_live"]]
    if live.empty:
        return made

    # 2. 동시시청자 시계열 (이 프로젝트의 존재 이유)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    cmap = config.member_colors()
    for en, g in live.groupby("name_en"):
        g = g.sort_values("kst")
        ax.plot(g["kst"], g["concurrent_users"], marker="o", markersize=3,
                linewidth=1.8, color=cmap.get(en, "#888"),
                label=g["name_ko"].iloc[0], zorder=3)
    ax.set_title("동시시청자 시계열 (KST)")
    ax.set_ylabel("동시시청자")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M", tz=live["kst"].dt.tz))
    fig.autofmt_xdate()
    ax.legend(frameon=False, ncol=3, fontsize=9)
    fig.tight_layout(); fig.savefig(CHARTS / "02_ccu_timeseries.png", dpi=140); plt.close(fig)
    made.append("02_ccu_timeseries.png")

    # 3. 피크 동시시청자
    d = metrics.dropna(subset=["peak_ccu"]).sort_values("peak_ccu")
    if len(d):
        fig, ax = plt.subplots(figsize=(9, 6))
        bars = ax.barh(d["name_ko"], d["peak_ccu"], color=_mc(d["name_en"]), height=0.72, zorder=3)
        ax.set_title("관측 구간 피크 동시시청자")
        ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        for b, v in zip(bars, d["peak_ccu"]):
            ax.annotate(f"{int(v):,}", (b.get_width(), b.get_y() + b.get_height() / 2),
                        va="center", ha="left", fontsize=9, color=config.INK["text"],
                        xytext=(4, 0), textcoords="offset points")
        ax.margins(x=0.16); fig.tight_layout()
        fig.savefig(CHARTS / "03_peak_ccu.png", dpi=140); plt.close(fig)
        made.append("03_peak_ccu.png")

    # 4. 팬덤 밀도: 팔로워 1천명당 피크 동시시청자
    d = metrics.dropna(subset=["ccu_per_1k_followers"]).sort_values("ccu_per_1k_followers")
    if len(d):
        fig, ax = plt.subplots(figsize=(9, 6))
        bars = ax.barh(d["name_ko"], d["ccu_per_1k_followers"], color=_mc(d["name_en"]),
                       height=0.72, zorder=3)
        ax.set_title("팬덤 밀도: 팔로워 1,000명당 피크 동시시청자")
        ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        for b, v in zip(bars, d["ccu_per_1k_followers"]):
            ax.annotate(f"{v:.1f}", (b.get_width(), b.get_y() + b.get_height() / 2),
                        va="center", ha="left", fontsize=9, color=config.INK["text"],
                        xytext=(4, 0), textcoords="offset points")
        ax.margins(x=0.16); fig.tight_layout()
        fig.savefig(CHARTS / "04_fandom_density.png", dpi=140); plt.close(fig)
        made.append("04_fandom_density.png")

    return made


def build_sql(df, sess, metrics):
    SQL.mkdir(parents=True, exist_ok=True)
    snaps = df.drop(columns=["kst"]).copy()
    snaps["collected_at"] = snaps["collected_at"].astype(str)
    tables = {"snapshots": snaps, "sessions": sess, "member_metrics": metrics}
    db.write_sqlite(SQL / "viewership.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables)
    db.dump_insert_sql(SQL / "member_metrics.sql", "member_metrics", metrics)
    if len(sess):
        db.dump_insert_sql(SQL / "sessions.sql", "sessions", sess)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")

    md = ["# 동시시청자 분석 쿼리 결과\n", "`sql/viewership.db`(SQLite) 실행 결과.\n"]
    for title, q in NAMED_QUERIES:
        try:
            res = db.run_query(SQL / "viewership.db", q)
            md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n")
            md.append(res.to_markdown(index=False)); md.append("\n")
        except Exception as e:
            md.append(f"## {title}\n\n(실행 불가: {e})\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


def build_outputs(df, sess, metrics, cov, charts, enough):
    metrics.to_csv(DATA / "member_metrics.csv", index=False)
    if len(sess):
        sess.to_csv(DATA / "sessions.csv", index=False)

    SITE.mkdir(parents=True, exist_ok=True)
    live = df[df["is_live"]]
    series = {}
    for en, g in live.groupby("name_en"):
        g = g.sort_values("kst")
        series[en] = dict(
            name_ko=g["name_ko"].iloc[0],
            points=[[t.strftime("%Y-%m-%d %H:%M"), int(v)]
                    for t, v in zip(g["kst"], g["concurrent_users"])],
        )
    (SITE / "data.json").write_text(json.dumps(dict(
        meta=json.loads((DATA / "_meta.json").read_text(encoding="utf-8")),
        coverage=cov, enough_coverage=enough,
        members=json.loads(metrics.to_json(orient="records", force_ascii=False)),
        sessions=json.loads(sess.to_json(orient="records", force_ascii=False)) if len(sess) else [],
        ccu_series=series,
    ), ensure_ascii=False, indent=2), encoding="utf-8")

    top_grow = metrics.iloc[metrics["follower_delta"].argmax()]
    lines = [
        "# 프로젝트 8 · StelLive 동시시청자 시계열 분석\n",
        "- 데이터 소스: 치지직 비공식 API (polling live-status) — 10분 간격 자체 수집",
        f"- 관측 구간: {cov['first'][:16]} ~ {cov['last'][:16]} (UTC), "
        f"약 {cov['span_hours']:.1f}시간 / 스냅샷 {cov['n_timepoints']}시점 · {cov['n_snapshots']}건",
        f"- 멤버 {cov['members']}명\n",
        "## 이 프로젝트가 따로 있는 이유\n",
        "프로젝트3(방송 패턴)은 VOD 다시보기 목록으로 과거 방송 이력을 **소급 수집**할 수 있다.",
        "하지만 동시시청자는 소급이 불가능하다. VOD는 누적 조회수(readCount)만 주고, 치지직에는",
        "동시시청자 히스토리 API가 없다. 이 시계열은 직접 찍어 쌓은 것만이 유일한 출처다.\n",
        "## 핵심 요약\n",
        f"- **관측 구간 팔로워 증가 1위**: {top_grow['name_ko']} — "
        f"{int(top_grow['follower_delta']):+,}명"
        + (f" (일 환산 {top_grow['follower_per_day']:+,.0f}명)" if pd.notna(top_grow["follower_per_day"]) else ""),
    ]

    if enough:
        top_peak = metrics.dropna(subset=["peak_ccu"]).iloc[0]
        dens = metrics.dropna(subset=["ccu_per_1k_followers"])
        lines += [
            f"- **피크 동시시청자 1위**: {top_peak['name_ko']} — {int(top_peak['peak_ccu']):,}명",
            f"- 관측된 방송 세션: {len(sess)}건",
        ]
        if len(dens):
            top_d = dens.sort_values("ccu_per_1k_followers", ascending=False).iloc[0]
            lines.append(
                f"- **팬덤 밀도 1위**: {top_d['name_ko']} — 팔로워 1,000명당 "
                f"{top_d['ccu_per_1k_followers']:.1f}명 동시 시청"
            )
    else:
        lines += [
            "",
            "## ⚠ 라이브 분석은 아직 커버리지 미달\n",
            f"- 관측된 방송 세션 {len(sess)}건 (기준 {MIN_LIVE_SESSIONS}건), "
            f"실관측 {cov['observed_hours']:.1f}시간 (기준 {MIN_OBSERVED_HOURS}시간) — "
            f"달력 구간은 {cov['span_hours']:.1f}시간이지만 커버리지 {cov['coverage_ratio']*100:.0f}%, "
            f"최대 단절 {cov['largest_gap_hours']:.1f}시간",
            "- 이 상태로 동시시청자 차트를 내면 표본이 우연에 좌우되므로 결론을 내지 않는다.",
            "- `collect.py --daemon`을 며칠 더 돌리면 자동으로 채워진다.",
        ]

    lines += [
        "\n## 산출물",
        "- `data/snapshots.csv` 원본 스냅샷(append-only), `data/member_metrics.csv` 멤버 집계",
        "- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과",
        f"- `charts/` 차트 {len(charts)}종",
        "- `site/index.html` 인터랙티브 대시보드\n",
        "## 데이터 함정",
        "치지직은 방송이 꺼져 있어도 `concurrentUserCount`에 직전 방송 값을 그대로 돌려준다.",
        "`common.chzzk.normalize_live_status()`에서 `status`를 확인해 라이브 지표를 비우고,",
        "잔존값은 `last_*`로 분리했다. 이 처리를 건너뛰면 오프라인 구간이 '시청자가 계속 있는",
        "평지'로 찍혀 그래프가 통째로 거짓이 된다.",
    ]
    (HERE / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("팔로워 증감 랭킹", """
SELECT rank AS 순위, name_ko AS 멤버, followers AS 팔로워,
       follower_delta AS 증감, follower_per_day AS 일환산
FROM member_metrics ORDER BY follower_delta DESC;"""),
    ("피크 동시시청자 랭킹", """
SELECT name_ko AS 멤버, peak_ccu AS 피크동시솔, avg_ccu AS 평균동시솔,
       n_sessions AS 관측세션
FROM member_metrics WHERE peak_ccu IS NOT NULL ORDER BY peak_ccu DESC;"""),
    ("팬덤 밀도 (팔로워 1천명당 동시시청자)", """
SELECT name_ko AS 멤버, followers AS 팔로워, peak_ccu AS 피크동시솔,
       ccu_per_1k_followers AS 밀도
FROM member_metrics WHERE ccu_per_1k_followers IS NOT NULL
ORDER BY ccu_per_1k_followers DESC;"""),
    ("유닛별 팔로워 증감 합계", """
SELECT unit AS 유닛, COUNT(*) AS 인원, SUM(follower_delta) AS 증감합계
FROM member_metrics GROUP BY unit ORDER BY 증감합계 DESC;"""),
    ("관측된 방송 세션 TOP 10", """
SELECT name_ko AS 멤버, start_kst AS 시작, observed_min AS 관측분,
       peak_ccu AS 피크, category AS 카테고리
FROM sessions ORDER BY peak_ccu DESC LIMIT 10;"""),
]
ANALYSIS_QUERIES = "-- StelLive 동시시청자 분석 쿼리 (SQLite: sql/viewership.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    df = load()
    # 수집 간격을 실측에서 먼저 구한다. 커버리지 계산과 세션 임계값이 둘 다 여기에 걸린다.
    interval = observed_interval_min(df)
    gap_threshold = interval * SESSION_GAP_FACTOR
    print(f"  실측 수집 간격 중앙값 {interval:.0f}분 · 세션 분리 임계값 {gap_threshold:.0f}분")

    cov = coverage(df, interval)
    grow = follower_growth(df)
    sess = sessions(df, gap_threshold)
    metrics = member_metrics(df, sess, grow)

    # span 이 아니라 observed_hours 로 판단한다. PC가 꺼져 있던 시간은 관측이 아니다.
    enough = len(sess) >= MIN_LIVE_SESSIONS and cov["observed_hours"] >= MIN_OBSERVED_HOURS

    build_sql(df, sess, metrics)
    charts = build_charts(df, sess, metrics, cov)
    build_outputs(df, sess, metrics, cov, charts, enough)

    print(f"\n=== 커버리지 ===")
    print(f"실관측 {cov['observed_hours']:.2f}시간 (달력 구간 {cov['span_hours']:.2f}시간, "
          f"커버리지 {cov['coverage_ratio']*100:.0f}%, 최대 단절 {cov['largest_gap_hours']:.1f}시간)")
    print(f"시점 {cov['n_timepoints']}개 / "
          f"스냅샷 {cov['n_snapshots']}건 / 라이브 관측 {cov['n_live_rows']}건 / 세션 {len(sess)}건")
    if not enough:
        print(f"→ 라이브 분석 기준 미달 (세션 {MIN_LIVE_SESSIONS}건 & 실관측 {MIN_OBSERVED_HOURS}시간). "
              f"수집을 더 돌리면 자동으로 채워집니다.")
    print("\n=== 멤버 지표 ===")
    cols = ["rank", "name_ko", "unit", "followers", "follower_delta",
            "n_sessions", "peak_ccu", "ccu_per_1k_followers"]
    with pd.option_context("display.width", 220):
        print(metrics[cols].to_string(index=False))


if __name__ == "__main__":
    main()
