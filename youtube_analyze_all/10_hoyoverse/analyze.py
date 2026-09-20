"""
프로젝트10 · 분석 단계
캐릭터 마스터(yatta.moe) + 앱스토어 리뷰(google-play-scraper) → "게임사가 미는 캐릭터"와
"유저가 실제로 반응하는 캐릭터"의 간극을 SQL/차트/사이트/리포트로 만든다.

  python 10_hoyoverse/analyze.py

## 방법론 요약 (README.md에도 동일 기재)

- **공식 푸시 신호**: 배너 이력 API를 찾지 못해(수집 단계 주석 참고) "재출시(rerun) 빈도"는
  쓸 수 없다. 대신 호요버스 가챠 구조상 **5성 캐릭터만 단독 배너로 마케팅된다**는 점에
  기대어, 5성 캐릭터를 **출시 최신순**으로 정렬한 것을 공식 푸시 프록시로 쓴다.
  ("최근에 낸 5성 = 지금 미는 캐릭터") 4성은 배너에서 조연이라 이 랭킹에서 제외한다.
- **유저 반응 신호**: Google Trends가 죽어서(README 참고) 검색 관심도 대신 **앱스토어
  리뷰 본문에 캐릭터 이름이 언급된 횟수**를 씀. 이건 검색량보다 훨씬 거친 프록시이고,
  아래 두 가지 잡음이 있다:
    1. 리뷰는 최신순 최대 N건만 수집한 표본이라 전수조사가 아니다.
    2. 한글은 띄어쓰기로 단어가 깨끗이 분리되지 않아 **이름 길이가 짧을수록 오탐**이
       늘어난다. 1글자 이름(예: 원신 "진", "소")은 아예 매칭에서 제외했고, 2글자 이름은
       `name_ambiguous=True`로 표시해 상한값(upper bound)으로만 읽어야 함을 남긴다.
- 이 분석은 **상관을 관찰**할 뿐 인과를 주장하지 않는다. "배너 스케줄이 반응을 만든다"는
  식의 인과 문장은 쓰지 않는다.
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

GAME_KO = {"genshin": "원신", "starrail": "붕괴:스타레일"}   # 데이터에 name_ko_game 이 없을 때만 쓰는 폴백
TOP_N = 15
SMALL_SAMPLE = 200     # 창 안 리뷰가 이보다 적으면 언급 순위를 해석하지 말라고 리포트에 적는다


def _loose_pattern(name: str) -> str:
    """'은랑 LV.999' → 리뷰 표기(은랑999·은랑 999·은랑 lv.999)까지 잡는 정규식."""
    import re as _re
    toks = [t for t in _re.split(r"[^0-9A-Za-z가-힣]+", name) if t]
    parts = []
    for t in toks:
        parts.append("(?:lv)?" if t.lower() == "lv" else _re.escape(t))
    return r"[\s•·.・]*".join(parts).replace("(?:lv)?", "(?i:lv)?")


def games_of(df: pd.DataFrame) -> list[str]:
    """분석 대상 게임 목록. 수집 순서를 유지한다(원신 → 스타레일 → …)."""
    return list(dict.fromkeys(df["game"].tolist()))


def game_ko(df: pd.DataFrame, game: str) -> str:
    m = df.loc[df["game"] == game, "name_ko_game"]
    return str(m.iloc[0]) if len(m) else GAME_KO.get(game, game)


def build_metrics():
    chars = pd.read_csv(DATA / "characters.csv")
    reviews = pd.read_csv(DATA / "reviews.csv")
    app_summary = pd.read_csv(DATA / "app_summary.csv")
    reviews["content"] = reviews["content"].fillna("")
    reviews["at_dt"] = pd.to_datetime(reviews["at"])
    reviews["month"] = reviews["at_dt"].dt.to_period("M").astype(str)

    gacha = chars[~chars["is_playable_avatar"]].copy()
    gacha["release_dt"] = pd.to_datetime(gacha["release_date"], utc=True, errors="coerce", format="mixed")
    if "rarity_label" not in gacha.columns:
        gacha["rarity_label"] = gacha["rank"].map(lambda r: f"{int(r)}성" if r == r else None)
    # 리뷰에서 찾는 문자열. 붕괴3rd 는 "키아나 카슬라나"가 아니라 "키아나"로 불리므로
    # 수동 표의 match_name 을 쓴다. 다른 게임은 표시 이름 그대로.
    if "match_name" not in gacha.columns:
        gacha["match_name"] = None
    gacha["match_name"] = gacha["match_name"].where(gacha["match_name"].notna(), gacha["name_ko"])
    gacha["name_len"] = gacha["match_name"].fillna("").str.len()
    gacha["name_ambiguous"] = gacha["name_len"].between(1, 2)   # 2글자 이하는 오탐 위험 표시
    gacha["matchable"] = gacha["name_len"] >= 2                  # 1글자·이름 없음은 매칭하지 않음

    n_reviews_by_game = reviews.groupby("game").size().to_dict()
    # 리뷰가 없는 게임(마스터만 있고 리뷰 수집이 안 된 경우)은 0으로 나누지 않는다.

    # ── 유저 반응 코퍼스 ────────────────────────────────────────────────
    # 한국어 텍스트를 모을 수 있는 곳을 전부 시험해(reactions.py 주석) 되는 것만 담았다.
    # 플레이 리뷰는 평점이 붙어 있어 호불호 판단에 쓰고, 나머지는 언급량(화제성)에 쓴다.
    def _load(name, cols):
        f = DATA / name
        d = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=cols)
        if "content" in d.columns:
            d["content"] = d["content"].fillna("").astype(str)
        return d

    comments = _load("comments.csv", ["game", "name_ko", "video_id", "content"])
    apple = _load("apple_reviews.csv", ["game", "name_ko", "content", "title", "rating", "at"])
    if len(apple):
        # 애플은 제목에도 캐릭터 이름이 자주 들어간다.
        apple["content"] = apple["title"].fillna("").astype(str) + " " + apple["content"]
    hoyolab = _load("hoyolab.csv", ["game", "name_ko", "post_id", "content", "created_at"])

    # 공통 표본 = 다섯 게임 **모두** 가진 소스. HoYoLAB 은 호요버스 4개에만 있어서 빠진다.
    # 게임끼리 비교할 때는 공통 표본만 쓴다 — 소스 구성이 다른 수치를 나란히 놓으면
    # 게임 차이가 아니라 소스 차이를 재게 된다.
    CORPUS = {"youtube": comments, "apple": apple, "hoyolab": hoyolab}
    COMMON_SOURCES = ("reviews", "youtube", "apple")   # hoyolab 제외
    corpus_n = {k: (v.groupby("game").size().to_dict() if len(v) else {}) for k, v in CORPUS.items()}
    build_metrics.corpus_n = corpus_n
    n_comments_by_game = {g: sum(corpus_n[k].get(g, 0) for k in CORPUS) for g in gacha["game"].unique()}

    mention_rows = []
    for game, g in gacha.groupby("game"):
        rv = reviews[reviews["game"] == game]
        texts = rv["content"]
        scores = rv["score"]
        names = g["match_name"].dropna().tolist()
        for _, c in g.iterrows():
            if not c["matchable"]:
                mention_rows.append(dict(char_id=c["char_id"], mention_count=None,
                                          avg_mention_score=None, mention_rate_per_10k=None))
                continue
            # "은랑" 은 "은랑 LV.999"(리뷰에선 은랑999) 안에도 들어 있고, "블레이드"는 "천야•블레이드"
            # 안에 있다. 긴 이름을 먼저 지운 본문에서 짧은 이름을 찾아 이중 계산을 막는다.
            longer = [n for n in names if n != c["match_name"] and c["match_name"] in n]
            t = texts
            for n in longer:
                t = t.str.replace(_loose_pattern(n), " ", regex=True)
            mask = t.str.contains(c["match_name"], regex=False, na=False)
            n = int(mask.sum())
            # 나머지 소스도 같은 규칙(긴 이름 먼저 지움)으로 센다.
            per_source = {}
            for src, df in CORPUS.items():
                t2 = df.loc[df["game"] == game, "content"] if len(df) else pd.Series(dtype=str)
                for nn in longer:
                    if len(t2):
                        t2 = t2.str.replace(_loose_pattern(nn), " ", regex=True)
                per_source[src] = int(t2.str.contains(c["match_name"], regex=False, na=False).sum()) if len(t2) else 0
            nc = sum(per_source.values())
            mention_rows.append(dict(
                char_id=c["char_id"], mention_count=n,
                avg_mention_score=round(float(scores[mask].mean()), 2) if n else None,
                mention_rate_per_10k=round(n / n_reviews_by_game[game] * 10000, 2) if n_reviews_by_game.get(game) else None,
                comment_mentions=nc,
                youtube_mentions=per_source["youtube"], apple_mentions=per_source["apple"],
                hoyolab_mentions=per_source["hoyolab"],
                comment_rate_per_10k=round(nc / n_comments_by_game[game] * 10000, 2) if n_comments_by_game.get(game) else None,
            ))
    mentions = pd.DataFrame(mention_rows)
    gacha = gacha.merge(mentions, on="char_id", how="left")
    # 반응 순위의 기준 = 리뷰 언급 + 댓글 언급. 댓글이 있으면 그쪽이 표본을 지배한다.
    gacha["mentions_total"] = gacha["mention_count"].fillna(0) + gacha["comment_mentions"].fillna(0)
    # 공통 표본 기준 언급과 만 건당 비율 — 게임 간 비교는 이 열로만 한다.
    gacha["mentions_common"] = (gacha["mention_count"].fillna(0)
                                + gacha["youtube_mentions"].fillna(0)
                                + gacha["apple_mentions"].fillna(0))
    _common_n = {g: (n_reviews_by_game.get(g, 0) + corpus_n["youtube"].get(g, 0)
                     + corpus_n["apple"].get(g, 0)) for g in gacha["game"].unique()}
    gacha["common_sample_n"] = gacha["game"].map(_common_n)
    gacha["mentions_common_per_10k"] = (gacha["mentions_common"] / gacha["common_sample_n"] * 10000).round(2)
    build_metrics.common_n = _common_n
    build_metrics.n_comments_by_game = n_comments_by_game

    # 게임별 기준선(전체 리뷰 평균 평점) — 캐릭터별 언급 리뷰 평점과 비교할 기준
    baseline = reviews.groupby("game")["score"].mean().round(2).to_dict()
    gacha["game_avg_score"] = gacha["game"].map(baseline)
    gacha["sentiment_vs_baseline"] = (gacha["avg_mention_score"] - gacha["game_avg_score"]).round(2)

    # 순위는 **게임 안에서만** 매긴다. 원신과 스타레일은 출시 주기도, 리뷰 표본 수도,
    # 캐릭터 풀 크기도 다르다. 한 순위표에 섞으면 "원신 신캐가 스타레일 신캐보다 더
    # 밀렸다"는 식의, 아무도 묻지 않은 비교가 생긴다. 게임마다 따로 묻고 따로 답한다.
    #
    # 공식 푸시 랭킹: 5성만, 출시 최신순 (게임별)
    push = (gacha[(gacha["rank"] == 5) & gacha["release_dt"].notna()]
            .sort_values(["game", "release_dt"], ascending=[True, False])
            .reset_index(drop=True))
    push["push_rank"] = push.groupby("game").cumcount() + 1

    # 유저 반응 랭킹: 매칭 가능한 캐릭터 중 언급량 많은 순 (전체 등급 포함, 게임별)
    # 언급 0건은 순위가 아니다 — 리뷰가 68건뿐인 게임에서 0건 캐릭터가 "반응 4위"로 찍히지 않게.
    audience = (gacha[gacha["matchable"] & (gacha["mentions_total"] > 0)]
                .sort_values(["game", "mentions_total"], ascending=[True, False])
                .reset_index(drop=True))
    audience["audience_rank"] = audience.groupby("game").cumcount() + 1

    gacha = gacha.merge(push[["char_id", "push_rank"]], on="char_id", how="left")
    gacha = gacha.merge(audience[["char_id", "audience_rank"]], on="char_id", how="left")

    monthly = reviews.groupby(["game", "month"]).agg(
        avg_score=("score", "mean"), n_reviews=("score", "size")).reset_index()
    monthly["avg_score"] = monthly["avg_score"].round(3)

    return chars, gacha, reviews, monthly, app_summary, push, audience


def build_sql(gacha, reviews, monthly, app_summary):
    SQL.mkdir(parents=True, exist_ok=True)
    reviews_sql = reviews.drop(columns=["at_dt", "month"]).copy()
    gacha_sql = gacha.drop(columns=["release_dt"]).copy()
    tables = {
        "characters": gacha_sql, "reviews": reviews_sql,
        "monthly_sentiment": monthly, "app_summary": app_summary,
    }
    db.write_sqlite(SQL / "hoyoverse.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables,
                        primary_keys={"characters": "char_id", "reviews": "review_id"})
    for name, df in tables.items():
        db.dump_insert_sql(SQL / f"{name}.sql", name, df)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")
    md = ["# 호요버스 캐릭터 인기도 분석 쿼리 결과\n", "`sql/hoyoverse.db`(SQLite) 실행 결과.\n"]
    for title, q in NAMED_QUERIES:
        res = db.run_query(SQL / "hoyoverse.db", q)
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n")
        md.append(res.to_markdown(index=False)); md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


GAME_COLOR = {"genshin": config.PALETTE["series"][0], "starrail": config.PALETTE["series"][1],
              "zzz": config.PALETTE["series"][2], "hi3": config.PALETTE["series"][3],
              "ba": config.PALETTE["series"][4]}


def _gc(games):
    return [GAME_COLOR.get(g, "#888") for g in games]


def build_charts(gacha, reviews, monthly, push, audience):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    S = config.PALETTE["series"]

    # 게임마다 패널을 하나씩. 두 게임을 한 축에 올리면 순위·언급량이 게임 간 비교처럼
    # 읽히는데, 그런 비교는 이 프로젝트의 질문이 아니다.
    games = games_of(gacha)
    n = len(games)
    # 패널 배치: 게임이 셋 이상이면 2열 격자. 한 줄에 넷을 놓으면 150mm 인쇄 폭에서 글자가 안 읽힌다.
    ncol = min(n, 2)
    nrow = -(-n // ncol)

    def grid(w=6.4, h=6.2):
        fig, axes = plt.subplots(nrow, ncol, figsize=(w * ncol, h * nrow), squeeze=False)
        flat = [ax for row in axes for ax in row]
        for ax in flat[n:]:
            ax.axis("off")
        return fig, flat[:n]

    # 1. 공식 푸시 프록시: 5성 캐릭터 출시 최신순 TOP 15 — 게임별
    fig, axes = grid(6.4, 6.4)
    for ax, game in zip(axes, games):
        d = push[push["game"] == game].head(TOP_N).sort_values("release_dt")
        if d.empty:
            ax.text(0.5, 0.5, "출시일 데이터 없음 —\n푸시 순위를 만들 수 없다", ha="center", va="center",
                    transform=ax.transAxes, color=config.INK["text"])
        ax.barh(d["name_ko"], range(len(d)), color=_gc([game])[0], height=0.72, zorder=3)
        ax.set_xticks([]); ax.set_title(f"{game_ko(gacha, game)} · 5성 출시 최신순 TOP {TOP_N}")
        for i, (_, r) in enumerate(d.iterrows()):
            ax.annotate(str(r["release_date"])[:10], (0, i), va="center", ha="left",
                        fontsize=9, color=config.INK["text"], xytext=(6, 0), textcoords="offset points")
        ax.grid(False); ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)
    fig.suptitle("공식 푸시 프록시 (게임별 순위 — 게임 간 비교 아님)")
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(CHARTS / "01_push_proxy_top15.png", dpi=140); plt.close(fig)

    # 2. 유저 반응: 댓글+리뷰 언급량 TOP 15 — 게임별
    fig, axes = grid(6.4, 6.4)
    for ax, game in zip(axes, games):
        d = audience[audience["game"] == game].head(TOP_N).sort_values("mentions_total")
        bars = ax.barh(d["name_ko"], d["mentions_total"], color=_gc([game])[0], height=0.72, zorder=3)
        ax.set_title(f"{game_ko(gacha, game)} · 댓글+리뷰 언급량 TOP {TOP_N}")
        ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
        for b, v in zip(bars, d["mentions_total"]):
            ax.annotate(f"{int(v)}건", (b.get_width(), b.get_y()+b.get_height()/2), va="center", ha="left",
                        fontsize=9, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
        ax.margins(x=0.16)
    fig.suptitle("유저 반응 프록시: 공식 채널 댓글 + 스토어 리뷰 (게임별 — 표본 수가 달라 게임 간 건수 비교 아님)")
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(CHARTS / "02_audience_mentions_top15.png", dpi=140); plt.close(fig)

    # 3. 푸시 랭크 vs 반응 랭크 산점도 — 게임별 (두 랭킹에 모두 든 캐릭터)
    fig, axes = grid(6.6, 6.4)
    for ax, game in zip(axes, games):
        both = gacha[(gacha["game"] == game)].dropna(subset=["push_rank", "audience_rank"])
        ax.scatter(both["push_rank"], both["audience_rank"], s=90, c=_gc([game])[0],
                   alpha=0.8, edgecolors="white", linewidths=1.2, zorder=3)
        lim = max(both["push_rank"].max(), both["audience_rank"].max()) + 2 if len(both) else 10
        ax.plot([0, lim], [0, lim], color=config.INK["grid"], linestyle="--", zorder=1, label="푸시 순위 = 반응 순위")
        for _, r in both.iterrows():
            ax.annotate(r["name_ko"], (r["push_rank"], r["audience_rank"]), fontsize=8,
                        xytext=(5, 4), textcoords="offset points", color=config.INK["text"])
        ax.set_xlabel("공식 푸시 순위 (5성·출시 최신순, 1=가장 최근)")
        ax.set_ylabel("유저 반응 순위 (리뷰 언급량, 1=가장 많이 언급)")
        ax.set_title(f"{game_ko(gacha, game)} · 푸시 순위 vs 반응 순위")
        ax.invert_yaxis(); ax.grid(True, zorder=0); ax.legend(frameon=False, loc="lower right")
    fig.suptitle("점선 위=반응이 순위보다 약함 · 점선 아래=반응이 순위보다 강함")
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(CHARTS / "03_push_vs_audience_rank.png", dpi=140); plt.close(fig)

    # 4. 게임별 월간 평균 평점 추이
    # ⚠ 두 게임의 리뷰 표본 기간이 다르다(붕괴:스타레일 리뷰가 원신보다 6개월 더 과거까지 있음).
    #   게임별로 따로 정렬된 문자열을 ax.plot에 순서대로 넘기면 matplotlib이 카테고리 축을
    #   "먼저 본 순서"로 등록해버려서, 나중에 등장하는 과거 월이 축 뒤쪽에 붙어버리는 버그가
    #   난다. 그래서 두 게임을 합친 전체 월 목록을 먼저 만들고 공통 x좌표에 매핑한다.
    all_months = sorted(monthly["month"].unique())
    xi = {m: i for i, m in enumerate(all_months)}
    fig, ax = plt.subplots(figsize=(11, 4.6))
    for game, d in monthly.groupby("game"):
        d = d.sort_values("month")
        ax.plot([xi[m] for m in d["month"]], d["avg_score"], marker="o", markersize=4, linewidth=2,
                color=_gc([game])[0], label=game_ko(gacha, game), zorder=3)
    ax.set_xticks(range(0, len(all_months), 2))
    ax.set_xticklabels([all_months[i] for i in range(0, len(all_months), 2)])
    ax.set_title("게임별 월간 평균 리뷰 평점 추이"); ax.set_ylabel("평균 평점 (1~5)")
    ax.grid(zorder=0); ax.legend(frameon=False)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout(); fig.savefig(CHARTS / "04_monthly_score_trend.png", dpi=140); plt.close(fig)

    # 5. 게임별 리뷰 평점 분포
    fig, ax = plt.subplots(figsize=(8, 5.5))
    width = 0.8 / n
    for i, game in enumerate(games):
        d = reviews[reviews["game"] == game]["score"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        x = np.arange(1, 6) + (i - (n - 1) / 2) * width
        ax.bar(x, d.values, width=width, color=_gc([game])[0], label=game_ko(gacha, game), zorder=3)
    ax.set_xticks(range(1, 6)); ax.set_xlabel("별점"); ax.set_ylabel("리뷰 수")
    ax.set_title("게임별 리뷰 평점 분포"); ax.grid(axis="y", zorder=0); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(CHARTS / "05_score_distribution.png", dpi=140); plt.close(fig)

    # 6. 게임별 희귀도 구성 — 최고 등급(5성/S급)과 그 아래(4성/A급·B급). 게임마다 등급
    #    이름이 달라 숫자 rank(5=최고)로 묶고 라벨은 게임별 표기를 쓴다.
    fig, ax = plt.subplots(figsize=(1.8 * n + 3, 5))
    ct = gacha.groupby(["game", "rank"]).size().unstack(fill_value=0)
    ct = ct.reindex(games).fillna(0)
    top = ct.get(5, pd.Series(0, index=ct.index)); rest = ct.sum(axis=1) - top
    ax.bar(range(n), top, color=S[4], label="최고 등급(5성·S급)", zorder=3)
    ax.bar(range(n), rest, bottom=top, color=S[3], label="그 아래(4성·A급·B급)", zorder=3)
    for i, g in enumerate(games):
        labels = gacha[gacha["game"] == g].groupby("rarity_label").size()
        ax.annotate(" · ".join(f"{k} {v}" for k, v in labels.items()), (i, top.iloc[i] + rest.iloc[i]),
                    ha="center", va="bottom", fontsize=8.5, color=config.INK["text"],
                    xytext=(0, 3), textcoords="offset points")
    ax.set_xticks(range(n)); ax.set_xticklabels([game_ko(gacha, g) for g in games])
    ax.set_title("게임별 캐릭터 희귀도 구성 (플레이어 캐릭터 제외)")
    ax.grid(axis="y", zorder=0); ax.legend(frameon=False); ax.margins(y=0.15)
    fig.tight_layout(); fig.savefig(CHARTS / "06_rarity_composition.png", dpi=140); plt.close(fig)

    # 7. 원소/속성 분포 (게임별)
    fig, axes = grid(6.5, 4.8)
    for ax, game in zip(axes, games):
        d = gacha[gacha["game"] == game]["element"].value_counts()
        if d.empty:
            ax.text(0.5, 0.5, "속성 데이터 없음\n(전투복 등급·버전만 수집)", ha="center", va="center",
                    transform=ax.transAxes, color=config.INK["text"]); ax.set_xticks([]); ax.set_yticks([])
        ax.barh(d.index[::-1], d.values[::-1], color=S[:len(d)][::-1], zorder=3)
        ax.set_title(f"{game_ko(gacha, game)} 원소/속성 분포"); ax.grid(axis="x", zorder=0)
        ax.spines["left"].set_visible(False)
    fig.tight_layout(); fig.savefig(CHARTS / "07_element_distribution.png", dpi=140); plt.close(fig)

    # 8. 언급량 vs 감성(언급 리뷰 평균 평점) 산점도 — 게임별, 언급 5건 이상만 (표본 최소 확보)
    fig, axes = grid(6.5, 5.8)
    for ax, game in zip(axes, games):
        d = gacha[(gacha["game"] == game) & (gacha["mention_count"].fillna(0) >= 5)]
        ax.scatter(d["mention_count"], d["avg_mention_score"], s=90, c=_gc([game])[0],
                   alpha=0.8, edgecolors="white", linewidths=1.2, zorder=3)
        for _, r in d.iterrows():
            ax.annotate(r["name_ko"], (r["mention_count"], r["avg_mention_score"]), fontsize=8,
                        xytext=(5, 4), textcoords="offset points", color=config.INK["text"])
        base = reviews[reviews["game"] == game]["score"].mean()
        ax.axhline(base, color=config.INK["grid"], linestyle="--", zorder=1, label=f"게임 평균 평점 {base:.2f}")
        ax.set_xlabel("리뷰 언급 횟수 (평점은 리뷰에서만 나온다 · 5건 이상만 표시)"); ax.set_ylabel("언급 리뷰 평균 평점")
        ax.set_title(f"{game_ko(gacha, game)} · 언급량 vs 언급 리뷰 감성"); ax.grid(True, zorder=0)
        ax.legend(frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(CHARTS / "08_mentions_vs_sentiment.png", dpi=140); plt.close(fig)

    print(f"차트 8종 -> {CHARTS}")


def _grand_total(by_game: dict) -> int:
    return sum(int(v) for bg in by_game.values() for v in (bg.get("corpus") or {}).values())


def _cross_game_table(gacha: pd.DataFrame) -> str:
    """게임 간 비교 — 공통 표본(플레이+애플+유튜브)에서 만 건당 언급."""
    rows = []
    for g in games_of(gacha):
        d = gacha[(gacha["game"] == g) & gacha["matchable"]]
        if d.empty or not d["common_sample_n"].iloc[0]:
            continue
        top = d.nlargest(1, "mentions_common")
        rows.append((game_ko(gacha, g), int(d["common_sample_n"].iloc[0]),
                     float(d["mentions_common_per_10k"].sum()),
                     float((d["mentions_common"] > 0).mean() * 100),
                     str(top["name_ko"].iloc[0]), float(top["mentions_common_per_10k"].iloc[0])))
    if not rows:
        return ""
    out = ["| 게임 | 공통 표본 | 캐릭터 언급 합(만 건당) | 한 번이라도 언급된 비율 | 1위 캐릭터(만 건당) |",
           "|---|---:|---:|---:|---|"]
    for nm, n, tot, share, who, rate in rows:
        out.append(f"| {nm} | {n:,}건 | {tot:,.0f} | {share:.0f}% | {who} {rate:,.0f} |")
    return "\n".join(out)


def _sample_table(by_game: dict, meta: dict) -> str:
    ko = {"reviews": "플레이 리뷰", "apple": "애플 리뷰", "youtube": "공식 유튜브 댓글", "hoyolab": "HoYoLAB 댓글"}
    keys = ["reviews", "apple", "youtube", "hoyolab"]
    head = "| 게임 | " + " | ".join(ko[k] for k in keys) + " | 전체 | 공통 표본 |"
    sep = "|---|" + "---:|" * (len(keys) + 2)
    lines = [head, sep]
    for g, bg in by_game.items():
        c = bg.get("corpus") or {}
        cells = [f"{int(c.get(k, 0)):,}" if c.get(k) else "—" for k in keys]
        lines.append(f"| {bg['name_ko']} | " + " | ".join(cells)
                     + f" | {sum(int(v) for v in c.values()):,} | {int(bg.get('common_sample', 0)):,} |")
    days = meta.get("review_window_days", "?")
    return ("\n".join(lines) + f"\n\n모두 같은 기간({days}일, {str(meta.get('review_since',''))[:10]} ~ "
            f"{meta['fetched_at'][:10]})에 쓰인 한국어 텍스트다. 접근을 시험했지만 막힌 곳은 "
            "`data/source_probe.json` 에 이유와 함께 남겼다.")


def _corpus_line(bg: dict) -> str:
    c = bg.get("corpus") or {}
    ko = {"reviews": "플레이 리뷰", "youtube": "공식 채널 댓글", "apple": "애플 리뷰", "hoyolab": "HoYoLAB 댓글"}
    parts = [f"{ko[k]} {v:,}건" for k, v in c.items() if v]
    return " · ".join(parts) + f" = **{sum(c.values()):,}건**"


def _src_line(r) -> str:
    ko = [("youtube_mentions", "유튜브"), ("hoyolab_mentions", "HoYoLAB"),
          ("apple_mentions", "애플"), ("mention_count", "플레이")]
    parts = [f"{label} {int(r[k]):,}" for k, label in ko if r.get(k) == r.get(k) and int(r.get(k) or 0)]
    return " + ".join(parts) + f" = {int(r['mentions_total']):,}건"


def _total_comments(meta: dict) -> int:
    yt = sum(int(v.get("comments") or 0)
             for v in ((meta.get("official_comments") or {}).get("by_game") or {}).values())
    ap = sum(int(v.get("n") or 0) for v in (meta.get("apple_reviews") or {}).values())
    hl = sum(int(v.get("replies") or 0) for v in (meta.get("hoyolab") or {}).values())
    return yt + ap + hl


def _per_game_counts(gacha: pd.DataFrame) -> str:
    return " · ".join(f"{game_ko(gacha, g)} {int((gacha['game'] == g).sum())}명" for g in games_of(gacha))


def _window_line(meta: dict) -> str:
    bg = meta.get("reviews_by_game") or {}
    names = {"genshin": "원신", "starrail": "붕괴:스타레일", "zzz": "젠레스 존 제로", "hi3": "붕괴3rd", "ba": "블루 아카이브"}
    parts = []
    for g, v in bg.items():
        flag = "" if v.get("complete", True) else "(창 미완)"
        parts.append(f"{names.get(g, g)} {v.get('n', 0):,}건{flag}")
    return " · ".join(parts) if parts else "게임별 건수 기록 없음"


def _trends_line(status: dict) -> str:
    """Google Trends 상태를 실제 기록대로 한 줄로 쓴다.

    예전에는 "매 시도 즉시 429" 라고 본문에 박아 뒀는데, 실제 마지막 실행의 기록은
    `ModuleNotFoundError` 였다(라이브러리가 아예 없어서 호출조차 안 됨). 실패의 종류가
    다르면 독자가 판단할 것도 달라진다 — 기록된 것만 쓴다.
    """
    if status.get("ok"):
        return (f"**Google Trends 호출 성공** — 시험 질의(\"Genshin Impact\", 1개월)가 {status.get('n_rows', 0)}행을 "
                "받았다. 다만 **캐릭터 단위 검색 관심도는 아직 분석에 넣지 않았다** — 유저 반응 지표는 "
                "댓글+리뷰 언급량이다. 이 줄은 소스가 살아 있다는 기록이지 분석에 썼다는 뜻이 아니다.")
    err = status.get("error") or "원인 미기록"
    if status.get("attempted") is False:
        return (f"**Google Trends 미사용** — 이번 실행에서는 호출하지 않았다(`{err}`). "
                "검색 관심도는 다루지 않았고, 리뷰 본문 언급량으로 유저 반응을 근사했다.")
    return (f"**Google Trends 실패** — 호출했으나 `{err}` 로 데이터를 얻지 못했다. "
            "빈 값을 채워 넣지 않고, 리뷰 본문 언급량으로 유저 반응을 근사했다.")


def build_outputs(chars, gacha, reviews, monthly, app_summary, push, audience):
    gacha.drop(columns=["release_dt"], errors="ignore").to_csv(DATA / "character_metrics.csv", index=False)
    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    trends_status = json.loads((DATA / "trends_status.json").read_text(encoding="utf-8"))

    # collect.py 가 쓴 n_characters 는 수집한 **전체** 캐릭터 수다. 반면 아래
    # characters 배열은 is_playable_avatar(기본 지급 캐릭터 등)를 걸러낸 **가챠**
    # 캐릭터만 담는다 — 분석 대상이 가챠 캐릭터이기 때문이다.
    # 두 숫자를 같은 이름으로 두면 화면에서 "캐릭터 225명"이라고 표시해놓고 표에는
    # 201명만 나오는 모순이 생긴다. 이름을 나눠 무엇을 센 값인지 분명히 한다.
    meta["n_characters_collected"] = meta.get("n_characters")
    meta["n_characters_gacha"] = int(len(gacha))
    meta["n_characters"] = int(len(gacha))  # 앱·사이트가 쓰는 기본값 = 분석 대상 수
    meta["n_characters_note"] = (
        f"수집 {meta['n_characters_collected']}명 중 가챠 캐릭터 {meta['n_characters_gacha']}명이 분석 대상. "
        "기본 지급 캐릭터(is_playable_avatar)는 제외했다."
    )

    games = games_of(gacha)
    both = gacha.dropna(subset=["push_rank", "audience_rank"]).copy()
    both["gap"] = both["audience_rank"] - both["push_rank"]

    def _recs(df):
        return json.loads(df.drop(columns=["release_dt"], errors="ignore")
                            .to_json(orient="records", force_ascii=False))

    # 게임별 묶음. 순위·격차는 게임 안에서만 의미가 있으므로 "전체 TOP 15" 같은 건 없다.
    # push_top/audience_top/gap_* 의 평면 배열도 남기지만, 각 행의 game 으로 나눠 읽어야 한다.
    by_game = {}
    for game in games:
        g = gacha[gacha["game"] == game]
        b = both[both["game"] == game]
        by_game[game] = dict(
            name_ko=game_ko(gacha, game),
            n_gacha=int(len(g)),
            n_reviews=int((reviews["game"] == game).sum()),
            n_comments=int(getattr(build_metrics, "n_comments_by_game", {}).get(game, 0)),
            corpus=dict(reviews=int((reviews["game"] == game).sum()),
                        **{k: int(v.get(game, 0)) for k, v in getattr(build_metrics, "corpus_n", {}).items()}),
            common_sample=int(getattr(build_metrics, "common_n", {}).get(game, 0)),
            n_matchable=int(g["matchable"].sum()),
            n_zero_mention=int((g["matchable"] & (g["mentions_total"] == 0)).sum()),
            push_top=_recs(push[push["game"] == game].head(TOP_N)),
            audience_top=_recs(audience[audience["game"] == game].head(TOP_N)),
            # 격차의 부호가 맞는 쪽만. 두 순위에 든 캐릭터가 셋뿐인 게임(붕괴3rd)에서
            # 같은 셋이 양쪽 표에 다 나오는 일을 막는다.
            # "많이 밀렸는데"는 정말 최근에 민 것(출시 최신순 5위 안)만, "덜 밀렸는데"는 15위 밖만.
            # 그 사이 구간을 넣으면 4위짜리가 '최신 캐릭터'로 읽힌다.
            gap_overpushed=_recs(b[(b["gap"] > 0) & (b["push_rank"] <= 5)].sort_values("gap", ascending=False).head(5)),
            gap_sleeper=_recs(b[(b["gap"] < 0) & (b["push_rank"] > 15)].sort_values("gap").head(5)),
        )

    site_data = dict(
        meta=dict(meta, games=games, ranking_scope="per_game",
                  ranking_note="push_rank·audience_rank·gap 은 게임 안에서만 매긴 값이다. 게임을 섞어 비교하지 말 것."),
        trends_status=trends_status,
        app_summary=json.loads(app_summary.to_json(orient="records", force_ascii=False)),
        characters=_recs(gacha),
        push_top=[r for game in games for r in by_game[game]["push_top"]],
        audience_top=[r for game in games for r in by_game[game]["audience_top"]],
        monthly_sentiment=json.loads(monthly.to_json(orient="records", force_ascii=False)),
        gap_overpushed=[r for game in games for r in by_game[game]["gap_overpushed"]],
        gap_sleeper=[r for game in games for r in by_game[game]["gap_sleeper"]],
        by_game=by_game,
        n_matchable_low_confidence=int(gacha["name_ambiguous"].sum()),
    )
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _game_section(game: str) -> str:
        bg = by_game[game]
        tp = push[push["game"] == game]
        ta = audience[audience["game"] == game]
        src = (meta.get("character_sources") or {}).get(game, {})
        src_line = ""
        if src.get("names", "").startswith("manual"):
            src_line = ("- ⚠ 한글 이름은 **사람이 적은 표**(`data/hi3_names_ko.csv`)다. 자동 소스가 없어서다. "
                        f"이름이 있는 캐릭터 {src.get('n_named', 0)}명만 리뷰 매칭 대상이고, 표기가 불확실한 "
                        "이름은 표에 uncertain 으로 적어 뒀다.\n")
        if tp.empty or ta.empty:
            why = []
            if tp.empty:
                why.append(f"출시일이 있는 최고 등급 캐릭터가 없다(출시일 소스: {src.get('release', '?')}, "
                           f"확보 {src.get('n_release', 0)}명)")
            if ta.empty:
                why.append("리뷰에 매칭할 이름이 없거나 리뷰가 없다")
            return (f"### {bg['name_ko']}\n\n- 가챠 캐릭터 {bg['n_gacha']}명 · 리뷰 {bg['n_reviews']:,}건\n"
                    f"- 순위를 매길 수 없다 — " + "; ".join(why) + "\n" + src_line)
        tp, ta = tp.iloc[0], ta.iloc[0]
        over = bg["gap_overpushed"][:3]
        sleep = bg["gap_sleeper"][:3]
        thin = ""
        sample = bg["n_reviews"] + bg["n_comments"]
        if sample < SMALL_SAMPLE:
            thin = (f"- ⚠ 같은 {meta.get('review_window_days', '?')}일 창에서 리뷰 {bg['n_reviews']}건 + 공식 채널 댓글 "
                    f"{bg['n_comments']:,}건 = **{sample:,}건**뿐이다. 언급 순위는 한두 건 차이로 뒤집히므로 "
                    "**해석하지 말 것** — 표본이 이만큼 작다는 것 자체가 결과다.\n")
        def _sc(r):
            v = r.get("avg_mention_score")
            return f", 언급 리뷰 평점 {v:.1f}" if v is not None and v == v else ""
        fmt = lambda rows: ", ".join(
            f"{r['name_ko']}(푸시 {int(r['push_rank'])}위→반응 {int(r['audience_rank'])}위, 언급 {int(r.get('mentions_total') or 0):,}건{_sc(r)})"
            for r in rows) or "—"
        variants = sorted(n for n in g["name_ko"].dropna() if "•" in n or "·" in n)
        var_line = ""
        if variants:
            var_line = ("- 이름에 •가 든 캐릭터(" + ", ".join(variants[:6]) + (" 등" if len(variants) > 6 else "")
                        + ")는 기존 캐릭터의 **변주판**으로, 마스터 데이터의 별도 출시일을 가진 새 캐릭터로 센다. "
                        "원본 이름(예: 블레이드)의 언급은 변주판 표기를 지운 뒤 세어 이중 계산하지 않는다.\n")
        ta_score = (f", 언급 리뷰 평점 {ta['avg_mention_score']:.1f} / 게임 평균 {ta['game_avg_score']:.1f}"
                    if ta['avg_mention_score'] == ta['avg_mention_score'] else "")
        return f"""### {bg['name_ko']}

