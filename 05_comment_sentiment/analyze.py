"""
프로젝트5 · 분석 단계
Claude로 라벨링된 댓글(감성·토픽) -> 멤버별 여론 지표 -> SQL -> 차트 -> 사이트 -> 리포트.
  python 05_comment_sentiment/analyze.py
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

TOPIC_KO = {
    "voice_singing": "목소리·노래", "personality": "성격·개그",
    "visual_design": "비주얼·디자인", "content_gameplay": "방송내용·게임",
    "member_interaction": "멤버 케미", "growth_nostalgia": "성장·추억", "other": "기타",
}
SENTI_KO = {"positive": "긍정", "negative": "부정", "neutral": "중립"}


def build_metrics():
    df = pd.read_csv(DATA / "comments_labeled.csv")
    df["topic_ko"] = df["topic"].map(TOPIC_KO).fillna("기타")
    df["sentiment_ko"] = df["sentiment"].map(SENTI_KO).fillna("중립")

    rows = []
    for (ko, en, unit), g in df.groupby(["name_ko", "name_en", "unit"]):
        n = len(g)
        pos = (g["sentiment"] == "positive").sum()
        neg = (g["sentiment"] == "negative").sum()
        neu = (g["sentiment"] == "neutral").sum()
        top_topic = g["topic_ko"].value_counts().idxmax()
        rows.append(dict(
            name_ko=ko, name_en=en, unit=unit, n_comments=n,
            positive_share=round(pos / n, 3), negative_share=round(neg / n, 3),
            neutral_share=round(neu / n, 3),
            sentiment_score=round((pos - neg) / n, 3),   # -1..1
            top_topic=top_topic,
            avg_likes=round(g["like_count"].mean(), 1),
        ))
    members = pd.DataFrame(rows).sort_values("sentiment_score", ascending=False).reset_index(drop=True)
    members.insert(0, "rank", members.index + 1)

    topic_matrix = (df.groupby(["name_ko", "topic_ko"]).size()
                    .unstack(fill_value=0))
    return df, members, topic_matrix


def build_sql(df, members):
    SQL.mkdir(parents=True, exist_ok=True)
    tables = {"comments": df.drop(columns=["text_len"], errors="ignore"), "sentiment_metrics": members}
    db.write_sqlite(SQL / "sentiment.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables, primary_keys={"comments": "comment_id"})
    db.dump_insert_sql(SQL / "comments.sql", "comments", tables["comments"])
    db.dump_insert_sql(SQL / "sentiment_metrics.sql", "sentiment_metrics", members)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")
    md = ["# 댓글 감성 분석 쿼리 결과\n", "`sql/sentiment.db`(SQLite) 실행 결과. 라벨링: Claude(본 세션)가 상위 댓글 표본을 감성·토픽 분류.\n"]
    for title, q in NAMED_QUERIES:
        res = db.run_query(SQL / "sentiment.db", q)
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n"); md.append(res.to_markdown(index=False)); md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


def _mc(names):
    cmap = config.member_colors(); return [cmap.get(n, "#888") for n in names]


def build_charts(df, members, topic_matrix):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()

    # 1. 감성 점수 랭킹
    d = members.sort_values("sentiment_score")
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(d["name_ko"], d["sentiment_score"], color=_mc(d["name_en"]), height=0.72, zorder=3)
    ax.axvline(0, color=config.INK["muted"], lw=1)
    ax.set_title("멤버별 댓글 감성 점수 (긍정비율 − 부정비율)")
    ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
    for b, v in zip(bars, d["sentiment_score"]):
        ax.annotate(f"{v:+.2f}", (b.get_width(), b.get_y()+b.get_height()/2), va="center",
                    ha="left" if v >= 0 else "right", fontsize=9, color=config.INK["text"],
                    xytext=(4 if v >= 0 else -4, 0), textcoords="offset points")
    fig.tight_layout(); fig.savefig(CHARTS / "01_sentiment_score.png", dpi=140); plt.close(fig)

    # 2. 감성 구성 스택바 (긍정/중립/부정)
    d = members.sort_values("positive_share")
    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    y = range(len(d))
    ax.barh(y, d["positive_share"]*100, color=config.PALETTE["series"][2], label="긍정", zorder=3)
    ax.barh(y, d["neutral_share"]*100, left=d["positive_share"]*100, color=config.INK["muted"], label="중립", zorder=3)
    ax.barh(y, d["negative_share"]*100, left=(d["positive_share"]+d["neutral_share"])*100,
            color=config.PALETTE["series"][7], label="부정", zorder=3)
    ax.set_yticks(list(y)); ax.set_yticklabels(d["name_ko"]); ax.set_xlim(0, 100)
    ax.set_title("댓글 감성 구성 (%)"); ax.legend(frameon=False, ncol=3, loc="lower right")
    ax.grid(axis="x", zorder=0); ax.spines["left"].set_visible(False)
    fig.tight_layout(); fig.savefig(CHARTS / "02_sentiment_composition.png", dpi=140); plt.close(fig)

    # 3. 전체 토픽 분포
    topic_tot = df["topic_ko"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.bar(topic_tot.index, topic_tot.values, color=config.PALETTE["series"][:len(topic_tot)], zorder=3)
    ax.set_title("전체 댓글 토픽 분포"); ax.grid(axis="y", zorder=0)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    for b, v in zip(bars, topic_tot.values):
        ax.annotate(str(v), (b.get_x()+b.get_width()/2, v), ha="center", va="bottom", fontsize=9,
                    color=config.INK["text"], xytext=(0, 2), textcoords="offset points")
    fig.tight_layout(); fig.savefig(CHARTS / "03_topic_distribution.png", dpi=140); plt.close(fig)

    # 4. 멤버 x 토픽 히트맵
    order_members = members.sort_values("rank")["name_ko"].tolist()
    tm = topic_matrix.reindex(index=order_members).fillna(0)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    im = ax.imshow(tm.values, aspect="auto", cmap="Blues")
    ax.set_yticks(range(len(tm.index))); ax.set_yticklabels(tm.index)
    ax.set_xticks(range(len(tm.columns))); ax.set_xticklabels(tm.columns, rotation=30, ha="right")
    ax.set_title("멤버 × 토픽 댓글 수 히트맵")
    fig.colorbar(im, ax=ax, label="댓글 수", shrink=0.8)
    fig.tight_layout(); fig.savefig(CHARTS / "04_member_topic_heatmap.png", dpi=140); plt.close(fig)

    print(f"차트 4종 -> {CHARTS}")


def build_outputs(df, members, topic_matrix):
    members.to_csv(DATA / "sentiment_metrics.csv", index=False)
    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    top_liked = df.sort_values("like_count", ascending=False).head(15)[
        ["name_ko", "text", "like_count", "sentiment", "topic_ko"]]
    site_data = dict(
        meta=meta,
        members=json.loads(members.to_json(orient="records", force_ascii=False)),
        topic_totals=[{"topic": k, "count": int(v)} for k, v in df["topic_ko"].value_counts().items()],
        heatmap=dict(members=topic_matrix.index.tolist(), topics=topic_matrix.columns.tolist(),
                     values=topic_matrix.values.tolist()),
        top_liked=json.loads(top_liked.to_json(orient="records", force_ascii=False)),
        overall_sentiment=dict(
            positive=int((df["sentiment"] == "positive").sum()),
            neutral=int((df["sentiment"] == "neutral").sum()),
            negative=int((df["sentiment"] == "negative").sum()),
        ),
    )
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    best = members.iloc[0]
    toptopic = df["topic_ko"].value_counts().idxmax()
    n = len(df)
    pos_pct = site_data["overall_sentiment"]["positive"] / n * 100
    md = f"""# 프로젝트 5 · StelLive 댓글 여론/감성 분석

