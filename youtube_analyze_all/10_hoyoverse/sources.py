# -*- coding: utf-8 -*-
"""
프로젝트10 · 캐릭터 마스터 소스 — 젠레스 존 제로 / 붕괴3rd

원신·붕괴:스타레일은 yatta.moe 하나로 이름·등급·출시일이 다 나온다. 나머지 두 게임은
그런 소스가 없어서 조각을 이어 붙인다. 어느 조각이 빠졌는지는 status 로 남기고, 빠진
조각은 빈 값으로 둔다(추측해서 채우지 않는다).

젠레스 존 제로 (60명)
  · 이름(ko/en)·등급(S/A) — Enka.Network 공개 저장소(raw.githubusercontent.com)
      store/zzz/avatars.json (id, Rarity 4=S/3=A, 내부 Name)
      store/zzz/locs.json    (내부 Name → 13개 언어 표시 이름)
  · 출시일 — Zenless Zone Zero Fandom 위키의 Agent Infobox `releaseDate`.
      Enka 의 짧은 영문 이름(예: Nekomata)과 위키의 brief_name/name 으로 잇는다.
      Fandom 은 이 저장소의 개발 샌드박스에서는 403 이라 GitHub Actions 러너에서만 채워진다.

붕괴3rd (플레이어블 캐릭터 41명 · 전투복 ~90종)
  · 전투복 — Honkai Impact 3 Fandom 위키 Battlesuit Introduction (character, version, rank).
  · 버전 → 날짜 — 같은 위키의 Version 페이지(GLB 서버 출시일).
  · 한글 이름 — 위키의 Other Languages 에 ko 가 비어 있고, 한국어 위키·나무위키는 봇을
      막는다. 그래서 data/hi3_names_ko.csv 에 **사람이 적은 표**를 둔다. 자동 수집이
      아니라는 뜻이고, 리포트에 그렇게 표시한다.
  · 분석 단위는 **캐릭터**다(리뷰는 "키아나"라고 쓰지 "종언의 율자"라고 쓰지 않는다).
      등급은 그 캐릭터의 최고 전투복 등급, 출시일은 가장 최근 S급 전투복의 출시일이다
      ("가장 최근에 민 것"이 푸시 프록시이므로).
"""
from __future__ import annotations

import csv
import html
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
ENKA = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/zzz/"
ZZZ_WIKI = "https://zenless-zone-zero.fandom.com/api.php"
HI3_WIKI = "https://honkaiimpact3.fandom.com/api.php"
DATE_RE = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")
MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)}


def _get(url: str, params: dict | None = None, tries: int = 3, timeout: int = 40):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def _field(wikitext: str, key: str) -> str | None:
    """{{Template |key = value}} 에서 value 하나. 첫 등장만."""
    m = re.search(r"\|\s*" + re.escape(key) + r"\s*=\s*([^|}\n]*)", wikitext)
    if not m:
        return None
    v = html.unescape(m.group(1)).replace("­", "").strip()
    v = re.sub(r"<!--.*?-->", "", v).strip()
    return v or None


def _parse_date(text: str | None) -> str | None:
    """'2024-07-04' 또는 'July 4, 2024' → ISO 날짜. 못 읽으면 None."""
    if not text:
        return None
    m = DATE_RE.search(text)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(20\d{2})", text)
    if m:
        mon = m.group(1).lower()
        key = next((k for k in MONTHS if k.startswith(mon[:3])), None)
        if key:
            return f"{m.group(3)}-{MONTHS[key]:02d}-{int(m.group(2)):02d}"
    return None


def _iso_to_unix(d: str | None) -> int | None:
    if not d:
        return None
    return int(datetime(int(d[:4]), int(d[5:7]), int(d[8:10]), tzinfo=timezone.utc).timestamp())


def _iso_dt(d: str | None) -> str | None:
    """yatta.moe 와 같은 규격(ISO 8601, UTC)으로 맞춘다. 한 열에 형식이 섞이면 pandas 가
    첫 값의 형식으로 전부 읽으려다 나머지를 NaT 로 만든다."""
    return f"{d}T00:00:00+00:00" if d else None


