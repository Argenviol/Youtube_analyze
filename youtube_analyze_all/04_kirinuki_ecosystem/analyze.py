"""
프로젝트4 · 분석 단계
키리누키(팬 클립) 생태계: 멤버별 관심도 + 팬채널 규모/전문성.
  python 04_kirinuki_ecosystem/analyze.py
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
    df = pd.read_csv(DATA / "clips.csv")
    for c in ("views", "likes", "comments", "clip_channel_subs"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 멤버별 생태계 지표
    mrows = []
    for (ko, en, unit), g in df.groupby(["source_member_ko", "source_member_en", "unit"]):
        best = g.loc[g["views"].idxmax()]
        mrows.append(dict(
            name_ko=ko, name_en=en, unit=unit,
            clip_count=len(g),
            total_clip_views=int(g["views"].sum()),
            avg_clip_views=round(g["views"].mean(), 1),
            fan_channels=g["clip_channel_id"].nunique(),
            top_clip=str(best["title"]), top_clip_views=int(best["views"]),
            top_channel=str(best["clip_channel_title"]),
        ))
    members = pd.DataFrame(mrows).sort_values("total_clip_views", ascending=False).reset_index(drop=True)
    members.insert(0, "rank", members.index + 1)

    # 팬채널별 지표
    crows = []
    for (cid, title), g in df.groupby(["clip_channel_id", "clip_channel_title"]):
        crows.append(dict(
            clip_channel_id=cid, clip_channel_title=title,
            subs=int(g["clip_channel_subs"].dropna().iloc[0]) if g["clip_channel_subs"].notna().any() else None,
            clip_count=len(g),
            total_views=int(g["views"].sum()),
            members_covered=g["source_member_ko"].nunique(),
            primary_member=g["source_member_ko"].value_counts().idxmax(),
        ))
    channels = pd.DataFrame(crows).sort_values("total_views", ascending=False).reset_index(drop=True)
    channels.insert(0, "rank", channels.index + 1)
    return df, members, channels


def build_sql(df, members, channels):
    SQL.mkdir(parents=True, exist_ok=True)
    tables = {"clips": df, "member_ecosystem": members, "channel_ecosystem": channels}
    db.write_sqlite(SQL / "kirinuki.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables,
                       primary_keys={"clips": "video_id", "channel_ecosystem": "clip_channel_id"})
    db.dump_insert_sql(SQL / "clips.sql", "clips", df)
    db.dump_insert_sql(SQL / "member_ecosystem.sql", "member_ecosystem", members)
    db.dump_insert_sql(SQL / "channel_ecosystem.sql", "channel_ecosystem", channels)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")
    md = ["# 키리누키 생태계 분석 쿼리 결과\n", "`sql/kirinuki.db`(SQLite) 실행 결과.\n"]
    for title, q in NAMED_QUERIES:
        res = db.run_query(SQL / "kirinuki.db", q)
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n"); md.append(res.to_markdown(index=False)); md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


def _mc(names):
    cmap = config.member_colors(); return [cmap.get(n, "#888") for n in names]


def build_charts(df, members, channels):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()

    def hbar(d, col, title, fmt, fname, labels="name_ko", colors=None):
        d = d.sort_values(col)
        fig, ax = plt.subplots(figsize=(9, 6))
        cols = colors(d) if colors else _mc(d["name_en"])
        bars = ax.barh(d[labels], d[col], color=cols, height=0.72, zorder=3)
        ax.set_title(title); ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        for b, v in zip(bars, d[col]):
            ax.annotate(fmt.format(v), (b.get_width(), b.get_y()+b.get_height()/2), va="center", ha="left",
                        fontsize=9, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
        ax.margins(x=0.16); fig.tight_layout(); fig.savefig(CHARTS / fname, dpi=140); plt.close(fig)

    hbar(members, "clip_count", "멤버별 팬 클립 수", "{:.0f}", "01_clips_per_member.png")
    hbar(members.assign(tv=members["total_clip_views"]/1e6), "tv", "멤버별 팬 클립 총 조회수 (백만)", "{:.1f}M", "02_views_per_member.png")
    hbar(members, "fan_channels", "멤버를 다루는 팬채널 수 (관심도)", "{:.0f}", "03_channels_per_member.png")

    # 4. 상위 팬채널 (총 조회수)
    topc = channels.head(12).sort_values("total_views")
    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    bars = ax.barh(topc["clip_channel_title"], topc["total_views"]/1e6,
                   color=config.PALETTE["series"][4], height=0.72, zorder=3)
    ax.set_title("상위 키리누키 채널 · 총 클립 조회수 (백만)")
    ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
    for b, v, n in zip(bars, topc["total_views"]/1e6, topc["clip_count"]):
        ax.annotate(f"{v:.2f}M · {n}개", (b.get_width(), b.get_y()+b.get_height()/2), va="center", ha="left",
                    fontsize=8, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
    ax.margins(x=0.2); fig.tight_layout(); fig.savefig(CHARTS / "04_top_channels.png", dpi=140); plt.close(fig)

    # 5. 팬채널 전문성: 다루는 멤버 수 분포
    dist = channels["members_covered"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(dist.index, dist.values, color=config.PALETTE["series"][2], zorder=3, width=0.7)
    ax.set_title("팬채널 전문성: 한 채널이 다루는 멤버 수"); ax.set_xlabel("다루는 멤버 수")
    ax.set_ylabel("채널 수"); ax.grid(axis="y", zorder=0)
    for x, y in zip(dist.index, dist.values):
        ax.annotate(str(y), (x, y), ha="center", va="bottom", fontsize=9, color=config.INK["text"], xytext=(0, 2), textcoords="offset points")
    fig.tight_layout(); fig.savefig(CHARTS / "05_channel_specialization.png", dpi=140); plt.close(fig)

    # 6. 산점도: 클립 수 vs 총 조회수 (버블=팬채널 수)
    fig, ax = plt.subplots(figsize=(9, 6.2))
    m = members
    ax.scatter(m["clip_count"], m["total_clip_views"]/1e6, s=m["fan_channels"]*22,
               c=_mc(m["name_en"]), alpha=0.75, edgecolors="white", linewidths=1.5, zorder=3)
    for _, r in m.iterrows():
        ax.annotate(r["name_ko"], (r["clip_count"], r["total_clip_views"]/1e6),
                    fontsize=9, xytext=(6, 4), textcoords="offset points", color=config.INK["text"])
    ax.set_title("클립 수 vs 총 조회수 (버블=팬채널 수)")
    ax.set_xlabel("클립 수"); ax.set_ylabel("총 조회수 (백만)"); ax.grid(True, zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "06_count_vs_views.png", dpi=140); plt.close(fig)
    print(f"차트 6종 -> {CHARTS}")


def build_outputs(df, members, channels):
    members.to_csv(DATA / "member_ecosystem.csv", index=False)
    channels.to_csv(DATA / "channel_ecosystem.csv", index=False)
    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    site_data = dict(
        meta=meta,
        members=json.loads(members.to_json(orient="records", force_ascii=False)),
        channels=json.loads(channels.head(20).to_json(orient="records", force_ascii=False)),
        specialization=[{"members": int(k), "channels": int(v)}
                        for k, v in channels["members_covered"].value_counts().sort_index().items()],
    )
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    hot = members.iloc[0]
    mostch = members.iloc[members["fan_channels"].argmax()]
    bigch = channels.iloc[0]
    total_views = int(members["total_clip_views"].sum())
    md = f"""# 프로젝트 4 · StelLive 키리누키(2차창작) 생태계 분석

