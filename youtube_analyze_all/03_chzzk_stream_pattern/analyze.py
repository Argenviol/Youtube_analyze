"""
프로젝트3 · 분석 단계
치지직 방송(VOD replay) 데이터 → 방송 패턴 지표 → SQL → 차트 → 사이트 → 리포트.
  python 03_chzzk_stream_pattern/analyze.py
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
WD = ["월", "화", "수", "목", "금", "토", "일"]


def build_metrics():
    df = config.drop_founder(pd.read_csv(DATA / "streams.csv"))
    ch = config.drop_founder(pd.read_csv(DATA / "chzzk_channels.csv"))
    df["dt"] = pd.to_datetime(df["publish_date"])          # KST naive
    df["hour"] = df["dt"].dt.hour
    df["dow"] = df["dt"].dt.dayofweek
    df["dur_h"] = df["duration_sec"] / 3600
    df["is_game"] = df["category_type"] == "GAME"
    df["is_talk"] = df["category"] == "talk"
    df["is_night"] = df["hour"].isin([0, 1, 2, 3, 4, 5])

    foll = dict(zip(ch["name_en"], ch["followers"]))
    rows = []
    for (name_ko, name_en, unit), g in df.groupby(["name_ko", "name_en", "unit"]):
        span_days = max(1, (g["dt"].max() - g["dt"].min()).days)
        top_cat = g["category"].value_counts().idxmax()
        rows.append(dict(
            name_ko=name_ko, name_en=name_en, unit=unit,
            followers=int(foll.get(name_en, 0)),
            stream_count=len(g),
            span_days=span_days,
            streams_per_week=round(len(g) / (span_days / 7), 2),
            avg_duration_h=round(g["dur_h"].mean(), 2),
            median_duration_h=round(g["dur_h"].median(), 2),
            total_hours=round(g["dur_h"].sum(), 1),
            hours_per_week=round(g["dur_h"].sum() / (span_days / 7), 1),
            avg_start_hour=round(g["hour"].mean(), 1),
            night_share=round(g["is_night"].mean(), 3),
            game_share=round(g["is_game"].mean(), 3),
            talk_share=round(g["is_talk"].mean(), 3),
            top_category=top_cat,
            avg_vod_views=int(g["read_count"].mean()),
        ))
    metrics = pd.DataFrame(rows).sort_values("hours_per_week", ascending=False).reset_index(drop=True)
    metrics.insert(0, "rank", metrics.index + 1)
    return df, metrics


def build_sql(df, metrics):
    SQL.mkdir(parents=True, exist_ok=True)
    streams = df.drop(columns=["dt", "hour", "dow", "dur_h", "is_game", "is_talk", "is_night"]).copy()
    tables = {"streams": streams, "stream_metrics": metrics}
    db.write_sqlite(SQL / "chzzk.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables, primary_keys={"streams": "video_no"})
    db.dump_insert_sql(SQL / "stream_metrics.sql", "stream_metrics", metrics)
    db.dump_insert_sql(SQL / "streams.sql", "streams", streams)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")
    md = ["# 치지직 방송 패턴 분석 쿼리 결과\n", "`sql/chzzk.db`(SQLite) 실행 결과.\n"]
    for title, q in NAMED_QUERIES:
        res = db.run_query(SQL / "chzzk.db", q)
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n")
        md.append(res.to_markdown(index=False)); md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


def _mc(names):
    cmap = config.member_colors(); return [cmap.get(n, "#888") for n in names]


def build_charts(df, metrics):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()

    def hbar(d, col, title, fmt, fname):
        d = d.sort_values(col)
        fig, ax = plt.subplots(figsize=(9, 6))
        bars = ax.barh(d["name_ko"], d[col], color=_mc(d["name_en"]), height=0.72, zorder=3)
        ax.set_title(title); ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        for b, v in zip(bars, d[col]):
            ax.annotate(fmt.format(v), (b.get_width(), b.get_y()+b.get_height()/2), va="center",
                        ha="left", fontsize=9, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
        ax.margins(x=0.16); fig.tight_layout(); fig.savefig(CHARTS / fname, dpi=140); plt.close(fig)

    hbar(metrics, "streams_per_week", "주간 방송 횟수 (최근 방송 기준)", "{:.1f}회", "01_streams_per_week.png")
    hbar(metrics, "avg_duration_h", "평균 방송 시간 (시간)", "{:.1f}h", "02_avg_duration.png")
    hbar(metrics, "hours_per_week", "주간 방송 시간 (시간)", "{:.1f}h", "03_hours_per_week.png")

    # 4. 방송 시작 시간 히트맵 (요일 x 시)
    heat = df.pivot_table(index="dow", columns="hour", values="video_no", aggfunc="count", fill_value=0)
    heat = heat.reindex(index=range(7), columns=range(24), fill_value=0)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    im = ax.imshow(heat.values, aspect="auto", cmap="Purples")
    ax.set_yticks(range(7)); ax.set_yticklabels(WD)
    ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels(range(0, 24, 2))
    ax.set_title("방송 시작 시간 히트맵 (KST · 전체 멤버)"); ax.set_xlabel("시(hour)")
    fig.colorbar(im, ax=ax, label="방송 수", shrink=0.8)
    fig.tight_layout(); fig.savefig(CHARTS / "04_start_heatmap.png", dpi=140); plt.close(fig)

    # 5. 시작 시간 분포
    fig, ax = plt.subplots(figsize=(10, 4.5))
    counts = df["hour"].value_counts().reindex(range(24), fill_value=0)
    ax.bar(counts.index, counts.values, color=config.PALETTE["series"][6], zorder=3, width=0.8)
    ax.set_title("방송 시작 시간 분포 (전체)"); ax.set_xlabel("시(hour)"); ax.set_ylabel("방송 수")
    ax.set_xticks(range(0, 24, 2)); ax.grid(axis="y", zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "05_start_hour_dist.png", dpi=140); plt.close(fig)

    # 6. 인기 카테고리 TOP 12
    topcat = df["category"].value_counts().head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(topcat.index, topcat.values, color=config.PALETTE["series"][0], zorder=3, height=0.72)
    ax.set_title("방송 카테고리 TOP 12 (전체 방송 수)"); ax.grid(axis="x", zorder=0)
    ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
    for b, v in zip(bars, topcat.values):
        ax.annotate(f"{v}", (b.get_width(), b.get_y()+b.get_height()/2), va="center", ha="left",
                    fontsize=9, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
    ax.margins(x=0.1); fig.tight_layout(); fig.savefig(CHARTS / "06_top_categories.png", dpi=140); plt.close(fig)

    # 7. 산점도: 주간 방송횟수 vs 평균 방송시간 (버블=팔로워)
    fig, ax = plt.subplots(figsize=(9, 6.2))
    m = metrics
    ax.scatter(m["streams_per_week"], m["avg_duration_h"], s=(m["followers"]/1000),
               c=_mc(m["name_en"]), alpha=0.75, edgecolors="white", linewidths=1.5, zorder=3)
    for _, r in m.iterrows():
        ax.annotate(r["name_ko"], (r["streams_per_week"], r["avg_duration_h"]),
                    fontsize=9, xytext=(6, 4), textcoords="offset points", color=config.INK["text"])
    ax.set_title("주간 방송 횟수 vs 평균 방송 시간 (버블=팔로워)")
    ax.set_xlabel("주간 방송 횟수"); ax.set_ylabel("평균 방송 시간 (h)"); ax.grid(True, zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "07_freq_vs_duration.png", dpi=140); plt.close(fig)

    # 8. 게임 vs 토크 비중 (스택 바)
    d = metrics.sort_values("game_share")
    fig, ax = plt.subplots(figsize=(9, 6))
    y = range(len(d))
    ax.barh(y, d["game_share"]*100, color=config.PALETTE["series"][1], label="게임", zorder=3)
    ax.barh(y, (1-d["game_share"])*100, left=d["game_share"]*100,
            color=config.PALETTE["series"][2], label="토크/기타", zorder=3)
    ax.set_yticks(list(y)); ax.set_yticklabels(d["name_ko"])
    ax.set_title("방송 내용 구성: 게임 vs 토크/기타 (%)"); ax.set_xlim(0, 100)
    ax.legend(frameon=False, ncol=2, loc="lower right"); ax.grid(axis="x", zorder=0); ax.spines["left"].set_visible(False)
    fig.tight_layout(); fig.savefig(CHARTS / "08_game_vs_talk.png", dpi=140); plt.close(fig)

    print(f"차트 8종 -> {CHARTS}")


def build_outputs(df, metrics):
    metrics.to_csv(DATA / "stream_metrics.csv", index=False)
    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    heat = df.pivot_table(index="dow", columns="hour", values="video_no", aggfunc="count", fill_value=0)
    heat = heat.reindex(index=range(7), columns=range(24), fill_value=0)
    topcat = df["category"].value_counts().head(12)
    site_data = dict(
        meta=meta,
        members=json.loads(metrics.to_json(orient="records", force_ascii=False)),
        heatmap=heat.values.tolist(),
        top_categories=[{"name": k, "count": int(v)} for k, v in topcat.items()],
        hour_dist=[int(df["hour"].value_counts().reindex(range(24), fill_value=0)[h]) for h in range(24)],
    )
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    grind = metrics.iloc[0]
    longest = metrics.iloc[metrics["avg_duration_h"].argmax()]
    freq = metrics.iloc[metrics["streams_per_week"].argmax()]
    night = metrics.iloc[metrics["night_share"].argmax()]
    peak_hour = int(np.argmax(site_data["hour_dist"]))
    md = f"""# 프로젝트 3 · StelLive 치지직 방송 패턴 분석