- 가챠 캐릭터 {bg['n_gacha']}명 · 한국어 표본 {_corpus_line(bg)}
{thin}- **공식 푸시 1위**(최고 등급·최신 출시): {tp['name_ko']} ({str(tp['release_date'])[:10]} 출시)
- **유저 반응 1위**(전체 언급): {ta['name_ko']} ({_src_line(ta)}{ta_score})
- 언급량은 **호불호를 가리지 않는 화제성**이다. 싫어서 쓴 리뷰도 언급이다. 언급 리뷰 평점이 게임 평균보다
  낮으면 부정 화제로 읽는다(각 항목의 평점 참고).
{var_line}- 매칭 가능한 {bg['n_matchable']}명 중 **{bg['n_zero_mention']}명은 댓글·리뷰 어디에서도 언급되지 않았다**
- 많이 밀렸는데 반응이 약한 쪽: {fmt(over)}
- 덜 밀렸는데 반응이 강한 쪽: {fmt(sleep)}
{src_line}"""

    game_sections = "\n".join(_game_section(g) for g in games)
    n_zero_mention = int((gacha["matchable"] & (gacha["mentions_total"] == 0)).sum())
    n_matchable = int(gacha["matchable"].sum())

    md = f"""# 프로젝트 10 · 호요버스 캐릭터 인기도 분석

