# -*- coding: utf-8 -*-
"""11개 프로젝트 리포트를 **한 파일**로 조립한다 (화면용 HTML + 인쇄용 PDF 소스).

결과물/ 은 프로젝트별로 흩어져 있어서 "지금 전체가 어떤 상태인지"를 한 번에 보려면
11개 폴더를 돌아다녀야 한다. 이 스크립트는 같은 소스에서 한 페이지짜리 종합본을 만든다.

  python scripts/build_unified.py

만들어지는 것 (결과물/_build/ — 용량이 커서 git 에는 올리지 않는다):
  stellive-analytics.html   본문 fragment (아티팩트 퍼블리시용)
  StelLive-리포트.html      단독 문서 (doctype·charset·viewport 포함 — 모바일에서 그냥 열림)
  _print.html               PDF 렌더 소스 (details 펼침·lazy 제거·웹폰트 제거)

PDF 는 헤드리스 크로미움으로 뽑는다:

  chromium --headless=new --no-pdf-header-footer \
    --print-to-pdf=StelLive-리포트.pdf file://$PWD/결과물/_build/_print.html

내용은 새로 쓰지 않는다 — 결론·본문은 build_deliverables 의 소스(PROJECTS 결론 +
각 프로젝트 REPORT.md 섹션)를 그대로 재사용하고, 추세만 history.csv 에서 직접
계산한다(1일/7일/28일). 차트 67장은 base64 로 인라인해 파일 하나로 자체완결시킨다.
"""
import base64
import importlib.util
import io
import re
import sys
from pathlib import Path

import markdown as md_lib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]      # youtube_analyze_all/
REPO = ROOT.parent
OUT = REPO / "결과물" / "_build" / "stellive-analytics.html"

OUT.parent.mkdir(parents=True, exist_ok=True)

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
        cells = ""
        for _, w in wins:
            v = w.get(nm)
            cls = "up" if v and v > 0.005 else ("dn" if v and v < -0.005 else "zero")
            cells += f"<td class='{cls}'>{v:+.2f}%</td>" if v == v else "<td class='zero'>—</td>"
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


def charts_html(slug: str) -> str:
    charts = sorted((ROOT / slug / "charts").glob("*.png"))
    if not charts:
        return ""
    figs = "".join(
        f"<figure><img src='{data_uri(c)}' alt='{c.stem}' loading='lazy'></figure>"
        for c in charts)
    return f"<div class='charts'>{figs}</div>"


def section(slug, num, short, acc, conclusion) -> str:
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
  {charts_html(slug)}
