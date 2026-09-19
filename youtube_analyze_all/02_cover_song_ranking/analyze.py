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
from common import config
from common import db, viz
from common.songs import add_song_key, pair_topic_tracks, summable
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SQL = HERE / "sql"
CHARTS = HERE / "charts"
SITE = HERE / "site"


def build_metrics():
    df = config.drop_founder(pd.read_csv(DATA / "covers.csv"))
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    for c in ("views", "likes", "comments"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # 방금 올라온 커버는 좋아요보다 조회수 집계가 늦게 붙는다. views>0 만으로는
    # "조회수 1 · 좋아요 443" 이 통과해 평균 참여율이 수천 %로 폭파된다(2026-08-25 실측,
    # 01과 동일한 함정). 비율 지표는 조회수 1,000 이상만 계산에 넣는다.
    df["engagement_rate"] = np.where(df["views"] >= 1000,
                                     (df["likes"].fillna(0) + df["comments"].fillna(0)) / df["views"], np.nan)

    # ── 곡 단위로 묶는다 ──────────────────────────────────────────────────
    # 한 곡이 본편·[4K]·3D·쇼츠·티저로 여러 번 올라온다. 영상 수로 세면 곡 수가 부풀고,
    # 곡당 평균도 왜곡된다. song_key(common/songs)로 같은 채널의 판들을 한 곡으로 묶는다.
    names = [r["name_ko"] for r in config.member_rows(include_founder=True)] + \
            [r["name_en"] for r in config.member_rows(include_founder=True)]
    df = add_song_key(df, member_names=names)
    song_rows = []
    for (cid, name_ko, key), g in df.groupby(["channel_id", "name_ko", "song_key"], sort=False):
        best = g.loc[g["views"].idxmax()]
        song_rows.append(dict(
            channel_id=cid, name_ko=name_ko, song_key=key, title=str(best["title"]),
            video_id=best["video_id"], n_versions=int(len(g)),
            version_ids="|".join(g["video_id"]),
            published_at=g["published_at"].min().isoformat(),
            views=int(g["views"].sum()), likes=int(g["likes"].fillna(0).sum()),
            is_collab=bool(g["is_collab"].any()),
        ))
    songs = pd.DataFrame(song_rows)

    # ── Topic 채널 음원 판을 곡에 붙인다 ───────────────────────────────────
    # 제목으로는 못 잇는다(봄꿈 ↔ Springdream). 같은 멤버·발매일 ±3일이면 짝으로 본다.
    topic_p = DATA / "topic_tracks.csv"
    manual_p = DATA / "topic_pairs_manual.csv"
    topic = pd.read_csv(topic_p) if topic_p.exists() else pd.DataFrame(
        columns=["video_id", "topic_channel_id", "name_ko", "name_en", "unit", "title", "published_at", "views", "likes"])
    manual = pd.read_csv(manual_p) if manual_p.exists() else None
    paired = pair_topic_tracks(topic, songs, manual) if not topic.empty else topic.assign(
        paired_video_id=None, pair_reason="unpaired")
    ok = summable(paired) if not paired.empty else paired
    tv = ok.groupby("paired_video_id")["views"].sum() if not ok.empty else pd.Series(dtype=float)
    tid = ok.groupby("paired_video_id")["video_id"].agg("|".join) if not ok.empty else pd.Series(dtype=str)
    songs["topic_views"] = songs["video_id"].map(tv).fillna(0).astype(int)
    songs["topic_video_ids"] = songs["video_id"].map(tid).fillna("")
    songs["views_incl_topic"] = songs["views"] + songs["topic_views"]
    songs = songs.sort_values("views_incl_topic", ascending=False).reset_index(drop=True)

    rows = []
    for (cid, name_ko, name_en, unit), g in df.groupby(["channel_id", "name_ko", "name_en", "unit"]):
        best = g.loc[g["views"].idxmax()]
        sg = songs[songs["channel_id"] == cid]
        rows.append(dict(
            channel_id=cid, name_ko=name_ko, name_en=name_en, unit=unit,
            cover_count=len(g),                       # 영상 수 (history.csv 연속성 때문에 이름 유지)
            song_count=int(len(sg)),                  # 곡 수 (여러 판을 한 곡으로)
            total_views=int(g["views"].sum()),        # 멤버 채널 영상 조회수 합
            topic_views=int(sg["topic_views"].sum()), # 짝지어진 Topic 음원 판 조회수 합
            total_views_incl_topic=int(g["views"].sum() + sg["topic_views"].sum()),
            avg_views=round(g["views"].mean(), 1),    # 영상당
            avg_views_per_song=round(sg["views_incl_topic"].mean(), 1) if len(sg) else None,  # 곡당(음원 포함)
            median_views=round(g["views"].median(), 1),
            max_views=int(g["views"].max()),
            best_cover=str(best["title"]),
            total_likes=int(g["likes"].fillna(0).sum()),
            avg_engagement_rate=round(g["engagement_rate"].mean(), 5),
            collab_share=round(g["is_collab"].mean(), 3),
        ))
    metrics = pd.DataFrame(rows).sort_values("total_views", ascending=False).reset_index(drop=True)
    metrics.insert(0, "rank", metrics.index + 1)
    build_metrics.songs, build_metrics.topic = songs, paired
    return df, metrics


def build_sql(df, metrics):
    SQL.mkdir(parents=True, exist_ok=True)
    covers = df.copy()
    covers["published_at"] = covers["published_at"].astype(str)
    covers["is_collab"] = covers["is_collab"].astype(int)
    tables = {"covers": covers, "cover_metrics": metrics, "cover_songs": build_metrics.songs}
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
    songs, topic = build_metrics.songs, build_metrics.topic
    songs.to_csv(DATA / "cover_songs.csv", index=False)
    if not topic.empty:
        topic.to_csv(DATA / "topic_pairs.csv", index=False)
    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    n_multi = int((songs["n_versions"] > 1).sum())
    n_paired = int(len(summable(topic))) if not topic.empty else 0
    n_amb = int(topic["pair_reason"].astype(str).str.startswith("ambiguous").sum()) if not topic.empty else 0
    meta["songs"] = dict(n_songs=int(len(songs)), n_videos=int(len(df)), n_multi_version=n_multi,
                         topic_tracks=int(len(topic)), topic_paired_to_covers=n_paired,
                         topic_ambiguous=n_amb,
                         topic_instrumental=int(topic["is_instrumental"].sum()) if "is_instrumental" in topic else 0,
                         note="여러 판(MV·4K·3D·쇼츠·티저)은 song_key 로 한 곡. Topic 음원 판은 같은 멤버·발매일 ±3일 "
                              "안에서 제목까지 맞아야 짝(title+date). 날짜만 맞는 건 합산하지 않는다. 반주(Inst.) 판 제외.")
    top = df.sort_values("views", ascending=False).head(20)[
        ["name_ko", "title", "views", "likes", "comments", "published_at"]].copy()
    top["published_at"] = top["published_at"].astype(str)
    site_data = dict(
        meta=meta,
        members=json.loads(metrics.to_json(orient="records", force_ascii=False)),
        top_covers=json.loads(top.to_json(orient="records", force_ascii=False)),
        songs=json.loads(songs.head(60).to_json(orient="records", force_ascii=False)),
    )
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    king = metrics.iloc[0]
    most = metrics.iloc[metrics["song_count"].argmax()]
    besteff = metrics.iloc[metrics["avg_views"].argmax()]
    topcover = df.sort_values("views", ascending=False).iloc[0]
    md = f"""# 프로젝트 2 · StelLive 커버곡 성과 랭킹 분석

- 데이터 소스: YouTube Data API v3 (채널 검색 + 영상 지표), 수집 {meta['fetched_at'][:10]}
- 멤버 {meta['n_members']}명 · 커버 영상 {meta['n_covers']}개 = 곡 {meta['songs']['n_songs']}곡
  (여러 판으로 올라온 곡 {meta['songs']['n_multi_version']}곡)
- Topic 채널 음원 판: 트랙 {meta['songs']['topic_tracks']}개 중 커버와 짝지어진 것 {meta['songs']['topic_paired_to_covers']}개
  (짝이 둘 이상이라 안 붙인 것 {meta['songs']['topic_ambiguous']}개). 나머지는 오리지널곡 음원이라 12에서 쓴다.

## 조회수를 세는 법 — 한 곡은 한 곡으로

한 곡이 본편 MV·[4K]·3D 라이브·쇼츠·티저로 여러 번 올라온다. 여기에 유튜브가 유통사 배급분으로
자동 생성하는 **"<이름> - Topic" 채널의 음원 판**이 따로 있다(예: 마시로 '봄꿈' MV ↔ Neneko
Mashiro - Topic 'Springdream'). 그래서:

- **총 조회수(total_views)** = 멤버 채널에 올라온 커버 영상 전부의 합. 여러 판이면 다 더한다.
- **음원 포함(total_views_incl_topic)** = 위 + 같은 멤버·발매일 ±3일 안에서 **제목까지 맞는** Topic
  트랙 조회수(반주 판 제외). Topic 트랙은 대부분 오리지널곡 음원이라 커버에 붙는 건 드물다 —
  날짜만 맞는 것은 붙이지 않는다(같은 날 나온 오리지널이 커버에 붙는 사고를 막기 위해).
- **곡 수(song_count)** 는 판을 한 곡으로 묶은 수, **영상 수(cover_count)** 는 그대로 센 수.

## 핵심 요약
- **커버 총 조회수 1위**: {king['name_ko']} — {king['total_views']/1e6:.1f}M (영상 {king['cover_count']}개 · {king['song_count']}곡
  · 음원 포함 {king['total_views_incl_topic']/1e6:.1f}M)
- **최다 커버**: {most['name_ko']} — {most['song_count']}곡 (영상 {most['cover_count']}개)
- **영상당 평균 조회수 1위**: {besteff['name_ko']} — {besteff['avg_views']/1e6:.2f}M
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
SELECT rank AS 순위, name_ko AS 멤버, song_count AS 곡수, cover_count AS 영상수,
       total_views AS 총조회수, total_views_incl_topic AS 음원포함, CAST(avg_views AS INT) AS 영상당평균
FROM cover_metrics ORDER BY total_views DESC;"""),
    ("여러 판으로 올라온 곡", """
SELECT name_ko AS 멤버, title AS 대표제목, n_versions AS 판수, views AS 판합계조회수, topic_views AS 음원조회수
FROM cover_songs WHERE n_versions > 1 ORDER BY views DESC;"""),
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