**질문**: 게임사가 밀어주는 캐릭터와 유저가 실제로 반응하는 캐릭터는 일치하는가?

- 데이터 소스: 캐릭터 마스터 — 원신·붕괴:스타레일 yatta.moe / 젠레스 존 제로 Enka.Network 저장소 +
  Fandom 위키(출시일) / 붕괴3rd Fandom 위키(전투복·버전) + 수동 한글 표. 리뷰 — 한국 Google Play.
- **수집 기간은 다섯 게임 모두 같다**: 수집 시점부터 {meta.get('review_window_days', '?')}일
  ({str(meta.get('review_since', ''))[:10]} ~ {meta['fetched_at'][:10]}). 건수는 게임마다 다르다 —
  {_window_line(meta)}.
- **유저 반응은 한국어 텍스트 {_total_comments(meta) + meta['n_reviews']:,}건**에서 센다 — 구글 플레이 리뷰,
  애플 앱스토어 리뷰, 공식 한국 유튜브 채널 댓글, HoYoLAB 한국어 글의 댓글. 플레이 리뷰만 쓰던 때는
  캐릭터당 언급이 한 자릿수~십몇 건이라 순위가 한두 건 차이로 뒤집혔다. 접근 가능한 소스를 전부
  시험해 되는 것만 썼고, 막힌 곳(arca.live·dcinside·reddit 등)은 `data/source_probe.json` 에
  이유와 함께 남겼다. 대신 **공식 채널·HoYoLAB 댓글은 그 게임을 이미 보는 사람의 말**이라
  스토어 리뷰보다 호의적으로 기울 수 있다. 평점은 스토어 리뷰에서만 나온다.
