"""
YouTube Data API v3 얇은 클라이언트.
requests 만으로 동작(외부 SDK 불필요). 페이지네이션/배치 처리 내장.
"""
from __future__ import annotations

import time
from typing import Iterable, Iterator

import requests

BASE = "https://www.googleapis.com/youtube/v3"


class YouTube:
    def __init__(self, api_key: str, session: requests.Session | None = None):
        self.key = api_key
        self.s = session or requests.Session()

    def _get(self, endpoint: str, params: dict) -> dict:
        params = {**params, "key": self.key}
        for attempt in range(4):
            r = self.s.get(f"{BASE}/{endpoint}", params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            # 429/5xx 재시도
            if r.status_code in (429, 500, 503):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"{endpoint} 실패 {r.status_code}: {r.text[:300]}")
        raise RuntimeError(f"{endpoint} 재시도 초과")

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
            except RuntimeError:
                break  # 댓글 사용 중지된 영상 등
            items.extend(data.get("items", []))
            token = data.get("nextPageToken")
            if not token:
                break
        return items
