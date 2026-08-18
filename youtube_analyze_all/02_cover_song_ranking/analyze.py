"""
프로젝트2 · 분석 단계
커버곡 데이터 → 파생지표 → SQL 산출물 → 차트 → 사이트 데이터 → 리포트.
  python 02_cover_song_ranking/analyze.py
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


def build_metrics():
    df = pd.read_csv(DATA / "covers.csv")
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    for c in ("views", "likes", "comments"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["engagement_rate"] = np.where(df["views"] > 0,
                                     (df["likes"].fillna(0) + df["comments"].fillna(0)) / df["views"], np.nan)

    rows = []
    for (cid, name_ko, name_en, unit), g in df.groupby(["channel_id", "name_ko", "name_en", "unit"]):
        best = g.loc[g["views"].idxmax()]
        rows.append(dict(
            channel_id=cid, name_ko=name_ko, name_en=name_en, unit=unit,
            cover_count=len(g),
            total_views=int(g["views"].sum()),
            avg_views=round(g["views"].mean(), 1),
            median_views=round(g["views"].median(), 1),
            max_views=int(g["views"].max()),
            best_cover=str(best["title"]),
            total_likes=int(g["likes"].fillna(0).sum()),
            avg_engagement_rate=round(g["engagement_rate"].mean(), 5),
            collab_share=round(g["is_collab"].mean(), 3),
        ))
    metrics = pd.DataFrame(rows).sort_values("total_views", ascending=False).reset_index(drop=True)
    metrics.insert(0, "rank", metrics.index + 1)
    return df, metrics


def build_sql(df, metrics):
    SQL.mkdir(parents=True, exist_ok=True)
    covers = df.copy()
    covers["published_at"] = covers["published_at"].astype(str)
    covers["is_collab"] = covers["is_collab"].astype(int)
    tables = {"covers": covers, "cover_metrics": metrics}
    db.write_sqlite(SQL / "covers.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables, primary_keys={"covers": "video_id"})
    db.dump_insert_sql(SQL / "covers.sql", "covers", covers)
    db.dump_insert_sql(SQL / "cover_metrics.sql", "cover_metrics", metrics)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")

    md = ["# 커버곡 분석 쿼리 실행 결과\n", "`sql/covers.db`(SQLite) 실행 결과입니다.\n"]
    for title, q in NAMED_QUERIES:
        res = db.run_query(SQL / "covers.db", q)
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n")
        md.append(res.to_markdown(index=False))
        md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


def _mcolors(names):
    cmap = config.member_colors()
    return [cmap.get(n, "#888") for n in names]


def build_charts(df, metrics):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()

    def hbar(d, col, title, fmt, fname, labelcol="name_ko"):
        d = d.sort_values(col)
        fig, ax = plt.subplots(figsize=(9, 6))
        bars = ax.barh(d[labelcol], d[col], color=_mcolors(d["name_en"]), height=0.72, zorder=3)
        ax.set_title(title); ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        for b, v in zip(bars, d[col]):
            ax.annotate(fmt.format(v), (b.get_width(), b.get_y() + b.get_height()/2),
                        va="center", ha="left", fontsize=9, color=config.INK["text"],
                        xytext=(4, 0), textcoords="offset points")
        ax.margins(x=0.16); fig.tight_layout(); fig.savefig(CHARTS / fname, dpi=140); plt.close(fig)

    # 1. Top 15 커버 (조회수)
    top = df.sort_values("views", ascending=False).head(15).copy()
    top["short"] = top["title"].str.slice(0, 34) + "…"
    fig, ax = plt.subplots(figsize=(10, 7))
    d = top.sort_values("views")
    bars = ax.barh(range(len(d)), d["views"], color=_mcolors(d["name_en"]), height=0.74, zorder=3)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels([f"{s}" for s in d["short"]], fontsize=9)
    ax.set_title("커버곡 조회수 TOP 15")
    ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
    for b, v, nm in zip(bars, d["views"], d["name_ko"]):
        ax.annotate(f"{v/1e6:.1f}M · {nm}", (b.get_width(), b.get_y()+b.get_height()/2),
                    va="center", ha="left", fontsize=8, color=config.INK["text"],
                    xytext=(4, 0), textcoords="offset points")
    ax.margins(x=0.22); fig.tight_layout(); fig.savefig(CHARTS / "01_top15_covers.png", dpi=140); plt.close(fig)

    # 2~5
    hbar(metrics, "cover_count", "멤버별 커버곡 수", "{:.0f}", "02_cover_count.png")
    hbar(metrics.assign(tv=metrics["total_views"]/1e6), "tv", "멤버별 커버곡 총 조회수 (백만)", "{:.1f}M", "03_total_views.png")
    hbar(metrics.assign(av=metrics["avg_views"]/1e6), "av", "커버곡 평균 조회수 (백만)", "{:.2f}M", "04_avg_views.png")
    hbar(metrics.assign(er=metrics["avg_engagement_rate"]*100), "er", "커버곡 평균 참여율 %", "{:.1f}%", "05_engagement.png")

    # 6. 산점도: 커버 수 vs 평균 조회수
    fig, ax = plt.subplots(figsize=(9, 6.2))
    m = metrics
    ax.scatter(m["cover_count"], m["avg_views"], s=(m["total_views"]/m["total_views"].max()*900)+60,
               c=_mcolors(m["name_en"]), alpha=0.75, edgecolors="white", linewidths=1.5, zorder=3)
    for _, r in m.iterrows():
        ax.annotate(r["name_ko"], (r["cover_count"], r["avg_views"]),
                    fontsize=9, xytext=(6, 4), textcoords="offset points", color=config.INK["text"])
    ax.set_title("커버 수 vs 평균 조회수 (버블=총 조회수)")
    ax.set_xlabel("커버곡 수"); ax.set_ylabel("평균 조회수")
    ax.grid(True, zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "06_count_vs_avg.png", dpi=140); plt.close(fig)

    # 7. 멤버별 조회수 분포 (박스플롯, 로그축) — 중앙값 순
    order = metrics.sort_values("median_views")["name_ko"].tolist()
    groups = [df[df["name_ko"] == n]["views"].dropna().values for n in order]
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(groups, orientation="horizontal", patch_artist=True, widths=0.6,
                    medianprops=dict(color=config.INK["text"], linewidth=1.5))
    cmap = config.member_colors()
    en_by_ko = {r["name_ko"]: r["name_en"] for r in config.member_rows()}
    for patch, n in zip(bp["boxes"], order):
        patch.set_facecolor(cmap.get(en_by_ko.get(n), "#888")); patch.set_alpha(0.8)
    ax.set_yticklabels(order); ax.set_xscale("log")
    ax.set_title("멤버별 커버곡 조회수 분포 (로그 스케일)")
    ax.set_xlabel("조회수 (log)"); ax.grid(axis="x", zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "07_view_distribution.png", dpi=140); plt.close(fig)

    print(f"차트 7종 -> {CHARTS}")


def build_outputs(df, metrics):
    metrics.to_csv(DATA / "cover_metrics.csv", index=False)
    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    top = df.sort_values("views", ascending=False).head(20)[
        ["name_ko", "title", "views", "likes", "comments", "published_at"]].copy()
    top["published_at"] = top["published_at"].astype(str)
    site_data = dict(
        meta=meta,
        members=json.loads(metrics.to_json(orient="records", force_ascii=False)),
        top_covers=json.loads(top.to_json(orient="records", force_ascii=False)),
    )
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    king = metrics.iloc[0]
    most = metrics.iloc[metrics["cover_count"].argmax()]
    besteff = metrics.iloc[metrics["avg_views"].argmax()]
    topcover = df.sort_values("views", ascending=False).iloc[0]
    md = f"""# 프로젝트 2 · StelLive 커버곡 성과 랭킹 분석

