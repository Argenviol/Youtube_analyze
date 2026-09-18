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
    gacha["release_dt"] = pd.to_datetime(gacha["release_date"])
    gacha["name_len"] = gacha["name_ko"].str.len()
    gacha["name_ambiguous"] = gacha["name_len"] <= 2   # 2글자 이하는 오탐 위험 표시
    gacha["matchable"] = gacha["name_len"] >= 2         # 1글자는 매칭 자체를 하지 않음

    n_reviews_by_game = reviews.groupby("game").size().to_dict()

    mention_rows = []
    for game, g in gacha.groupby("game"):
        rv = reviews[reviews["game"] == game]
        texts = rv["content"]
        scores = rv["score"]
        for _, c in g.iterrows():
            if not c["matchable"]:
                mention_rows.append(dict(char_id=c["char_id"], mention_count=None,
                                          avg_mention_score=None, mention_rate_per_10k=None))
                continue
            mask = texts.str.contains(c["name_ko"], regex=False, na=False)
            n = int(mask.sum())
            mention_rows.append(dict(
                char_id=c["char_id"], mention_count=n,
                avg_mention_score=round(float(scores[mask].mean()), 2) if n else None,
                mention_rate_per_10k=round(n / n_reviews_by_game[game] * 10000, 2),
            ))
    mentions = pd.DataFrame(mention_rows)
    gacha = gacha.merge(mentions, on="char_id", how="left")

    # 게임별 기준선(전체 리뷰 평균 평점) — 캐릭터별 언급 리뷰 평점과 비교할 기준
    baseline = reviews.groupby("game")["score"].mean().round(2).to_dict()
    gacha["game_avg_score"] = gacha["game"].map(baseline)
    gacha["sentiment_vs_baseline"] = (gacha["avg_mention_score"] - gacha["game_avg_score"]).round(2)

    # 순위는 **게임 안에서만** 매긴다. 원신과 스타레일은 출시 주기도, 리뷰 표본 수도,
    # 캐릭터 풀 크기도 다르다. 한 순위표에 섞으면 "원신 신캐가 스타레일 신캐보다 더
    # 밀렸다"는 식의, 아무도 묻지 않은 비교가 생긴다. 게임마다 따로 묻고 따로 답한다.
    #
    # 공식 푸시 랭킹: 5성만, 출시 최신순 (게임별)
    push = (gacha[gacha["rank"] == 5]
            .sort_values(["game", "release_dt"], ascending=[True, False])
            .reset_index(drop=True))
    push["push_rank"] = push.groupby("game").cumcount() + 1

    # 유저 반응 랭킹: 매칭 가능한 캐릭터 중 언급량 많은 순 (전체 등급 포함, 게임별)
    audience = (gacha[gacha["matchable"] & gacha["mention_count"].notna()]
                .sort_values(["game", "mention_count"], ascending=[True, False])
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


def _gc(games):
    cmap = {"genshin": config.PALETTE["series"][0], "starrail": config.PALETTE["series"][1]}
    return [cmap.get(g, "#888") for g in games]


def build_charts(gacha, reviews, monthly, push, audience):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    S = config.PALETTE["series"]

    # 게임마다 패널을 하나씩. 두 게임을 한 축에 올리면 순위·언급량이 게임 간 비교처럼
    # 읽히는데, 그런 비교는 이 프로젝트의 질문이 아니다.
    games = games_of(gacha)
    n = len(games)

    # 1. 공식 푸시 프록시: 5성 캐릭터 출시 최신순 TOP 15 — 게임별
    fig, axes = plt.subplots(1, n, figsize=(6.2 * n, 6.5), squeeze=False)
    for ax, game in zip(axes[0], games):
        d = push[push["game"] == game].head(TOP_N).sort_values("release_dt")
        ax.barh(d["name_ko"], range(len(d)), color=_gc([game])[0], height=0.72, zorder=3)
        ax.set_xticks([]); ax.set_title(f"{game_ko(gacha, game)} · 5성 출시 최신순 TOP {TOP_N}")
        for i, (_, r) in enumerate(d.iterrows()):
            ax.annotate(str(r["release_date"])[:10], (0, i), va="center", ha="left",
                        fontsize=9, color=config.INK["text"], xytext=(6, 0), textcoords="offset points")
        ax.grid(False); ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)
    fig.suptitle("공식 푸시 프록시 (게임별 순위 — 게임 간 비교 아님)")
    fig.tight_layout(); fig.savefig(CHARTS / "01_push_proxy_top15.png", dpi=140); plt.close(fig)

    # 2. 유저 반응: 리뷰 언급량 TOP 15 — 게임별
    fig, axes = plt.subplots(1, n, figsize=(6.2 * n, 6.5), squeeze=False)
    for ax, game in zip(axes[0], games):
        d = audience[audience["game"] == game].head(TOP_N).sort_values("mention_count")
        bars = ax.barh(d["name_ko"], d["mention_count"], color=_gc([game])[0], height=0.72, zorder=3)
        ax.set_title(f"{game_ko(gacha, game)} · 리뷰 언급량 TOP {TOP_N}")
        ax.grid(axis="x", zorder=0); ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
        for b, v in zip(bars, d["mention_count"]):
            ax.annotate(f"{int(v)}건", (b.get_width(), b.get_y()+b.get_height()/2), va="center", ha="left",
                        fontsize=9, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
        ax.margins(x=0.16)
    fig.suptitle("유저 반응 프록시 (게임별 — 리뷰 표본 수가 달라 게임 간 건수 비교 아님)")
    fig.tight_layout(); fig.savefig(CHARTS / "02_audience_mentions_top15.png", dpi=140); plt.close(fig)

    # 3. 푸시 랭크 vs 반응 랭크 산점도 — 게임별 (두 랭킹에 모두 든 캐릭터)
    fig, axes = plt.subplots(1, n, figsize=(6.5 * n, 6.8), squeeze=False)
    for ax, game in zip(axes[0], games):
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
    fig.tight_layout(); fig.savefig(CHARTS / "03_push_vs_audience_rank.png", dpi=140); plt.close(fig)

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

    # 6. 게임별 희귀도(4성/5성) 구성
    fig, ax = plt.subplots(figsize=(7, 5))
    ct = gacha.groupby(["game", "rank"]).size().unstack(fill_value=0)
    games = ct.index.tolist()
    b5 = ax.bar(games, ct.get(5, 0), color=S[4], label="5성", zorder=3)
    b4 = ax.bar(games, ct.get(4, 0), bottom=ct.get(5, 0), color=S[3], label="4성", zorder=3)
    ax.set_xticks(range(len(games))); ax.set_xticklabels([game_ko(gacha, g) for g in games])
    ax.set_title("게임별 캐릭터 희귀도 구성 (여행자/개척자 제외)")
    ax.grid(axis="y", zorder=0); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(CHARTS / "06_rarity_composition.png", dpi=140); plt.close(fig)

    # 7. 원소/속성 분포 (게임별)
    fig, axes = plt.subplots(1, n, figsize=(6.5 * n, 5), squeeze=False)
    for ax, game in zip(axes[0], games):
        d = gacha[gacha["game"] == game]["element"].value_counts()
        ax.barh(d.index[::-1], d.values[::-1], color=S[:len(d)][::-1], zorder=3)
        ax.set_title(f"{game_ko(gacha, game)} 원소/속성 분포"); ax.grid(axis="x", zorder=0)
        ax.spines["left"].set_visible(False)
    fig.tight_layout(); fig.savefig(CHARTS / "07_element_distribution.png", dpi=140); plt.close(fig)

    # 8. 언급량 vs 감성(언급 리뷰 평균 평점) 산점도 — 게임별, 언급 5건 이상만 (표본 최소 확보)
    fig, axes = plt.subplots(1, n, figsize=(6.5 * n, 6), squeeze=False)
    for ax, game in zip(axes[0], games):
        d = gacha[(gacha["game"] == game) & (gacha["mention_count"].fillna(0) >= 5)]
        ax.scatter(d["mention_count"], d["avg_mention_score"], s=90, c=_gc([game])[0],
                   alpha=0.8, edgecolors="white", linewidths=1.2, zorder=3)
        for _, r in d.iterrows():
            ax.annotate(r["name_ko"], (r["mention_count"], r["avg_mention_score"]), fontsize=8,
                        xytext=(5, 4), textcoords="offset points", color=config.INK["text"])
        base = reviews[reviews["game"] == game]["score"].mean()
        ax.axhline(base, color=config.INK["grid"], linestyle="--", zorder=1, label=f"게임 평균 평점 {base:.2f}")
        ax.set_xlabel("리뷰 언급 횟수 (언급 5건 이상만 표시)"); ax.set_ylabel("언급 리뷰 평균 평점")
        ax.set_title(f"{game_ko(gacha, game)} · 언급량 vs 언급 리뷰 감성"); ax.grid(True, zorder=0)
        ax.legend(frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(CHARTS / "08_mentions_vs_sentiment.png", dpi=140); plt.close(fig)

    print(f"차트 8종 -> {CHARTS}")


def _trends_line(status: dict) -> str:
    """Google Trends 상태를 실제 기록대로 한 줄로 쓴다.

    예전에는 "매 시도 즉시 429" 라고 본문에 박아 뒀는데, 실제 마지막 실행의 기록은
    `ModuleNotFoundError` 였다(라이브러리가 아예 없어서 호출조차 안 됨). 실패의 종류가
    다르면 독자가 판단할 것도 달라진다 — 기록된 것만 쓴다.
    """
    if status.get("ok"):
        return (f"**Google Trends 사용** — {status.get('n_rows', 0)}행 확보. "
                "검색 관심도와 리뷰 언급량을 함께 본다.")
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
            n_matchable=int(g["matchable"].sum()),
            n_zero_mention=int((g["matchable"] & (g["mention_count"] == 0)).sum()),
            push_top=_recs(push[push["game"] == game].head(TOP_N)),
            audience_top=_recs(audience[audience["game"] == game].head(TOP_N)),
            gap_overpushed=_recs(b.sort_values("gap", ascending=False).head(5)),
            gap_sleeper=_recs(b.sort_values("gap").head(5)),
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
        if tp.empty or ta.empty:
            return f"### {bg['name_ko']}\n\n- 순위를 매길 데이터가 부족하다.\n"
        tp, ta = tp.iloc[0], ta.iloc[0]
        over = bg["gap_overpushed"][:3]
        sleep = bg["gap_sleeper"][:3]
        fmt = lambda rows: ", ".join(f"{r['name_ko']}(푸시 {int(r['push_rank'])}위→반응 {int(r['audience_rank'])}위)" for r in rows) or "—"
        return f"""### {bg['name_ko']}

- 가챠 캐릭터 {bg['n_gacha']}명 · 리뷰 {bg['n_reviews']:,}건
- **공식 푸시 1위**(5성·최신 출시): {tp['name_ko']} ({str(tp['release_date'])[:10]} 출시)
- **유저 반응 1위**(리뷰 언급량): {ta['name_ko']} ({int(ta['mention_count'])}건 언급)
- 매칭 가능한 {bg['n_matchable']}명 중 **{bg['n_zero_mention']}명은 리뷰에서 한 번도 언급되지 않았다**
- 많이 밀렸는데 반응이 약한 쪽: {fmt(over)}
- 덜 밀렸는데 반응이 강한 쪽: {fmt(sleep)}
"""

    game_sections = "\n".join(_game_section(g) for g in games)
    n_zero_mention = int((gacha["matchable"] & (gacha["mention_count"] == 0)).sum())
    n_matchable = int(gacha["matchable"].sum())

    md = f"""# 프로젝트 10 · 호요버스 캐릭터 인기도 분석

**질문**: 게임사가 밀어주는 캐릭터와 유저가 실제로 반응하는 캐릭터는 일치하는가?

- 데이터 소스: yatta.moe(Project Amber 후신, 캐릭터 마스터) + Google Play 리뷰
  (원신·붕괴:스타레일, 게임당 최근 리뷰 최대 {meta['n_reviews_requested_per_app']:,}건)
- 수집 {meta['fetched_at'][:10]} · 캐릭터 {meta['n_characters']}명(가챠 대상 {len(gacha)}명,
  여행자/개척자 {meta['n_playable_avatars_excluded']}명 제외) · 리뷰 {meta['n_reviews']:,}건
- {_trends_line(trends_status)}

## 게임은 따로 본다

원신과 붕괴:스타레일은 출시 주기·캐릭터 풀·리뷰 표본 수가 다르다. 그래서 **순위(푸시·반응)와
격차는 게임 안에서만 매기고**, 게임을 가로지르는 순위표는 만들지 않는다. 아래 요약과 차트의
모든 순위는 그 게임 안에서의 순위다. 젠레스 존 제로·붕괴3rd 는 캐릭터 마스터 소스가 없어
아직 없다(README 참고) — 소스가 생기면 같은 규격으로 한 절씩 추가된다.

## 게임별 핵심 요약

{game_sections}
### 공통으로 보이는 것

- 두 게임 모두 매칭 가능한 캐릭터 대부분이 리뷰에 등장하지 않는다(합쳐서 {n_matchable}명 중
  {n_zero_mention}명 무언급). 표본이 게임당 {meta['n_reviews_requested_per_app']:,}건이라 리뷰에
  이름이 오르는 캐릭터는 소수다.
- **가장 최근에 나온 캐릭터와 가장 많이 언급된 캐릭터는 게임마다 상당 부분 일치하지 않는다** —
  게임별 산점도(`03_push_vs_audience_rank.png`)에서 대각선(순위 일치선)을 얼마나 벗어나는지로 확인.
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
3. **Google Trends 없음.** "검색 관심도"라는, 원래 계획했던 더 깨끗한 반응 지표를
   못 썼다. 리뷰 언급량은 검색량의 대체재이지 동의어가 아니다 — 리뷰를 남기는 유저는
   전체 플레이어의 일부이고, 특정 성향(불만이 있는 유저)에 쏠렸을 가능성이 있다.

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