- 데이터 소스: YouTube Data API v3 (멤버명+키리누키/클립/切り抜き 검색), 수집 {meta['fetched_at'][:10]}
- 공식 채널 제외 후 팬 제작 클립만 집계: 클립 {meta['n_clips']}개 · 팬채널 {meta['n_clip_channels']}개
- 필터: {meta.get('filter','제목/채널명 키리누키·클립 토큰')}

## 핵심 요약
- **팬 클립 총 조회수 1위**: {hot['name_ko']} — {hot['total_clip_views']/1e6:.1f}M ({hot['clip_count']}개 클립)
- **가장 많은 팬채널이 다루는 멤버**: {mostch['name_ko']} — {mostch['fan_channels']}개 채널
- **최대 키리누키 채널**: {bigch['clip_channel_title']} — 총 {bigch['total_views']/1e6:.1f}M ({bigch['clip_count']}개)
- 생태계 표본 합계 조회수: {total_views/1e6:.1f}M

## 산출물
- `data/clips.csv` 클립 원천, `member_ecosystem.csv`·`channel_ecosystem.csv` 집계
- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과
- `charts/` 차트 6종(멤버별 클립수·조회수·팬채널수·상위채널·전문성·산점도)
- `site/index.html` 인터랙티브 대시보드

> 방법론 주의: 유튜브 검색 상위 표본 기반이라 생태계 전수가 아닌 **대표 표본**입니다.
> 제목/채널명에 키리누키·클립 토큰이 없는 클립은 제외되어 실제 규모는 더 클 수 있습니다.
"""
    (HERE / "REPORT.md").write_text(md, encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("멤버별 키리누키 생태계", """
SELECT rank AS 순위, name_ko AS 멤버, clip_count AS 클립수,
       total_clip_views AS 총조회수, fan_channels AS 팬채널수
FROM member_ecosystem ORDER BY total_clip_views DESC;"""),
    ("상위 키리누키 채널 TOP 10", """
SELECT rank AS 순위, clip_channel_title AS 채널, subs AS 구독자,
       clip_count AS 클립수, total_views AS 총조회수, primary_member AS 주력멤버
FROM channel_ecosystem ORDER BY total_views DESC LIMIT 10;"""),
    ("팬채널 전문성 분포(다루는 멤버 수)", """
SELECT members_covered AS 다루는멤버수, COUNT(*) AS 채널수
FROM channel_ecosystem GROUP BY members_covered ORDER BY members_covered;"""),
    ("멤버별 최고 조회 클립", """
SELECT name_ko AS 멤버, top_clip AS 최고클립, top_clip_views AS 조회수, top_channel AS 제작채널
FROM member_ecosystem ORDER BY top_clip_views DESC;"""),
]
ANALYSIS_QUERIES = "-- StelLive 키리누키 생태계 분석 쿼리 (SQLite: sql/kirinuki.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    df, members, channels = build_metrics()
    build_sql(df, members, channels)
    build_charts(df, members, channels)
    build_outputs(df, members, channels)
    print("\n=== 멤버별 키리누키 생태계 ===")
    with pd.option_context("display.width", 200):
        print(members[["rank", "name_ko", "clip_count", "total_clip_views", "fan_channels"]].to_string(index=False))


if __name__ == "__main__":
    main()
