"""
프로젝트6 · 분석 단계
StelLive vs 홀로라이브 vs 이세계아이돌 그룹 비교 지표 -> SQL -> 차트 -> 사이트 -> 리포트.
  python 06_competitor_comparison/analyze.py
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

GROUP_COLOR = {"StelLive": config.PALETTE["series"][0],
               "홀로라이브": config.PALETTE["series"][1],
               "이세계아이돌": config.PALETTE["series"][2]}


def build_metrics():
    ch = pd.read_csv(DATA / "channels.csv")
    vids = pd.read_csv(DATA / "videos.csv")
    vids["published_at"] = pd.to_datetime(vids["published_at"], utc=True)
    for c in ("views", "likes", "comments"):
        vids[c] = pd.to_numeric(vids[c], errors="coerce")
    # 신규 영상은 조회수 집계가 늦게 붙는다 — views>0 만으로는 "조회수 1·좋아요 443"
    # 이 통과해 평균 참여율을 폭파시킨다(01·02와 동일 함정, 2026-08-25 실측). 1,000 미만 제외.
    vids["engagement_rate"] = np.where(vids["views"] >= 1000,
                                       (vids["likes"].fillna(0)+vids["comments"].fillna(0))/vids["views"], np.nan)

    # 데이터 계약(PRD 7): name_en을 조인 키로 하는 unit 필드가 필요하다.
    # StelLive 멤버는 common/config.py 로스터가 정본. 경쟁사는 StelLive 유닛 체계에
    # 속하지 않으므로 unit=None(그룹 소속은 이미 "group" 컬럼이 표현).
    unit_by_name_en = {r["name_en"]: r["unit"] for r in config.member_rows()}

    rows = []
    for _, c in ch.iterrows():
        v = vids[vids["channel_id"] == c["channel_id"]]
        span_days = max(1, (v["published_at"].max() - v["published_at"].min()).days)
        rows.append(dict(
            group=c["group"], channel_id=c["channel_id"], name_ko=c["name_ko"], name_en=c["name_en"],
            unit=unit_by_name_en.get(c["name_en"]),
            subscribers=int(c["subscribers"]), total_views=int(c["total_views"]), video_count=int(c["video_count"]),
            recent_avg_views=round(v["views"].mean(), 1),
            recent_avg_engagement_rate=round(v["engagement_rate"].mean(), 5),
            uploads_per_week=round((len(v)-1)/(span_days/7), 2),
            reach_ratio=round(v["views"].mean()/c["subscribers"], 3),
        ))
    members = pd.DataFrame(rows).sort_values("subscribers", ascending=False).reset_index(drop=True)
    members.insert(0, "rank", members.index+1)

    group_summary = (members.groupby("group").agg(
        n_members=("name_ko", "count"),
        avg_subscribers=("subscribers", "mean"), median_subscribers=("subscribers", "median"),
        total_subscribers=("subscribers", "sum"),
        avg_recent_views=("recent_avg_views", "mean"),
        avg_engagement_rate=("recent_avg_engagement_rate", "mean"),
        avg_uploads_per_week=("uploads_per_week", "mean"),
        avg_reach_ratio=("reach_ratio", "mean"),
    ).round(4).reset_index())
    return vids, members, group_summary


def build_sql(vids, members, group_summary):
    SQL.mkdir(parents=True, exist_ok=True)
    v = vids.copy(); v["published_at"] = v["published_at"].astype(str)
    tables = {"videos": v, "member_metrics": members, "group_summary": group_summary}
    db.write_sqlite(SQL / "competitors.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables, primary_keys={"videos": "video_id"})
    db.dump_insert_sql(SQL / "member_metrics.sql", "member_metrics", members)
    db.dump_insert_sql(SQL / "group_summary.sql", "group_summary", group_summary)
    db.dump_insert_sql(SQL / "videos.sql", "videos", v)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")
    md = ["# 경쟁사 비교 분석 쿼리 결과\n", "`sql/competitors.db`(SQLite) 실행 결과.\n"]
    for title, q in NAMED_QUERIES:
        res = db.run_query(SQL / "competitors.db", q)
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n"); md.append(res.to_markdown(index=False)); md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


def build_charts(vids, members, group_summary):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    order = ["StelLive", "홀로라이브", "이세계아이돌"]
    gs = group_summary.set_index("group").reindex(order).reset_index()
    colors = [GROUP_COLOR[g] for g in gs["group"]]

    def gbar(col, title, fmt, fname, ylabel=""):
        fig, ax = plt.subplots(figsize=(7.5, 5.5))
        bars = ax.bar(gs["group"], gs[col], color=colors, zorder=3, width=0.55)
        ax.set_title(title); ax.grid(axis="y", zorder=0)
        if ylabel: ax.set_ylabel(ylabel)
        for b, v in zip(bars, gs[col]):
            ax.annotate(fmt.format(v), (b.get_x()+b.get_width()/2, v), ha="center", va="bottom",
                        fontsize=10, color=config.INK["text"], xytext=(0, 3), textcoords="offset points")
        fig.tight_layout(); fig.savefig(CHARTS / fname, dpi=140); plt.close(fig)

    gbar("avg_subscribers", "그룹별 평균 구독자 (표본 6명)", "{:,.0f}", "01_avg_subscribers.png")
    gbar("avg_recent_views", "그룹별 최근 영상 평균 조회수", "{:,.0f}", "02_avg_recent_views.png")
    gbar("avg_engagement_rate", "그룹별 평균 참여율", "{:.1%}", "03_avg_engagement.png")
    gbar("avg_uploads_per_week", "그룹별 주간 업로드 빈도", "{:.1f}회", "04_upload_cadence.png")
    gbar("avg_reach_ratio", "그룹별 도달 효율 (평균조회수/구독자)", "{:.0%}", "05_reach_ratio.png")

    # 6. 멤버별 구독자 (그룹 색상 구분, 전체 18명)
    d = members.sort_values("subscribers")
    fig, ax = plt.subplots(figsize=(9.5, 8))
    bars = ax.barh(d["name_ko"], d["subscribers"], color=[GROUP_COLOR[g] for g in d["group"]], height=0.7, zorder=3)
    ax.set_title("전체 18명 구독자 비교 (그룹별 색상)")
    ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
    for b, v in zip(bars, d["subscribers"]):
        ax.annotate(f"{v/1e6:.2f}M" if v >= 1e6 else f"{v/1e3:.0f}K", (b.get_width(), b.get_y()+b.get_height()/2),
                    va="center", ha="left", fontsize=8, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLOR[g]) for g in order]
    ax.legend(handles, order, frameon=False, loc="lower right")
    ax.margins(x=0.14); fig.tight_layout(); fig.savefig(CHARTS / "06_all_members_subs.png", dpi=140); plt.close(fig)

    # 7. 산점도: 구독자 vs 참여율 (그룹별 색상)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    for g in order:
        d = members[members["group"] == g]
        ax.scatter(d["subscribers"], d["recent_avg_engagement_rate"]*100, s=90, color=GROUP_COLOR[g],
                  label=g, alpha=0.8, edgecolors="white", linewidths=1.3, zorder=3)
    ax.set_xscale("log")
    ax.set_title("구독자(로그) vs 참여율 — 그룹별"); ax.set_xlabel("구독자 (log)"); ax.set_ylabel("참여율 (%)")
    ax.legend(frameon=False); ax.grid(True, zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "07_subs_vs_engagement.png", dpi=140); plt.close(fig)

    print(f"차트 7종 -> {CHARTS}")


def build_outputs(vids, members, group_summary):
    members.to_csv(DATA / "member_metrics.csv", index=False)
    group_summary.to_csv(DATA / "group_summary.csv", index=False)
    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    site_data = dict(meta=meta,
                     members=json.loads(members.to_json(orient="records", force_ascii=False)),
                     groups=json.loads(group_summary.to_json(orient="records", force_ascii=False)))
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    gs = group_summary.set_index("group")
    stel, holo, ise = gs.loc["StelLive"], gs.loc["홀로라이브"], gs.loc["이세계아이돌"]
    md = f"""# 프로젝트 6 · 경쟁사 비교 분석 (StelLive vs 홀로라이브 vs 이세계아이돌)