</section>"""


ARCHIVE = ROOT / "_archive" / "2026-08-03_original"

def _pct_table(rows, cols):
    """rows: [(이름, [셀들])] — 셀은 (표시문자열, up/dn/zero 클래스)"""
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = ""
    for nm, cells in rows:
        tds = "".join(f"<td class='{k}'>{t}</td>" for t, k in cells)
        body += f"<tr><td class='nm'>{nm}</td>{tds}</tr>"
    return (f"<div class='tblwrap'><table><thead><tr><th>멤버</th>{head}</tr></thead>"
            f"<tbody>{body}</tbody></table></div>")

def _cls(v):
    return "up" if v > 0.005 else ("dn" if v < -0.005 else "zero")

def _md(iso: str) -> str:
    """2026-08-28 → 8/28. 제목에서 시작일(8/3)과 표기를 맞춘다."""
    if not iso:
        return "현재"
    y, m, d = iso.split("-")
    return f"{int(m)}/{int(d)}"


def monthly_section() -> str:
    """8/3 보존본 → 현재. 탤런트 10명만 (강지 제외)."""
    o1 = pd.read_csv(ARCHIVE/"01_member_channel_performance/data/channel_metrics.csv").set_index("name_ko")
    n1 = pd.read_csv(ROOT/"01_member_channel_performance/data/channel_metrics.csv").set_index("name_ko")
    talents = [m for m in n1.index if n1.loc[m, "role"] == "talent" and m in o1.index]
    date_to = bd._report_date(ROOT/"01_member_channel_performance/REPORT.md") or ""
    o3 = pd.read_csv(ARCHIVE/"03_chzzk_stream_pattern/data/stream_metrics.csv").set_index("name_ko")
    n3 = pd.read_csv(ROOT/"03_chzzk_stream_pattern/data/stream_metrics.csv").set_index("name_ko")
    o2 = pd.read_csv(ARCHIVE/"02_cover_song_ranking/data/cover_metrics.csv").set_index("name_ko")
    n2 = pd.read_csv(ROOT/"02_cover_song_ranking/data/cover_metrics.csv").set_index("name_ko")

    rows = []
    for m in talents:
        sub = (n1.loc[m,"subscribers"]-o1.loc[m,"subscribers"])/o1.loc[m,"subscribers"]*100
        vw  = (n1.loc[m,"recent_avg_views"]-o1.loc[m,"recent_avg_views"])/o1.loc[m,"recent_avg_views"]*100
        fo  = (n3.loc[m,"followers"]-o3.loc[m,"followers"])/o3.loc[m,"followers"]*100 if m in o3.index and m in n3.index else None
        cv  = (n2.loc[m,"total_views"]-o2.loc[m,"total_views"])/o2.loc[m,"total_views"]*100 if m in o2.index and m in n2.index else None
        dc  = int(n2.loc[m,"cover_count"]-o2.loc[m,"cover_count"]) if m in o2.index and m in n2.index else 0
        rows.append((m, sub, vw, fo, cv, dc))
    rows.sort(key=lambda r: -r[1])
    tbl = _pct_table(
        [(m, [(f"{sub:+.2f}%", _cls(sub)), (f"{vw:+.1f}%", _cls(vw)),
              (f"{fo:+.2f}%", _cls(fo)) if fo is not None else ("—","zero"),
              (f"{cv:+.1f}%", _cls(cv)) if cv is not None else ("—","zero"),
              (f"{dc:+d}곡" if dc else "—", "zero")])
         for m, sub, vw, fo, cv, dc in rows],
        ["구독자", "평균조회수", "치지직 팔로워", "커버 총조회수", "커버 추가"])

    o4 = pd.read_csv(ARCHIVE/"04_kirinuki_ecosystem/data/member_ecosystem.csv")
    n4 = pd.read_csv(ROOT/"04_kirinuki_ecosystem/data/member_ecosystem.csv")
    clip = (n4.clip_count.sum()-o4.clip_count.sum())/o4.clip_count.sum()*100
    cvw = (n4.total_clip_views.sum()-o4.total_clip_views.sum())/o4.total_clip_views.sum()*100

    return f"""
<section id="monthly">
  <header class="sec-head"><span class="num">M</span><div>
    <h2>월간 변화 — 8/3 → {_md(date_to)}</h2>
    <div class="badges"><span class="badge">보존 스냅샷 대비 약 3주</span>
    <span class="badge acc">탤런트 10명</span></div></div></header>
  <div class="verdict"><p class="verdict-label">읽는 법</p>
  <p>8월 3일 보존 스냅샷과 최신 수집을 비교한 값이다(정확히는 약 3주 — 아직 한 달치 일일
  축적이 없어 보존본이 기준이다). 규모가 달라 절대값 대신 <strong>성장률(%)</strong>로
  비교한다.</p></div>
  {tbl}
  <p class='note'>키리누키 생태계(04): 팬 클립 {clip:+.1f}% · 클립 표본 조회수 {cvw:+.1f}%
  — 공식 채널 밖 2차창작도 같은 기간 함께 늘었다. 09 재무는 분기 공시라 월간 변화 없음.</p>
</section>"""

def fixes_section() -> str:
    """이번 회차에서 고친 것 — 숫자가 왜 지난번과 다른지 설명이 없으면 신뢰가 안 간다."""
    return """
