"""
Montage (Wanted Lab Design System for Web) 디자인 토큰.

출처: https://github.com/wanteddev/montage-web  (MIT)
      packages/wds-theme/src/theme/{atomic,semantic,spacing}

Montage 본체는 React 컴포넌트 라이브러리(@wanteddev/wds)라 정적 HTML 대시보드에
그대로 넣을 수 없다. 그래서 **토큰 값만 추출해 CSS 변수 / matplotlib 색으로 옮긴다.**
컴포넌트가 아니라 색·간격·타이포 체계를 따르는 방식이다.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Atomic — 원자 팔레트 (wds-theme/src/theme/atomic)
# ---------------------------------------------------------------------------
COOL_NEUTRAL = {
    5: "#0F0F10", 7: "#141415", 10: "#171719", 15: "#1B1C1E", 17: "#212225",
    20: "#292A2D", 22: "#2E2F33", 23: "#333438", 25: "#37383C", 30: "#46474C",
    40: "#5A5C63", 50: "#70737C", 60: "#878A93", 70: "#989BA2", 80: "#AEB0B6",
    90: "#C2C4C8", 95: "#DBDCDF", 96: "#E1E2E4", 97: "#EAEBEC", 98: "#F4F4F5",
    99: "#F7F7F8",
}
BLUE = {40: "#0054D1", 45: "#005EEB", 50: "#0066FF", 55: "#1A75FF", 60: "#3385FF"}
RED = {40: "#E52222", 50: "#FF4242", 60: "#FF6363"}
RED_ORANGE = {48: "#F55A00", 50: "#FF5E00", 60: "#FF7B2E"}
ORANGE = {39: "#D17600", 50: "#FF9200", 60: "#FFA938"}
LIME = {37: "#429E00", 50: "#58CF04", 60: "#6BE016"}
GREEN = {40: "#009632", 50: "#00BF40", 60: "#1ED45A"}
CYAN = {40: "#0098B2", 50: "#00BDDE", 60: "#28D0ED"}
LIGHT_BLUE = {40: "#008DCF", 50: "#00AEFF", 60: "#3DC2FF"}
VIOLET = {45: "#5B37ED", 50: "#6541F2", 60: "#7D5EF7"}
PURPLE = {40: "#AD36E3", 50: "#CB59FF", 60: "#D478FF"}
PINK = {46: "#E846CD", 50: "#F553DA", 60: "#FA73E3"}
WHITE, BLACK = "#ffffff", "#000000"

# ---------------------------------------------------------------------------
# Semantic — 라이트/다크 (wds-theme/src/theme/semantic)
#   Montage 원본은 알파 합성(addHexOpacity)을 쓰지만, matplotlib은 8자리 hex를
#   일관되게 다루지 못한다. 그래서 불투명 근사값으로 평탄화했다.
# ---------------------------------------------------------------------------
LIGHT = {
    "primary": BLUE[50],
    "primary_strong": BLUE[45],
    "bg": WHITE,                       # background.normal.normal
    "bg_alt": COOL_NEUTRAL[99],        # background.normal.alternative
    "bg_elevated": WHITE,
    "label": COOL_NEUTRAL[10],         # label.normal
    "label_strong": BLACK,
    "label_neutral": COOL_NEUTRAL[25],
    "label_alt": COOL_NEUTRAL[50],     # label.alternative
    "label_assistive": COOL_NEUTRAL[70],
    "line": COOL_NEUTRAL[96],          # line.solid.normal
    "line_neutral": COOL_NEUTRAL[97],
    "line_alt": COOL_NEUTRAL[98],
    "fill": COOL_NEUTRAL[98],
    "positive": GREEN[50],
    "cautionary": ORANGE[50],
    "negative": RED[50],
}

DARK = {
    "primary": BLUE[60],
    "primary_strong": BLUE[55],
    "bg": COOL_NEUTRAL[15],
    "bg_alt": COOL_NEUTRAL[5],
    "bg_elevated": COOL_NEUTRAL[17],
    "label": COOL_NEUTRAL[99],
    "label_strong": WHITE,
    "label_neutral": COOL_NEUTRAL[90],
    "label_alt": COOL_NEUTRAL[80],
    "label_assistive": COOL_NEUTRAL[70],
    "line": COOL_NEUTRAL[25],
    "line_neutral": COOL_NEUTRAL[23],
    "line_alt": COOL_NEUTRAL[22],
    "fill": COOL_NEUTRAL[22],
    "positive": GREEN[60],
    "cautionary": ORANGE[60],
    "negative": RED[60],
}

# ---------------------------------------------------------------------------
# Accent — 카테고리(멤버) 식별용 시리즈 색
#   Montage semantic.accent.foreground 순서 그대로. 라이트 배경 대비를 고려한
#   전경색 세트라 차트 마크·텍스트에 바로 쓸 수 있다.
#
#   ⚠ 11색 카테고리는 색각 이상 사용자가 완전히 구분하기 어렵다. 이건 Montage의
#     한계가 아니라 "11개 계열을 색으로만 구분"하려는 설계 자체의 한계다.
#     차트에서 색에만 의존하지 말고 직접 라벨을 함께 붙인다.
# ---------------------------------------------------------------------------
ACCENT_LIGHT = [
    BLUE[45], RED_ORANGE[48], GREEN[40], ORANGE[39], PINK[46], LIME[37],
    VIOLET[45], RED[40], CYAN[40], PURPLE[40], LIGHT_BLUE[40],
]
ACCENT_DARK = [
    BLUE[60], RED_ORANGE[60], GREEN[60], ORANGE[50], PINK[60], LIME[50],
    VIOLET[60], RED[60], CYAN[60], PURPLE[60], LIGHT_BLUE[60],
]

# ---------------------------------------------------------------------------
# Spacing / Radius / Typography
# ---------------------------------------------------------------------------
SPACING = [0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 32, 40, 48, 56, 64, 72, 80]
RADIUS = {"sm": "4px", "md": "8px", "lg": "12px", "xl": "16px", "full": "9999px"}

# Montage는 Pretendard를 표준 서체로 쓴다. 설치돼 있지 않을 수 있으므로
# 한글이 깨지지 않는 시스템 서체로 폴백한다.
FONT_STACK = (
    'Pretendard, "Pretendard Variable", -apple-system, BlinkMacSystemFont, '
    '"Malgun Gothic", "Noto Sans KR", system-ui, sans-serif'
)
# matplotlib용 후보 (앞에서부터 실제 설치된 것을 고른다)
FONT_CANDIDATES = ["Pretendard", "Noto Sans CJK KR", "Noto Sans CJK JP",
                   "Noto Sans KR", "NanumGothic", "Malgun Gothic",
                   "AppleGothic", "UnDotum"]

SHADOW = {
    "xsmall": "0px 1px 2px -1px rgba(23,23,23,0.10)",
    "small": "0px 2px 4px -2px rgba(23,23,23,0.06), 0px 4px 6px -1px rgba(23,23,23,0.06)",
    "medium": "0px 4px 6px -2px rgba(23,23,23,0.07), 0px 10px 15px -3px rgba(23,23,23,0.07)",
    "large": "0px 6px 10px -4px rgba(23,23,23,0.08), 0px 16px 24px -6px rgba(23,23,23,0.08)",
}


def css_variables() -> str:
    """라이트/다크 토큰을 CSS 변수 블록으로 emit."""
    def block(tokens: dict) -> str:
        return "\n".join(f"  --{k.replace('_', '-')}: {v};" for k, v in tokens.items())

    accents_l = "\n".join(f"  --accent-{i}: {c};" for i, c in enumerate(ACCENT_LIGHT))
    accents_d = "\n".join(f"  --accent-{i}: {c};" for i, c in enumerate(ACCENT_DARK))
    radius = "\n".join(f"  --radius-{k}: {v};" for k, v in RADIUS.items())
    shadow = "\n".join(f"  --shadow-{k}: {v};" for k, v in SHADOW.items())

    return f""":root {{
{block(LIGHT)}
{accents_l}
{radius}
{shadow}
  --font: {FONT_STACK};
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
{block(DARK)}
{accents_d}
  }}
}}
:root[data-theme="dark"] {{
{block(DARK)}
{accents_d}
}}"""