- 데이터 소스: 치지직(Chzzk) 비공식 API — 다시보기(VOD replay) {meta['n_streams']}건, 수집 {meta['fetched_at'][:10]}
- 멤버 {meta['n_members']}명, 멤버당 최근 최대 {meta['max_items']}개 방송

## 핵심 요약
- **주간 방송 시간 1위**: {grind['name_ko']} — 주 {grind['hours_per_week']:.0f}시간
- **최장 평균 방송**: {longest['name_ko']} — 회당 평균 {longest['avg_duration_h']:.1f}시간
- **최다 방송 빈도**: {freq['name_ko']} — 주 {freq['streams_per_week']:.1f}회
- **최고 심야형(0~5시 시작)**: {night['name_ko']} — {night['night_share']*100:.0f}%
- 전체 방송이 가장 많이 시작되는 시간대: **{peak_hour}시** (KST)

## 산출물
- `data/streams.csv` 방송별(시작시각·길이·카테고리·조회), `data/stream_metrics.csv` 멤버 집계
- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과
- `charts/` 차트 8종(빈도·길이·주간시간·시작시간 히트맵·시간분포·카테고리·산점도·게임vs토크)
- `site/index.html` 인터랙티브 대시보드(히트맵 포함)
"""
    (HERE / "REPORT.md").write_text(md, encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("주간 방송 시간 랭킹", """