<section id="fixes">
  <header class="sec-head"><span class="num">✓</span><div>
    <h2>이번에 고친 것 — 숫자가 바뀐 이유</h2>
    <div class="badges"><span class="badge">데이터 정합성</span>
    <span class="badge">기준 변경</span></div></div></header>

  <div class="verdict"><p class="verdict-label">요약</p>
  <p>지난 버전과 숫자가 다른 항목이 있다면 대부분 아래 세 가지 때문이다:
  <strong>참여율 계산 버그</strong>(조회수가 아직 안 붙은 신규 업로드가 4,000%대 참여율을
  만들어냈다), <strong>강지 제외</strong>(창립자를 빼고 탤런트 10명만 비교),
  <strong>차트 한글 깨짐</strong>(러너에 한글 폰트가 없어 라벨이 전부 □ 였다).
  모두 원인을 고친 뒤 과거 축적분까지 되돌려 정정했다.</p></div>

  <div class="tblwrap txt"><table>
  <thead><tr><th>고친 것</th><th>증상</th><th>원인과 조치</th></tr></thead>
  <tbody>
  <tr><td class="nm">참여율 폭주</td>
      <td>마시로 1,028% · 커버곡 평균 4,397%</td>
      <td>업로드 직후 영상은 좋아요·댓글이 먼저 붙고 조회수가 늦게 반영된다(조회수 1, 좋아요 443).
          <code>조회수 1,000 미만은 참여율 계산에서 제외</code>로 바꾸고, 같은 원본을 쓰는
          01·02·06 <b>세 곳 모두</b>에 적용한 뒤 오염된 과거 행을 정정했다. 마시로 커버 참여율 4,397% → 2.5%.</td></tr>
  <tr><td class="nm">강지 제외</td>
      <td>평균·순위가 창립자 기준으로 왜곡</td>
      <td>구독자 규모가 7배라 섞으면 비교가 무의미하다. 리포트·차트에서 전면 제외(수집은 계속 —
          08 동시시청자는 소급이 불가능해 기준이 바뀌어도 복구 가능해야 한다).
          04는 멤버 컬럼 이름이 달라 필터가 조용히 안 먹고 있었다 — 함께 고쳤다.</td></tr>
  <tr><td class="nm">차트 한글 깨짐</td>
      <td>모든 라벨이 □□□</td>
      <td>자동화 러너에 한글 폰트가 없어 matplotlib 이 폴백했다. 폰트 설치 단계를 추가하고
          67장을 다시 그렸다.</td></tr>
  <tr><td class="nm">동시시청자 공백</td>
      <td>수집 간격 중앙값 64분 · 8~10시간 공백 3회</td>
      <td>스케줄러가 10분 cron 을 집행해주지 않았다. 구조를 바꿔 <b>한 번 깨어나면 잡 안에서
          5시간 반 동안 10분마다</b> 찍게 했다. 전환 후 중앙값 <b>10분</b>으로 회복.</td></tr>
  <tr><td class="nm">07이 06과 다른 숫자</td>
      <td>06은 148,356, 07은 155,586</td>
      <td>07은 수집이 없어 자동화에서 아예 빠져 있었다. "수집만 건너뛰고 재분석은 매일"로 바꿨다.</td></tr>
  <tr><td class="nm">부분 실패 시 데이터 유실</td>
      <td>한 프로젝트가 죽으면 성공분도 커밋 안 됨</td>
      <td>커밋 단계를 <code>always()</code>로. 실제로 10이 실패한 날 04·05·11의 68개 파일이 살아남았다.</td></tr>
  </tbody></table></div>
  <p class="note">그 외: 결론 문장이 본문 숫자와 어긋나던 것(하드코딩)을 방향·비율 서술로 바꿔
  데이터가 갱신돼도 어긋나지 않게 했고, 댓글 데이터에서 시청자 핸들 1,305개를 제거했다.</p>
</section>"""


def events_section() -> str:
    return """
