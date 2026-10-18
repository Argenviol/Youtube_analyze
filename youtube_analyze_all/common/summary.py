"""
리포트 "핵심 요약" 문장 헬퍼 — 멤버 이름을 붙인 1위·최하위 대신 분포와 패턴으로 쓴다.

공개 저장소라 "○○ 1위" 같은 문장은 그대로 캡처돼 멤버끼리의 비교로 퍼진다(2026-10-18 결정).
멤버별 수치는 표·차트에 그대로 두고, 요약 문장은 이 헬퍼로 분포(중앙값·범위)와
"지표 A 상위와 지표 B 상위가 겹치는가" 같은 패턴만 쓴다.
"""
from __future__ import annotations

from typing import Callable

import pandas as pd


def spread(s: pd.Series, fmt: Callable[[float], str]) -> str:
    """'중앙값 X · 범위 A~B' — 결측은 뺀다."""
    s = pd.to_numeric(s, errors="coerce").dropna()
    if s.empty:
        return "값 없음"
    return f"중앙값 {fmt(s.median())} · 범위 {fmt(s.min())}~{fmt(s.max())}"


def top_overlap(df: pd.DataFrame, a: str, b: str, k: int = 3) -> tuple[int, int]:
    """지표 a 상위 k명과 지표 b 상위 k명이 몇 명 겹치는지. (겹친 수, 실제 k)"""
    d = df.dropna(subset=[a, b])
    k = min(k, len(d))
    if k == 0:
        return 0, 0
    return len(set(d.nlargest(k, a).index) & set(d.nlargest(k, b).index)), k


def overlap_line(df: pd.DataFrame, a: str, b: str, label_a: str, label_b: str, k: int = 3) -> str:
    n, k = top_overlap(df, a, b, k)
    if k == 0:
        return f"{label_a}·{label_b}를 함께 비교할 값이 없다"
    if n == 0:
        return f"{label_a} 상위 {k}명과 {label_b} 상위 {k}명은 한 명도 겹치지 않는다"
    if n == k:
        return f"{label_a} 상위 {k}명과 {label_b} 상위 {k}명이 같다"
    return f"{label_a} 상위 {k}명과 {label_b} 상위 {k}명 중 겹치는 멤버는 {n}명이다"
