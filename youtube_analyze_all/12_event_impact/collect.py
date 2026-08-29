"""
프로젝트12 · 수집 단계
이벤트(대규모 합방·커버곡 발매·콘서트 등)를 찾아내 append-only 로 기억한다.

  python 12_event_impact/collect.py

## 이 프로젝트가 API를 안 쓰는 이유
새로 수집하는 게 없다. 01·02·03이 이미 가져다 둔 데이터를 **다시 읽어서** 이벤트를
추출할 뿐이다. 그래서 YouTube 쿼터 소모가 0이고, 다른 프로젝트 뒤에만 돌면 된다.

## 어떻게 합방을 찾아내나
치지직 VOD 제목·카테고리에 이미 답이 들어 있다. 두 신호를 쓴다.

  1) 카테고리 동시성 — 같은 날 같은 게임을 4명 이상이 방송했다.
     마인크래프트 서버·팰월드 같은 건 이걸로 잡힌다. 다만 talk 은 치지직의
     기본 카테고리라 "그날 다들 잡담했다"만으로도 8명이 걸린다. 그래서 제외한다.

  2) 제목 토큰 공유 — 같은 날 4명 이상의 제목에 같은 단어가 들어 있다.
     이게 talk 카테고리로 열리는 합방(봉켓몬·갈틱폰·3주년·연말 시상식)을 잡는다.
     문제는 '오늘'·'같이'·'게임' 같은 흔한 말도 4명을 넘긴다는 것. 불용어 목록을
     손으로 쓰면 계속 새는 단어가 생기므로, **토큰이 전체 날짜 중 몇 %에
     등장하는지(df)를 세서 흔한 말은 자동으로 떨어뜨린다.** 실측에서 df<=10%
     기준이 '오늘·같이·게임'을 전부 걸러내고 '봉켓몬·갈틱폰·모라하지마'만 남겼다.

## 기억(append-only)
`events_seen.csv` 에 이벤트를 **처음 감지한 날짜**를 적어 둔다. 자동 감지분은 원천
데이터에서 매번 다시 계산되므로 파일이 지워져도 복원되지만, "언제 새로 나타났는지"는
복원되지 않는다 — 주간 리포트가 "이번 주 새 이벤트"를 말하려면 이 기록이 필요하다.

콘서트·오리지널곡·오프라인 행사는 방송 데이터에 흔적이 없어 자동으로 못 찾는다.
`data/events_manual.csv` 에 손으로 적는다 — 그 파일이 유일한 진실이고, 여기서는
읽기만 한다.
"""
from __future__ import annotations

import collections
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = HERE / "data"

# 합방으로 인정할 최소 동시 참여 인원. 스텔라이브는 11명이라 4명이면 로스터의
# 3분의 1이 넘는다 — "대규모"의 하한으로 쓴다. 2~3명 콜라보는 훨씬 흔해서
# 이 기준을 내리면 이벤트가 아니라 일상이 잡힌다.
MIN_MEMBERS = 4

# 토큰이 전체 방송일 중 이 비율을 넘게 등장하면 고유명사가 아니라 흔한 말로 본다.
MAX_TOKEN_DF = 0.10

# 치지직 기본 카테고리. "같은 날 다들 잡담함"은 합방의 증거가 아니다.
DEFAULT_CATEGORIES = {"talk", "TALK", "", "nan"}

# 여러 날에 걸친 같은 이벤트(봉켓몬 6/23~7/2)를 하나로 묶을 때 허용하는 공백.
# 하루 쉬고 이어가는 경우가 흔해서 1일까지는 같은 이벤트로 본다.
RUN_GAP_DAYS = 2

# 두 신호를 한 이벤트로 볼 날짜 집합 유사도(자카드) 하한.
MIN_DATE_JACCARD = 0.5

# ── 시리즈 후보(검토 대기열) ──
#
# 신호 1·2 는 "같은 날 4명"을 본다. 며칠에 걸쳐 멤버가 번갈아 참여하는 기획은
# 하루만 떼어 보면 1~2명이라 통째로 빠진다. 실제로 봉누도(8/15~8/28, 4명)가
# 그렇게 빠졌다.
#
# 창을 넓혀 잡아 봤더니 재현율은 올라가는데 정밀도가 무너졌다 — 이벤트가 33건에서
# 106건으로 늘면서 '오늘'·'광고'·'많이' 같은 말이 이벤트로 올라왔다. 창을 넓히면
# 흔하지 않은 단어도 여러 날에 걸쳐 멤버를 그러모으기 때문이다.
#
# 그래서 이 신호는 events.csv 에 넣지 않고 **후보 파일로 따로 뺀다.** 사람이 보고
# events_manual.csv 로 올리는 검토 대기열이다. 리포트는 정밀도가 높은 신호 1·2와
# 사람이 확인한 수동 등록만 쓴다.
SERIES_WINDOW_DAYS = 21
SERIES_MAX_DF = 0.03