<section id="events">
  <header class="sec-head"><span class="num">E</span><div>
    <h2>이벤트 효과 — 커버곡 업로드 · 콘서트</h2>
    <div class="badges"><span class="badge">치지직 팔로워 일일 순증 기준</span></div></div></header>

  <div class="verdict"><p class="verdict-label">결론</p>
  <p>관측 창 안의 커버곡 업로드 2건은 <strong>서로 반대 방향</strong>으로 움직였다 —
  커버 업로드가 팔로워 증가로 이어진다고 말할 근거가 아직 없다. 콘서트(리제, 7/11)는
  일일 수집 시작 <strong>이전</strong>이라 전후 비교가 불가능하다. 억지 결론 대신
  측정 가능해진 것과 불가능한 것을 구분해 둔다.</p></div>

  <h4>커버곡 업로드 전후 — 치지직 팔로워 일일 순증</h4>
  <div class="tblwrap"><table>
  <thead><tr><th>이벤트</th><th>업로드 전</th><th>업로드 후 5일</th><th>변화</th></tr></thead>
  <tbody>
  <tr><td class="nm">하나코 나나 · 8/16 「논브레스 오블리주」</td><td>+246/일</td><td>+66/일</td><td class="dn">−73%</td></tr>
  <tr><td class="nm">유즈하 리코 · 8/22 「숨바꼭질」</td><td>+134/일</td><td>+208/일</td><td class="up">+56%</td></tr>
  </tbody></table></div>
  <p class="note">표본 2건, 방향 상반 — 결론 불가. 커버는 유튜브에 올라가는데 측정은 치지직
  팔로워라 플랫폼도 어긋난다. 유튜브 구독자는 1,000 단위 반올림이라 일 단위 귀속이 안 된다.
  리코의 경우 업로드 다음날(8/23) 유튜브 +1,000 계단이 온 것은 정황상 부합하지만,
  나나는 커버 이후 오히려 감속했다. 이벤트가 더 쌓이면 자동으로 판별력이 생긴다.</p>

  <h4>콘서트 — 아카네 리제 첫 단독 콘서트 (7/11~12)</h4>
  <p>일일 수집이 8/12에 시작돼 <strong>콘서트 전 기준선이 존재하지 않는다.</strong>
  전후 변화율은 계산할 수 없고, 계산한 척하지 않는다. 확인 가능한 사후 정황은:</p>
  <ul>
  <li>콘서트 안내 쇼츠 2건이 각각 <strong>86만·167만 조회</strong> — 리제 채널 최상위권</li>
  <li>8/3→8/12 (콘서트 3~4주 후): 구독자 <strong>+6,000 (+1.75%)</strong>, 평균 조회수
  <strong>+30,872</strong> — 두 지표 모두 그 구간 전 멤버 1위</li>
  <li>8/12→8/26: +2,000 으로 둔화 — 사후 효과가 잦아드는 모양새</li>
  </ul>
  <p class="note">다음 콘서트부터는 일일 축적(history.csv)이 있어 전후 비교가 실제로
  가능하다 — 이번에 측정 불가였던 것이 시스템 개선의 이유다.</p>
</section>"""

sections = (fixes_section() + monthly_section() + events_section()
            + "".join(section(*p) for p in bd.PROJECTS))
today = pd.Timestamp.now().strftime("%Y-%m-%d")

nav = ("<a href='#fixes'><b>✓</b> 고친 것</a>"
       "<a href='#monthly'><b>M</b> 월간 변화</a><a href='#events'><b>E</b> 이벤트</a>"
       + "".join(f"<a href='#p{num:02d}'><b>{num:02d}</b> {short}</a>"
                 for _, num, short, _, _ in bd.PROJECTS))

html = f"""<title>StelLive 팬덤 애널리틱스</title>
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

  section {{ break-before:page; padding:0 0 10px; border-bottom:none; }}
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
  footer {{ break-before:page; padding-top:0; }}
}}
</style>

<nav class="topnav">{nav}</nav>
<div class="wrap">

