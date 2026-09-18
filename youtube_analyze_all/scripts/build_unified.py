# -*- coding: utf-8 -*-
"""프로젝트 리포트를 **소재별로 한 파일씩** 조립한다 (화면용 HTML + 인쇄용 PDF 소스).

결과물/ 은 프로젝트별로 흩어져 있어서 "지금 전체가 어떤 상태인지"를 한 번에 보려면
폴더를 여럿 돌아다녀야 한다. 이 스크립트는 같은 소스에서 한 페이지짜리 종합본을 만든다.

## 왜 두 권인가
버추얼 크리에이터 팬덤(01~09·11·12)과 게임 캐릭터 인기도(10)는 읽는 사람도, 묻는
질문도 다르다. 한 문서에 섞으면 독자가 중간에 맥락을 갈아타야 한다. 소재가 다르면
문서를 나눈다 — 스텔라이브 리포트 한 권, 게임 리포트 한 권.

  python scripts/build_unified.py

만들어지는 것 (결과물/_build/ — 용량이 커서 git 에는 올리지 않는다):
  StelLive-리포트.html / 게임-리포트.html   단독 문서(doctype·viewport 포함)
  *-fragment.html                           본문 fragment (아티팩트 퍼블리시용)
  *-print.html                              PDF 렌더 소스 (details 펼침·lazy 제거)

PDF 는 헤드리스 크로미움으로 뽑는다:

  chromium --headless=new --no-pdf-header-footer \
    --print-to-pdf=StelLive-리포트.pdf file://$PWD/결과물/_build/StelLive-리포트-print.html

내용은 새로 쓰지 않는다 — 결론·본문은 build_deliverables 의 소스(PROJECTS 결론 +
각 프로젝트 REPORT.md 섹션)를 그대로 재사용하고, 추세만 history.csv 에서 직접
계산한다(1일/7일/28일). 차트는 base64 로 인라인해 파일 하나로 자체완결시킨다.

## 같은 그림은 한 번만
프로젝트가 서로의 데이터를 재사용하다 보면 같은 그림이 두 절에 들어간다. 픽셀이
같은 PNG 는 문서 전체에서 한 번만 싣는다(charts_html 의 seen 집합).
"""
import base64
import hashlib
import importlib.util
import io
import re
import sys
from pathlib import Path

import markdown as md_lib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]      # youtube_analyze_all/
REPO = ROOT.parent
BUILD = REPO / "결과물" / "_build"

BUILD.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("bd", ROOT / "scripts" / "build_deliverables.py")
bd = importlib.util.module_from_spec(spec)
sys.modules["bd"] = bd
spec.loader.exec_module(bd)

MD = md_lib.Markdown(extensions=["tables"])

GROUP_LABEL = {True: "날짜별 축적", False: "고정 리포트"}
CADENCE = {
    "01_member_channel_performance": "daily",
    "02_cover_song_ranking": "daily",
    "03_chzzk_stream_pattern": "daily",
    "06_competitor_comparison": "daily",
    "07_market_analysis": "daily·재분석만",
    "04_kirinuki_ecosystem": "weekly",
    "05_comment_sentiment": "weekly",
    "10_hoyoverse": "weekly",
    "11_fan_commerce": "weekly",
    "09_dart_financials": "monthly",
    "08_live_viewership": "10분 폴링",
    "12_event_impact": "daily",
}