def _tokens(title: str) -> set[str]:
    """제목에서 2~12자 토큰을 뽑는다. 이모지·기호는 버린다."""
    return {w for w in re.sub(r"[^\w가-힣]+", " ", str(title)).split()
            if 2 <= len(w) <= 12}


def detect_collabs(streams: pd.DataFrame) -> list[dict]:
    """치지직 VOD에서 대규모 합방 후보를 뽑는다."""
    df = streams.copy()
    df["date"] = pd.to_datetime(df["publish_date"]).dt.date

    # ── 신호 2를 위한 토큰 문서빈도 ──
    per_day: dict[date, dict[str, set]] = {}
    dfreq: collections.Counter = collections.Counter()
    for d, g in df.groupby("date"):
        m: dict[str, set] = collections.defaultdict(set)
        for title, name in zip(g["title"], g["name_ko"]):
            for w in _tokens(title):
                m[w].add(name)
        per_day[d] = m
        for w in m:
            dfreq[w] += 1
    ndates = max(len(per_day), 1)

    found: list[dict] = []

    # ── 신호 1: 같은 날 같은 게임 카테고리 ──
    for (d, cat), g in df.groupby(["date", "category"]):
        if str(cat) in DEFAULT_CATEGORIES:
            continue
        members = sorted(set(g["name_ko"]))
        if len(members) >= MIN_MEMBERS:
            found.append({"date": d, "key": str(cat), "members": members,
                          "signal": "카테고리"})

    # ── 신호 2: 같은 날 제목 토큰 공유 ──
    for d, m in per_day.items():
        for w, members in m.items():
            if len(members) >= MIN_MEMBERS and dfreq[w] / ndates <= MAX_TOKEN_DF:
                found.append({"date": d, "key": w, "members": sorted(members),
                              "signal": "제목"})

    return _merge_overlapping(_merge_runs(found))


def _merge_runs(found: list[dict]) -> list[dict]:
    """같은 key 가 며칠 연속이면 한 이벤트로 묶는다(봉켓몬 6/23~7/2 = 1건).

    묶지 않으면 8일짜리 이벤트가 8건으로 잡혀 리포트가 같은 말을 여덟 번 한다.
    """
    by_key: dict[str, list[dict]] = collections.defaultdict(list)
    for f in found:
        by_key[f["key"]].append(f)

    events = []
    for key, items in by_key.items():
        items.sort(key=lambda x: x["date"])
        run = [items[0]]
        for cur in items[1:]:
            if (cur["date"] - run[-1]["date"]).days <= RUN_GAP_DAYS:
                run.append(cur)
            else:
                events.append(_fold(key, run))
                run = [cur]
        events.append(_fold(key, run))
    return events


def _fold(key: str, run: list[dict]) -> dict:
    members = sorted({m for r in run for m in r["members"]})
    signals = sorted({r["signal"] for r in run})
    return {
        "date": run[0]["date"],
        "end_date": run[-1]["date"],
        "type": "합방",
        "title": key,
        "_top": key,
        "members": "|".join(members),
        "n_members": len(members),
        "n_days": len({r["date"] for r in run}),
        # 두 신호가 같은 이벤트를 동시에 가리키면 훨씬 확실한 건이다.
        "signal": "+".join(signals),
        "_dates": {r["date"] for r in run},
        "source": "자동(치지직 VOD)",
    }


