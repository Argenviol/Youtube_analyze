"""
프로젝트6 · 분석 단계 — 데뷔 코호트 매칭 비교

  python 06_competitor_comparison/analyze.py

## 왜 코호트인가
구독자는 매일 조금씩만 늘고 거의 줄지 않는 **누적 지표**다. 그래서 두 채널의 구독자
차이는 대부분 "누가 더 잘했나"가 아니라 "누가 더 오래 했나"를 잰다. 2019년 데뷔
채널과 2024년 데뷔 채널을 같은 막대그래프에 올리면 그 그래프는 데뷔 연도를 그린
것에 가깝다.

그래서 이 분석은 두 축으로만 본다.
  1) **코호트 안에서만 그룹을 비교한다.** 같은 시기에 시작한 사람들끼리.
  2) **경과 개월로 나눈 값(월평균 구독자 획득)을 같이 본다.** 코호트가 달라도
     속도는 비교할 수 있다. 다만 이것도 초기 급증 구간이 섞이면 신생 채널에
     유리하므로 보조 지표로만 쓴다.

그룹이 하나뿐인 코호트는 그룹 비교에서 제외한다 — 비교 상대가 없는데 막대를
그리면 비교한 것처럼 보이기 때문이다. 대신 리포트에 "비교군 없음"으로 남긴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config, db, viz
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SQL = HERE / "sql"
CHARTS = HERE / "charts"
SITE = HERE / "site"

GROUP_ORDER = ["StelLive", "홀로라이브", "이세계아이돌"]
GROUP_COLOR = {"StelLive": config.PALETTE["series"][0],
               "홀로라이브": config.PALETTE["series"][1],
               "이세계아이돌": config.PALETTE["series"][2]}

DAYS_PER_MONTH = 30.4375


def _meta() -> dict:
    return json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))


def build_metrics():
    meta = _meta()
    asof = pd.Timestamp(meta["fetched_at"]).tz_convert("UTC")

    ch = pd.read_csv(DATA / "channels.csv")
    vids = pd.read_csv(DATA / "videos.csv")
    vids["published_at"] = pd.to_datetime(vids["published_at"], utc=True)
    for c in ("views", "likes", "comments"):
        vids[c] = pd.to_numeric(vids[c], errors="coerce")
    # 업로드 직후 영상은 좋아요·댓글이 먼저 붙고 조회수가 늦게 반영된다(조회수 1에
    # 좋아요 443 같은 행이 실제로 있었다). 1,000 미만은 참여율 계산에서 제외한다.
    vids["engagement_rate"] = np.where(
        vids["views"] >= 1000,
        (vids["likes"].fillna(0) + vids["comments"].fillna(0)) / vids["views"],
        np.nan)

    unit_by_name_en = {r["name_en"]: r["unit"] for r in config.member_rows()}

    rows = []
    for _, c in ch.iterrows():
        v = vids[vids["channel_id"] == c["channel_id"]]
        if v.empty:
            continue
        span_days = max(1, (v["published_at"].max() - v["published_at"].min()).days)
        debut = pd.Timestamp(c["debut_date"], tz="UTC") if pd.notna(c["debut_date"]) else pd.NaT
        months = ((asof - debut).days / DAYS_PER_MONTH) if pd.notna(debut) else np.nan
        subs = int(c["subscribers"])
        rows.append(dict(
            group=c["group"], cohort=c["cohort"], generation=c["generation"],
            debut_date=c["debut_date"],
            channel_id=c["channel_id"], name_ko=c["name_ko"], name_en=c["name_en"],
            unit=unit_by_name_en.get(c["name_en"]),
            months_since_debut=round(months, 1) if months == months else np.nan,
            subscribers=subs,
            total_views=int(c["total_views"]), video_count=int(c["video_count"]),
            subs_per_month=round(subs / months, 1) if months and months == months else np.nan,
            recent_avg_views=round(v["views"].mean(), 1),
            recent_avg_engagement_rate=round(v["engagement_rate"].mean(), 5),
            uploads_per_week=round((len(v) - 1) / (span_days / 7), 2),
            reach_ratio=round(v["views"].mean() / subs, 3),
        ))

    members = (pd.DataFrame(rows)
               .sort_values(["cohort", "group", "subscribers"],
                            ascending=[True, True, False])
               .reset_index(drop=True))
    # 코호트가 없는 멤버(구간 밖)는 순위가 정의되지 않는다 — NaN 을 0 으로 두고
    # 리포트에서 따로 표시한다. 여기서 astype(int) 를 그냥 부르면 터진다.
    members.insert(0, "rank_in_cohort",
                   members.groupby("cohort")["subscribers"]
                   .rank(ascending=False, method="min")
                   .fillna(0).astype(int))

    cohort_summary = (members.dropna(subset=["cohort"])
                      .groupby(["cohort", "group"]).agg(
        n_members=("name_ko", "count"),
        avg_months_since_debut=("months_since_debut", "mean"),
        median_subscribers=("subscribers", "median"),
        avg_subscribers=("subscribers", "mean"),
        median_subs_per_month=("subs_per_month", "median"),
        avg_recent_views=("recent_avg_views", "mean"),
        avg_engagement_rate=("recent_avg_engagement_rate", "mean"),
        avg_uploads_per_week=("uploads_per_week", "mean"),
        avg_reach_ratio=("reach_ratio", "mean"),
    ).round(4).reset_index())

    return vids, members, cohort_summary


def comparable_cohorts(cohort_summary: pd.DataFrame) -> list[str]:
    """그룹이 2개 이상인 코호트만 그룹 비교 대상이다."""
    n = cohort_summary.groupby("cohort")["group"].nunique()
    return [c for c in n[n >= 2].index.tolist()]


def build_sql(vids, members, cohort_summary):
    SQL.mkdir(parents=True, exist_ok=True)
    v = vids.copy()
    v["published_at"] = v["published_at"].astype(str)
    tables = {"videos": v, "member_metrics": members, "cohort_summary": cohort_summary}
    db.write_sqlite(SQL / "competitors.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables, primary_keys={"videos": "video_id"})
    db.dump_insert_sql(SQL / "member_metrics.sql", "member_metrics", members)
    db.dump_insert_sql(SQL / "cohort_summary.sql", "cohort_summary", cohort_summary)
    db.dump_insert_sql(SQL / "videos.sql", "videos", v)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")
    md = ["# 경쟁사 비교(데뷔 코호트 매칭) 쿼리 결과\n",
          "`sql/competitors.db`(SQLite) 실행 결과.\n"]
    for title, q in NAMED_QUERIES:
        res = db.run_query(SQL / "competitors.db", q)
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n")
        md.append(res.to_markdown(index=False))
        md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


def _grouped_bar(ax, gs, cohorts, col, fmt):
    """x=코호트, 묶음=그룹 인 그룹 막대. 값 라벨을 직접 붙인다(색만으로 읽히지 않게)."""
    groups = [g for g in GROUP_ORDER if g in gs["group"].unique()]
    width = 0.8 / max(1, len(groups))
    xs = np.arange(len(cohorts))
    for i, g in enumerate(groups):
        vals, labels = [], []
        for c in cohorts:
            row = gs[(gs["cohort"] == c) & (gs["group"] == g)]
            vals.append(float(row[col].iloc[0]) if len(row) else np.nan)
            labels.append(int(row["n_members"].iloc[0]) if len(row) else 0)
        pos = xs - 0.4 + width * (i + 0.5)
        bars = ax.bar(pos, vals, width=width * 0.92, color=GROUP_COLOR[g],
                      label=g, zorder=3)
        for b, v, n in zip(bars, vals, labels):
            if v != v:
                continue
            ax.annotate(f"{fmt.format(v)}\n(n={n})",
                        (b.get_x() + b.get_width() / 2, v), ha="center", va="bottom",
                        fontsize=8.5, color=config.INK["text"],
                        xytext=(0, 3), textcoords="offset points")
    ax.set_xticks(xs)
    ax.set_xticklabels(cohorts)
    ax.grid(axis="y", zorder=0)
    ax.legend(frameon=False)
    ax.margins(y=0.18)


def build_charts(vids, members, cohort_summary):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    cohorts = comparable_cohorts(cohort_summary)
    gs = cohort_summary[cohort_summary["cohort"].isin(cohorts)]

    def cohort_chart(col, title, fmt, fname, ylabel=""):
        fig, ax = plt.subplots(figsize=(9, 5.8))
        _grouped_bar(ax, gs, cohorts, col, fmt)
        ax.set_title(title)
        if ylabel:
            ax.set_ylabel(ylabel)
        fig.tight_layout()
        fig.savefig(CHARTS / fname, dpi=140)
        plt.close(fig)

    cohort_chart("median_subscribers", "데뷔 코호트별 구독자 중앙값", "{:,.0f}",
                 "01_cohort_subscribers.png", "구독자")
    cohort_chart("avg_reach_ratio", "데뷔 코호트별 도달 효율 (평균조회수/구독자)",
                 "{:.0%}", "02_cohort_reach_ratio.png")
    cohort_chart("avg_engagement_rate", "데뷔 코호트별 참여율", "{:.1%}",
                 "03_cohort_engagement.png")
    cohort_chart("avg_uploads_per_week", "데뷔 코호트별 주간 업로드 빈도", "{:.1f}회",
                 "04_cohort_upload_cadence.png")

    # 05. 월평균 구독자 획득 — 코호트가 달라도 비교 가능한 속도 지표
    d = members.dropna(subset=["subs_per_month"]).sort_values("subs_per_month")
    fig, ax = plt.subplots(figsize=(9.5, max(6, 0.32 * len(d))))
    bars = ax.barh(d["name_ko"], d["subs_per_month"],
                   color=[GROUP_COLOR[g] for g in d["group"]], height=0.72, zorder=3)
    ax.set_title("데뷔 후 월평균 구독자 획득 (구독자 ÷ 데뷔 후 경과 개월)")
    ax.grid(axis="x", zorder=0)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    for b, v in zip(bars, d["subs_per_month"]):
        ax.annotate(f"{v:,.0f}", (b.get_width(), b.get_y() + b.get_height() / 2),
                    va="center", ha="left", fontsize=8, color=config.INK["text"],
                    xytext=(4, 0), textcoords="offset points")
    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLOR[g])
               for g in GROUP_ORDER if g in set(d["group"])]
    ax.legend(handles, [g for g in GROUP_ORDER if g in set(d["group"])],
              frameon=False, loc="lower right")
    ax.margins(x=0.16)
    fig.tight_layout()
    fig.savefig(CHARTS / "05_subs_per_month.png", dpi=140)
    plt.close(fig)

    # 06. 데뷔 후 경과 개월 vs 구독자 — 이 분석이 왜 필요한지 한 장으로 보여주는 그림
    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    for g in GROUP_ORDER:
        d = members[(members["group"] == g) & members["months_since_debut"].notna()]
        if d.empty:
            continue
        ax.scatter(d["months_since_debut"], d["subscribers"], s=90,
                   color=GROUP_COLOR[g], label=g, alpha=0.85,
                   edgecolors="white", linewidths=1.3, zorder=3)
    ax.set_yscale("log")
    ax.set_title("데뷔 후 경과 개월 vs 구독자 — 같은 세로선 위에 있는 사람끼리만 비교한다")
    ax.set_xlabel("데뷔 후 경과 개월")
    ax.set_ylabel("구독자 (log)")
    ax.legend(frameon=False)
    ax.grid(True, zorder=0)
    fig.tight_layout()
    fig.savefig(CHARTS / "06_age_vs_subs.png", dpi=140)
    plt.close(fig)

    print(f"차트 6종 -> {CHARTS}")


def _cohort_table(members: pd.DataFrame, cohort_summary: pd.DataFrame,
                  cohort: str) -> str:
    gs = cohort_summary[cohort_summary["cohort"] == cohort]
    groups = [g for g in GROUP_ORDER if g in gs["group"].tolist()]
    head = "| 지표 | " + " | ".join(groups) + " |"
    sep = "|------|" + "---:|" * len(groups)

    def row(label, col, fmt):
        cells = []
        for g in groups:
            r = gs[gs["group"] == g]
            cells.append(fmt.format(float(r[col].iloc[0])) if len(r) else "—")
        return f"| {label} | " + " | ".join(cells) + " |"

    lines = [head, sep,
             row("인원", "n_members", "{:.0f}명"),
             row("데뷔 후 경과", "avg_months_since_debut", "{:.1f}개월"),
             row("구독자 중앙값", "median_subscribers", "{:,.0f}"),
             row("월평균 구독자 획득", "median_subs_per_month", "{:,.0f}"),
             row("최근 영상 평균 조회수", "avg_recent_views", "{:,.0f}"),
             row("참여율", "avg_engagement_rate", "{:.1%}"),
             row("주간 업로드", "avg_uploads_per_week", "{:.1f}회"),
             row("도달 효율", "avg_reach_ratio", "{:.0%}")]

    gens = (members[members["cohort"] == cohort]
            .groupby("group")["generation"].unique())
    detail = []
    for g in groups:
        if g in gens.index:
            detail.append(f"{g}: " + "·".join(sorted(set(gens[g]))))
    return "\n".join(lines) + "\n\n" + "  \n".join(detail) + "\n"


def build_outputs(vids, members, cohort_summary):
    members.to_csv(DATA / "member_metrics.csv", index=False)
    cohort_summary.to_csv(DATA / "cohort_summary.csv", index=False)
    meta = _meta()
    site_data = dict(
        meta=meta,
        members=json.loads(members.to_json(orient="records", force_ascii=False)),
        cohorts=json.loads(cohort_summary.to_json(orient="records", force_ascii=False)))
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2),
                                    encoding="utf-8")

    comparable = comparable_cohorts(cohort_summary)
    lonely = sorted(set(cohort_summary["cohort"]) - set(comparable))

    md = [f"# 프로젝트 6 · 경쟁사 비교 (데뷔 코호트 매칭)", "",
          f"- 대상 {meta['n_channels']}채널 · 채널당 최근 {meta['recent_per_channel']}개 영상. "
          f"수집 {meta['fetched_at'][:10]}",
          "- 표본은 **기수 전원**이다. 개인 인지도로 고르지 않는다 — 유명한 사람만 "
          "뽑으면 그 표본이 곧 생존편향이다.",
          "- 그룹 비교는 **같은 코호트 안에서만** 한다. 구독자는 누적 지표라 데뷔 "
          "시기가 다르면 비교가 성립하지 않는다.",
          ""]

    md += ["## 핵심 요약", ""]
    for c in comparable:
        md += [f"### {c}", "", _cohort_table(members, cohort_summary, c), ""]

    if lonely:
        md += ["### 비교군 없는 코호트", "",
               "다음 코호트는 같은 시기에 데뷔한 다른 그룹 표본이 없어 그룹 비교를 "
               "하지 않았다. 숫자는 멤버 표에만 남긴다.", ""]
        for c in lonely:
            who = members[members["cohort"] == c]
            md.append(f"- **{c}** — " + ", ".join(
                f"{r.name_ko}({r.group}, {r.months_since_debut:.0f}개월)"
                for r in who.itertuples()))
        md.append("")

    no_cohort = members[members["cohort"].isna()]
    if len(no_cohort):
        md += ["> 코호트 구간(common/config.py `COHORT_BINS`)에 들어가지 않은 멤버: "
               + ", ".join(no_cohort["name_ko"]) + " — 버리지 않고 멤버 표에는 남겼다.", ""]

    md += ["## 읽는 법", "",
           "- **구독자 중앙값**: 같은 코호트 안에서만 비교한다. 코호트가 다르면 이 값의 "
           "차이는 대부분 활동 기간 차이다.",
           "- **월평균 구독자 획득**: 구독자 ÷ 데뷔 후 경과 개월. 코호트가 달라도 속도는 "
           "견줄 수 있지만, 데뷔 직후 급증 구간이 포함되므로 신생 채널에 유리하게 "
           "치우친다. 보조 지표로만 쓴다.",
           "- **도달 효율·참여율**: 누적이 아니라 최근 영상 기준이라 데뷔 시기 영향이 "
           "가장 적다. 코호트 간 비교에 그나마 가장 안전한 지표다.",
           "",
           "> 표본 주의: 그룹 전체가 아니라 **선택된 기수 전원**이다. 홀로라이브는 "
           "StelLive·이세계아이돌과 데뷔 시기가 겹치는 기수만 넣었으므로, 여기 숫자를 "
           "홀로라이브 전체 평균으로 읽으면 안 된다.",
           ""]
    (HERE / "REPORT.md").write_text("\n".join(md), encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("코호트 × 그룹 요약", """
