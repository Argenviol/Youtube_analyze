"""
치지직 **생방송** 채팅 집계 — 분당 채팅·고유 시청자·후원 건수와 **후원 금액**, 시청자(고유 id)별 한 시간 채팅 수.

왜 생방인가: 다시보기 채팅은 후원 금액(payAmount)이 항상 0 이고 초당 ~20건에서 잘려 저장된다.
생방 채팅 웹소켓(읽기 전용, 로그인 불필요)은 금액을 그대로 준다. 방송을 놓치면 소급할 수 없다.

동작: 스텔라이브 15명의 방송 여부를 60초마다 확인해, 켜진 채널의 채팅방에 접속하고 꺼지면 닫는다.
  - 닉네임·채팅 본문은 **저장하지 않는다.** 메시지마다 시청자 해시(userIdHash)와 종류·금액만 집계한다.
  - 후원 금액은 후원 메시지(msgTypeCode 10)의 payAmount(원). 익명 후원도 금액은 온다. 일부 후원은 금액 0 으로 온다(2026-11-07 시험에서 건수 대비 금액 0 인 분이 있었다 — 원인 미확인, 건수와 금액을 따로 둔다).
  - 연결이 끊기면 토큰을 다시 받아 재접속한다. 못 받은 구간은 그대로 비어 있고, 추정으로 채우지 않는다.

산출(collect/data/):
  live_chat_minutes.csv      minute_utc, name_ko, chats, unique_chatters, donations, donation_krw, subs, chat_members_max
  live_chat_user_hours.csv   hour_utc, name_ko, user, chats, donations, donation_krw
사용: python collect/chzzk_live_chat.py --minutes 5      (몇 분 동안 돌리고 끝낸다)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common import config  # noqa: E402

DATA = HERE / "data"
MIN_CSV = DATA / "live_chat_minutes.csv"
HOUR_CSV = DATA / "live_chat_user_hours.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
WS_URL = "wss://kr-ss1.chat.naver.com/chat"
CHAT, DONATION, SUB = 1, 10, 11
POLL = 60


def utc_minute(ms: int) -> str:
    return datetime.fromtimestamp(ms // 60000 * 60, timezone.utc).strftime("%Y-%m-%dT%H:%M")


def utc_hour(ms: int) -> str:
    return datetime.fromtimestamp(ms // 3600000 * 3600, timezone.utc).strftime("%Y-%m-%dT%H:00")


class Agg:
    """메모리 집계. 끝난 분·시간만 파일로 내보낸다."""

    def __init__(self) -> None:
        self.minutes: dict[tuple[str, str], dict] = defaultdict(lambda: {"chats": 0, "users": set(), "donations": 0, "krw": 0, "subs": 0, "members": 0})
        self.hours: dict[tuple[str, str, str], list[int]] = defaultdict(lambda: [0, 0, 0])

    def add(self, name: str, m: dict) -> None:
        code, ms = m.get("msgTypeCode"), int(m.get("msgTime") or m.get("ctime") or time.time() * 1000)
        row = self.minutes[(utc_minute(ms), name)]
        row["members"] = max(row["members"], int(m.get("mbrCnt") or 0))
        if code not in (CHAT, DONATION, SUB):
            return
        user = m.get("uid") or ""
        h = self.hours[(utc_hour(ms), name, user)] if user else None
        if code == CHAT:
            row["chats"] += 1
            if h is not None:
                h[0] += 1
        elif code == DONATION:
            try:
                krw = int(json.loads(m.get("extras") or "{}").get("payAmount") or 0)
            except (ValueError, TypeError):
                krw = 0
            row["donations"] += 1
            row["krw"] += krw
            if h is not None:
                h[1] += 1
                h[2] += krw
        else:
            row["subs"] += 1
        if user:
            row["users"].add(user)

    def flush(self, now_ms: int, final: bool = False) -> tuple[int, int]:
        """이번 분·이번 시간(아직 진행 중)은 남기고 지난 것만 내보낸다. final 이면 전부."""
        cur_min, cur_hour = utc_minute(now_ms), utc_hour(now_ms)
        mrows = [{"minute_utc": k[0], "name_ko": k[1], "chats": v["chats"], "unique_chatters": len(v["users"]), "donations": v["donations"],
                  "donation_krw": v["krw"], "subs": v["subs"], "chat_members_max": v["members"]}
                 for k, v in sorted(self.minutes.items()) if final or k[0] < cur_min]
        hrows = [{"hour_utc": k[0], "name_ko": k[1], "user": k[2], "chats": v[0], "donations": v[1], "donation_krw": v[2]}
                 for k, v in sorted(self.hours.items()) if final or k[0] < cur_hour]
        for r in mrows:
            del self.minutes[(r["minute_utc"], r["name_ko"])]
        for r in hrows:
            del self.hours[(r["hour_utc"], r["name_ko"], r["user"])]
        DATA.mkdir(exist_ok=True)
        for rows, path in ((mrows, MIN_CSV), (hrows, HOUR_CSV)):
            if rows:
                pd.DataFrame(rows).to_csv(path, mode="a", header=not path.exists(), index=False, encoding="utf-8-sig")
        return len(mrows), len(hrows)


def live_chat_channel(channel_id: str) -> str | None:
    r = requests.get(f"https://api.chzzk.naver.com/service/v3/channels/{channel_id}/live-detail", headers=HEADERS, timeout=20)
    r.raise_for_status()
    c = (r.json().get("content") or {})
    return c.get("chatChannelId") if c.get("status") == "OPEN" else None


def access_token(chat_channel: str) -> str:
    r = requests.get("https://comm-api.game.naver.com/nng_main/v1/chats/access-token",
                     params={"channelId": chat_channel, "chatType": "STREAMING"}, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()["content"]["accessToken"]


async def listen(name: str, chat_channel: str, agg: Agg, stop: asyncio.Event) -> None:
    import websockets
    tok = await asyncio.to_thread(access_token, chat_channel)
    async with websockets.connect(WS_URL, origin="https://chzzk.naver.com", open_timeout=20, ping_interval=None) as ws:
        await ws.send(json.dumps({"ver": "3", "cmd": 100, "svcid": "game", "cid": chat_channel,
                                  "bdy": {"uid": None, "devType": 2001, "accTkn": tok, "auth": "READ"}, "tid": 1}))
        while not stop.is_set():
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), 30))
            except asyncio.TimeoutError:
                await ws.send(json.dumps({"ver": "3", "cmd": 0}))       # 조용한 방도 연결을 유지한다
                continue
            cmd = msg.get("cmd")
            if cmd == 0:
                await ws.send(json.dumps({"ver": "3", "cmd": 10000}))
            elif cmd == 10000:
                await ws.send(json.dumps({"ver": "3", "cmd": 10001}))
            elif cmd in (93101, 93102):
                for m in msg.get("bdy") or []:
                    agg.add(name, m)


async def supervise(minutes: float) -> None:
    ids = {config.CHZZK_IDS[m[1]]: m[0] for m in config.MEMBERS if m[1] in config.CHZZK_IDS}
    agg, stop = Agg(), asyncio.Event()
    tasks: dict[str, asyncio.Task] = {}
    end = time.time() + minutes * 60
    last_flush = time.time()
    try:
        while time.time() < end:
            for cid, name in ids.items():
                t = tasks.get(cid)
                if t and t.done():
                    err = t.exception()
                    if err:
                        print(f"  {name} 연결 종료: {type(err).__name__} {err}")
                    tasks.pop(cid)
                if cid not in tasks:
                    try:
                        cc = await asyncio.to_thread(live_chat_channel, cid)
                    except requests.RequestException as e:
                        print(f"  {name} 방송 확인 실패: {e}")
                        continue
                    if cc:
                        print(f"  {name} 채팅방 접속 ({cc})")
                        tasks[cid] = asyncio.create_task(listen(name, cc, agg, stop))
            if time.time() - last_flush >= 300:
                print("  저장 분 %d · 시간 %d" % agg.flush(int(time.time() * 1000)))
                last_flush = time.time()
            await asyncio.sleep(POLL)
    finally:
        stop.set()
        for t in tasks.values():
            t.cancel()
        await asyncio.gather(*tasks.values(), return_exceptions=True)
        print("  최종 저장 분 %d · 시간 %d" % agg.flush(int(time.time() * 1000), final=True))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--minutes", type=float, default=5)
    a = ap.parse_args()
    asyncio.run(supervise(a.minutes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