- 각 그룹 대표 멤버 6명 표본, 채널당 최근 {meta['recent_per_channel']}개 영상. 수집 {meta['fetched_at'][:10]}
- 홀로라이브: 우사다 페코라·가우르 구라·호쇼 마린·모리 캘리오프·모모스즈 네네·이누가미 코로네
- 이세계아이돌: 아이네·징버거·릴파·주르르·고세구·비챤

## 핵심 요약
| 지표 | StelLive | 홀로라이브 | 이세계아이돌 |
|------|---------:|----------:|-------------:|
| 평균 구독자 | {stel['avg_subscribers']:,.0f} | {holo['avg_subscribers']:,.0f} | {ise['avg_subscribers']:,.0f} |
| 평균 최근 조회수 | {stel['avg_recent_views']:,.0f} | {holo['avg_recent_views']:,.0f} | {ise['avg_recent_views']:,.0f} |
| 평균 참여율 | {stel['avg_engagement_rate']*100:.1f}% | {holo['avg_engagement_rate']*100:.1f}% | {ise['avg_engagement_rate']*100:.1f}% |
| 주간 업로드 | {stel['avg_uploads_per_week']:.1f}회 | {holo['avg_uploads_per_week']:.1f}회 | {ise['avg_uploads_per_week']:.1f}회 |
| 도달 효율 | {stel['avg_reach_ratio']*100:.0f}% | {holo['avg_reach_ratio']*100:.0f}% | {ise['avg_reach_ratio']*100:.0f}% |

