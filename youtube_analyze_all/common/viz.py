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
from . import montage as montage_mod

# apt 설치 폰트를 matplotlib 캐시가 못 잡는 경우가 있어 명시적으로 등록.
# Noto Sans CJK: 한글+일본어(커버곡 제목의 가나/한자)를 한 폰트로 커버.
for _p in (glob.glob("/usr/share/fonts/truetype/nanum/*.ttf")
           + glob.glob("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")):
    try:
        font_manager.fontManager.addfont(_p)
    except Exception:
        pass

SURFACE = config.INK["surface"]
TEXT = config.INK["text"]
MUTED = config.INK["muted"]
GRID = config.INK["grid"]


def _pick_korean_font():
    """설치된 한글 폰트가 있으면 사용, 없으면 기본(한글은 □로 나올 수 있음).

    이름만 보고 고르면 안 된다. 예를 들어 Windows에 Noto Sans KR이 Thin(100) 웨이트만
    설치돼 있으면 matplotlib이 bold 제목을 렌더하지 못하고 100으로 폴백해서
    제목이 흐릿하게 나온다. 그래서 normal(400) 웨이트 face가 실제로 있는지 확인한다.
    """
    # Montage 표준 서체(Pretendard)를 우선하고, 없으면 한글+일본어를 함께 커버하는
    # CJK 통합 폰트로 폴백한다.
    candidates = montage_mod.FONT_CANDIDATES

    weights: dict[str, set] = {}
    for f in font_manager.fontManager.ttflist:
        weights.setdefault(f.name, set()).add(f.weight)

    def has_regular(name: str) -> bool:
        w = weights.get(name, set())
        # matplotlib은 웨이트를 숫자 또는 문자열로 들고 있다.
        return any(x in (400, "normal", "regular") for x in w)

    for c in candidates:
        if has_regular(c):
            return c
    # 정상 웨이트를 가진 후보가 없으면 이름만이라도 맞는 것으로 폴백.
    for c in candidates:
        if c in weights:
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