SELECT cohort AS 코호트, "group" AS 그룹, n_members AS 인원,
       ROUND(avg_months_since_debut,1) AS 경과개월,
       CAST(median_subscribers AS INT) AS 구독자중앙값,
       CAST(median_subs_per_month AS INT) AS 월평균획득,
       ROUND(avg_engagement_rate*100,2) AS 참여율_pct,
       ROUND(avg_reach_ratio*100,1) AS 도달효율_pct
FROM cohort_summary ORDER BY 코호트, 구독자중앙값 DESC;"""),
    ("코호트 안에서의 구독자 순위", """
SELECT cohort AS 코호트, rank_in_cohort AS 순위, "group" AS 그룹, name_ko AS 멤버,
       subscribers AS 구독자, ROUND(months_since_debut,1) AS 경과개월
FROM member_metrics WHERE cohort IS NOT NULL
ORDER BY 코호트, 순위;"""),
    ("월평균 구독자 획득 상위 15명", """
SELECT "group" AS 그룹, name_ko AS 멤버, cohort AS 코호트,
       CAST(subs_per_month AS INT) AS 월평균획득
FROM member_metrics WHERE subs_per_month IS NOT NULL
ORDER BY subs_per_month DESC LIMIT 15;"""),
    ("도달 효율 상위 15명", """
SELECT "group" AS 그룹, name_ko AS 멤버, cohort AS 코호트, subscribers AS 구독자,
       ROUND(reach_ratio*100,0) AS 도달효율_pct
FROM member_metrics ORDER BY reach_ratio DESC LIMIT 15;"""),
]
ANALYSIS_QUERIES = ("-- 경쟁사 비교(데뷔 코호트 매칭) 분석 쿼리 "
                    "(SQLite: sql/competitors.db)\n\n"
                    + "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n")


def main():
    vids, members, cohort_summary = build_metrics()
    build_sql(vids, members, cohort_summary)
    build_charts(vids, members, cohort_summary)
    build_outputs(vids, members, cohort_summary)
    print("\n=== 코호트 × 그룹 요약 ===")
    with pd.option_context("display.width", 200):
        print(cohort_summary.to_string(index=False))


if __name__ == "__main__":
    main()
