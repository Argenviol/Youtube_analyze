"""
기존 프로젝트(1~7)의 build_site.py CSS 토큰을 Montage 값으로 치환한다.

  python scripts/apply_montage_tokens.py --dry-run
  python scripts/apply_montage_tokens.py

왜 값만 바꾸는가:
  1~7번 사이트는 정렬·필터·툴팁·테마토글 JS와 고유 클래스명(.kpi, .chart-svg,
  .gridline ...)을 쓴다. 스타일시트를 통째로 갈아끼우면 마크업과 JS가 깨진다.
  그래서 구조는 그대로 두고 **CSS 변수 값만** Montage 토큰으로 바꾼다.
  결과적으로 8개 사이트가 같은 색 체계를 공유하되, 각자의 인터랙션은 유지된다.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 기존값 -> Montage값. 선언 단위로 바꿔서 줄 구성이 달라도(03의 --heat 등) 안전하다.
REPLACEMENTS = {
    # ---- 감성 시맨틱 (05번) — Montage status 토큰 ----
    # 라이트/다크 모두 --neu 가 같은 리터럴이라 선언 그룹 단위로 바꿔야 구분된다.
    "--pos:#1baf7a; --neu:#898781; --neg:#e34948":
        "--pos:#00BF40; --neu:#70737C; --neg:#FF4242",   # green50 / coolNeutral50 / red50
    "--pos:#199e70; --neu:#898781; --neg:#e66767":
        "--pos:#1ED45A; --neu:#989BA2; --neg:#FF6363",   # green60 / coolNeutral70 / red60

    # ---- 라이트 ----
    "--bg:#f9f9f7": "--bg:#F7F7F8",             # coolNeutral 99
    "--surface:#fcfcfb": "--surface:#ffffff",   # common 100
    "--text:#0b0b0b": "--text:#171719",         # coolNeutral 10 (label.normal)
    "--text2:#52514e": "--text2:#37383C",       # coolNeutral 25
    "--muted:#898781": "--muted:#70737C",       # coolNeutral 50
    "--grid:#e1e0d9": "--grid:#E1E2E4",         # coolNeutral 96 (line.solid)
    "--border:rgba(11,11,11,.10)": "--border:rgba(112,115,124,.22)",  # line.normal
    "--heat:74,58,167": "--heat:91,55,237",     # violet 45
    # 시리즈 8색 — Montage accent.foreground (light)
    "--s1:#2a78d6": "--s1:#005EEB",   # blue 45
    "--s2:#eb6834": "--s2:#F55A00",   # redOrange 48
    "--s3:#1baf7a": "--s3:#009632",   # green 40
    "--s4:#eda100": "--s4:#D17600",   # orange 39
    "--s5:#e87ba4": "--s5:#E846CD",   # pink 46
    "--s6:#008300": "--s6:#429E00",   # lime 37
    "--s7:#4a3aa7": "--s7:#5B37ED",   # violet 45
    "--s8:#e34948": "--s8:#E52222",   # red 40

    # ---- 다크 ----
    "--bg:#0d0d0d": "--bg:#0F0F10",             # coolNeutral 5
    "--surface:#1a1a19": "--surface:#212225",   # coolNeutral 17 (elevated)
    "--text:#fff": "--text:#F7F7F8",            # coolNeutral 99
    "--text2:#c3c2b7": "--text2:#C2C4C8",       # coolNeutral 90
    "--grid:#2c2c2a": "--grid:#37383C",         # coolNeutral 25
    "--border:rgba(255,255,255,.10)": "--border:rgba(112,115,124,.32)",
    "--heat:144,133,233": "--heat:125,94,247",  # violet 60
    # 시리즈 8색 — Montage accent (dark)
    "--s1:#3987e5": "--s1:#3385FF",   # blue 60
    "--s2:#d95926": "--s2:#FF7B2E",   # redOrange 60
    "--s3:#199e70": "--s3:#1ED45A",   # green 60
    "--s4:#c98500": "--s4:#FF9200",   # orange 50
    "--s5:#d55181": "--s5:#FA73E3",   # pink 60
    "--s7:#9085e9": "--s7:#7D5EF7",   # violet 60
    "--s8:#e66767": "--s8:#FF6363",   # red 60
}

# --muted 와 --s6 는 라이트/다크가 같은 값이라 위에서 한 번만 정의된다.
# 다크 블록의 --s6:#008300 도 같은 규칙으로 함께 치환된다.

FONT_OLD = 'font-family:system-ui,-apple-system,"Segoe UI","Noto Sans KR",sans-serif'
FONT_NEW = (
    'font-family:Pretendard,"Pretendard Variable",-apple-system,BlinkMacSystemFont,'
    '"Malgun Gothic","Noto Sans KR",system-ui,sans-serif'
)


def targets() -> list[Path]:
    return sorted(ROOT.glob("0[1-7]_*/build_site.py"))


def main(dry_run: bool) -> None:
    total = 0
    for path in targets():
        text = original = path.read_text(encoding="utf-8")
        hits = {}

        for old, new in REPLACEMENTS.items():
            n = text.count(old)
            if n:
                text = text.replace(old, new)
                hits[old] = n

        n_font = text.count(FONT_OLD)
        if n_font:
            text = text.replace(FONT_OLD, FONT_NEW)
            hits["font-family"] = n_font

        changed = sum(hits.values())
        total += changed
        status = "변경없음" if not changed else f"{changed}곳 치환"
        print(f"{path.parent.name:<32} {status}")

        # 놓친 구형 토큰이 남아 있으면 알려준다.
        leftovers = sorted(set(re.findall(r"#(?:f9f9f7|fcfcfb|0b0b0b|52514e|898781|"
                                          r"e1e0d9|2c2c2a|1a1a19|0d0d0d|c3c2b7)", text)))
        if leftovers:
            print(f"  ⚠ 남은 구형 색상: {', '.join(leftovers)}")

        if text != original and not dry_run:
            path.write_text(text, encoding="utf-8")

    print(f"\n{'(dry-run) ' if dry_run else ''}총 {total}곳")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    main(ap.parse_args().dry_run)
