"""
프로젝트1 · 분석 단계
수집한 데이터로 파생지표 계산 → SQL 산출물(스키마/INSERT/분석쿼리/SQLite) →
matplotlib 차트(PNG) → 사이트용 JSON → 요약 리포트(markdown).

  python 01_member_channel_performance/analyze.py
"""
from __future__ import annotations

import json
import re
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

ISO_DUR = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def dur_seconds(s: str) -> int:
    if not isinstance(s, str):
        return 0
    m = ISO_DUR.fullmatch(s)
    if not m:
        return 0
    h, mi, se = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + se


# ---------------------------------------------------------------------------
# 1) 로드 & 파생지표
# ---------------------------------------------------------------------------
def build_metrics():
    ch = pd.read_csv(DATA / "channels.csv")
    vids = pd.read_csv(DATA / "videos.csv")

    vids["published_at"] = pd.to_datetime(vids["published_at"], utc=True)
    vids["published_kst"] = vids["published_at"].dt.tz_convert("Asia/Seoul")
    vids["dur_sec"] = vids["duration"].map(dur_seconds)
    vids["is_short"] = vids["dur_sec"].between(1, 60)
    for col in ("views", "likes", "comments"):
        vids[col] = pd.to_numeric(vids[col], errors="coerce")
    vids["engagement"] = (vids["likes"].fillna(0) + vids["comments"].fillna(0))
    # 비율 지표는 조회수가 자리를 잡은 영상만 쓴다. 방금 올라온 영상은 좋아요·댓글보다
    # 조회수 집계가 훨씬 늦게 붙어서, views>0 가드만으로는 "조회수 1 · 좋아요 443"
    # 같은 행이 통과한다. 실제로 2026-08-25 수집에서 이 한 행이 마시로의 평균 참여율을
    # 4.97% -> 1028.9% 로 폭파시켰다. 절대 지표(조회수 합 등)에는 그대로 포함한다.
    RATE_MIN_VIEWS = 1000
    rate_ok = vids["views"] >= RATE_MIN_VIEWS
    vids["engagement_rate"] = np.where(rate_ok, vids["engagement"] / vids["views"], np.nan)
    vids["like_rate"] = np.where(rate_ok, vids["likes"] / vids["views"], np.nan)

    rows = []
    for _, c in ch.iterrows():
        v = vids[vids["channel_id"] == c["channel_id"]]
        span_days = (v["published_at"].max() - v["published_at"].min()).days or 1
        n = len(v)
        created = pd.to_datetime(c["created_at"], utc=True)
        age_years = (pd.Timestamp.now(tz="UTC") - created).days / 365.25
        rows.append(dict(
            channel_id=c["channel_id"], name_ko=c["name_ko"], name_en=c["name_en"],
            unit=c["unit"], role=c["role"], handle=c["handle"],
            subscribers=int(c["subscribers"]),
            total_views=int(c["total_views"]),
            video_count=int(c["video_count"]),
            created_at=c["created_at"],
            channel_age_years=round(age_years, 2),
            recent_n=n,
            recent_avg_views=round(v["views"].mean(), 1),
            recent_median_views=round(v["views"].median(), 1),
            recent_max_views=int(v["views"].max()),
            recent_avg_engagement_rate=round(v["engagement_rate"].mean(), 5),
            recent_avg_like_rate=round(v["like_rate"].mean(), 5),
            uploads_per_week=round((n - 1) / (span_days / 7), 2),
            uploads_per_month=round((n - 1) / (span_days / 30.44), 2),
            shorts_share=round(v["is_short"].mean(), 3),
            reach_ratio=round(v["views"].mean() / c["subscribers"], 3),   # 최근영상 평균조회수 / 구독자
            lifetime_views_per_sub=round(c["total_views"] / c["subscribers"], 1),
            lifetime_views_per_video=round(c["total_views"] / c["video_count"], 1),
        ))
    metrics = pd.DataFrame(rows).sort_values("subscribers", ascending=False).reset_index(drop=True)
    metrics.insert(0, "rank_subs", metrics.index + 1)
    return ch, vids, metrics


