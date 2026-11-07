"""
4기 데뷔 전후 디시 갤러리 반응 — 글 수·조회·추천·댓글, 제목에 4기가 언급된 글 수.

자료: collect/data/dc_posts.csv (collect/dcinside.py). 목록에 보이는 값만 쓰며 글쓴이·본문은 없다.
기준: 데뷔 전 3일(10-14~16)과 데뷔 후 7일(10-17~23)을 같은 길이의 일평균으로 비교한다.
한계: 제목에 이름이 든 글만 센다 — 줄임말·초성·별명은 놓치고(하한), 다른 뜻의 단어(예: '랑')는 섞일 수 있다(상한).
산출: analysis/out/dc_reaction.md · dc_daily.csv
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out"
POSTS = ROOT / "collect" / "data" / "dc_posts.csv"
PRE = ("2026-10-14", "2026-10-16")
POST = ("2026-10-17", "2026-10-23")
# 제목에서 찾을 말. 한 글자 이름('랑')은 오탐이 커서 '코가네'와 같이 쓰이는 경우만 센다.
WORDS = {"토아": r"토아", "랑": r"코가네\s*랑|코가네|랑이", "히요리": r"히요리", "메리": r"토키노|메리", "4기 전체": r"4기|어비스|ABYSS"}


def days(a: str, b: str) -> int:
    return (pd.Timestamp(b) - pd.Timestamp(a)).days + 1


def main() -> int:
    OUT.mkdir(exist_ok=True)
    if not POSTS.exists():
        print("collect/data/dc_posts.csv 가 아직 없다 — collect-community 의 dcinside 를 먼저 실행")
        return 1
    d = pd.read_csv(POSTS)
    d["date"] = d["posted_at"].str[:10]
    L = ["# 4기 데뷔 전후 디시 갤러리 반응", ""]
    for g, gd in d.groupby("gallery"):
        lo, hi = gd["date"].min(), gd["date"].max()
        L += [f"## {g} 갤러리", "", f"수집된 글 {len(gd):,}개 · 작성일 {lo} ~ {hi}", ""]
        if lo > PRE[0] or hi < POST[1]:
            L += [f"⚠ 수집 구간이 비교 구간({PRE[0]}~{POST[1]})을 다 덮지 못해 비교를 보류한다.", ""]
            continue
        daily = gd.groupby("date").agg(posts=("no", "count"), views=("views", "sum"), recommends=("recommends", "sum"),
                                       comments=("comments", "sum")).reset_index()
        for k, pat in WORDS.items():
            m = gd[gd["title"].str.contains(pat, flags=re.I, regex=True, na=False)]
            daily[f"mention_{k}"] = daily["date"].map(m.groupby("date").size()).fillna(0).astype(int)
        daily.to_csv(OUT / f"dc_daily_{g}.csv", index=False, encoding="utf-8-sig")

        def avg(col, span):
            x = daily[(daily["date"] >= span[0]) & (daily["date"] <= span[1])][col]
            return x.sum() / days(*span)
        L += ["| 지표 | 데뷔 전 3일 일평균 | 데뷔 후 7일 일평균 | 배수 |", "|---|---|---|---|"]
        for col, label in [("posts", "글 수"), ("views", "조회 합"), ("recommends", "추천 합"), ("comments", "댓글 합")] + \
                          [(f"mention_{k}", f"제목에 '{k}'") for k in WORDS]:
            a, b = avg(col, PRE), avg(col, POST)
            L.append(f"| {label} | {a:,.0f} | {b:,.0f} | {(f'{b / a:.2f}배' if a else '전 0건')} |")
        peak = daily.loc[daily["posts"].idxmax()]
        L += ["", f"글이 가장 많았던 날은 {peak['date']}({int(peak['posts']):,}글)이다.", ""]
    L += ["## 한계", "", "- 목록에 보이는 제목·수치만 쓴다. 본문과 댓글 내용(감성)은 보지 않는다.",
          "- 갤러리 전체 글 수는 4기 때문만이 아니라 같은 기간 다른 일(합방·이슈)에도 움직인다 — 인과가 아니라 동시 변화다."]
    (OUT / "dc_reaction.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