- 수집 {meta['fetched_at'][:10]} · 가챠 캐릭터 {_per_game_counts(gacha)} (플레이어 캐릭터
  {meta['n_playable_avatars_excluded']}명 제외) · 리뷰 {meta['n_reviews']:,}건
- {_trends_line(trends_status)}

## 표본 — 무엇을 세었나

{_sample_table(by_game, meta)}

**게임끼리 비교할 때는 공통 표본만 쓴다.** 다섯 게임이 모두 가진 소스는 플레이 리뷰·애플 리뷰·
공식 유튜브 댓글 셋이다. HoYoLAB 은 호요버스 4개에만 있어 블루 아카이브와 견줄 수 없으므로
게임 간 수치에서는 뺀다. 게임 **안에서의** 순위는 그 게임의 모든 캐릭터가 같은 표본을 보므로
전체 표본(HoYoLAB 포함)을 쓴다. 두 값은 `mentions_total`(게임 안) 과
`mentions_common_per_10k`(게임 간)로 나눠 저장한다.

## 게임은 따로 본다

다섯 게임은 출시 주기·캐릭터 풀·표본 수가 다르다. 그래서 **순위(푸시·반응)와 격차는 게임
안에서만 매기고**, 게임을 가로지르는 순위표는 만들지 않는다. 아래 요약과 차트의 모든 순위는
그 게임 안에서의 순위다. 비교할 수 있게 맞춘 것은 **수집 기간** 하나다.