# ---------------------------------------------------------------------------
# 2) SQL 산출물
# ---------------------------------------------------------------------------
def build_sql(ch, vids, metrics):
    SQL.mkdir(parents=True, exist_ok=True)
    vids_out = vids.drop(columns=["published_kst"]).copy()
    vids_out["published_at"] = vids_out["published_at"].astype(str)
    tables = {"channels": ch, "videos": vids_out, "channel_metrics": metrics}

    db.write_sqlite(SQL / "stellive.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables,
                       primary_keys={"channels": "channel_id", "videos": "video_id"})
    db.dump_insert_sql(SQL / "channels.sql", "channels", ch)
    db.dump_insert_sql(SQL / "channel_metrics.sql", "channel_metrics", metrics)
    db.dump_insert_sql(SQL / "videos.sql", "videos", vids_out)

    queries = ANALYSIS_QUERIES
    (SQL / "analysis_queries.sql").write_text(queries, encoding="utf-8")

    # 쿼리 실행 결과를 markdown으로 저장
    md = ["# 분석 쿼리 실행 결과\n",
          "`sql/stellive.db`(SQLite)에 대해 `analysis_queries.sql`을 실행한 결과입니다.\n"]
    for title, q in NAMED_QUERIES:
        res = db.run_query(SQL / "stellive.db", q)
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n")
        md.append(res.to_markdown(index=False))
        md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL 산출물 -> {SQL}")


# ---------------------------------------------------------------------------
# 3) 차트
# ---------------------------------------------------------------------------
def _mcolors(names):
    cmap = config.member_colors()
    return [cmap.get(n, "#888888") for n in names]


