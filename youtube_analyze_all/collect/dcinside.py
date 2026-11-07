"""
디시인사이드 마이너 갤러리 글 목록 수집 — 스텔라이브(stellive)·버츄얼 스나(vtubersnipe)·버츄얼 스트리머(virtual_streamer)·버츄얼 유튜버(vtuber) 갤러리.

받는 것(공개 목록 페이지에 보이는 값만): 글 번호, 작성시각, 말머리, 제목, 조회수, 추천수, 댓글 수.
받지 않는 것: **글쓴이(닉네임·아이피)·본문·댓글 내용.** 분석은 "언제, 얼마나, 무슨 말이 제목에 올랐나"만 쓴다.
공지·설문·광고 행은 제외한다.

방법: 한 페이지 100글(list_num=100). 작성시각이 시간순이라 이진 탐색으로 --since 가 있는 페이지를 찾은 뒤, 최신 쪽에서 거기까지 걷는다.
호출 사이 0.6초 쉰다. 이미 받은 글은 (gallery, no) 로 건너뛰므로 다시 돌려도 안전하다.
오류(차단·구조 변경)가 나면 삼키지 않고 멈춘다.

산출: collect/data/dc_posts.csv  (gallery, no, posted_at, subject, title, views, recommends, comments)
사용: python collect/dcinside.py --gallery stellive --since 2026-10-10
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "dc_posts.csv"
# 갤러리 id → 목록 주소. 마이너(mgallery)와 미니(mini) 갤러리는 경로가 다르다.
GALLERIES = {
    "stellive": "mgallery",        # 스텔라이브 마이너 갤러리
    "vtuber": "mgallery",          # 버츄얼 유튜버 마이너 갤러리 (글이 거의 없다)
    "vtubersnipe": "mini",         # 버츄얼 스나 (미니 갤러리)
    "virtual_streamer": "mini",    # 버츄얼 스트리머 (미니 갤러리)
}


def base(gallery: str) -> str:
    return f"https://gall.dcinside.com/{GALLERIES[gallery]}/board/lists/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
PAUSE = 0.6
COLS = ["gallery", "no", "posted_at", "subject", "title", "views", "recommends", "comments"]


class Blocked(RuntimeError):
    pass


def get_page(s: requests.Session, gallery: str, page: int) -> list[dict]:
    for attempt in range(4):
        try:
            r = s.get(base(gallery), params={"id": gallery, "list_num": 100, "page": page}, timeout=30)
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError):
            time.sleep(2 ** attempt)
            continue
        if r.status_code in (429, 500, 502, 503):
            time.sleep(2 ** attempt * 2)
            continue
        if r.status_code != 200:
            raise Blocked(f"{gallery} p{page} 응답 {r.status_code}")
        return parse(r.text, gallery)
    raise Blocked(f"{gallery} p{page} 재시도 초과")


def _int(text: str) -> int:
    m = re.sub(r"[^\d]", "", text or "")
    return int(m) if m else 0


def parse(html: str, gallery: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.select("tr.ub-content.us-post"):
        if tr.get("data-type") == "icon_notice":
            continue
        no = tr.get("data-no")
        date = tr.select_one("td.gall_date")
        tit = tr.select_one("td.gall_tit a b") or tr.select_one("td.gall_tit a")
        if not (no and date and tit and date.get("title")):
            continue
        reply = tr.select_one("span.reply_num")
        rows.append({"gallery": gallery, "no": int(no), "posted_at": date["title"],
                     "subject": (tr.select_one("td.gall_subject").get_text(strip=True) if tr.select_one("td.gall_subject") else ""),
                     "title": tit.get_text(strip=True),
                     "views": _int(tr.select_one("td.gall_count").get_text() if tr.select_one("td.gall_count") else ""),
                     "recommends": _int(tr.select_one("td.gall_recommend").get_text() if tr.select_one("td.gall_recommend") else ""),
                     "comments": _int(reply.get_text() if reply else "")})
    return rows


def oldest(rows: list[dict]) -> str:
    """그 페이지의 대표 시각 = 중간값. 최솟값을 쓰면 목록에 섞여 든 옛 날짜 글(예: 한 해 전 글)이 탐색을 망친다."""
    ts = sorted(r["posted_at"] for r in rows)
    return ts[len(ts) // 2]


def find_start_page(s: requests.Session, gallery: str, since: str) -> int:
    """oldest(page) >= since 인 마지막 페이지 근처를 이진 탐색 — 그 페이지부터 다음 페이지가 since 를 넘는다."""
    lo, hi = 1, 2
    while True:                                  # since 보다 오래된 글이 나오는 페이지를 찾는다
        rows = get_page(s, gallery, hi)
        time.sleep(PAUSE)
        if not rows or oldest(rows) < since:
            break
        lo, hi = hi, hi * 2
        if hi > 200000:
            raise Blocked(f"{gallery}: since 가 너무 오래됐다")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        rows = get_page(s, gallery, mid)
        time.sleep(PAUSE)
        if rows and oldest(rows) >= since:
            lo = mid
        else:
            hi = mid
    return lo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gallery", required=True, choices=list(GALLERIES))
    ap.add_argument("--since", required=True, help="YYYY-MM-DD 이후 글")
    ap.add_argument("--first-page", type=int, default=1, help="이 페이지(최신 쪽)부터 걷는다. 기본은 1")
    a = ap.parse_args()

    s = requests.Session()
    s.headers.update(HEADERS)
    have = pd.read_csv(OUT) if OUT.exists() else pd.DataFrame(columns=COLS)
    seen = set(zip(have["gallery"], have["no"]))
    start = find_start_page(s, a.gallery, a.since)
    print(f"{a.gallery}: {a.since} 가 있는 마지막 페이지 ≈ {start}")
    new, empty = [], 0
    for page in range(a.first_page, start + 2):            # 최신 쪽에서 오래된 쪽으로 — 새 글이 밀어내도 중복만 생기고 빠지지 않는다
        rows = get_page(s, a.gallery, page)
        time.sleep(PAUSE)
        if not rows:
            empty += 1
            if empty >= 3:
                raise Blocked(f"{a.gallery}: 빈 페이지가 이어진다(p{page}) — 차단이거나 구조가 바뀌었다")
            continue
        empty = 0
        new += [r for r in rows if r["posted_at"][:10] >= a.since and (r["gallery"], r["no"]) not in seen]
        seen |= {(r["gallery"], r["no"]) for r in rows}
        if page % 20 == 0:                                  # 중간 저장 — 끊겨도 남는다
            have = pd.concat([have, pd.DataFrame(new, columns=COLS)], ignore_index=True).drop_duplicates(["gallery", "no"])
            have.to_csv(OUT, index=False, encoding="utf-8-sig")
            new = []
            print(f"  p{page} ({oldest(rows)}) 누적 {len(have):,}")
    have = pd.concat([have, pd.DataFrame(new, columns=COLS)], ignore_index=True).drop_duplicates(["gallery", "no"])
    have.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"{a.gallery}: 저장 {len(have[have.gallery == a.gallery]):,}글 ({OUT.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