## 게임별 핵심 요약

{game_sections}
### 공통으로 보이는 것

- 매칭 가능한 캐릭터의 상당수가 네 소스 어디에도 등장하지 않는다(합쳐서 {n_matchable}명 중
  {n_zero_mention}명 무언급). 한국어 텍스트를 {_grand_total(by_game):,}건까지 모아도 그렇다.
- **가장 최근에 나온 캐릭터와 가장 많이 언급된 캐릭터는 게임마다 상당 부분 일치하지 않는다** —
  게임별 산점도(`03_push_vs_audience_rank.png`)에서 대각선(순위 일치선)을 얼마나 벗어나는지로 확인.
- 게임 간 비교가 필요한 값은 **공통 표본 만 건당 언급**으로만 적는다(아래 표). 원 건수는 소스
  구성이 게임마다 달라 나란히 놓을 수 없다.

{_cross_game_table(gacha)}
- **주의**: 관측 데이터라 "배너를 자주 돌려서 언급량이 늘었다"는 인과 해석은 하지 않는다.
  언급량은 리뷰 작성 시점의 여러 이유(신캐 출시, 밸런스 논란, 버그 등)가 섞인 결과다.

## 데이터 함정

1. **배너/재출시 이력 데이터가 없다.** 무료·키 불필요 소스 중 배너 스케줄 API를 찾지
   못해(수집 단계 주석 참고), "공식 푸시"는 **5성 여부 + 출시 최신순**이라는 거친 프록시다.
   재출시(rerun) 빈도가 실제로는 더 정확한 푸시 신호지만 여기서는 반영하지 못했다.
