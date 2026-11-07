"""
같은 숏폼 형식을 스텔라이브 안에서 누가 가장 먼저 올렸고, 누구의 반응이 가장 좋았나.

'같은 형식' = 서로 다른 멤버 3명 이상의 쇼츠 제목에 같이 쓰인 해시태그(멤버 이름·스텔라이브·shorts 같은 공통 태그 제외, 쇼츠 5개 이상).
  → 해시태그가 없는 형식은 못 잡는다(하한). 같은 태그가 다른 뜻으로 쓰였을 수도 있다.
'먼저' = 그 형식 쇼츠의 가장 이른 업로드 날짜(날짜 단위 — 같은 날이면 동률).
'반응' = 상대 조회수(그 쇼츠 조회수 ÷ 그 멤버 쇼츠 조회수 중앙값, 멤버 규모 차이를 지운 값). 조회수는 2026-10-27 한 시점 누적이라
  오래된 쇼츠가 유리하다 — 형식 안에서 업로드 시기가 다르면 비교가 기울어진다.
결론 문장에는 멤버 이름을 붙이지 않는다(저장소 규칙). 멤버별 값은 표에만 둔다.
자료: member_views/data/<key>_full.json, 산출: analysis/out/shorts_first_movers.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import shorts_formats as sf  # noqa: E402

OUT = HERE / "out"
NAMES = {"yuni": "유니", "huya": "후야", "hina": "히나", "mashiro": "마시로", "lize": "리제", "tabi": "타비",
         "shibuki": "시부키", "rin": "린", "nana": "나나", "riko": "리코"}
MIN_MEMBERS, MIN_N = 3, 5


def main() -> int:
    OUT.mkdir(exist_ok=True)
    d = sf.load()
    d["member"] = d["member"].map(NAMES)
    d["tags"] = d["title"].map(lambda t: {x for x in sf.tags(t) if x.startswith("#")})
    ex = d.explode("tags").dropna(subset=["tags"])
    rows, detail = [], []
    for tag, g in ex.groupby("tags"):
        if g["member"].nunique() < MIN_MEMBERS or len(g) < MIN_N:
            continue
        g = g.sort_values("date")
        first_day = g["date"].iloc[0]
        firsts = g[g["date"] == first_day]
        top = g.loc[g["rel"].idxmax()]
        by_member = g.groupby("member").agg(first=("date", "min"), best=("rel", "max"), n=("id", "count"))
        later = g[g["date"] > first_day]
        rows.append({"형식(태그)": tag, "쇼츠": len(g), "멤버": g["member"].nunique(),
                     "가장 먼저": f"{'·'.join(sorted(firsts['member'].unique()))} ({first_day.date()})",
                     "반응 최고": f"{top['member']} ({top['rel']:.1f}배, {top['date'].date()})",
                     "먼저 올린 쇼츠 상대조회수": round(firsts["rel"].median(), 2),
                     "나중 쇼츠 중앙값": round(later["rel"].median(), 2) if len(later) else None,
                     "먼저 올린 쪽이 최고?": "예" if top["member"] in set(firsts["member"]) else "아니오",
                     "_by": by_member})
        detail.append((tag, by_member))
    L = ["# 같은 숏폼 형식 — 누가 먼저 올렸고 누가 반응이 좋았나", "",
         f"쇼츠 {len(d):,}개 · 멤버 10명. 같은 형식 = 서로 다른 멤버 {MIN_MEMBERS}명 이상이 제목에 같이 쓴 해시태그(쇼츠 {MIN_N}개 이상).", ""]
    if not rows:
        L += ["조건을 만족하는 형식이 없다."]
    else:
        t = pd.DataFrame(rows).sort_values("쇼츠", ascending=False)
        yes = int((t["먼저 올린 쪽이 최고?"] == "예").sum())
        valid = t.dropna(subset=["나중 쇼츠 중앙값"])
        win = int((valid["먼저 올린 쇼츠 상대조회수"] > valid["나중 쇼츠 중앙값"]).sum())
        L += ["## 요약", "", f"- 형식 {len(t)}개 중 가장 먼저 올린 쪽의 쇼츠가 그 형식에서 반응 최고인 경우는 **{yes}개({yes / len(t):.0%})** 이다.",
              f"- 먼저 올린 쇼츠의 상대조회수가 나중 쇼츠 중앙값보다 높은 형식은 {len(valid)}개 중 **{win}개** 이다.",
              ("- 가장 먼저 올린 쪽이 반응도 가장 좋은 경우가 절반에 못 미친다 — **먼저 올렸다고 반응이 더 좋다고 말할 근거가 약하다.**"
               if yes / len(t) < 0.5 else "- 가장 먼저 올린 쪽이 반응도 가장 좋은 경우가 절반 이상이다."),
              f"- 형식 수가 {len(t)}개로 작아 검정은 내지 않았다.", "",
              "## 형식별", "", sf.table(t.drop(columns="_by")), "",
              "## 형식별 멤버 첫 업로드·최고 반응", ""]
        for tag, bm in detail:
            bm = bm.sort_values("first")
            L += [f"**{tag}**", "", sf.table(bm.reset_index().assign(first=lambda x: x["first"].dt.date, best=lambda x: x["best"].round(2))
                                            .rename(columns={"member": "멤버", "first": "첫 업로드", "best": "최고 상대조회수", "n": "쇼츠"})), ""]
    L += ["## 한계", "", "- 해시태그가 없는 형식은 못 잡고(하한), 같은 태그가 다른 뜻으로 쓰였을 수 있다.",
          "- 조회수는 한 시점 누적이라 먼저 올린(=오래된) 쇼츠가 유리하다. 같은 업로드 후 일수로 비교하려면 `collect-shorts` 이력이 쌓여야 한다.",
          "- 날짜 단위라 같은 날 올린 것은 순서를 못 가린다. 멤버 10명(1~3기)만이고 4기·창립자는 빠진다."]
    (OUT / "shorts_first_movers.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
