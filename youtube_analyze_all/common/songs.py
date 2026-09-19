# -*- coding: utf-8 -*-
"""
곡 단위 묶기 — 한 곡이 여러 영상으로 올라오는 문제

멤버 채널에는 같은 곡이 여러 판으로 올라온다: 본편 MV, [4K] 재인코딩, 3D 라이브 판, 쇼츠,
티저. 여기에 유튜브가 음원 유통사 배급분으로 자동 생성하는 "<이름> - Topic" 채널의
음원 트랙(예: 네네코 마시로 '봄꿈' MV ↔ Neneko Mashiro - Topic 'Springdream')이 따로 있다.

영상 단위로 세면 곡 수가 부풀고, 곡 단위로 안 묶으면 "그 곡이 얼마나 봤나"를 말할 수 없다.
그래서 두 단계로 묶는다.

  1) 같은 채널 안의 여러 판 → song_key (제목에서 판 표식·괄호·멤버명을 걷어낸 곡명).
  2) Topic 채널 트랙 → 같은 멤버의 영상 중 **발매일이 ±PAIR_DAYS 안에 있는 곡**과 짝짓기.
     Topic 트랙 제목은 유통 메타데이터(영문 제목이 흔함)라 제목으로는 못 잇는다.
     후보가 하나면 붙이고, 둘 이상이거나 없으면 붙이지 않고 unpaired 로 남긴다.
     사람이 확정한 짝은 topic_pairs_manual.csv 가 우선한다.

이 규칙은 근사다. 정확한 짝은 유통사 메타데이터에만 있고 그건 공개돼 있지 않다.
"""
from __future__ import annotations

import re
from datetime import timedelta

import pandas as pd

PAIR_DAYS = 3

# 판 표식 — 곡명이 아니라 "어떤 판인지"를 말하는 토큰. 곡 키에서 걷어낸다.
VERSION_TOKENS = re.compile(
    r"\[?\b4K\b\]?|\b3D\b|\bshorts?\b|#\S+|\bteaser\b|티저|\blive\b|라이브|\bMV\b|\bM/V\b|"
    r"official|음원|audio|lyric|가사|full ver\.?|short ver\.?|ver\.?\s*\d|cover|커버|"
    r"歌ってみた|うたってみた|불러[봤본]다?|by\b",
    re.IGNORECASE)
BRACKETS = re.compile(r"\(.*?\)|\[.*?\]|【.*?】|「.*?」|『.*?』|<.*?>")
SEPARATORS = re.compile(r"\s*[ㅣ|│/／]\s*|\s+[-–—]\s+|\s+x\s+", re.IGNORECASE)


def song_key(title: str | None, member_names: list[str] | None = None) -> str:
    """제목 → 곡 키. 완벽하지 않다(원제·영문·한글 표기가 섞이면 다른 키가 된다)."""
    t = str(title or "")
    t = BRACKETS.sub(" ", t)
    parts = [p for p in SEPARATORS.split(t) if p and p.strip()]
    if not parts:
        return ""
    # 멤버 이름이 든 조각은 곡명이 아니다. 남는 조각 중 가장 긴 것을 곡명으로 본다.
    names = [n.lower() for n in (member_names or [])]
    cand = [p for p in parts if not any(n and n in p.lower() for n in names)] or parts
    best = max(cand, key=lambda p: len(VERSION_TOKENS.sub("", p).strip()))
    best = VERSION_TOKENS.sub(" ", best)
    return re.sub(r"[^0-9a-z가-힣ぁ-んァ-ン一-龥]", "", best.lower())


def add_song_key(df: pd.DataFrame, title_col: str = "title",
                 member_names: list[str] | None = None) -> pd.DataFrame:
    out = df.copy()
    out["song_key"] = out[title_col].map(lambda t: song_key(t, member_names))
    return out


def pair_topic_tracks(tracks: pd.DataFrame, items: pd.DataFrame,
                      manual: pd.DataFrame | None = None,
                      days: int = PAIR_DAYS) -> pd.DataFrame:
    """Topic 트랙 하나마다 같은 멤버의 영상(items) 중 발매일이 ±days 안인 것을 찾는다.

    items 는 곡 단위로 이미 묶인 표(한 곡 = 한 행, 대표 video_id·date 보유)여야 한다.
    반환: tracks 에 paired_video_id / pair_reason 이 붙은 표.
    """
    t = tracks.copy()
    t["paired_video_id"] = None
    t["pair_reason"] = "unpaired"
    if t.empty or items.empty:
        return t
    t["date"] = pd.to_datetime(t["published_at"], utc=True, format="mixed").dt.date
    it = items.copy()
    it["date"] = pd.to_datetime(it["published_at"], utc=True, format="mixed").dt.date
    man = {}
    if manual is not None and not manual.empty:
        man = dict(zip(manual["topic_video_id"], manual["member_video_id"]))
    for i, r in t.iterrows():
        if r["video_id"] in man:
            t.at[i, "paired_video_id"] = man[r["video_id"]]
            t.at[i, "pair_reason"] = "manual"
            continue
        cands = it[(it["name_ko"] == r["name_ko"])
                   & (it["date"] >= r["date"] - timedelta(days=days))
                   & (it["date"] <= r["date"] + timedelta(days=days))]
        if len(cands) == 1:
            t.at[i, "paired_video_id"] = cands.iloc[0]["video_id"]
            t.at[i, "pair_reason"] = f"date±{days}d"
        elif len(cands) > 1:
            t.at[i, "pair_reason"] = f"ambiguous({len(cands)})"
    return t