- 데이터: 멤버별 인기 영상 {meta['n_videos']}개의 상위(추천순) 댓글 {meta['n_comments']}개 중,
  좋아요 상위 330개 표본을 **Claude(본 세션)** 가 직접 읽고 감성(긍정/중립/부정)·토픽 7종으로 분류.
- 수집 {meta['fetched_at'][:10]}

## 핵심 요약
- 표본 전체 긍정 비율 **{pos_pct:.0f}%** — 상위 댓글은 대부분 팬 애정 표현.
- **감성 점수 1위**: {best['name_ko']} (점수 {best['sentiment_score']:+.2f})
- 가장 많이 언급되는 토픽: **{toptopic}**
- 멤버×토픽 히트맵에서 목소리·노래, 성격·개그가 대다수 멤버의 상위 토픽으로 나타남.

## 방법론 & 한계
- 댓글은 유튜브 `order=relevance`(추천순) 상위 표본 — 실제 시청자에게 가장 잘 보이는 댓글이며,
  전체 댓글의 무작위 표본은 아님(추천 알고리즘이 긍정/재치있는 댓글을 우선 노출하는 경향 있음).
- 라벨링은 규칙 기반이 아닌 Claude의 문맥 판단(반어법·팬덤 용어 고려)으로 수행.

## 산출물
- `data/comments_raw.csv` 원천 댓글, `comments_sample.csv` 표본, `comments_labeled.csv` 라벨링 결과
- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과
- `charts/` 차트 4종(감성점수·감성구성·토픽분포·멤버x토픽 히트맵)
- `site/index.html` 인터랙티브 대시보드
"""
    (HERE / "REPORT.md").write_text(md, encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("멤버별 감성 점수 랭킹", """
SELECT rank AS 순위, name_ko AS 멤버, n_comments AS 댓글수,
       ROUND(positive_share*100,0) AS 긍정_pct, ROUND(negative_share*100,0) AS 부정_pct,
       sentiment_score AS 감성점수
FROM sentiment_metrics ORDER BY sentiment_score DESC;"""),
    ("멤버별 주요 토픽", """
SELECT name_ko AS 멤버, top_topic AS 주요토픽, avg_likes AS 평균좋아요
FROM sentiment_metrics ORDER BY avg_likes DESC;"""),
    ("전체 감성 분포", """
SELECT sentiment_ko AS 감성, COUNT(*) AS 댓글수
FROM comments GROUP BY sentiment_ko ORDER BY 댓글수 DESC;"""),
    ("토픽별 댓글 수", """
SELECT topic_ko AS 토픽, COUNT(*) AS 댓글수
FROM comments GROUP BY topic_ko ORDER BY 댓글수 DESC;"""),
    ("좋아요 최다 댓글 TOP 10", """
SELECT name_ko AS 멤버, text AS 댓글, like_count AS 좋아요, sentiment_ko AS 감성
FROM comments ORDER BY like_count DESC LIMIT 10;"""),
]
ANALYSIS_QUERIES = "-- StelLive 댓글 감성 분석 쿼리 (SQLite: sql/sentiment.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    df, members, topic_matrix = build_metrics()
    build_sql(df, members)
    build_charts(df, members, topic_matrix)
    build_outputs(df, members, topic_matrix)
    print("\n=== 멤버별 감성 요약 ===")
    with pd.option_context("display.width", 200):
        print(members[["rank", "name_ko", "n_comments", "positive_share", "negative_share",
                       "sentiment_score", "top_topic"]].to_string(index=False))


if __name__ == "__main__":
    main()