- 데이터 소스: YouTube Data API v3 (채널 검색 + 영상 지표), 수집 {meta['fetched_at'][:10]}
- 멤버 {meta['n_members']}명 · 커버곡 {meta['n_covers']}개

## 핵심 요약
- **커버 총 조회수 1위**: {king['name_ko']} — {king['total_views']/1e6:.1f}M ({king['cover_count']}곡)
- **최다 커버 업로드**: {most['name_ko']} — {most['cover_count']}곡
- **곡당 평균 조회수 1위**: {besteff['name_ko']} — {besteff['avg_views']/1e6:.2f}M
- **역대 최고 조회 커버**: {topcover['name_ko']} — {topcover['views']/1e6:.1f}M
  - 「{topcover['title']}」

## 산출물
- `data/covers.csv` 커버곡 원천 지표, `data/cover_metrics.csv` 멤버 집계
- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과
- `charts/` 차트 7종(TOP15·커버수·총조회수·평균조회수·참여율·산점도·분포)
- `site/index.html` 인터랙티브 대시보드
"""
    (HERE / "REPORT.md").write_text(md, encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("커버곡 조회수 TOP 15", """
SELECT name_ko AS 멤버, title AS 곡, views AS 조회수, likes AS 좋아요
FROM covers ORDER BY views DESC LIMIT 15;"""),
    ("멤버별 커버 성과 랭킹", """
SELECT rank AS 순위, name_ko AS 멤버, cover_count AS 곡수,
       total_views AS 총조회수, CAST(avg_views AS INT) AS 평균조회수
FROM cover_metrics ORDER BY total_views DESC;"""),
    ("곡당 평균 조회수 상위(5곡 이상)", """
SELECT name_ko AS 멤버, cover_count AS 곡수, CAST(avg_views AS INT) AS 평균조회수
FROM cover_metrics WHERE cover_count>=5 ORDER BY avg_views DESC;"""),
    ("멤버별 최고 커버", """
SELECT name_ko AS 멤버, best_cover AS 최고커버, max_views AS 조회수
FROM cover_metrics ORDER BY max_views DESC;"""),
    ("유닛별 커버 요약", """
SELECT unit AS 유닛, COUNT(*) AS 멤버수, SUM(cover_count) AS 총곡수,
       SUM(total_views) AS 총조회수
FROM cover_metrics GROUP BY unit ORDER BY 총조회수 DESC;"""),
    ("솔로 vs 콜라보 비중", """
SELECT name_ko AS 멤버, ROUND(collab_share*100,0) AS 콜라보비중_pct, cover_count AS 곡수
FROM cover_metrics ORDER BY collab_share DESC;"""),
]
ANALYSIS_QUERIES = "-- StelLive 커버곡 분석 쿼리 (SQLite: sql/covers.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    df, metrics = build_metrics()
    build_sql(df, metrics)
    build_charts(df, metrics)
    build_outputs(df, metrics)
    print("\n=== 멤버별 커버 성과 ===")
    cols = ["rank", "name_ko", "unit", "cover_count", "total_views", "avg_views", "max_views"]
    with pd.option_context("display.width", 200):
        print(metrics[cols].to_string(index=False))


if __name__ == "__main__":
    main()