def mdhtml(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def trend_table(slug: str) -> str:
    hist = ROOT / slug / "data" / "history.csv"
    metric = bd.TREND_METRIC.get(slug)
    if not hist.exists() or not metric:
        return ""
    col, label = metric
    df = pd.read_csv(hist)
    if col not in df.columns:
        return ""
    df["date"] = pd.to_datetime(df["date"])
    dates = sorted(df["date"].unique())
    if len(dates) < 2:
        return ""
    # 강지는 운영자(창립자)라 탤런트 멤버 비교에서 제외한다 — 구독자 규모가 7배라
    # 섞어 놓으면 평균·순위가 전부 강지 기준으로 왜곡된다.
    df = df[df["name_ko"] != "강지"]
    latest = dates[-1]
    cur = df[df["date"] == latest].groupby("name_ko")[col].first()
    wins = []
    for lab, days in (("1일", 1), ("7일", 7), ("28일", 28)):
        past = [d for d in dates if (latest - d).days >= days]
        if not past:
            continue
        prev = df[df["date"] == past[-1]].groupby("name_ko")[col].first()
        pct = ((cur - prev) / prev * 100).dropna()
        wins.append((f"{lab}<span class='dim'>({(latest-past[-1]).days}d)</span>", pct))
    if not wins:
        return ""
    head = "".join(f"<th>{w}</th>" for w, _ in wins)
    rows = []
    first = wins[0][1]
    for nm in sorted(cur.index, key=lambda x: -first.get(x, -999)):
        vals = [w.get(nm) for _, w in wins]
        # 어느 창에도 값이 없는 행(오늘 처음 들어온 채널 — 06 로스터 교체 직후처럼)은
        # 전부 '—' 인 줄만 늘리므로 싣지 않는다. 내일부터 1일 창에 값이 생기면 나타난다.
        if all(v is None or v != v for v in vals):
            continue
        cells = ""
        for v in vals:
            if v is None or v != v:
                cells += "<td class='zero'>—</td>"
                continue
            cls = "up" if v > 0.005 else ("dn" if v < -0.005 else "zero")
            cells += f"<td class='{cls}'>{v:+.2f}%</td>"
        rows.append(f"<tr><td class='nm'>{nm}</td>{cells}</tr>")
    note = ""
    if col == "subscribers":
        note = ("<p class='note'>유튜브 구독자는 API가 1,000 단위로 반올림해 준다 — "
                "<code>+0.00%</code>는 반올림 경계를 안 넘었다는 뜻이지 정체가 아니다. "
                "짧은 창은 치지직 팔로워(정확한 정수)를 같이 볼 것.</p>")
    return (f"<div class='trend'><h4>추세 · {label} <span class='dim'>축적 {len(dates)}일 · "
            f"기준 {pd.Timestamp(latest):%Y-%m-%d}</span></h4>"
            f"<div class='tblwrap'><table><thead><tr><th>멤버</th>{head}</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div>{note}</div>")


def charts_html(slug: str, seen: set[str] | None = None) -> str:
    """한 절의 차트들. 이미 문서에 실린 것과 픽셀이 같으면 건너뛴다.

    파일명이 달라도 내용이 같으면 독자에게는 같은 그림이다. 파일명 규칙에 기대면
    이름만 바꿔 저장된 같은 그림을 못 잡으므로 내용 해시로 판정한다.
    """
    seen = seen if seen is not None else set()
    figs = []
    for c in sorted((ROOT / slug / "charts").glob("*.png")):
        h = hashlib.sha256(c.read_bytes()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        figs.append(
            f"<figure><img src='{data_uri(c)}' alt='{c.stem}' loading='lazy'></figure>")
    if not figs:
        return ""
    return f"<div class='charts'>{''.join(figs)}</div>"


def section(slug, num, short, acc, conclusion, seen=None) -> str:
    src = ROOT / slug / "REPORT.md"
    date = bd._report_date(src)
    _, sec = bd._split_report(src.read_text(encoding="utf-8")) if src.exists() else ("", {})

    intro = mdhtml(sec.get("_intro", ""))
    glance = mdhtml(sec.get("핵심 요약", ""))
    detail_names = [n for n in sec if n not in {"_intro", "핵심 요약", "산출물"}]
    details = "".join(
        f"<h4>{n}</h4>{mdhtml(sec[n])}" for n in detail_names)

    badges = f"<span class='badge'>{CADENCE.get(slug,'')}</span>"
    if date:
        badges += f"<span class='badge'>기준 {date}</span>"
    if acc:
        badges += "<span class='badge acc'>날짜별 축적</span>"

    trend = trend_table(slug) if acc else ""
    detail_block = (
        f"<details class='more'><summary>상세 분석</summary>{details}</details>"
        if details else "")

    return f"""
<section id="p{num:02d}">
  <header class="sec-head">
    <span class="num">{num:02d}</span>
    <div>
      <h2>{short}</h2>
      <div class="badges">{badges}</div>
    </div>
  </header>
  <div class="verdict"><p class="verdict-label">결론</p>{mdhtml(conclusion)}</div>
  {f"<div class='meta'>{intro}</div>" if intro else ""}
  {f"<div class='glance'>{glance}</div>" if glance else ""}
  {trend}
  {detail_block}
  {charts_html(slug, seen)}
</section>"""



# ---------------------------------------------------------------------------
# 리포트 정의 — 소재가 다르면 문서를 나눈다
#
#   버추얼 크리에이터 팬덤 지표와 게임 캐릭터 인기도는 독자도 질문도 다르다.
#   한 권에 묶으면 중간에 맥락이 끊기고, 목차가 두 배로 길어져 둘 다 안 읽힌다.
#   slugs 에 없는 프로젝트는 그 리포트에 실리지 않는다.
# ---------------------------------------------------------------------------
GAME_SLUGS = ["10_hoyoverse"]

STELLIVE_FINDINGS = [
    ("규모 1위와 밀도 1위는<br>다른 사람이다",
     "구독자 상위 멤버와 참여율·도달효율 상위 멤버가 겹치지 않는다. 참여율↔구독자 상관은 "
     "뚜렷한 음수 — 팬덤이 커질수록 느슨해진다. (01·06·08)"),
    ("플랫폼마다 성장 곡선이<br>다르다",
     "유튜브 구독자 성장 1위와 치지직 팔로워 성장 1위가 다르다. 한 플랫폼 지표만 보면 "
     "성장을 오판한다. (01·03)"),
    ("팬은 쓰지만, 회사에<br>남지 않는다",
     "정기 구독은 만원 미만, 한정 굿즈엔 수십만원 — 그런데 동종업계 감사 재무는 연속 "
     "영업적자다. 지출과 수익성 사이의 구조적 간극. (09·11)"),
]

GAME_FINDINGS = [
    ("미는 캐릭터와 반응하는<br>캐릭터가 다르다",
     "공식 푸시 1위(최신 5성)와 리뷰 언급량 1위가 일치하지 않는다. 출시 순서는 회사가 "
     "정하지만 화제는 그대로 따라오지 않는다."),
    ("언급량은 인기가 아니라<br>화제성이다",
     "매칭 가능한 캐릭터의 3분의 1 이상이 수집된 리뷰에 한 번도 등장하지 않는다. "
     "언급 0을 비인기로 읽으면 안 된다 — 표본이 닿지 않은 것이다."),
    ("못 쓴 지표도<br>기록한다",
     "원래 쓰려던 검색 관심도(Google Trends)는 이 환경에서 확보하지 못했다. 실패를 "
     "숨기지 않고 상태 파일로 남겨 다음 실행이 다시 시도하게 했다."),
]

REPORTS = [
    dict(
        key="StelLive-리포트",
        title="StelLive 팬덤 애널리틱스",
        kicker="StelLive Fandom Analytics",
        headline="팬덤 지표 {n}개 프로젝트,<br>한 페이지 종합 리포트",
        lead="버추얼 크리에이터 그룹 스텔라이브를 소재로, 공개 데이터만으로 팬덤 지표와 "
             "실제 재무를 연결한 분석입니다. 각 프로젝트의 결론 → 지표 → 추세 → 차트를 "
             "이 한 페이지에서 볼 수 있습니다. 멤버 비교는 <strong>탤런트 10명 기준</strong>, "
             "그룹 비교는 <strong>데뷔 시기를 맞춘 코호트 기준</strong>입니다.",
        findings=STELLIVE_FINDINGS,
        include=lambda slug: slug not in GAME_SLUGS,
    ),
    dict(
        key="게임-리포트",
        title="게임 캐릭터 인기도 애널리틱스",
        kicker="Game Character Analytics",
        headline="게임사가 미는 캐릭터,<br>유저가 반응하는 캐릭터",
        lead="원신·붕괴:스타레일의 캐릭터 마스터와 스토어 리뷰만으로 "
             "<strong>공식 푸시</strong>와 <strong>유저 반응</strong>이 어디서 갈리는지 봅니다. "
             "설문도 내부 지표도 쓰지 않았고, 확보하지 못한 지표는 못 썼다고 적었습니다.",
        findings=GAME_FINDINGS,
        include=lambda slug: slug in GAME_SLUGS,
    ),
]


def document(body: str) -> str:
    """다운로드용 단독 문서. viewport 가 없으면 모바일이 980px 데스크톱 폭으로 렌더한다."""
    return ("<!DOCTYPE html>\n<html lang=\"ko\">\n<head>\n"
            "<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def build_report(cfg: dict) -> None:
    projects = [p for p in bd.PROJECTS if cfg["include"](p[0])]
    if not projects:
        print(f"건너뜀: {cfg['key']} — 해당 프로젝트 없음")
        return

    # 같은 그림을 두 번 싣지 않기 위한 문서 단위 기억. 절 사이를 넘어 공유한다.
    seen: set[str] = set()
    sections = "".join(section(*p, seen=seen) for p in projects)
    today = pd.Timestamp.now().strftime("%Y-%m-%d")

    nav = "".join(f"<a href='#p{num:02d}'><b>{num:02d}</b> {short}</a>"
                  for _, num, short, _, _ in projects)
    findings = "".join(
        f"<div class='finding'><h3>{h}</h3><p>{p}</p></div>" for h, p in cfg["findings"])
    headline = cfg["headline"].replace("{n}", str(len(projects)))

    html = f"""<title>{cfg['title']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@800;900&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<style>
:root {{
  --bg:#ffffff; --bg-alt:#F7F7F8; --surface:#ffffff; --ink:#171719; --ink-strong:#000;
  --muted:#70737C; --faint:#989BA2; --line:#E1E2E4; --line-soft:#EAEBEC;
  --primary:#0066FF; --primary-soft:#E8F0FE; --up:#009632; --dn:#E52222;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#141415; --bg-alt:#0F0F10; --surface:#1B1C1E; --ink:#F4F4F5; --ink-strong:#fff;
    --muted:#989BA2; --faint:#70737C; --line:#333438; --line-soft:#2E2F33;
    --primary:#3385FF; --primary-soft:#1c2b45; --up:#1ED45A; --dn:#FF6363;
  }}
}}
:root[data-theme="dark"] {{
  --bg:#141415; --bg-alt:#0F0F10; --surface:#1B1C1E; --ink:#F4F4F5; --ink-strong:#fff;
  --muted:#989BA2; --faint:#70737C; --line:#333438; --line-soft:#2E2F33;
  --primary:#3385FF; --primary-soft:#1c2b45; --up:#1ED45A; --dn:#FF6363;
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; scroll-padding-top:72px; }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior:auto; }} }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans KR",-apple-system,"Apple SD Gothic Neo","Malgun Gothic",
              "NanumSquareRound","Nanum Gothic","Noto Sans CJK KR",sans-serif;
  font-size:15px; line-height:1.75; -webkit-font-smoothing:antialiased;
  word-break:keep-all; overflow-wrap:break-word;
}}
.wrap {{ max-width:880px; margin:0 auto; padding:0 24px 96px; }}

/* ── top nav ─────────────────────────────── */
.topnav {{
  position:sticky; top:0; z-index:10; background:var(--bg);
  border-bottom:1px solid var(--line); overflow-x:auto; white-space:nowrap;
  padding:10px 16px; display:flex; gap:4px; scrollbar-width:none;
}}
.topnav::-webkit-scrollbar {{ display:none; }}
.topnav a {{
  color:var(--muted); text-decoration:none; font-size:12.5px; padding:5px 10px;
  border-radius:6px; letter-spacing:.01em;
}}
.topnav a b {{ color:var(--primary); font-weight:800; margin-right:2px; }}
.topnav a:hover, .topnav a:focus-visible {{ background:var(--bg-alt); color:var(--ink); outline:none; }}

/* ── hero ────────────────────────────────── */
.hero {{ padding:64px 0 40px; border-bottom:1px solid var(--line); }}
.hero .kicker {{
  font-size:12px; font-weight:700; letter-spacing:.14em; color:var(--primary);
  text-transform:uppercase; margin:0 0 14px;
}}
.hero h1 {{
  font-family:"Gothic A1","Noto Sans KR","NanumSquareRound","Nanum Gothic",sans-serif; font-weight:900;
  font-size:clamp(30px,5.4vw,46px); line-height:1.22; margin:0 0 12px;
  color:var(--ink-strong); text-wrap:balance; letter-spacing:-.015em;
}}
.hero .sub {{ color:var(--muted); max-width:62ch; margin:0 0 32px; }}
.findings {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px; }}
.finding {{
  border:1px solid var(--line); border-radius:10px; padding:18px 20px; background:var(--surface);
}}
.finding h3 {{
  font-family:"Gothic A1","NanumSquareRound","Nanum Gothic",sans-serif; font-weight:800; font-size:16px;
  margin:0 0 8px; line-height:1.4; color:var(--ink-strong);
}}
.finding p {{ margin:0; font-size:13.5px; color:var(--muted); line-height:1.7; }}
.hero .stamp {{ margin-top:26px; font-size:12.5px; color:var(--faint); }}
.hero .stamp code {{ font-family:inherit; background:var(--bg-alt); padding:2px 7px; border-radius:5px; }}

/* ── sections ────────────────────────────── */
section {{ padding:56px 0 40px; border-bottom:1px solid var(--line); }}
.sec-head {{ display:flex; gap:16px; align-items:flex-start; margin-bottom:22px; }}
.sec-head .num {{
  font-family:"Gothic A1","NanumSquareRound","Nanum Gothic",sans-serif; font-weight:900; font-size:34px;
  color:var(--primary); line-height:1; padding-top:4px;
  font-variant-numeric:tabular-nums;
}}
.sec-head h2 {{
  font-family:"Gothic A1","Noto Sans KR","NanumSquareRound","Nanum Gothic",sans-serif; font-weight:800;
  font-size:24px; margin:0 0 6px; line-height:1.3; color:var(--ink-strong);
}}
.badges {{ display:flex; flex-wrap:wrap; gap:6px; }}
.badge {{
  font-size:11.5px; color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:2px 10px; background:var(--bg);
}}
.badge.acc {{ color:var(--primary); border-color:var(--primary); }}

.verdict {{
  border-left:3px solid var(--primary); background:var(--primary-soft);
  border-radius:0 10px 10px 0; padding:16px 22px; margin:0 0 24px;
}}
.verdict-label {{
  margin:0 0 4px; font-size:11.5px; font-weight:700; letter-spacing:.12em;
  color:var(--primary);
}}
.verdict p {{ margin:6px 0 0; }}
.verdict p:first-of-type {{ margin-top:0; }}

.meta {{ color:var(--muted); font-size:13.5px; margin-bottom:14px; }}
.meta ul {{ margin:0; padding-left:18px; }}
.meta li {{ margin:2px 0; }}

.glance ul {{ padding-left:20px; margin:0 0 8px; }}
.glance li {{ margin:5px 0; }}

/* tables */
.tblwrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; font-size:13.5px; margin:10px 0 6px; }}
th, td {{
  padding:7px 12px; border-bottom:1px solid var(--line-soft); text-align:left;
  font-variant-numeric:tabular-nums;
}}
th {{ color:var(--muted); font-weight:500; font-size:12.5px; border-bottom:1px solid var(--line); }}
td:not(:first-child), th:not(:first-child) {{ text-align:right; }}
.trend h4 {{ margin:22px 0 4px; font-size:15px; }}
.trend .nm {{ font-weight:500; }}
.trend .up {{ color:var(--up); }}
.trend .dn {{ color:var(--dn); }}
.trend .zero {{ color:var(--faint); }}
.dim {{ color:var(--faint); font-weight:400; font-size:.85em; }}
.note {{ font-size:12.5px; color:var(--faint); margin:8px 0 0; }}
.note code, .glance code, .more code {{
  font-family:ui-monospace,monospace; font-size:.9em;
  background:var(--bg-alt); padding:1px 5px; border-radius:4px;
}}

/* details */
details.more {{ margin:20px 0 4px; border:1px solid var(--line); border-radius:10px; }}
details.more summary {{
  cursor:pointer; padding:11px 18px; font-weight:700; font-size:13.5px;
  color:var(--muted); list-style:none; display:flex; align-items:center; gap:8px;
}}
details.more summary::before {{ content:"▸"; color:var(--primary); transition:transform .15s; }}
details.more[open] summary::before {{ transform:rotate(90deg); }}
details.more summary:focus-visible {{ outline:2px solid var(--primary); border-radius:10px; }}
details.more > *:not(summary) {{ padding:0 20px; }}
details.more h4 {{ margin:14px 0 6px; font-size:14.5px; }}
details.more[open] {{ padding-bottom:16px; background:var(--bg-alt); }}
blockquote {{
  margin:10px 0; padding:2px 16px; border-left:2px solid var(--line);
  color:var(--muted); font-size:13.5px;
}}

/* charts */
.charts {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(min(320px,100%),1fr));
  gap:14px; margin-top:26px;
}}
.charts figure {{
  margin:0; border:1px solid var(--line); border-radius:10px; overflow:hidden;
  background:#fff;
}}
.charts img {{ display:block; width:100%; height:auto; }}

a {{ color:var(--primary); }}
strong {{ color:var(--ink-strong); }}
footer {{ padding-top:40px; font-size:12.5px; color:var(--faint); line-height:1.9; }}
.tblwrap.txt td {{ text-align:left; vertical-align:top; }}
.tblwrap.txt td.nm {{ white-space:nowrap; font-weight:700; }}
@media (max-width:600px) {{
  .wrap {{ padding:0 16px 72px; }}
  .hero {{ padding:40px 0 32px; }}
  .sec-head {{ gap:12px; }}
  .sec-head .num {{ font-size:26px; }}
  .sec-head h2 {{ font-size:20px; }}
  .verdict {{ padding:14px 16px; }}
  details.more > *:not(summary) {{ padding:0 14px; }}
  /* 산문이 들어간 표(고친 것)는 좁은 화면에서 3열을 유지하면 한 칸에 두세 글자씩
     떨어져 읽을 수가 없다. 행 단위 카드로 세운다. */
  .tblwrap.txt thead {{ display:none; }}
  .tblwrap.txt table, .tblwrap.txt tbody, .tblwrap.txt tr, .tblwrap.txt td {{ display:block; }}
  .tblwrap.txt tr {{ border-bottom:1px solid var(--line); padding:12px 0 14px; }}
  .tblwrap.txt tr:last-child {{ border-bottom:none; }}
  .tblwrap.txt td {{ border:none; padding:0; }}
  .tblwrap.txt td.nm {{ white-space:normal; font-size:15px; margin-bottom:4px; color:var(--ink-strong); }}
  .tblwrap.txt td:nth-child(2) {{ color:var(--dn); font-size:13px; margin-bottom:6px; }}
  .tblwrap.txt td:nth-child(2)::before {{ content:"증상 · "; color:var(--faint); }}
}}

/* ── print / PDF ──────────────────────────────
   페이지를 A4 대신 좁게(150×210mm) 잡는다. 휴대폰에서 PDF 를 볼 때 A4 는 한 줄이
   너무 길어 확대·좌우 스크롤을 하게 되는데, 좁은 페이지는 화면 폭에 맞춰도 글자가
   읽히는 크기가 된다. 색은 화면 팔레트를 그대로 인쇄한다(다크모드는 인쇄에 부적합해
   라이트 값으로 고정). 접힌 <details> 는 빌드 시 open 을 붙여 펼친 채 인쇄된다. */
@page {{ size: 150mm 210mm; margin: 12mm 11mm 14mm; }}
@media print {{
  :root {{
    --bg:#fff; --bg-alt:#F7F7F8; --surface:#fff; --ink:#171719; --ink-strong:#000;
    --muted:#5A5D64; --faint:#7C7F86; --line:#D8D9DC; --line-soft:#E8E9EA;
    --primary:#0052CC; --primary-soft:#EDF3FE; --up:#00752A; --dn:#C21A1A;
  }}
  * {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
  body {{ font-size:9.6pt; line-height:1.62; }}
  .topnav {{ display:none; }}
  .wrap {{ max-width:none; padding:0; }}
  .hero {{ padding:0 0 14px; }}
  .hero h1 {{ font-size:22pt; }}
  .hero .sub {{ font-size:9.6pt; max-width:none; }}
  .findings {{ grid-template-columns:1fr 1fr; gap:8px; }}
  .finding {{ padding:10px 12px; break-inside:avoid; }}
  .finding h3 {{ font-size:11pt; }}
  .finding p {{ font-size:8.4pt; }}

  section {{ break-before:page; padding:0; border-bottom:none; }}
  /* 섹션 끝의 여백이 다음 장으로 넘쳐 빈 페이지를 만들지 않게 */
  section > :last-child, .charts > :last-child, details.more > :last-child {{ margin-bottom:0 !important; padding-bottom:0 !important; }}
  #fixes table {{ font-size:8.2pt; }}
  #fixes th, #fixes td {{ padding:3px 6px; }}
  #fixes .note {{ break-before:avoid; margin-top:6px; }}
  .sec-head {{ margin-bottom:12px; break-after:avoid; }}
  .sec-head .num {{ font-size:20pt; }}
  .sec-head h2 {{ font-size:15pt; }}
  h4 {{ break-after:avoid; }}
  .verdict {{ break-inside:avoid; padding:11px 14px; margin-bottom:14px; }}

  table {{ font-size:8.6pt; }}
  th, td {{ padding:4px 7px; }}
  tr, figure, .trend {{ break-inside:avoid; }}
  thead {{ display:table-header-group; }}
  .tblwrap {{ overflow:visible; }}

  /* 화면에선 접혀 있던 상세 분석 — 인쇄본은 넘길 수 없으니 펼쳐 둔다 */
  details.more {{ break-inside:auto; background:none; border-color:var(--line); }}
  details.more summary {{ list-style:none; }}
  details.more summary::before {{ content:"▾"; }}

  .charts {{ grid-template-columns:1fr; gap:10px; margin-top:16px; }}
  .charts figure {{ break-inside:avoid; }}
  /* 두 줄짜리 푸터를 새 장에 홀로 두면 마지막 장이 빈 종이가 된다. 본문 뒤에 붙인다. */
  footer {{ break-before:auto; margin-top:24px; padding-top:10px; }}
}}
</style>

<nav class="topnav">{nav}</nav>
<div class="wrap">

<header class="hero">
  <p class="kicker">{cfg['kicker']}</p>
  <h1>{headline}</h1>
  <p class="sub">{cfg['lead']}</p>
  <div class="findings">{findings}</div>
  <p class="stamp">생성 {today} · 자동 수집 기준 최신 스냅샷</p>
</header>

{sections}

<footer>
  이 문서는 저장소의 최신 수집분으로 자동 생성됐습니다. 수치는 각 절에 적힌 기준일의
  스냅샷이며, 데이터가 부족한 구간은 추정하지 않고 측정 불가로 남겨 뒀습니다.
</footer>
</div>
"""

    out = BUILD / f"{cfg['key']}-fragment.html"
    out.write_text(html, encoding="utf-8")

    standalone = BUILD / f"{cfg['key']}.html"
    standalone.write_text(document(html), encoding="utf-8")

    # PDF 소스 — 화면판과 세 군데가 다르다.
    #   1) <details> 를 열어 둔다: 종이는 클릭이 안 된다.
    #   2) loading=lazy 제거: 인쇄 시점에 아직 안 불러온 이미지가 빈칸으로 나갈 수 있다.
    #   3) 웹폰트 링크 제거: 렌더러가 네트워크를 못 쓰면 폰트 대기로 시간만 쓴다.
    print_body = (html
                  .replace("<details class='more'>", "<details class='more' open>")
                  .replace(" loading='lazy'", ""))
    print_body = re.sub(r'<link rel="(preconnect|stylesheet)"[^>]*>\n?', "", print_body)
    printed = BUILD / f"{cfg['key']}-print.html"
    printed.write_text(document(print_body), encoding="utf-8")

    for f in (out, standalone, printed):
        print(f"생성: {f.name}  ({f.stat().st_size/1e6:.1f} MB)  프로젝트 {len(projects)}개")


for _cfg in REPORTS:
    build_report(_cfg)