2. **리뷰 언급 매칭은 부정확하다.** 한글은 단어 경계가 리뷰에 명시적으로 표시되지
   않아서 이름이 짧을수록(2글자 이하) 다른 단어와 우연히 일치할 위험이 커진다.
   1글자 이름({', '.join(gacha[gacha['name_len']==1]['name_ko'].tolist()) or '없음'})은 매칭에서
   아예 제외했고, 2글자 이름 {int(gacha['name_ambiguous'].sum())}개는 상한값으로만 해석해야 한다.
3. **Google Trends 는 아직 분석에 없다.** "검색 관심도"라는, 원래 계획했던 더 깨끗한 반응
   지표를 아직 넣지 못했다(호출 가능 여부는 실행마다 `trends_status.json` 에 남는다 — 오래
   실패하다 2026-09-18 부터 시험 질의가 통과한다). 리뷰 언급량은 검색량의 대체재이지 동의어가
   아니다 — 리뷰를 남기는 유저는 전체 플레이어의 일부이고, 특정 성향(불만이 있는 유저)에
   쏠렸을 가능성이 있다.

## 산출물
- `data/characters.csv` 캐릭터 마스터, `data/reviews.csv` 리뷰 원본,
  `data/character_metrics.csv` 캐릭터별 푸시/반응 지표, `data/trends_status.json` Google Trends 실패 로그
- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과
- `charts/` 차트 8종(게임별 패널: 푸시 TOP15·반응 TOP15·순위 산점도·언급-감성 산점도 / 게임 비교: 월간 평점 추이·평점 분포·희귀도 구성·원소 분포)
- `site/index.html` 인터랙티브 대시보드
"""
    (HERE / "REPORT.md").write_text(md, encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("게임별 공식 푸시 TOP 10 (5성·출시 최신순 — 순위는 게임 안에서만)", """
SELECT name_ko_game AS 게임, push_rank AS 순위, name_ko AS 캐릭터, release_date AS 출시일
FROM characters WHERE push_rank <= 10 ORDER BY 게임, 순위;"""),
    ("게임별 유저 반응 TOP 10 (리뷰 언급량 — 순위는 게임 안에서만)", """
SELECT name_ko_game AS 게임, audience_rank AS 순위, name_ko AS 캐릭터,
       mention_count AS 언급수, avg_mention_score AS 언급리뷰평균평점
FROM characters WHERE audience_rank <= 10 ORDER BY 게임, 순위;"""),
    ("리뷰에서 한 번도 언급되지 않은 캐릭터 수 (게임별)", """
SELECT name_ko_game AS 게임, COUNT(*) AS 무언급_캐릭터수
FROM characters WHERE matchable=1 AND mention_count=0 GROUP BY name_ko_game;"""),
    ("게임별 월간 평균 평점", """
