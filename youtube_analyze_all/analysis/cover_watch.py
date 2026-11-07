"""
유명 곡의 커버는 정말 인기를 끌었나 — 곡마다 원곡(조회수 최대 영상)과 커버를 견주고, 커버 조회수를 올린 채널의 '평소' 조회수로 나눈다.

자료: collect/data/cover_watch_views.csv · cover_watch_baseline.csv (collect/cover_watch.py).
인기 판정: '평소 대비 배수' = 커버 조회수 ÷ 그 채널 최근 업로드 10개 조회수 중앙값.
  채널이 커서 조회수가 큰 것과 곡 덕에 큰 것을 가르려는 값이다. 한 채널 평소는 지금 시점이라 오래된 커버와는 시기가 다르다.
  1배 미만이면 평소보다 못 봤다, 3배 이상이면 곡 덕이 컸다고 읽는다(기준은 임의 — 표에 값을 그대로 둔다).
한계: 검색 상위 N개만 본다. 원곡은 '조회수 최대 영상'으로 가정한다. 시점별 성장은 스냅샷이 2일 이상 쌓여야 낸다.
산출: analysis/out/cover_watch.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out"
STEL = re.compile(r"스텔라이브|stellive|아야츠노|사키하네|시라유키|네네코|아카네|아라하시|텐코|아오쿠모|하나코|유즈하|시즈키|코가네|하나요|토키노", re.I)


def day(s: str):
    m = re.search(r"(\d{4})\. (\d+)\. (\d+)\.", s or "")
    return pd.Timestamp(int(m[1]), int(m[2]), int(m[3])) if m else pd.NaT


def table(df: pd.DataFrame) -> str:
    return "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n" + \
        "\n".join("| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False))


def main() -> int:
    OUT.mkdir(exist_ok=True)
    vp, bp = ROOT / "collect" / "data" / "cover_watch_views.csv", ROOT / "collect" / "data" / "cover_watch_baseline.csv"
    if not vp.exists():
        print("collect/data/cover_watch_views.csv 가 아직 없다 — collect/cover_watch.py 먼저")
        return 1
    v = pd.read_csv(vp)
    base = pd.read_csv(bp).drop_duplicates("channel_id", keep="last").set_index("channel_id")["median_views"] if bp.exists() else pd.Series(dtype=float)
    L = ["# 유명 곡의 커버는 정말 인기를 끌었나", ""]
    for song, g in v.groupby("song"):
        snap = g["collected_at"].max()
        cur = g[g["collected_at"] == snap].copy()
        cur["pub"] = cur["published"].map(day)
        age = (pd.Timestamp(snap[:10]) - cur["pub"]).dt.days.clip(lower=1)
        cur["per_day"] = (cur["views"] / age).round(0)
        cur["base"] = cur["channel_id"].map(base)
        cur["x_base"] = (cur["views"] / cur["base"]).round(2)
        orig = cur.loc[cur["views"].idxmax()]
        covers = cur.drop(index=orig.name)
        L += [f"## {song}", "", f"기준 {snap[:10]} · 검색 상위 {len(cur)}개. 원곡(조회수 최대 영상 가정): **{orig['channel']}** — {int(orig['views']):,}회.", ""]
        ok = covers.dropna(subset=["x_base"])
        if len(ok):
            L += [f"- 커버 {len(covers)}개 중 평소 대비 배수를 계산한 {len(ok)}개의 중앙값 **{ok['x_base'].median():.2f}배**, "
                  f"1배 미만 {int((ok['x_base'] < 1).sum())}개 · 3배 이상 {int((ok['x_base'] >= 3).sum())}개.",
                  f"- 커버 조회수는 원곡의 {covers['views'].max() / orig['views']:.1%}(최대)~{covers['views'].min() / orig['views']:.2%}(최소).", ""]
        stel = cur[cur["channel"].str.contains(STEL, na=False)]
        L += [f"- 스텔라이브 채널이 올린 영상: {len(stel)}개." if len(stel) else "- 스텔라이브 채널이 올린 영상은 검색 상위에 없다.", ""]
        show = cur.sort_values("views", ascending=False)[["channel", "published", "views", "per_day", "base", "x_base"]].copy()
        show["views"] = show["views"].map("{:,}".format)
        show["base"] = show["base"].map(lambda x: "—" if pd.isna(x) else f"{x:,.0f}")
        show["x_base"] = show["x_base"].map(lambda x: "—" if pd.isna(x) else f"{x:.2f}배")
        show["per_day"] = show["per_day"].map("{:,.0f}".format)
        L += [table(show.rename(columns={"channel": "채널", "published": "업로드", "views": "조회수", "per_day": "일평균 조회수",
                                         "base": "채널 평소(중앙)", "x_base": "평소 대비"})), ""]
        days = g["collected_at"].str[:10].nunique()
        L += [f"시점별 스냅샷 {days}일치" + (" — 2일 이상 쌓이면 일별 성장을 낸다." if days < 2 else "."), ""]
        if days >= 2:
            first = g[g["collected_at"].str[:10] == g["collected_at"].str[:10].min()].set_index("video_id")["views"]
            last = cur.set_index("video_id")["views"]
            gain = (last - first.reindex(last.index)).dropna()
            L += [f"- 첫 스냅샷 이후 조회수가 오른 영상 {int((gain > 0).sum())}개 · 합계 +{int(gain.sum()):,}회.", ""]
    L += ["## 한계", "", "- 검색 상위 N개만 본다(검색 순위는 변동). 원곡은 조회수 최대 영상으로 가정했다.",
          "- 채널 평소는 최근 10개 업로드의 지금 중앙값이라 오래된 커버와는 시기가 다르다.",
          "- 곡은 `collect/cover_watch.csv` 에 올린 것만 본다(현재 한 곡). 곡을 더하면 다음 실행부터 같은 표가 생긴다."]
    (OUT / "cover_watch.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