- **규모**: 홀로라이브(글로벌) > 이세계아이돌(국내 대형) > StelLive 순 — 신생/중견 그룹 포지션.
- **참여율·도달 효율**은 규모가 작을수록 오히려 높게 나타나는 경향 — 충성도 높은 소규모 팬덤 구조.

## 산출물
- `data/channels.csv`·`videos.csv` 원천, `member_metrics.csv`·`group_summary.csv` 집계
- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과
- `charts/` 차트 7종(그룹비교 5종 + 전체멤버 구독자 + 산점도)
- `site/index.html` 인터랙티브 대시보드

> 표본 주의: 각 그룹 6명 대표 표본 비교이며 전체 소속 인원 비교가 아닙니다.
> 홀로라이브는 EN/JP 혼합 대표 선정, StelLive/이세계아이돌은 창립자 제외 탤런트 기준입니다.
"""
    (HERE / "REPORT.md").write_text(md, encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("그룹별 요약 비교", """
SELECT "group" AS 그룹, n_members AS 인원, CAST(avg_subscribers AS INT) AS 평균구독자,
       CAST(avg_recent_views AS INT) AS 평균조회수,
       ROUND(avg_engagement_rate*100,2) AS 참여율_pct,
       ROUND(avg_reach_ratio*100,1) AS 도달효율_pct
FROM group_summary ORDER BY 평균구독자 DESC;"""),
    ("전체 멤버 구독자 랭킹", """
SELECT rank AS 순위, "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자
FROM member_metrics ORDER BY subscribers DESC;"""),
    ("참여율 상위 10명", """
SELECT "group" AS 그룹, name_ko AS 멤버,
       ROUND(recent_avg_engagement_rate*100,2) AS 참여율_pct
FROM member_metrics ORDER BY recent_avg_engagement_rate DESC LIMIT 10;"""),
    ("도달 효율 상위 10명", """
SELECT "group" AS 그룹, name_ko AS 멤버, subscribers AS 구독자,
       ROUND(reach_ratio*100,0) AS 도달효율_pct
FROM member_metrics ORDER BY reach_ratio DESC LIMIT 10;"""),
]
ANALYSIS_QUERIES = "-- 경쟁사 비교 분석 쿼리 (SQLite: sql/competitors.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    vids, members, group_summary = build_metrics()
    build_sql(vids, members, group_summary)
    build_charts(vids, members, group_summary)
    build_outputs(vids, members, group_summary)
    print("\n=== 그룹별 요약 ===")
    with pd.option_context("display.width", 200):
        print(group_summary.to_string(index=False))


if __name__ == "__main__":
    main()