def _merge_overlapping(events: list[dict]) -> list[dict]:
    """같은 이벤트를 가리키는 여러 신호를 한 건으로 합친다.

    한 이벤트가 여러 키로 동시에 걸린다. 2026-06-25 월드컵 시청 합방은
    '2026 FIFA 북중미 월드컵'(카테고리)·'대한민국'·'남아공'·'vs'(제목) 네 건으로
    잡혔고, 6/23 마인크래프트 서버는 '마인크래프트'(카테고리)와 '봉켓몬'(제목)
    두 건이었다. 합치지 않으면 리포트가 한 이벤트를 네 번 말한다.

    판정은 **날짜 집합의 자카드 유사도**로 한다. 기간이 겹치는지만 보면 6/25 하루짜리
    월드컵 시청이 6/23~7/2 마인크래프트 서버 안에 들어간다는 이유로 한 건이 돼버린다
    (실제로 그렇게 합쳐졌다). 자카드는 1일 ∩ 8일 = 0.125 로 떨어져 둘을 갈라놓고,
    같은 이벤트의 두 신호(봉켓몬 9일 · 마인크래프트 8일 = 0.89)는 그대로 묶는다.
    """
    events = sorted(events, key=lambda e: (e["date"], e["end_date"]))
    merged: list[dict] = []
    for e in events:
        e_mem = set(e["members"].split("|"))
        for m in merged:
            m_mem = set(m["members"].split("|"))
            inter = len(e["_dates"] & m["_dates"])
            union = len(e["_dates"] | m["_dates"])
            same_period = union and inter / union >= MIN_DATE_JACCARD
            # 참여자도 봐야 한다 — 같은 날 서로 다른 두 합방이 열릴 수 있다.
            if same_period and len(e_mem & m_mem) >= MIN_MEMBERS - 1:
                m["date"] = min(m["date"], e["date"])
                m["end_date"] = max(m["end_date"], e["end_date"])
                m["members"] = "|".join(sorted(m_mem | e_mem))
                m["n_members"] = len(m_mem | e_mem)
                m["_dates"] |= e["_dates"]
                m["n_days"] = len(m["_dates"])
                m["_keys"].append((e["_top"], e["n_members"]))
                m["signal"] = "+".join(sorted(set(
                    m["signal"].split("+") + e["signal"].split("+"))))
                break
        else:
            e["_keys"] = [(e["_top"], e["n_members"])]
            merged.append(e)

    for m in merged:
        # 참여 인원이 많고 긴 이름일수록 구체적이다 — 'vs' 보다
        # '2026 FIFA 북중미 월드컵' 이 이벤트 이름에 가깝다.
        keys = sorted(set(m["_keys"]), key=lambda k: (-k[1], -len(k[0])))
        m["title"] = " · ".join(k[0] for k in keys[:2])
        m["aliases"] = "|".join(k[0] for k in keys[2:])
        del m["_keys"], m["_dates"], m["_top"]
    return merged


def _series_tokens(title: str, exclude: set[str]) -> set[str]:
    """시리즈 후보용 토큰. 일반 토큰과 두 가지가 다르다.

    1) 끝의 숫자를 뗀다 — '봉누도2'(시즌2)를 '봉누도'와 같은 것으로 본다.
       떼지 않으면 봉누도 3명 + 봉누도2 2명으로 갈려서 둘 다 기준에 못 미친다.
    2) 멤버·유닛 이름을 뺀다 — 이름은 여러 사람 제목에 자주 등장해서
       '타비'·'클리셰' 같은 게 이벤트로 잡힌다.
    """
    out = set()
    for w in re.sub(r"[^\w가-힣]+", " ", str(title)).split():
        if 2 <= len(w) <= 12:
            out.add(re.sub(r"\d+$", "", w) or w)
    return {w for w in out if len(w) >= 2 and w not in exclude}


def detect_series_candidates(streams: pd.DataFrame) -> list[dict]:
    """며칠에 걸친 기획 후보를 뽑는다. events.csv 가 아니라 검토 대기열로 나간다."""
    base = {m[0] for m in config.MEMBERS}
    exclude = base | {"스텔", "스텔라이브", "클리셰", "유니버스", "에브리스"}
    exclude |= {n.split()[0] for n in base} | {n.split()[-1] for n in base}

    df = streams.copy()
    df["date"] = pd.to_datetime(df["publish_date"]).dt.date
    per_day: dict = {}
    dfreq: collections.Counter = collections.Counter()
    for d, g in df.groupby("date"):
        m: dict = collections.defaultdict(set)
        for title, name in zip(g["title"], g["name_ko"]):
            for w in _series_tokens(title, exclude):
                m[w].add(name)
        per_day[d] = m
        for w in m:
            dfreq[w] += 1
    ndates = max(len(per_day), 1)

    best: dict = {}
    for w in dfreq:
        if dfreq[w] / ndates > SERIES_MAX_DF:
            continue
        days = sorted(d for d in per_day if w in per_day[d])
        for i, anchor in enumerate(days):
            win = [d for d in days[i:] if (d - anchor).days < SERIES_WINDOW_DAYS]
            mem = set().union(*[per_day[d][w] for d in win])
            if len(mem) >= MIN_MEMBERS and len(win) >= 2:
                cur = {"title": w, "date": win[0], "end_date": win[-1],
                       "n_members": len(mem), "n_days": len(win),
                       "members": "|".join(sorted(mem)),
                       "doc_freq": round(dfreq[w] / ndates, 4)}
                if w not in best or cur["n_members"] > best[w]["n_members"]:
                    best[w] = cur
                break
    return sorted(best.values(), key=lambda c: (-c["n_members"], c["date"]))


