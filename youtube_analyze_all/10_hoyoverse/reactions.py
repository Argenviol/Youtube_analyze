# -*- coding: utf-8 -*-
"""
프로젝트10 · 유저 반응 코퍼스 — 한국어 텍스트를 모을 수 있는 곳 전부

캐릭터 언급을 세려면 한국어 텍스트가 많이 필요하다. 구글 플레이 리뷰만 쓰던 때는 게임당
1년에 수백~천 건뿐이라 캐릭터별 언급이 한 자릿수였고, 순위가 한두 건 차이로 뒤집혔다.
그래서 접근 가능한 소스를 전부 시험해 보고 되는 것만 쓴다. 시험 결과는 숨기지 않고
data/source_probe.json 에 남긴다.

되는 것 (2026-09-20 확인)
  1. Google Play 리뷰(KR)        — google-play-scraper. 창 안 전량.
  2. Apple App Store 리뷰(KR)    — itunes.apple.com RSS. 페이지당 50건, 10페이지가 상한
                                   (앱당 최대 500건, 원신 기준 약 1년치).
  3. 공식 한국 유튜브 채널 댓글  — YouTube Data API. 창 안 영상 전부 + 영상당 상위 댓글.
  4. HoYoLAB 한국어 글의 댓글    — bbs-api-os.hoyolab.com. 공식 공지·이벤트 글 하나에
                                   한국어 댓글 수백 건. 호요버스 4개 게임만(블루 아카이브 없음).

안 되는 것 (기록만 남긴다)
  · arca.live      — Cloudflare 챌린지(403)
  · dcinside       — 봇 차단(alert 스크립트만 반환)
  · reddit .json   — 403
  · 네이버 검색 API — 클라이언트 ID 필요(이 저장소는 키를 늘리지 않는다)
  · inven          — robots.txt 는 허용하지만 HTML 스크래핑이라 구조 변경에 취약해 쓰지 않는다
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 앱 ID — iTunes Search API 로 확인(2026-09-20)
APPLE_IDS = {
    "genshin": 1517783697, "starrail": 1599719154, "zzz": 1606356401,
    "hi3": 1286705196, "ba": 1571873795,
}
APPLE_MAX_PAGE = 10          # RSS 가 11페이지부터 빈 배열을 준다

# HoYoLAB 게임 코드 — 응답 제목으로 확인(2026-09-20). 블루 아카이브는 HoYoLAB 에 없다.
HOYOLAB_GIDS = {"hi3": 1, "genshin": 2, "starrail": 6, "zzz": 8}
HOYOLAB_POSTS = 60           # 게임당 공지·이벤트 글 수
HOYOLAB_REPLIES = 300        # 글당 댓글 상한


def merge_window(new: pd.DataFrame, path, key: str, when: str, window_days: int) -> pd.DataFrame:
    """이미 저장된 것과 합쳐 창 안의 것만 남긴다.

    애플 RSS 는 스로틀에 걸리면 200 인데 빈 배열을 돌려준다(실측). 그때 새로 받은 것만
    저장하면 지난 실행에서 받아 둔 리뷰까지 사라진다. 리뷰·댓글은 한 번 쓰이면 바뀌지 않으니
    합치는 쪽이 항상 맞다 — 창이 지난 것만 떨어뜨린다.
    """
    old = pd.read_csv(path) if Path(path).exists() else pd.DataFrame(columns=new.columns)
    both = pd.concat([old, new], ignore_index=True)
    if key in both.columns:
        both = both.drop_duplicates(subset=[key], keep="last")
    if when in both.columns:
        ts = pd.to_datetime(both[when], utc=True, errors="coerce", format="mixed")
        cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=window_days)
        both = both[ts.isna() | (ts >= cutoff)]
    return both.reset_index(drop=True)


def _get(url: str, params: dict | None = None, headers: dict | None = None, tries: int = 3):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers={**UA, **(headers or {})}, timeout=30)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


# ---------------------------------------------------------------------------
def fetch_apple_reviews(apps: list[dict], window_days: int) -> tuple[pd.DataFrame, dict]:
    """애플 앱스토어 한국 리뷰. RSS 는 최신순이고 10페이지가 끝이라 창보다 짧을 수 있다."""
    since = datetime.now(timezone.utc) - timedelta(days=window_days)
    cols = ["game", "name_ko", "review_id", "title", "content", "rating", "at", "app_version"]
    rows, status = [], {}
    for a in apps:
        app_id = APPLE_IDS.get(a["game"])
        if not app_id:
            continue
        n, reached, pages = 0, False, 0
        try:
            for page in range(1, APPLE_MAX_PAGE + 1):
                url = (f"https://itunes.apple.com/kr/rss/customerreviews/page={page}"
                       f"/id={app_id}/sortby=mostrecent/json")
                entries = (_get(url).json().get("feed") or {}).get("entry") or []
                # RSS 가 스로틀에 걸리면 200 인데 빈 배열을 준다. 진짜 끝인지 확인하려고
                # 두 번 더 쉬었다 물어본다 — 이걸 안 하면 창을 덮기 전에 끊긴다
                # (2026-09-20 CI 에서 원신이 4페이지 150건에서 멈췄다).
                for _retry in range(2):
                    if entries:
                        break
                    time.sleep(3 + 3 * _retry)
                    entries = (_get(url).json().get("feed") or {}).get("entry") or []
                pages += 1
                if not entries:
                    break
                for e in entries:
                    at = (e.get("updated") or {}).get("label")
                    if not at:
                        continue
                    when = datetime.fromisoformat(at.replace("Z", "+00:00"))
                    if when < since:
                        reached = True
                        continue
                    rows.append(dict(
                        game=a["game"], name_ko=a["name_ko"],
                        review_id=(e.get("id") or {}).get("label"),
                        title=(e.get("title") or {}).get("label"),
                        content=(e.get("content") or {}).get("label"),
                        rating=(e.get("im:rating") or {}).get("label"),
                        at=when.isoformat(),
                        app_version=(e.get("im:version") or {}).get("label"),
                    ))
                    n += 1
                if reached:
                    break
                time.sleep(0.4)
            status[a["game"]] = dict(app_id=app_id, n=n, pages=pages, window_complete=reached)
            print(f"  {a['name_ko']:14} 애플 리뷰 {n:,}건 ({pages}페이지"
                  + ("" if reached else ", RSS 10페이지 상한 — 창보다 짧음") + ")")
        except Exception as e:  # noqa: BLE001
            status[a["game"]] = dict(app_id=app_id, error=f"{type(e).__name__}: {str(e)[:120]}")
            print(f"  {a['name_ko']:14} 애플 리뷰 실패: {type(e).__name__}")
    return pd.DataFrame(rows, columns=cols), status


# ---------------------------------------------------------------------------
def fetch_hoyolab(apps: list[dict], window_days: int) -> tuple[pd.DataFrame, dict]:
    """HoYoLAB 한국어 글의 댓글. 공식 공지·이벤트 글이라 그 버전 캐릭터 이야기가 모인다."""
    since = datetime.now(timezone.utc) - timedelta(days=window_days)
    base = "https://bbs-api-os.hoyolab.com/community/post/wapi/"
    head = {"x-rpc-language": "ko-kr", "Referer": "https://www.hoyolab.com/"}
    cols = ["game", "name_ko", "post_id", "post_subject", "reply_id", "content", "created_at"]
    rows, status = [], {}
    for a in apps:
        gid = HOYOLAB_GIDS.get(a["game"])
        if not gid:
            status[a["game"]] = dict(note="HoYoLAB 에 없는 게임")
            continue
        n_posts = n_rep = 0
        try:
            posts, last_id = [], None
            while len(posts) < HOYOLAB_POSTS:
                params = dict(gids=gid, page_size=20, type=1)
                if last_id:
                    params["last_id"] = last_id
                data = _get(base + "getNewsList", params, head).json()
                batch = ((data.get("data") or {}).get("list") or [])
                if not batch:
                    break
                posts.extend(batch)
                last_id = (data.get("data") or {}).get("last_id")
                if not last_id:
                    break
                time.sleep(0.3)
            for p in posts[:HOYOLAB_POSTS]:
                post = p.get("post") or {}
                created = int(post.get("created_at") or 0)
                if created and datetime.fromtimestamp(created, tz=timezone.utc) < since:
                    continue
                n_posts += 1
                last_r = None
                got = 0
                while got < HOYOLAB_REPLIES:
                    rp = dict(post_id=post.get("post_id"), size=50, order_type=2)
                    if last_r:
                        rp["last_id"] = last_r
                    rd = _get(base + "getPostReplies", rp, head).json()
                    rl = ((rd.get("data") or {}).get("list") or [])
                    if not rl:
                        break
                    for it in rl:
                        r = it.get("reply") or {}
                        rows.append(dict(
                            game=a["game"], name_ko=a["name_ko"],
                            post_id=post.get("post_id"), post_subject=post.get("subject"),
                            reply_id=r.get("reply_id"), content=r.get("content"),
                            created_at=datetime.fromtimestamp(int(r.get("created_at") or 0),
                                                              tz=timezone.utc).isoformat(),
                        ))
                        got += 1
                        n_rep += 1
                    last_r = ((rd.get("data") or {}).get("last_id"))
                    if not last_r:
                        break
                    time.sleep(0.25)
                time.sleep(0.25)
            status[a["game"]] = dict(gid=gid, posts=n_posts, replies=n_rep)
            print(f"  {a['name_ko']:14} HoYoLAB 글 {n_posts}개 · 한국어 댓글 {n_rep:,}건")
        except Exception as e:  # noqa: BLE001
            status[a["game"]] = dict(gid=gid, error=f"{type(e).__name__}: {str(e)[:120]}")
            print(f"  {a['name_ko']:14} HoYoLAB 실패: {type(e).__name__}")
    return pd.DataFrame(rows, columns=cols), status


# ---------------------------------------------------------------------------
UNAVAILABLE = {
    "arca.live": "Cloudflare 챌린지(HTTP 403) — 우회하지 않는다",
    "dcinside": "봇 차단(본문 대신 alert 스크립트 반환)",
    "reddit(.json)": "HTTP 403",
    "naver 검색 API": "클라이언트 ID 필요 — 이 저장소는 키를 늘리지 않는다",
    "inven": "robots.txt 는 허용하지만 HTML 스크래핑이라 구조 변경에 취약해 채택하지 않았다",
}


def write_probe(path, extra: dict) -> None:
    path.write_text(json.dumps(dict(checked_at=datetime.now(timezone.utc).isoformat(),
                                    used=extra, unavailable=UNAVAILABLE),
                               ensure_ascii=False, indent=2), encoding="utf-8")