def build_charts(ch, vids, metrics):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    talents = metrics[metrics["role"] == "talent"].copy()

    def hbar(df, col, title, fmt="{:,.0f}", fname=None, ascending=True):
        d = df.sort_values(col, ascending=ascending)
        fig, ax = plt.subplots(figsize=(9, 6))
        colors = _mcolors(d["name_en"])
        bars = ax.barh(d["name_ko"], d[col], color=colors, height=0.7, zorder=3)
        ax.set_title(title)
        ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        for b, v in zip(bars, d[col]):
            ax.annotate(fmt.format(v), (b.get_width(), b.get_y() + b.get_height() / 2),
                        va="center", ha="left", fontsize=9, color=config.INK["text"],
                        xytext=(4, 0), textcoords="offset points")
        ax.margins(x=0.15)
        fig.tight_layout()
        fig.savefig(CHARTS / fname, dpi=140)
        plt.close(fig)

    # 1. 구독자 (전체 11명, 강지 포함)
    hbar(metrics, "subscribers", "멤버별 구독자 수 (강지=창립자 포함)",
         fmt="{:,.0f}", fname="01_subscribers.png")
    # 2. 최근 영상 평균 조회수 (탤런트)
    hbar(talents, "recent_avg_views", "최근 50개 영상 평균 조회수",
         fmt="{:,.0f}", fname="02_recent_avg_views.png")
    # 3. 참여율
    hbar(talents.assign(er_pct=talents["recent_avg_engagement_rate"] * 100),
         "er_pct", "평균 참여율 (좋아요+댓글)/조회수 · %", fmt="{:.1f}%",
         fname="03_engagement_rate.png")
    # 4. 업로드 주기
    hbar(talents, "uploads_per_week", "주간 업로드 빈도 (최근 영상 기준)",
         fmt="{:.1f}", fname="04_upload_cadence.png")
    # 5. 도달 효율 (평균조회수/구독자)
    hbar(talents.assign(rr_pct=talents["reach_ratio"] * 100),
         "rr_pct", "도달 효율 = 평균 조회수 / 구독자 · %", fmt="{:.0f}%",
         fname="05_reach_ratio.png")

    # 6. 구독자 vs 평균조회수 산점도 (버블=참여율)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    t = talents
    sizes = (t["recent_avg_engagement_rate"] * 1000).clip(lower=20) * 6
    ax.scatter(t["subscribers"], t["recent_avg_views"], s=sizes,
               c=_mcolors(t["name_en"]), alpha=0.75, edgecolors="white", linewidths=1.5, zorder=3)
    for _, r in t.iterrows():
        ax.annotate(r["name_ko"], (r["subscribers"], r["recent_avg_views"]),
                    fontsize=9, xytext=(6, 4), textcoords="offset points", color=config.INK["text"])
    # 회귀선
    z = np.polyfit(t["subscribers"], t["recent_avg_views"], 1)
    xs = np.linspace(t["subscribers"].min(), t["subscribers"].max(), 50)
    ax.plot(xs, np.polyval(z, xs), color=config.INK["muted"], ls="--", lw=1.2, zorder=2)
    corr = t["subscribers"].corr(t["recent_avg_views"])
    ax.set_title(f"구독자 vs 최근 평균 조회수  (r={corr:.2f}, 버블=참여율)")
    ax.set_xlabel("구독자"); ax.set_ylabel("최근 평균 조회수")
    ax.grid(True, zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "06_subs_vs_views.png", dpi=140); plt.close(fig)

    # 7. 유닛별 평균 (구독자 / 평균조회수)
    unit_agg = (talents.groupby("unit")
                .agg(avg_subs=("subscribers", "mean"),
                     avg_views=("recent_avg_views", "mean"),
                     members=("name_en", "count")).reset_index())
    fig, ax = plt.subplots(figsize=(8, 5.5))
    x = np.arange(len(unit_agg)); w = 0.38
    ax.bar(x - w/2, unit_agg["avg_subs"], w, label="평균 구독자",
           color=config.PALETTE["series"][0], zorder=3)
    ax.bar(x + w/2, unit_agg["avg_views"], w, label="최근 평균 조회수",
           color=config.PALETTE["series"][1], zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(unit_agg["unit"])
    ax.set_title("유닛별 평균 지표 (탤런트)"); ax.legend(frameon=False)
    ax.grid(axis="y", zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "07_unit_comparison.png", dpi=140); plt.close(fig)

    # 8. 업로드 시간대 히트맵 (KST, 요일 x 시간)
    v = vids.copy()
    v["dow"] = v["published_kst"].dt.dayofweek   # 0=월
    v["hour"] = v["published_kst"].dt.hour
    heat = v.pivot_table(index="dow", columns="hour", values="video_id",
                         aggfunc="count", fill_value=0).reindex(index=range(7), columns=range(24), fill_value=0)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    im = ax.imshow(heat.values, aspect="auto", cmap="Blues")
    ax.set_yticks(range(7)); ax.set_yticklabels(["월","화","수","목","금","토","일"])
    ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels(range(0, 24, 2))
    ax.set_title("업로드 시간대 히트맵 (KST · 전체 최근영상)")
    ax.set_xlabel("시(hour)")
    fig.colorbar(im, ax=ax, label="영상 수", shrink=0.8)
    fig.tight_layout(); fig.savefig(CHARTS / "08_upload_heatmap.png", dpi=140); plt.close(fig)

    print(f"차트 8종 -> {CHARTS}")


# ---------------------------------------------------------------------------
# 4) 사이트용 JSON + 요약 리포트
# ---------------------------------------------------------------------------
def build_outputs(ch, vids, metrics):
    metrics.to_csv(DATA / "channel_metrics.csv", index=False)

    # 상관계수
    t = metrics[metrics["role"] == "talent"]
    corrs = {
        "subs_vs_avgviews": round(t["subscribers"].corr(t["recent_avg_views"]), 3),
        "cadence_vs_subs": round(t["uploads_per_week"].corr(t["subscribers"]), 3),
        "cadence_vs_avgviews": round(t["uploads_per_week"].corr(t["recent_avg_views"]), 3),
        "engagement_vs_subs": round(t["recent_avg_engagement_rate"].corr(t["subscribers"]), 3),
        "reach_vs_subs": round(t["reach_ratio"].corr(t["subscribers"]), 3),
    }
    top_videos = (vids.sort_values("views", ascending=False)
                  .head(15)[["name_ko", "title", "views", "likes", "comments", "published_at"]])
    top_videos = top_videos.assign(published_at=top_videos["published_at"].astype(str))

    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    site_data = dict(
        meta=meta,
        correlations=corrs,
        members=json.loads(metrics.to_json(orient="records", force_ascii=False)),
        top_videos=json.loads(top_videos.to_json(orient="records", force_ascii=False)),
    )
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 요약 리포트
    lead = t.iloc[t["subscribers"].argmax()]
    eff = t.iloc[t["reach_ratio"].argmax()]
    busy = t.iloc[t["uploads_per_week"].argmax()]
    eng = t.iloc[t["recent_avg_engagement_rate"].argmax()]
    md = f"""# 프로젝트 1 · StelLive 멤버별 유튜브 채널 성과 분석

- 데이터 소스: YouTube Data API v3 (수집 {meta['fetched_at'][:10]})
- 대상: StelLive 멤버 11명(창립자 강지 포함), 채널당 최근 {meta['recent_per_channel']}개 영상
- 총 {meta['n_videos']}개 영상 지표 집계

## 핵심 요약
- **최다 구독자(탤런트)**: {lead['name_ko']} — {lead['subscribers']:,}명
- **도달 효율 1위**(평균조회수/구독자): {eff['name_ko']} — {eff['reach_ratio']*100:.0f}%
- **가장 부지런한 업로더**: {busy['name_ko']} — 주 {busy['uploads_per_week']:.1f}회
- **참여율 1위**(좋아요+댓글/조회수): {eng['name_ko']} — {eng['recent_avg_engagement_rate']*100:.1f}%

## 상관관계 (탤런트 {len(t)}명)
| 관계 | 상관계수 r |
|------|-----------|
| 구독자 ↔ 최근 평균 조회수 | {corrs['subs_vs_avgviews']} |
| 업로드 빈도 ↔ 구독자 | {corrs['cadence_vs_subs']} |
| 업로드 빈도 ↔ 평균 조회수 | {corrs['cadence_vs_avgviews']} |
| 참여율 ↔ 구독자 | {corrs['engagement_vs_subs']} |
| 도달 효율 ↔ 구독자 | {corrs['reach_vs_subs']} |

> 해석 힌트: 구독자와 평균 조회수의 상관이 높으면 "구독자 규모가 조회수를 견인",
> 도달 효율↔구독자 상관이 음수면 "소규모 채널일수록 구독자 대비 조회수가 높은"
> (덜 포화된) 경향으로 읽을 수 있습니다.

## 산출물
- `data/` 원천·정제 데이터 (CSV/JSON)
- `sql/` 스키마·INSERT·분석쿼리·SQLite DB·쿼리 실행결과
- `charts/` 차트 8종 (PNG)
- `site/index.html` 자체완결 대시보드
"""
    (HERE / "REPORT.md").write_text(md, encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")
    return site_data


# ---------------------------------------------------------------------------
# 분석 쿼리 정의
# ---------------------------------------------------------------------------
NAMED_QUERIES = [
    ("구독자 상위 랭킹", """
SELECT rank_subs AS 순위, name_ko AS 멤버, unit AS 유닛,
       subscribers AS 구독자, recent_avg_views AS 최근평균조회수
FROM channel_metrics ORDER BY subscribers DESC;"""),
    ("도달 효율(평균조회수/구독자) 상위", """
SELECT name_ko AS 멤버, subscribers AS 구독자,
       recent_avg_views AS 평균조회수,
       ROUND(reach_ratio*100,1) AS 도달효율_pct
FROM channel_metrics WHERE role='talent'
ORDER BY reach_ratio DESC;"""),
    ("유닛별 요약", """
SELECT unit AS 유닛, COUNT(*) AS 인원,
       CAST(AVG(subscribers) AS INT) AS 평균구독자,
       CAST(AVG(recent_avg_views) AS INT) AS 평균조회수,
       ROUND(AVG(recent_avg_engagement_rate)*100,2) AS 평균참여율_pct
FROM channel_metrics WHERE role='talent'
GROUP BY unit ORDER BY 평균구독자 DESC;"""),
    ("참여율 상위", """
SELECT name_ko AS 멤버,
       ROUND(recent_avg_engagement_rate*100,2) AS 참여율_pct,
       ROUND(recent_avg_like_rate*100,2) AS 좋아요율_pct
FROM channel_metrics WHERE role='talent'
ORDER BY recent_avg_engagement_rate DESC;"""),
    ("업로드 빈도 상위", """
SELECT name_ko AS 멤버, uploads_per_week AS 주간업로드,
       ROUND(shorts_share*100,0) AS 쇼츠비중_pct
FROM channel_metrics WHERE role='talent'
ORDER BY uploads_per_week DESC;"""),
    ("멤버별 최고 조회수 영상", """
SELECT m.name_ko AS 멤버, v.title AS 영상, v.views AS 조회수
FROM videos v
JOIN (SELECT channel_id, MAX(views) AS mx FROM videos GROUP BY channel_id) t
  ON v.channel_id=t.channel_id AND v.views=t.mx
JOIN channel_metrics m ON m.channel_id=v.channel_id
ORDER BY v.views DESC;"""),
]

ANALYSIS_QUERIES = "-- StelLive 멤버 성과 분석 쿼리 (SQLite: sql/stellive.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    ch, vids, metrics = build_metrics()
    build_sql(ch, vids, metrics)
    build_charts(ch, vids, metrics)
    build_outputs(ch, vids, metrics)
    print("\n=== 멤버별 지표 요약 ===")
    cols = ["rank_subs", "name_ko", "unit", "subscribers", "recent_avg_views",
            "uploads_per_week", "recent_avg_engagement_rate", "reach_ratio"]
    with pd.option_context("display.width", 200, "display.max_columns", None):
        print(metrics[cols].to_string(index=False))


if __name__ == "__main__":
    main()
