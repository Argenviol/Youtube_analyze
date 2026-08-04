"""
치지직(Chzzk) 비공식 API 얇은 클라이언트.
공개 엔드포인트(채널 정보 / 다시보기 VOD 목록)만 사용한다. 인증 불필요.
"""
from __future__ import annotations

import time
import requests

BASE = "https://api.chzzk.naver.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


class Chzzk:
    def __init__(self, session: requests.Session | None = None):
        self.s = session or requests.Session()
        self.s.headers.update(HEADERS)

    def _get(self, path: str, params: dict | None = None) -> dict:
        for attempt in range(4):
            r = self.s.get(f"{BASE}{path}", params=params or {}, timeout=30)
            if r.status_code == 200:
                return r.json().get("content", {}) or {}
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"{path} 실패 {r.status_code}: {r.text[:200]}")
        raise RuntimeError(f"{path} 재시도 초과")

    def search_channel(self, keyword: str) -> list[dict]:
        c = self._get("/service/v1/search/channels", {"keyword": keyword, "size": 5})
        return [it["channel"] for it in c.get("data", [])]

    def channel(self, channel_id: str) -> dict:
        return self._get(f"/service/v1/channels/{channel_id}")

    def videos(self, channel_id: str, max_items: int = 300, size: int = 50) -> list[dict]:
        """다시보기(VOD) 목록을 최신순으로 수집."""
        out, page = [], 0
        while len(out) < max_items:
            c = self._get(f"/service/v1/channels/{channel_id}/videos",
                          {"size": size, "page": page})
            data = c.get("data", [])
            if not data:
                break
            out.extend(data)
            page += 1
            if page >= c.get("totalPages", 0):
                break
        return out[:max_items]
