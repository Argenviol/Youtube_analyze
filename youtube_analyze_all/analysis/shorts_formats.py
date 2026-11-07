"""
스텔라이브 쇼츠 형식 현황 — 어떤 해시태그·말이 제목에 든 쇼츠가 상대적으로 잘 봤나, 최근 늘고 있는 형식은 무엇인가.
그리고 **그 순위가 시간이 지나도 이어지는지**(= 유행을 미리 알 수 있는지)를 같은 자료로 검증한다.

자료: member_views/data/<key>_full.json (멤버 10명 채널의 쇼츠 전부, 조회수는 수집 시점 1회분 — 2026-10-27).
      collect/data/shorts_views.csv (collect/shorts_snapshot.py 가 매일 쌓는 시점별 조회수 — 쌓인 만큼만 쓴다).
방법: 멤버 규모 차이를 지우려고 조회수를 **그 멤버 쇼츠 조회수 중앙값으로 나눈 값(상대 조회수)** 으로 본다.
한계(결론에 그대로 적는다):
  - 조회수는 한 시점 누적값이라 오래된 쇼츠가 유리하다. 업로드 후 같은 날수로 맞춘 값이 아니다.
  - 캐릭터 디자인은 이미지 분석이 필요해 공개 자료로 신뢰할 수 있게 못 잰다 — 다루지 않는다.
  - 스텔라이브 멤버 10명의 쇼츠만이다. 다른 버튜버·일반 숏폼 유행은 이 자료에 없다.
산출: analysis/out/shorts_formats.md
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out"
KEYS = ["yuni", "huya", "hina", "mashiro", "lize", "tabi", "shibuki", "rin", "nana", "riko"]
GENERIC = {"stella", "mode", "on", "stellive", "스텔라이브", "shorts", "vtuber", "버튜버", "쇼츠", "short", "stellar", "virtual", "youtubeshorts"}
MEMBER_TAGS = {"유니", "후야", "히나", "마시로", "리제", "타비", "시부키", "린", "나나", "리코", "토아", "랑", "히요리", "메리", "강지",
               "아야츠노유니", "사키하네후야", "시라유키히나", "네네코마시로", "아카네리제", "아라하시타비", "텐코시부키", "아오쿠모린", "하나코나나", "유즈하리코"}
NAME_STEMS = ("유니", "후야", "히나", "마시로", "리제", "타비", "시부키", "린", "나나", "리코", "토아", "히요리", "메리", "강지", "하나코", "아야츠노", "사키하네",
              "시라유키", "네네코", "아카네", "아라하시", "텐코", "아오쿠모", "유즈하", "시즈키", "코가네", "하나요", "토키노", "nana", "yuni", "huya", "hina")
MIN_N = 10
HIT = 2.0          # 상대 조회수가 이 값 이상이면 '터진' 쇼츠


def _day(s: str):
    m = re.search(r"(\d{4})\. (\d+)\. (\d+)\.", s or "")
    return pd.Timestamp(int(m[1]), int(m[2]), int(m[3])) if m else pd.NaT


def load() -> pd.DataFrame:
    rows = []
    for k in KEYS:
        p = ROOT / "member_views" / "data" / f"{k}_full.json"
        for x in json.loads(p.read_text(encoding="utf-8")):
            if x.get("shorts") == 1 and x.get("views") is not None:
                rows.append({"member": k, "id": x["id"], "title": x["title"], "views": x["views"], "date": _day(x["date"])})
    d = pd.DataFrame(rows).dropna(subset=["date"])
    d["rel"] = d["views"] / d.groupby("member")["views"].transform("median")
    return d


def tags(title: str) -> set[str]:
    t = unicodedata.normalize("NFKC", title)
    out = set()
    for h in re.findall(r"#([^\s#]+)", t):
        h = h.lower()
        if h not in GENERIC and h not in MEMBER_TAGS and len(h) >= 2:
            out.add("#" + h)
    plain = re.sub(r"#[^\s#]+", " ", t)                     # 해시태그를 뺀 제목의 말(2글자 이상). 조사가 섞이므로 MIN_N 이상 쓰인 것만 센다.
    for w in re.findall(r"[가-힣A-Za-z0-9]{2,}", plain):
        w = w.lower()
        if w not in GENERIC and w not in MEMBER_TAGS and not w.startswith(NAME_STEMS):    # '타비가'·'히나의' 같은 멤버 이름+조사도 뺀다
            out.add(w)
    return out


def table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(해당 없음)"
    return "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n" + \
        "\n".join("| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False))


def lift(d: pd.DataFrame) -> pd.DataFrame:
    ex = d.explode("tags").dropna(subset=["tags"])
    g = ex.groupby("tags")
    r = pd.DataFrame({"n": g.size(), "중앙 상대조회수": g["rel"].median(), "터진 비율": g["rel"].apply(lambda s: (s >= HIT).mean())})
    return r[r["n"] >= MIN_N].sort_values("중앙 상대조회수", ascending=False)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    d = load()
    d["tags"] = d["title"].map(tags)
    base_hit = (d["rel"] >= HIT).mean()
    cut = d["date"].max() - pd.Timedelta(days=90)
    L = ["# 스텔라이브 쇼츠 형식 현황", "",
         f"쇼츠 {len(d):,}개 · 멤버 10명 · 업로드 {d['date'].min().date()} ~ {d['date'].max().date()} · 조회수 수집 시점 2026-10-27", "",
         f"상대 조회수 = 쇼츠 조회수 ÷ 그 멤버 쇼츠 중앙값. 전체에서 상대 조회수 ≥{HIT:g} 인 '터진' 쇼츠 비율은 {base_hit:.1%}.", ""]

    r = lift(d)
    L += [f"## 1. 해시태그·제목 말별 (쇼츠 {MIN_N}개 이상에 쓰인 것만)", "",
          f"'#'로 시작하는 것은 해시태그, 나머지는 제목 속 말이다(조사가 섞여 있다). {len(r)}개. "
          "멤버 이름·스텔라이브·shorts 등 모든 쇼츠에 붙는 말은 뺐다.", "", "**상대 조회수가 높은 쪽**", "",
          table(r.head(12).round(2).reset_index().rename(columns={"tags": "말"})), "", "**낮은 쪽**", "",
          table(r.drop(r.head(12).index).tail(8).round(2).reset_index().rename(columns={"tags": "말"})), ""]

    # 최근 90일에 늘어난 태그
    ex = d.explode("tags").dropna(subset=["tags"])
    rec, old = d[d["date"] > cut], d[d["date"] <= cut]
    cnt = pd.DataFrame({"최근 90일 쇼츠 중 비중": ex[ex["date"] > cut].groupby("tags").size() / max(len(rec), 1),
                        "그 전 비중": ex[ex["date"] <= cut].groupby("tags").size() / max(len(old), 1),
                        "최근 n": ex[ex["date"] > cut].groupby("tags").size()}).fillna(0)
    cnt = cnt[cnt["최근 n"] >= 5]
    cnt["최근 n"] = cnt["최근 n"].astype(int)
    cnt["증가(%p)"] = (cnt["최근 90일 쇼츠 중 비중"] - cnt["그 전 비중"]) * 100
    up = cnt.sort_values("증가(%p)", ascending=False).head(10)
    L += [f"## 2. 최근 90일({cut.date()} 이후, 쇼츠 {len(rec):,}개)에 쓰임이 늘어난 말", "",
          table(up.assign(**{"최근 90일 쇼츠 중 비중": up["최근 90일 쇼츠 중 비중"].map("{:.1%}".format), "그 전 비중": up["그 전 비중"].map("{:.1%}".format),
                             "증가(%p)": up["증가(%p)"].round(1)}).reset_index().rename(columns={"tags": "말"})), ""]

    # 예측 가능성 검증 — 앞 절반 시기의 순위가 뒤 절반에서도 이어지나
    mid = d["date"].sort_values().iloc[len(d) // 2]
    a, b = lift(d[d["date"] <= mid]), lift(d[d["date"] > mid])
    both = a.join(b, lsuffix="_앞", rsuffix="_뒤", how="inner")
    L += ["## 3. 형식의 인기가 시간이 지나도 이어지나 (예측 가능성 검증)", "",
          f"업로드 시기를 {mid.date()} 기준 앞·뒤 절반으로 나눠, 양쪽에 {MIN_N}개 이상 쓰인 말 {len(both)}개의 중앙 상대조회수를 비교했다."]
    if len(both) >= 8:
        rho = both["중앙 상대조회수_앞"].rank().corr(both["중앙 상대조회수_뒤"].rank())
        top_a = set(both.sort_values("중앙 상대조회수_앞", ascending=False).head(max(len(both) // 4, 3)).index)
        top_b = set(both.sort_values("중앙 상대조회수_뒤", ascending=False).head(max(len(both) // 4, 3)).index)
        L += ["", f"- 앞 절반 순위와 뒤 절반 순위의 스피어만 상관: **{rho:+.2f}** (말 {len(both)}개)",
              f"- 앞 절반 상위 {len(top_a)}개 중 뒤 절반에서도 상위인 것: **{len(top_a & top_b)}개**",
              ("- 상관이 약해 과거에 잘 본 형식이 앞으로도 잘 본다고 **예측할 근거가 없다.**" if rho < 0.4 else
               f"- 순위가 어느 정도는 이어지지만 비교할 수 있는 말이 {len(both)}개뿐이라 **예측 모델을 만들 만큼은 아니다.**"),
              "- 이 자료로는 '어떤 쇼츠가 유행을 탈지' 예측 모델을 만들지 않는다. 시점별 조회수 이력이 쌓인 뒤(아래 4절) 다시 본다.", ""]
    else:
        L += ["", "- 표본이 모자라 검증하지 못했다.", ""]

    # 시점별 조회수 이력
    sp = ROOT / "collect" / "data" / "shorts_views.csv"
    L += ["## 4. 시점별 조회수 이력(수집 중)", ""]
    if sp.exists():
        s = pd.read_csv(sp)
        days = pd.to_datetime(s["collected_at"]).dt.strftime("%Y-%m-%d").nunique()
        L += [f"`collect/shorts_snapshot.py` 가 매일 쌓는다 — 지금 {days}일치({s['video_id'].nunique():,}개 영상). "
              + ("업로드 후 같은 날수의 조회수를 비교하려면 최소 14일이 필요하다." if days < 14 else "14일 이상 쌓여 업로드 후 일수별 비교가 가능하다."), ""]
    else:
        L += ["아직 쌓이지 않았다 — 처음 한 번 돌고 나면 다음 실행부터 보인다.", ""]
    L += ["## 한계", "", "- 조회수는 한 시점 누적이라 오래된 쇼츠가 유리하다. 같은 업로드 후 일수로 맞춘 비교가 아니다.",
          "- 캐릭터 디자인 유행은 이미지 분석이 필요해 다루지 않는다. 스텔라이브 10명 밖의 숏폼 유행도 이 자료에 없다."]
    (OUT / "shorts_formats.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
