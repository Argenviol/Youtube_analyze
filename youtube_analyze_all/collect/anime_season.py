"""
다음 분기 TV 애니메이션 일정 수집 (AniList GraphQL, 키 불필요).

받는 것: 제목(일본어·로마자), 첫 방영일(일/월 단위로만 알려진 것도 있다), 포맷, 제작사, 인기도·팔로워 수, 장르.
못 받는 것: **OP/ED 곡·아티스트**. AniList 에 곡 정보가 없고, 곡 발표는 방영 직전까지 나뉘어 공개된다.
  → 곡 일정은 이 파일로 만들 수 없다. 곡이 공개되면 운영자가 따로 등록해야 한다.
버튜버·우타이테 곡 발매 일정은 한곳에 모인 공개 출처가 없어 수집하지 않는다.

산출: collect/data/anime_season.csv
사용: python collect/anime_season.py --season WINTER --year 2027
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import requests

URL = "https://graphql.anilist.co"
HERE = Path(__file__).resolve().parent
QUERY = """
query ($season: MediaSeason, $year: Int, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    media(season: $season, seasonYear: $year, type: ANIME, format: TV, sort: POPULARITY_DESC) {
      id title { romaji native } startDate { year month day } format genres popularity favourites
      studios(isMain: true) { nodes { name } } isAdult
    }
  }
}
"""


def fetch(season: str, year: int) -> pd.DataFrame:
    rows, page = [], 1
    while True:
        r = requests.post(URL, json={"query": QUERY, "variables": {"season": season, "year": year, "page": page}}, timeout=30)
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            raise RuntimeError(f"AniList 오류: {data['errors']}")
        p = data["data"]["Page"]
        for m in p["media"]:
            d = m["startDate"]
            rows.append({"anilist_id": m["id"], "title_native": m["title"]["native"], "title_romaji": m["title"]["romaji"],
                         "start_year": d["year"], "start_month": d["month"], "start_day": d["day"],
                         "genres": "|".join(m["genres"] or []), "popularity": m["popularity"], "favourites": m["favourites"],
                         "studio": ", ".join(n["name"] for n in m["studios"]["nodes"]), "is_adult": m["isAdult"],
                         "season": season, "season_year": year})
        if not p["pageInfo"]["hasNextPage"]:
            return pd.DataFrame(rows)
        page += 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", default="WINTER", choices=["WINTER", "SPRING", "SUMMER", "FALL"])
    ap.add_argument("--year", type=int, default=2027)
    a = ap.parse_args()
    df = fetch(a.season, a.year)
    (HERE / "data").mkdir(exist_ok=True)
    df.to_csv(HERE / "data" / "anime_season.csv", index=False, encoding="utf-8-sig")
    print(f"{a.year} {a.season} TV 애니 {len(df)}편 · 시작일 미정 {int(df['start_month'].isna().sum())}편")
    return 0


if __name__ == "__main__":
    sys.exit(main())