def fandom_category_pages(api: str, category: str) -> dict[str, str]:
    """카테고리 안 문서 전부의 wikitext. {제목: 본문}. generator 로 50개씩 넘긴다."""
    out, cont = {}, {}
    while True:
        params = dict(action="query", generator="categorymembers", gcmtitle=f"Category:{category}",
                      gcmlimit=50, gcmnamespace=0, prop="revisions", rvprop="content",
                      rvslots="main", format="json", formatversion=2, **cont)
        data = _get(api, params).json()
        for p in data.get("query", {}).get("pages", []):
            revs = p.get("revisions") or []
            if revs:
                out[p["title"]] = revs[0].get("slots", {}).get("main", {}).get("content", "") or ""
        cont = data.get("continue") or {}
        if not cont:
            break
        time.sleep(0.5)
    return out


def _norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


# ---------------------------------------------------------------------------
# 젠레스 존 제로
# ---------------------------------------------------------------------------
def zzz_master() -> tuple[list[dict], dict]:
    status = dict(names="enka", release="fandom", ok=False, error=None, n=0, n_release=0)
    avatars = _get(ENKA + "avatars.json").json()
    locs = _get(ENKA + "locs.json").json()
    ko, en = locs.get("ko", {}), locs.get("en", {})
    rows = []
    for cid, v in avatars.items():
        rarity = {4: "S", 3: "A", 2: "B"}.get(int(v.get("Rarity", 0)), str(v.get("Rarity")))
        rows.append(dict(
            # char_id 는 게임을 넘어 유일해야 한다 — 젠존제 내부 ID(1011…)가 스타레일 ID(1001…)와
            # 겹쳐서 merge 가 행을 두 배로 불린 적이 있다. 접두어를 붙인다.
            game="zzz", name_ko_game="젠레스 존 제로", char_id=f"zzz:{cid}",
            name_ko=ko.get(v["Name"]), name_en=en.get(v["Name"]),
            route_en=None, rank={"S": 5, "A": 4, "B": 3}.get(rarity), rarity_label=f"{rarity}급",
            element=",".join(v.get("ElementTypes") or []) or None,
            weapon_or_path=v.get("ProfessionType"),
            is_playable_avatar=False, release_unix=None, release_date=None,
        ))
    status["n"] = len(rows)

    # 출시일: Fandom Agent Infobox. 샌드박스에서는 403 → 빈 채로 두고 status 에 남긴다.
    try:
        pages = fandom_category_pages(ZZZ_WIKI, "Playable_Agents")
        by_key = {}
        for title, wt in pages.items():
            rd = _parse_date(_field(wt, "releaseDate"))
            if not rd:
                continue
            for k in (title, _field(wt, "name"), _field(wt, "brief_name")):
                if k:
                    by_key[_norm(k)] = rd
        for r in rows:
            k = _norm(r["name_en"])
            rd = by_key.get(k)
            if not rd:   # "Soldier 11" ↔ "Soldier 11", "Anby" ↔ "Anby Demara" 처럼 접두 일치
                cands = [d for kk, d in by_key.items() if kk.startswith(k) or k.startswith(kk)]
                rd = cands[0] if len(set(cands)) == 1 else None
            r["release_date"] = _iso_dt(rd)
            r["release_unix"] = _iso_to_unix(rd)
        status["n_release"] = sum(1 for r in rows if r["release_date"])
        status["ok"] = True
    except Exception as e:  # noqa: BLE001
        status["error"] = f"{type(e).__name__}: {str(e)[:160]}"
    return rows, status