SELECT rank AS 순위, name_ko AS 멤버, streams_per_week AS 주간횟수,
       avg_duration_h AS 평균시간, hours_per_week AS 주간시간
FROM stream_metrics ORDER BY hours_per_week DESC;"""),
    ("심야 방송 비중(0~5시 시작)", """
SELECT name_ko AS 멤버, ROUND(night_share*100,0) AS 심야비중_pct,
       avg_start_hour AS 평균시작시
FROM stream_metrics ORDER BY night_share DESC;"""),
    ("게임 vs 토크 성향", """
SELECT name_ko AS 멤버, ROUND(game_share*100,0) AS 게임_pct,
       ROUND(talk_share*100,0) AS 토크_pct, top_category AS 주력카테고리
FROM stream_metrics ORDER BY game_share DESC;"""),
    ("인기 방송 카테고리 TOP 10", """
SELECT category AS 카테고리, COUNT(*) AS 방송수
FROM streams GROUP BY category ORDER BY 방송수 DESC LIMIT 10;"""),
    ("시작 시간대별 방송 수", """
SELECT CAST(substr(publish_date,12,2) AS INT) AS 시작시,
       COUNT(*) AS 방송수
FROM streams GROUP BY 시작시 ORDER BY 방송수 DESC LIMIT 8;"""),
]
ANALYSIS_QUERIES = "-- StelLive 치지직 방송 패턴 분석 쿼리 (SQLite: sql/chzzk.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    df, metrics = build_metrics()
    build_sql(df, metrics)
    build_charts(df, metrics)
    build_outputs(df, metrics)
    print("\n=== 방송 패턴 요약 ===")
    cols = ["rank", "name_ko", "streams_per_week", "avg_duration_h", "hours_per_week",
            "night_share", "game_share", "top_category"]
    with pd.option_context("display.width", 220):
        print(metrics[cols].to_string(index=False))


if __name__ == "__main__":
    main()
