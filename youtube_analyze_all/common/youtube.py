"""
YouTube Data API v3 얇은 클라이언트.
requests 만으로 동작(외부 SDK 불필요). 페이지네이션/배치 처리 내장.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

BASE = "https://www.googleapis.com/youtube/v3"

# -- 일일 예산 ---------------------------------------------------------------
# Google 한도는 10,000 units/일 + search.list 100회/일, 태평양 자정에 풀린다.
# 한도에 닿기 **전에** 멈추려고 호출마다 장부에 적고, 자체 예산을 넘길 호출은 보내지 않는다.
# 20% 여유는 수동 실행·로컬 시험 몫이다. 장부는 저장소에 커밋되므로 CI 실행끼리(같은 날
# daily·weekly·수동 재실행) 서로의 소모를 본다.
DAILY_UNIT_BUDGET = 8_000
DAILY_SEARCH_BUDGET = 90
COST = {"search": 100}          # 나머지 list 엔드포인트는 1 unit
LEDGER = Path(__file__).resolve().parents[1] / "_state" / "youtube_quota.json"
LEDGER_KEEP_DAYS = 14


class QuotaExceeded(RuntimeError):
    """일일 한도 소진. 재시도해도 한도가 풀리는 태평양 자정(UTC 07/08시)까지는 안 된다."""


# 하루 한도 소진을 뜻하는 403 사유. rateLimitExceeded(초당 속도 제한)는 잠깐 쉬면 풀리므로
# 여기 넣지 않는다 — 넣으면 순간 스로틀 한 번에 그날 YouTube 수집이 전부 멈춘다.
QUOTA_REASONS = ("quotaExceeded", "dailyLimitExceeded")
RETRY_REASONS = ("rateLimitExceeded", "userRateLimitExceeded")
TRIES = 4


def _quota_day() -> str:
    """쿼터 날짜 = 미국 태평양 날짜."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    except Exception:  # noqa: BLE001  tzdata 가 없으면 PST 고정(경계가 한 시간 늦게 넘어갈 뿐)
        return (datetime.now(timezone.utc) - timedelta(hours=8)).date().isoformat()


def _caller() -> str:
    """장부에 적을 호출자 = 실행 중인 스크립트의 프로젝트 폴더명."""
    try:
        return Path(sys.argv[0]).resolve().parent.name or "?"
    except Exception:  # noqa: BLE001
        return "?"


def _load_ledger() -> dict:
    try:
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def usage_today() -> dict:
    return _load_ledger().get(_quota_day(), {"units": 0, "search": 0})


def _record(endpoint: str, cost: int, exhausted: str | None = None) -> None:
    """호출 한 번을 장부에 적는다. exhausted 는 "units"(전부 소진) 또는 "search"(검색 한도만)."""
    led = _load_ledger()
    day = _quota_day()
    d = led.setdefault(day, {"units": 0, "search": 0, "by_caller": {}})
    d["units"] = d.get("units", 0) + cost
    if endpoint == "search":
        d["search"] = d.get("search", 0) + 1
    who = _caller()
    d.setdefault("by_caller", {})[who] = d["by_caller"].get(who, 0) + cost
    if exhausted:
        d.setdefault("exhausted", [])
        if exhausted not in d["exhausted"]:
            d["exhausted"].append(exhausted)
    cutoff = (datetime.fromisoformat(day) - timedelta(days=LEDGER_KEEP_DAYS)).date().isoformat()
    led = {k: v for k, v in sorted(led.items()) if k >= cutoff}
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")


def _check_budget(endpoint: str, cost: int) -> None:
    d = usage_today()
    gone = d.get("exhausted") or []
    if "units" in gone or (endpoint == "search" and "search" in gone):
        what = "search 한도" if "units" not in gone else "한도"
        raise QuotaExceeded(f"{endpoint} 건너뜀 — 오늘({_quota_day()} PT) Google {what}가 이미 소진됨")
    if d.get("units", 0) + cost > DAILY_UNIT_BUDGET:
        raise QuotaExceeded(f"{endpoint} 건너뜀 — 자체 예산 {DAILY_UNIT_BUDGET:,} units 중 "
                            f"{d.get('units', 0):,} 사용({_quota_day()} PT)")
    if endpoint == "search" and d.get("search", 0) + 1 > DAILY_SEARCH_BUDGET:
        raise QuotaExceeded(f"search 건너뜀 — 자체 예산 {DAILY_SEARCH_BUDGET}회 중 "
                            f"{d.get('search', 0)}회 사용({_quota_day()} PT)")