# ---------------------------------------------------------------------------
# 붕괴3rd
# ---------------------------------------------------------------------------
def _hi3_version_dates(versions: set[str]) -> dict[str, str]:
    """Version X.Y 페이지에서 GLB 출시일. Version Entry 템플릿의 날짜 필드를 넓게 찾는다."""
    dates = {}
    for ver in sorted(versions):
        try:
            data = _get(HI3_WIKI, dict(action="parse", page=f"Version_{ver}", prop="wikitext",
                                       format="json", formatversion=2)).json()
            wt = data.get("parse", {}).get("wikitext", "") or ""
            m = re.search(r"\{\{Version Entry(.*?)\}\}", wt, re.S)
            block = m.group(1) if m else wt[:3000]
            # Version Entry 는 서버별 debut_* 필드를 둔다. 한국 서버(debut_KR)가 있으면 그것,
            # 없으면(N/A) 글로벌 NA 서버 날짜를 쓴다. 옛 버전 페이지는 필드가 없을 수 있어
            # 마지막에는 블록 안의 아무 날짜나 집는다.
            cand = None
            for key in ("debut_KR", "debut_NA", "debut_EU", "debut_SEA", "glb_date", "date", "release"):
                cand = _parse_date(_field(block, key))
                if cand:
                    break
            if not cand:
                cand = _parse_date(block)
            if cand:
                dates[ver] = cand
            time.sleep(0.4)
        except Exception:  # noqa: BLE001
            continue
    return dates


def hi3_names_ko() -> tuple[dict[str, str], str]:
    """사람이 적은 한글 이름 표. 없으면 빈 dict (그러면 리뷰 매칭이 안 된다 — 숨기지 않는다)."""
    p = DATA / "hi3_names_ko.csv"
    if not p.exists():
        return {}, "data/hi3_names_ko.csv 없음"
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["name_en"].strip(): r["name_ko"].strip() for r in rows if r.get("name_ko")}, \
        f"data/hi3_names_ko.csv ({len(rows)}행, 수동 입력)"


def hi3_master() -> tuple[list[dict], dict]:
    status = dict(names="manual(data/hi3_names_ko.csv)", release="fandom", ok=False,
                  error=None, n=0, n_release=0, n_battlesuits=0, n_named=0)
    names, names_note = hi3_names_ko()
    status["names_note"] = names_note
    try:
        pages = fandom_category_pages(HI3_WIKI, "Battlesuits")
        suits = []
        for title, wt in pages.items():
            if "{{Battlesuit Introduction" not in wt:
                continue
            block = wt.split("{{Battlesuit Introduction", 1)[1]
            suits.append(dict(
                battlesuit=title,
                character=(_field(block, "character") or "").replace("{{PAGENAME}}", title),
                version=_field(block, "version"), rank=_field(block, "rank"),
                type=_field(block, "type"),
            ))
        status["n_battlesuits"] = len(suits)
        vdates = _hi3_version_dates({s["version"] for s in suits if s["version"]})
        status["n_versions_dated"] = len(vdates)

        rows_by_char: dict[str, dict] = {}
        for s in suits:
            ch = s["character"] or ""
            if not ch:
                continue
            r = rows_by_char.setdefault(ch, dict(
                game="hi3", name_ko_game="붕괴3rd", char_id=f"hi3:{_norm(ch)}",
                name_ko=names.get(ch), name_en=ch, route_en=None,
                rank=None, rarity_label=None, element=None, weapon_or_path=None,
                is_playable_avatar=False, release_unix=None, release_date=None,
                n_battlesuits=0, best_rank=None, latest_s_battlesuit=None,
            ))
            r["n_battlesuits"] += 1
            order = {"S": 3, "A": 2, "B": 1}
            if order.get(s["rank"], 0) > order.get(r["best_rank"], 0):
                r["best_rank"] = s["rank"]
            d = vdates.get(s["version"] or "")
            if s["rank"] == "S" and d and (r["release_date"] is None or d > r["release_date"]):
                r["release_date"], r["latest_s_battlesuit"] = d, s["battlesuit"]
        for r in rows_by_char.values():
            r["rank"] = {"S": 5, "A": 4, "B": 3}.get(r["best_rank"])
            r["rarity_label"] = f"{r['best_rank']}급" if r["best_rank"] else None
            r["release_unix"] = _iso_to_unix(r["release_date"])
            r["release_date"] = _iso_dt(r["release_date"])
        rows = list(rows_by_char.values())
        status.update(n=len(rows), n_release=sum(1 for r in rows if r["release_date"]),
                      n_named=sum(1 for r in rows if r["name_ko"]), ok=True)
        return rows, status
    except Exception as e:  # noqa: BLE001
        status["error"] = f"{type(e).__name__}: {str(e)[:160]}"
        return [], status
