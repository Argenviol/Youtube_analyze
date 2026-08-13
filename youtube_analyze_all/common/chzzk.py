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

    def live_status(self, channel_id: str) -> dict:
        """현재 라이브 상태(동시시청자 포함).

        ⚠ 치지직은 방송이 꺼져 있어도 concurrentUserCount / accumulateCount /
        liveTitle 에 **직전 방송의 값**을 그대로 돌려준다. status 를 반드시 확인할 것.
        정규화는 normalize_live_status() 를 쓴다.
        """
        return self._get(f"/polling/v2/channels/{channel_id}/live-status")

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


def normalize_live_status(raw: dict) -> dict:
    """live_status 원본을 시계열에 넣어도 안전한 형태로 정규화.

    방송이 꺼져 있으면 라이브 지표는 None 으로 비우고, 잔존값은 last_* 로 분리한다.
    이 처리를 건너뛰면 오프라인 구간이 '시청자가 계속 있는 평지'로 찍혀서
    동시시청자 그래프가 통째로 거짓이 된다.
    """
    is_live = raw.get("status") == "OPEN"
    tags = raw.get("tags")
    return dict(
        status=raw.get("status"),
        is_live=is_live,
        concurrent_users=raw.get("concurrentUserCount") if is_live else None,
        accumulate_count=raw.get("accumulateCount") if is_live else None,
        live_title=raw.get("liveTitle") if is_live else None,
        category=(raw.get("liveCategoryValue") or raw.get("liveCategory")) if is_live else None,
        tags="|".join(tags) if is_live and isinstance(tags, list) else "",
        # 참고용 잔존값 — 시계열로 쓰지 말 것.
        last_concurrent_users=None if is_live else raw.get("concurrentUserCount"),
        last_live_title=None if is_live else raw.get("liveTitle"),
    )
