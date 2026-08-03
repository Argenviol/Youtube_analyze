"""
matplotlib 공통 스타일 (StelLive 분석용).
검증된 팔레트를 쓰고, 라이트 배경/얇은 축/직접 라벨 지향.
"""
from __future__ import annotations

import glob

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from . import config

# apt로 설치된 나눔 폰트를 matplotlib 캐시가 못 잡는 경우가 있어 명시적으로 등록
for _p in glob.glob("/usr/share/fonts/truetype/nanum/*.ttf"):
    try:
        font_manager.fontManager.addfont(_p)
    except Exception:
        pass

SURFACE = config.INK["surface"]
TEXT = config.INK["text"]
MUTED = config.INK["muted"]
GRID = config.INK["grid"]


def _pick_korean_font():
    """설치된 한글 폰트가 있으면 사용, 없으면 기본(한글은 □로 나올 수 있음)."""
    candidates = ["NanumGothic", "Noto Sans CJK KR", "Noto Sans KR",
                  "Malgun Gothic", "AppleGothic", "UnDotum"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for c in candidates:
        if c in available:
            return c
    return None


def apply_style():
    font = _pick_korean_font()
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": config.INK["grid"],
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlecolor": TEXT,
        "axes.labelcolor": MUTED,
        "text.color": TEXT,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.size": 11,
    })
    if font:
        plt.rcParams["font.family"] = font
        plt.rcParams["axes.unicode_minus"] = False
    return font


def barlabels(ax, bars, fmt="{:,.0f}", pad=3):
    for b in bars:
        h = b.get_height()
        ax.annotate(fmt.format(h), (b.get_x() + b.get_width() / 2, h),
                    ha="center", va="bottom", fontsize=9, color=TEXT,
                    xytext=(0, pad), textcoords="offset points")