class YouTube:
    def __init__(self, api_key: str, session: requests.Session | None = None):
        self.key = api_key
        self.s = session or requests.Session()

    def _get(self, endpoint: str, params: dict) -> dict:
        params = {**params, "key": self.key}
        cost = COST.get(endpoint, 1)
        r = None
        for attempt in range(TRIES):
            _check_budget(endpoint, cost)
            r = self.s.get(f"{BASE}/{endpoint}", params=params, timeout=30)
            quota_hit = (r.status_code == 403 and any(k in r.text for k in QUOTA_REASONS))
            _record(endpoint, cost, exhausted="units" if quota_hit else None)   # 실패한 호출도 쿼터를 먹는다
            if r.status_code == 200:
                return r.json()
            if quota_hit:
                raise QuotaExceeded(f"{endpoint} 한도 소진 403: {r.text[:300]}")
            # 429/5xx·속도 제한 403 은 재시도(마지막 시도 뒤에는 기다리지 않는다)
            if r.status_code in (429, 500, 503) or (
                    r.status_code == 403 and any(k in r.text for k in RETRY_REASONS)):
                if attempt < TRIES - 1:
                    time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"{endpoint} 실패 {r.status_code}: {r.text[:300]}")
        # 429 가 TRIES 번 연속이면 일시적 혼잡이 아니라 한도다(2026-09-20: search.list 일일 100회를
        # weekly 세 번이 같은 날 나눠 쓰다 세 번째에서 막혔다). search 면 검색만 막고 나머지는 둔다.
        if r is not None and r.status_code == 429:
            _record(endpoint, 0, exhausted="search" if endpoint == "search" else "units")
            raise QuotaExceeded(f"{endpoint} 한도 소진 429: {r.text[:300]}")
        raise RuntimeError(f"{endpoint} 재시도 초과 {r.status_code if r is not None else ''}")

    # -- 채널 --------------------------------------------------------------
    def channels(self, ids: list[str], part="snippet,statistics,contentDetails,brandingSettings") -> list[dict]:
        out = []
        for i in range(0, len(ids), 50):
            chunk = ids[i:i + 50]
            data = self._get("channels", {"part": part, "id": ",".join(chunk), "maxResults": 50})
            out.extend(data.get("items", []))
        return out

    # -- 업로드 재생목록의 영상 ID (최신순) --------------------------------
    def playlist_video_ids(self, playlist_id: str, limit: int = 50) -> list[str]:
        ids: list[str] = []
        token = None
        while len(ids) < limit:
            params = {"part": "contentDetails", "playlistId": playlist_id, "maxResults": 50}
            if token:
                params["pageToken"] = token
            data = self._get("playlistItems", params)
            for it in data.get("items", []):
                ids.append(it["contentDetails"]["videoId"])
            token = data.get("nextPageToken")
            if not token:
                break
        return ids[:limit]

    def uploads_playlist_id(self, channel_id: str) -> str | None:
        """채널의 '업로드' 재생목록 ID. 이걸로 전체 영상을 결정적으로 열거할 수 있다."""
        items = self.channels([channel_id], part="contentDetails")
        if not items:
            return None
        return items[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

    def playlist_videos(self, playlist_id: str, limit: int = 5000) -> list[dict]:
        """재생목록의 영상을 (id, title, published_at)으로 전량 열거한다.

        playlist_video_ids()와 달리 제목까지 받아온다. 제목으로 먼저 걸러내면
        videos.list 를 후보에만 호출할 수 있어 쿼터가 크게 줄어든다.
        비용은 페이지(50건)당 1 unit — search.list(100 units)와 비교가 안 된다.
        """
        out: list[dict] = []
        token = None
        while len(out) < limit:
            params = {"part": "snippet", "playlistId": playlist_id, "maxResults": 50}
            if token:
                params["pageToken"] = token
            data = self._get("playlistItems", params)
            for it in data.get("items", []):
                sn = it.get("snippet", {})
                vid = sn.get("resourceId", {}).get("videoId")
                if not vid:
                    continue
                out.append({
                    "video_id": vid,
                    "title": sn.get("title", ""),
                    "published_at": sn.get("publishedAt"),
                })
            token = data.get("nextPageToken")
            if not token:
                break
        return out[:limit]

    # -- 영상 상세 --------------------------------------------------------
    def videos(self, ids: list[str], part="snippet,statistics,contentDetails") -> list[dict]:
        out = []
        for i in range(0, len(ids), 50):
            chunk = ids[i:i + 50]
            data = self._get("videos", {"part": part, "id": ",".join(chunk), "maxResults": 50})
            out.extend(data.get("items", []))
        return out

    # -- 검색 -------------------------------------------------------------
    def search(self, q: str, type_="video", max_results=50, channel_id=None,
               order="relevance", **extra) -> list[dict]:
        items, token, fetched = [], None, 0
        while fetched < max_results:
            params = {"part": "snippet", "q": q, "type": type_,
                      "maxResults": min(50, max_results - fetched), "order": order, **extra}
            if channel_id:
                params["channelId"] = channel_id
            if token:
                params["pageToken"] = token
            data = self._get("search", params)
            batch = data.get("items", [])
            items.extend(batch)
            fetched += len(batch)
            token = data.get("nextPageToken")
            if not token or not batch:
                break
        return items

    # -- 댓글 -------------------------------------------------------------
    def comment_threads(self, video_id: str, limit: int = 100, order="relevance") -> list[dict]:
        items, token = [], None
        while len(items) < limit:
            params = {"part": "snippet", "videoId": video_id,
                      "maxResults": min(100, limit - len(items)), "order": order, "textFormat": "plainText"}
            if token:
                params["pageToken"] = token
            try:
                data = self._get("commentThreads", params)
            except QuotaExceeded:
                raise  # 한도는 영상 탓이 아니다 — 삼키면 남은 영상마다 재시도하며 잡 시간을 다 쓴다
            except RuntimeError:
                break  # 댓글 사용 중지된 영상 등
            items.extend(data.get("items", []))
            token = data.get("nextPageToken")
            if not token:
                break
        return items