SELECT game AS 게임, month AS 월, avg_score AS 평균평점, n_reviews AS 리뷰수
FROM monthly_sentiment ORDER BY game, month;"""),
    ("언급 리뷰 평점이 게임 평균보다 높은 캐릭터 TOP 10", """
SELECT name_ko_game AS 게임, name_ko AS 캐릭터, mention_count AS 언급수,
       avg_mention_score AS 언급리뷰평점, sentiment_vs_baseline AS 기준선대비
FROM characters WHERE mention_count >= 5
ORDER BY 게임, sentiment_vs_baseline DESC;"""),
]
ANALYSIS_QUERIES = "-- 호요버스 캐릭터 인기도 분석 쿼리 (SQLite: sql/hoyoverse.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    chars, gacha, reviews, monthly, app_summary, push, audience = build_metrics()
    build_sql(gacha, reviews, monthly, app_summary)
    build_charts(gacha, reviews, monthly, push, audience)
    build_outputs(chars, gacha, reviews, monthly, app_summary, push, audience)
    for game in games_of(gacha):
        print(f"\n=== {game_ko(gacha, game)} · 공식 푸시 TOP 5 / 유저 반응 TOP 5 ===")
        with pd.option_context("display.width", 200):
            print(push[push["game"] == game][["push_rank", "name_ko", "release_date"]].head(5).to_string(index=False))
            print(audience[audience["game"] == game][["audience_rank", "name_ko", "mention_count", "avg_mention_score"]]
                  .head(5).to_string(index=False))


if __name__ == "__main__":
    main()
