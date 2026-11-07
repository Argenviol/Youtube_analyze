"""
커버곡 반응 + 다음 분기 애니 방영 일정.

1) 커버곡 반응(과거): 02·12 가 이미 계산한 '커버곡 조회수 ÷ 같은 멤버의 평소 영상 조회수' 배수를 표로 옮긴다.
2) 다음 분기 TV 애니(collect/anime_season.py, AniList): 방영일·제작사·인기도 상위 목록.
못 하는 것: **OP/ED 곡·아티스트**(AniList 에 없고 공개 직전까지 나뉘어 발표된다), **버튜버·우타이테 발매 일정**(모아둔 공개 출처 없음).
  그래서 '어떤 곡이 커버 후보인가'는 이 자료로 정할 수 없고, 애니 일정은 곡 공개를 기다릴 날짜표로만 쓴다.
산출: analysis/out/cover_reaction.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out"


def table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(자료 없음)"
    return "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n" + \
        "\n".join("| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False))


def main() -> int:
    OUT.mkdir(exist_ok=True)
    L = ["# 커버곡 반응과 다음 분기 애니 일정", ""]
    ce = ROOT / "12_event_impact" / "data" / "cover_effect.csv"
    L += ["## 1. 커버곡은 평소 영상보다 얼마나 봤나", ""]
    if ce.exists():
        c = pd.read_csv(ce)
        c = c[c["n_covers"] > 0]
        L += [f"커버곡이 있는 멤버 {len(c)}명. 배수 = 커버곡 조회수 중앙값 ÷ 같은 기간 평소 영상 조회수 중앙값(곡 단위, 공식 MV+음원 합산).", "",
              f"- 멤버별 배수 중앙값 **{c['views_multiple'].median():.2f}배**, 범위 {c['views_multiple'].min():.2f}~{c['views_multiple'].max():.2f}배. "
              f"1배 미만인 멤버 {int((c['views_multiple'] < 1).sum())}명.",
              f"- 커버곡이 3곡 이상인 멤버는 {int((c['n_covers'] >= 3).sum())}명뿐이라 멤버별 배수는 표본이 작다.", "",
              table(c[["name_ko", "n_covers", "cover_median_views", "n_normal", "normal_median_views", "views_multiple"]]
                    .rename(columns={"name_ko": "멤버", "n_covers": "커버 곡 수", "cover_median_views": "커버 중앙 조회수", "n_normal": "평소 영상 수",
                                     "normal_median_views": "평소 중앙 조회수", "views_multiple": "배수"})), ""]
    else:
        L += ["자료 없음(12 분석 결과가 없다).", ""]

    ap = ROOT / "collect" / "data" / "anime_season.csv"
    L += ["## 2. 다음 분기 TV 애니 (AniList)", ""]
    if ap.exists():
        a = pd.read_csv(ap)
        a = a[~a["is_adult"]]
        season = f"{int(a['season_year'].iloc[0])} {a['season'].iloc[0]}"
        a["start"] = a.apply(lambda r: f"{int(r.start_year)}-{int(r.start_month):02d}" + (f"-{int(r.start_day):02d}" if pd.notna(r.start_day) else " (일 미정)"), axis=1)
        top = a.sort_values("popularity", ascending=False).head(20)
        L += [f"{season} TV 애니 {len(a)}편(성인물 제외). 인기도(AniList 등록 수) 상위 20편. 방영일은 일 단위로 안 정해진 것도 있다.", "",
              table(top[["title_native", "start", "studio", "popularity"]].rename(columns={"title_native": "작품", "start": "시작", "studio": "제작사", "popularity": "인기도"})), "",
              "- **OP/ED 곡은 이 자료에 없다.** 곡이 공개되면 운영자가 따로 등록해야 한다.", ""]
    else:
        L += ["자료 없음 — `collect-community` 의 anime 를 먼저 실행", ""]
    L += ["## 못 하는 것", "", "- 버튜버·우타이테의 신곡 발매 일정: 모아둔 공개 출처가 없다.",
          "- 어떤 곡을 커버하면 반응이 클지의 예측: 위 배수는 과거 커버곡의 평균이고, 곡별 반응을 미리 알 근거(자료)가 없다."]
    (OUT / "cover_reaction.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