def detect_releases(covers: pd.DataFrame) -> list[dict]:
    """커버곡 발매. published_at 이 곧 이벤트 날짜다."""
    df = covers.copy()
    df["date"] = pd.to_datetime(df["published_at"], format="mixed",
                                utc=True).dt.tz_convert("Asia/Seoul").dt.date
    out = []
    for _, r in df.iterrows():
        out.append({
            "date": r["date"], "end_date": r["date"], "type": "커버곡",
            "title": str(r["title"])[:120], "members": r["name_ko"],
            "n_members": 1 + str(r["title"]).count(" x "),
            "n_days": 1, "signal": "발매",
            "source": "자동(YouTube)",
        })
    return out


def load_manual() -> list[dict]:
    p = DATA / "events_manual.csv"
    if not p.exists():
        return []
    df = pd.read_csv(p).fillna("")
    out = []
    for _, r in df.iterrows():
        d = pd.to_datetime(r["date"]).date()
        end = pd.to_datetime(r["end_date"]).date() if r["end_date"] else d
        members = str(r["members"])
        out.append({
            "date": d, "end_date": end, "type": r["type"], "title": r["title"],
            "members": members, "n_members": len(members.split("|")),
            "n_days": (end - d).days + 1, "signal": "수동",
            "source": "수동", "note": r.get("note", ""),
        })
    return out


def event_id(e: dict) -> str:
    slug = re.sub(r"[^\w가-힣]+", "", str(e["title"]))[:24]
    return f"{e['date']}_{e['type']}_{slug}"


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)

    streams_p = ROOT / "03_chzzk_stream_pattern" / "data" / "streams.csv"
    covers_p = ROOT / "02_cover_song_ranking" / "data" / "covers.csv"
    if not streams_p.exists() or not covers_p.exists():
        print("  ✗ 03·02의 수집 데이터가 없다. 그 프로젝트를 먼저 돌려야 한다.")
        return 1

    streams = pd.read_csv(streams_p)
    collabs = detect_collabs(streams)
    candidates = detect_series_candidates(streams)
    pd.DataFrame(candidates).to_csv(DATA / "event_candidates.csv",
                                    index=False, encoding="utf-8-sig")
    releases = detect_releases(pd.read_csv(covers_p))
    manual = load_manual()

    auto = collabs + releases
    for e in auto:
        e["event_id"] = event_id(e)
    for e in manual:
        e["event_id"] = event_id(e)

    pd.DataFrame(auto).sort_values("date", ascending=False).to_csv(
        DATA / "events_auto.csv", index=False, encoding="utf-8-sig")

    # 수동 항목이 같은 날 같은 종류의 자동 항목을 덮어쓴다 — 사람이 붙인 이름이
    # 토큰('봉켓몬')보다 정확하기 때문이다.
    manual_keys = {(e["date"], e["type"]) for e in manual}
    merged = manual + [e for e in auto if (e["date"], e["type"]) not in manual_keys]
    events = pd.DataFrame(merged).sort_values("date", ascending=False)
    events.to_csv(DATA / "events.csv", index=False, encoding="utf-8-sig")

    # ── 기억: 처음 본 날을 append-only 로 남긴다 ──
    seen_p = DATA / "events_seen.csv"
    today = datetime.now().date().isoformat()
    seen = pd.read_csv(seen_p) if seen_p.exists() else pd.DataFrame(
        columns=["event_id", "first_seen", "date", "type", "title"])
    known = set(seen["event_id"])
    new = events[~events["event_id"].isin(known)]
    if len(new):
        add = new[["event_id", "date", "type", "title"]].copy()
        add["first_seen"] = today
        seen = pd.concat([seen, add[seen.columns]], ignore_index=True)
        seen.to_csv(seen_p, index=False, encoding="utf-8-sig")

    by_type = events["type"].value_counts().to_dict()
    print(f"  이벤트 {len(events)}건 · {by_type}")
    print(f"  합방 {len(collabs)}건 (자동) · 커버곡 {len(releases)}건 · 수동 {len(manual)}건")
    print(f"  새로 감지 {len(new)}건 (누적 기억 {len(seen)}건)")
    print(f"  시리즈 후보 {len(candidates)}건 → event_candidates.csv (검토 후 수동 등록)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