<header class="hero">
  <p class="kicker">StelLive Fandom Analytics</p>
  <h1>팬덤 지표 11개 프로젝트,<br>한 페이지 종합 리포트</h1>
  <p class="sub">버추얼 크리에이터 그룹 스텔라이브를 소재로, 공개 데이터만으로 팬덤 지표와
  실제 재무를 연결한 분석 포트폴리오입니다. 각 프로젝트의 결론 → 지표 → 추세 → 차트를
  이 한 페이지에서 볼 수 있습니다. 멤버 비교는 <strong>탤런트 10명 기준</strong>입니다.</p>
  <div class="findings">
    <div class="finding"><h3>규모 1위와 밀도 1위는<br>다른 사람이다</h3>
      <p>구독자 상위 멤버와 참여율·도달효율 상위 멤버가 겹치지 않는다. 참여율↔구독자 상관은
      뚜렷한 음수 — 팬덤이 커질수록 느슨해진다. (01·06·08)</p></div>
    <div class="finding"><h3>플랫폼마다 성장 곡선이<br>다르다</h3>
      <p>유튜브 구독자 성장 1위와 치지직 팔로워 성장 1위가 다르다. 한 플랫폼 지표만 보면
      성장을 오판한다. (01·03)</p></div>
    <div class="finding"><h3>팬은 쓰지만, 회사에<br>남지 않는다</h3>
      <p>정기 구독은 만원 미만, 한정 굿즈엔 수십만원 — 그런데 동종업계 감사 재무는 연속
      영업적자다. 지출과 수익성 사이의 구조적 간극. (09·11)</p></div>
  </div>
  <p class="stamp">생성 {today} · 데이터 저장소 <code>Argenviol/Youtube_analyze</code> ·
  자동 수집: 동시시청자 폴링 + daily/weekly/monthly</p>
</header>

{sections}

<footer>
  이 문서는 저장소의 최신 수집분으로 생성됐습니다. 원자료·코드·SQL·인터랙티브 대시보드는
  GitHub 저장소 <b>Argenviol/Youtube_analyze</b> 의 각 프로젝트 폴더(<code>youtube_analyze_all/</code>)와
  <code>결과물/</code>에 있습니다. 날짜별 축적 리포트는 <code>결과물/&lt;프로젝트&gt;/REPORTn - YYYYMMDD.md</code>
  로 매일 쌓입니다.
</footer>
</div>
"""

# 아티팩트용 — 래퍼가 doctype/head/viewport 를 채워주므로 fragment 그대로.
OUT.write_text(html, encoding="utf-8")

# 다운로드용 — 파일 단독으로 열리므로 완전한 문서여야 한다. viewport 가 없으면
# 모바일 브라우저가 980px 데스크톱 폭으로 렌더링해 페이지가 깨져 보인다.
def document(body: str) -> str:
    return ("<!DOCTYPE html>\n<html lang=\"ko\">\n<head>\n"
            "<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "</head>\n<body>\n" + body + "\n</body>\n</html>\n")


STANDALONE = OUT.with_name("StelLive-리포트.html")
STANDALONE.write_text(document(html), encoding="utf-8")

# PDF 소스 — 화면판과 세 군데가 다르다.
#   1) <details> 를 열어 둔다: 종이는 클릭이 안 된다.
#   2) loading=lazy 제거: 인쇄 시점에 아직 안 불러온 이미지가 빈칸으로 나갈 수 있다.
#   3) 웹폰트 링크 제거: 렌더러가 네트워크를 못 쓰면 폰트 대기로 시간만 쓰고 결국
#      로컬 폰트로 떨어진다. 처음부터 로컬 한글 폰트로 확정한다.
PRINT = OUT.with_name("_print.html")
print_body = (html
              .replace("<details class='more'>", "<details class='more' open>")
              .replace(" loading='lazy'", ""))
print_body = re.sub(r'<link rel="(preconnect|stylesheet)"[^>]*>\n?', "", print_body)
PRINT.write_text(document(print_body), encoding="utf-8")

for f in (OUT, STANDALONE, PRINT):
    print(f"생성: {f.name}  ({f.stat().st_size/1e6:.1f} MB)")
