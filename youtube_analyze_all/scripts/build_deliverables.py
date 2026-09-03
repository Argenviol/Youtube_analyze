"""저장소 루트에 `결과물/` 을 생성한다.

각 프로젝트 폴더에는 코드·원천 데이터·SQLite 가 함께 들어 있어서, 결과만 보고 싶은
사람에게는 뒤져야 할 것이 너무 많다. `결과물/` 은 **읽을 것만** 모은다.

## 리포트는 한 파일로 완결된다
원본 `REPORT.md` 는 핵심 요약만 담은 짧은 문서다. 여기서는 그걸 그대로 복사하지 않고
**결론을 맨 위에 놓고, 추세·차트·상세분석·방법론을 아래로 나열한 문서**로 조립한다.
차트를 본문에 박기 때문에 이 파일 하나만 열면 근거까지 다 보인다.

## 파일명
수집할 때마다 숫자가 바뀌는 프로젝트(01·02·03·06·08)는 날짜를 파일명에 넣어 날짜별로
쌓는다. 지난 리포트를 지우지 않으므로 시간이 지나면 그 자체가 기록이 된다.

  REPORT1 - 20260818.md      ← 매일 갱신되는 프로젝트
  REPORT.md                  ← 숫자가 잘 안 바뀌는 프로젝트(04·05·07·09·10·11)

## 차트는 최신본 하나만 둔다
차트까지 날짜별로 쌓으면 67종 × 날짜 수로 저장소가 급격히 커진다. 대신 각 리포트의
차트 절에 차트가 어느 시점 기준인지 명시한다 — 옛 리포트를 열면 본문 숫자와 차트
날짜가 다를 수 있고, 그건 숨기지 말고 드러내야 한다.

  python scripts/build_deliverables.py

`결과물/` 은 생성물이다. 직접 고치지 말 것 — refresh.py 가 분석 후 자동 호출한다.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "결과물"

# slug -> (번호, 짧은 제목, 결론, 날짜별로 쌓을지)
#
# 결론은 "누가 1위" 가 아니라 **이 분석이 무엇을 밝혔는가**를 쓴다. 순위는 아래
# 상세분석에 이미 있고, 맨 위에서 필요한 건 해석이다.
PROJECTS = [
    ("01_member_channel_performance", 1, "멤버별 유튜브 채널 성과", True,
     "규모와 밀도는 반대로 간다. 참여율과 구독자, 도달 효율과 구독자가 모두 "
     "**뚜렷한 음의 상관**이다(둘 다 -0.4 이하). 구독자가 많은 채널일수록 구독자 대비 조회수와 "
     "참여율이 낮다 — 팬덤이 커질수록 느슨해진다는 뜻이다. 반면 업로드 빈도와 평균 조회수는 "
     "**+0.8 안팎**으로 강하게 붙어 있어, 이 규모대에서는 물량이 조회수를 견인한다."),

    ("02_cover_song_ranking", 2, "커버곡 성과 랭킹", True,
     "커버곡은 업로드 수와 성과가 비례하지 않는다. 최다 업로더와 총 조회수 1위가 다른 사람이고, "
     "곡당 평균 조회수 1위는 업로드가 중간인 멤버다. 즉 커버곡에서는 **어떤 곡을 고르느냐가 "
     "몇 곡을 올리느냐보다 크게 작용한다.** 다만 프로젝트 1에서 업로드 빈도가 조회수를 "
     "견인한 것과는 방향이 달라, 콘텐츠 종류에 따라 물량 전략의 효과가 갈린다고 읽어야 한다."),

    ("03_chzzk_stream_pattern", 3, "치지직 방송 패턴", True,
     "방송이 가장 많이 시작되는 시간대는 **새벽 1시(KST)** 다. 심야 편성이 예외가 아니라 "
     "기본값이고, 주간 방송 시간 1위와 방송 빈도 1위가 서로 다른 사람이라 '길게 적게' 와 "
     "'짧게 자주' 라는 두 전략이 공존한다. 게임 대 토크 비중도 멤버마다 갈려, 이 그룹에는 "
     "단일한 방송 공식이 없다."),

    ("04_kirinuki_ecosystem", 4, "키리누키(2차창작) 생태계", False,
     "팬 제작 클립은 공식 채널 성과와 순위가 일치하지 않는다. 클립 총 조회수 1위와 "
     "가장 많은 팬채널이 다루는 멤버가 다르다 — 전자는 소수 대형 클립 채널의 선택에, 후자는 "
     "저변의 넓이에 좌우되기 때문이다. 표본 합계 조회수는 "
     "공식 채널 조회수에 비하면 작지만, **아무도 돈을 받지 않고 만든 것**이라는 점에서 "
     "팬덤 활성도의 직접 지표다."),

    ("05_comment_sentiment", 5, "댓글 여론/감성", False,
     "상위 댓글의 **80% 가 긍정**이다. 다만 이건 '팬덤이 화목하다'가 아니라 **표본의 성격**으로 "
     "읽어야 한다. 유튜브 추천순 상위 댓글은 좋아요를 많이 받은 것들이고, 팬 커뮤니티에서 "
     "좋아요를 모으는 건 대체로 애정 표현이다. 부정 여론이 없다는 근거로는 쓸 수 없다. "
     "토픽 분포에서는 성격·개그가 목소리·노래를 앞서, 팬들이 콘텐츠보다 **사람**에 반응한다."),

    ("06_competitor_comparison", 6, "경쟁사 비교", True,
     "StelLive 는 규모에서 밀리지만 **도달 효율에서 압도한다.** 평균 구독자는 홀로라이브의 "
     "10분의 1 수준인데 도달 효율(평균조회수/구독자)은 **4배 이상** 앞선다. "
     "구독자 수가 곧 영향력이 아니라는 뜻이고, 규모가 작을수록 구독자가 실제 시청으로 "
     "이어지는 비율이 높다는 프로젝트 1의 발견과 같은 방향이다."),

    ("07_market_analysis", 7, "버추얼 크리에이터 시장", False,
     "VTuber 시장 추정치는 리서치사마다 2026년 31.3억~33.1억 달러로 갈리고 2032년 전망은 "
     "49.4억 대 82.4억 달러로 **1.7배 차이**가 난다. 단일 숫자로 인용하면 안 되고 범위로 "
     "이해해야 한다. 확실한 건 수익 구조로, 구독+후원이 **52.7%** 를 차지해 광고가 아니라 "
     "**직접 후원이 이 산업의 본체**다. 지역은 아시아태평양이 65.1% 로 편중돼 있다."),

    ("08_live_viewership", 8, "동시시청자 시계열", True,
     "이 포트폴리오에서 **유일하게 소급 수집이 불가능한** 지표다. 치지직은 동시시청자 히스토리 "
     "API 를 제공하지 않고 VOD 는 누적 조회수만 준다. 직접 찍어 쌓은 것만이 유일한 출처이며, "
     "수집이 멈춘 구간은 영구 공백으로 남는다. 팬덤 밀도(팔로워 1,000명당 동시시청자)에서 "
     "순위가 구독자 순위와 크게 어긋나, 규모가 아니라 **밀도**가 따로 존재하는 지표임을 보여준다."),

    ("09_dart_financials", 9, "DART 재무 분석", False,
     "**핵심 발견은 부재다.** 스텔라이브 운영법인이 DART 기업코드 마스터에 없다 — 비상장·소규모라 "
     "외부감사 대상이 아니거나 국내 법인이 아닐 수 있다. 즉 팬덤 지표로는 활발한 이 회사의 "
     "재무를 **공적 자료로는 검증할 수 없다.** 대신 확보한 동종업계 4곳에서 드러난 건 "
     "적자 구조로, 샌드박스네트워크는 2018년 이후 8년 내리 영업적자이고 패러블엔터테인먼트의 "
     "FY2025 영업이익은 -91억원이다. 팬덤 규모와 회사 수익성은 별개 문제다."),

    ("10_hoyoverse", 10, "호요버스 캐릭터 인기도", False,
     "게임사가 미는 캐릭터와 유저가 반응하는 캐릭터가 **다르다.** 공식 푸시 1위(최신 5성)와 "
     "리뷰 언급량 1위가 일치하지 않는다. 다만 매칭 가능한 캐릭터의 **3분의 1 이상**이 수집된 리뷰에 "
     "한 번도 언급되지 않아, 언급량은 '인기'가 아니라 **'화제성'** 의 근사치로만 읽어야 한다. "
     "Google Trends 는 매 호출 429 로 실패해 설계에서 드롭했고, 그 실패도 데이터로 기록했다."),

    ("11_fan_commerce", 11, "팬 커머스", False,
     "팬은 돈을 쓰지만 회사에 남지 않는다. 팬딩 월 구독 중앙값은 만원 미만인데 크라우드펀딩 "
     "1인당 후원액은 그 **수십 배**다 — 같은 팬이 정기 구독에는 만원 미만을, "
     "한정 굿즈에는 수십만원을 쓴다. 그런데 같은 IP 를 운영하는 패러블엔터테인먼트의 감사받은 "
     "FY2025 영업이익은 **-91억원**이다. 지출과 수익성 사이에 구조적 간극이 있다."),

    ("12_event_impact", 12, "이벤트 임팩트", True,
     "**연속 며칠짜리 기획은 예외 없이 터진다.** 4명 이상이 연속 2일 이상 함께한 대규모 "
     "컨텐츠만 골라내면 **전부**가 참여자의 평소 방송 대비 1.5배 이상 조회수를 냈다"
     "(최고 2.9배, 마인크래프트 서버). 하루짜리 합방을 섞으면 이 비율이 절반으로 떨어진다 — "
     "단발 합방과 며칠짜리 기획은 아예 다른 이벤트다. "
     "그런데 **가장 크게 터지는 건 합방이 아니라 신의상 공개다.** 조회수는 평소의 3.6~5.6배"
     "(합방 1.4~2.7배), 동시시청자 피크는 **7.4~19.3배**(같은 기간 나란히 돌던 10인 "
     "마인크래프트 합방은 1.0~1.7배)로 두 지표 모두 앞선다. 합방은 며칠에 걸쳐 **분량**을, "
     "신의상은 하루에 **순간 최대치**를 만드는 성격이 다른 레버다. "
     "콘서트는 **단독이냐 합동이냐**로 갈린다 — 본인 첫 단독 콘서트 후기 방송은 평소의 5.9배"
     "(안내 쇼츠 171만 회)였지만, 같은 멤버가 참여한 그룹 페스티벌은 1.2배였다. "
     "합동 무대는 관심이 10명에게 나뉜다. "
     "다만 팔로워·구독자 전후 비교는 일일 수집이 시작된 **2026-08-12 이후 이벤트만** 가능하고, "
     "**수익은 어떤 방법으로도 잴 수 없다** — 치지직·유튜브 모두 공개하지 않는다. "
     "지어낸 추정 대신 노출량(조회수·동시시청자)을 대리 지표로 둔다."),
]

ACCUMULATING = {slug for slug, _, _, acc, _ in PROJECTS if acc}

# history.csv 에서 추세를 뽑을 때 프로젝트별 대표 지표
TREND_METRIC = {
    "01_member_channel_performance": ("subscribers", "구독자"),
    "02_cover_song_ranking": ("total_views", "커버 총 조회수"),
    "03_chzzk_stream_pattern": ("followers", "치지직 팔로워"),
    "06_competitor_comparison": ("subscribers", "구독자"),
}


def _report_date(src: Path) -> str | None:
    """원본 REPORT.md 본문에서 기준 날짜(YYYY-MM-DD)를 찾는다."""
    if not src.exists():
        return None
    head = "\n".join(src.read_text(encoding="utf-8").splitlines()[:8])
    m = re.search(r"(\d{4}-\d{2}-\d{2})", head)
    return m.group(1) if m else None


def _split_report(text: str) -> tuple[str, dict[str, str]]:
    """원본 REPORT.md 를 제목과 (## 섹션명 -> 본문) 으로 쪼갠다."""
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else ""
    body = "\n".join(lines[1:])
    parts = re.split(r"^## +", body, flags=re.M)
    intro, sections = parts[0].strip(), {}
    for p in parts[1:]:
        nl = p.find("\n")
        name = p[:nl].strip() if nl > 0 else p.strip()
        sections[name] = (p[nl + 1:] if nl > 0 else "").strip()
    if intro:
        sections["_intro"] = intro
    return title, sections


def _trend_block(slug: str) -> str:
    """history.csv 로 1일/7일/28일 변화율 표를 만든다. 없으면 빈 문자열."""
    hist = ROOT / slug / "data" / "history.csv"
    metric = TREND_METRIC.get(slug)
    if not hist.exists() or not metric:
        return ""
    col, label = metric
    df = pd.read_csv(hist)
    if col not in df.columns or "name_ko" not in df.columns:
        return ""
    df["date"] = pd.to_datetime(df["date"])
    dates = sorted(df["date"].unique())
    if len(dates) < 2:
        return (f"### 추세\n\n지금까지 **{len(dates)}일** 축적됐다. 변화를 계산하려면 "
                f"최소 2일이 필요하다.\n")
    latest = dates[-1]
    cur = df[df["date"] == latest].groupby("name_ko")[col].first()

    windows, cols = [], []
    for lab, days in (("1일", 1), ("7일", 7), ("28일", 28)):
        past = [d for d in dates if (latest - d).days >= days]
        if not past:
            continue
        prev = df[df["date"] == past[-1]].groupby("name_ko")[col].first()
        pct = ((cur - prev) / prev * 100).dropna()
        windows.append((f"{lab}({(latest - past[-1]).days}d)", pct))
        cols.append(lab)

    if not windows:
        return ""
    head = "| 멤버 | " + " | ".join(w for w, _ in windows) + " |"
    sep = "|---|" + "---:|" * len(windows)
    rows = []
    first = windows[0][1]
    for nm in sorted(cur.index, key=lambda x: -first.get(x, -999)):
        cells = " | ".join(f"{w.get(nm, float('nan')):+.2f}%" for _, w in windows)
        rows.append(f"| {nm} | {cells} |")

    note = ""
    if col == "subscribers":
        note = ("\n> 유튜브 구독자는 API 가 1,000 단위로 반올림해 준다. 작은 채널은 하루에 "
                "0 또는 +1,000 으로만 움직여 짧은 창에서는 `+0.00%` 로 찍힌다. 실제로 "
                "안 늘어난 것이 아니라 반올림 경계를 안 넘은 것이다 — 짧은 구간은 "
                "치지직 팔로워(정확한 정수)를 같이 보는 편이 낫다.\n")
    return (f"### 추세 · {label}\n\n축적 {len(dates)}일 (기준 {pd.Timestamp(latest):%Y-%m-%d})\n\n"
            + head + "\n" + sep + "\n" + "\n".join(rows) + "\n" + note)


def _charts_block(slug: str, chart_date: str | None) -> str:
    charts = sorted((ROOT / slug / "charts").glob("*.png"))
    if not charts:
        return ""
    when = f" (최신 실행 {chart_date} 기준)" if chart_date else ""
    # 캡션을 따로 달지 않는다. 차트 PNG 안에 이미 한글 제목이 렌더돼 있어서
    # 파일명을 영문 그대로 노출하면 오히려 지저분해진다.
    out = [f"### 차트 {len(charts)}종{when}\n"]
    for c in charts:
        out.append(f"![{c.stem}](charts/{c.name})\n")
    return "\n".join(out)


def _compose(slug: str, num: int, short: str, conclusion: str,
             accumulating: bool, date: str | None) -> str:
    src = ROOT / slug / "REPORT.md"
    title, sections = _split_report(src.read_text(encoding="utf-8")) if src.exists() else (short, {})

    md = [f"# 프로젝트 {num} · {short}", ""]
    if date:
        md.append(f"**기준 {date}**" + ("  · 날짜별 축적" if accumulating else ""))
        md.append("")

    md += ["## 결론", "", conclusion, "", "---", ""]

    if sections.get("_intro"):
        md += ["## 데이터", "", sections["_intro"], ""]

    for name in ("핵심 요약",):
        if sections.get(name):
            md += [f"## 한눈에", "", sections[name], ""]

    if accumulating:
        t = _trend_block(slug)
        if t:
            md += ["## 시간에 따른 변화", "", t, ""]

    detail = [n for n in sections
              if n not in {"_intro", "핵심 요약", "산출물"}]
    if detail:
        md += ["## 상세 분석", ""]
        for n in detail:
            md += [f"### {n}", "", sections[n], ""]

    ch = _charts_block(slug, date)
    if ch:
        md += ["## 근거 자료", "", ch, ""]

    md += [
        "## 원자료", "",
        f"이 리포트를 만든 코드와 데이터는 저장소의 [`youtube_analyze_all/{slug}/`]"
        f"(../../youtube_analyze_all/{slug}/) 에 있다.", "",
        "| 경로 | 내용 |", "|---|---|",
        "| `collect.py` | 수집 |",
        "| `analyze.py` | 정제·집계·차트 생성 |",
        "| `data/` | 원천·정제 데이터 (CSV/JSON) |",
        "| `sql/` | 스키마·INSERT·분석쿼리·SQLite·쿼리 실행결과 |",
        "| `site/index.html` | 자체완결 인터랙티브 대시보드 |",
    ]
    if accumulating:
        md.append("| `data/history.csv` | 날짜별 지표 축적 (이 리포트의 추세 절 근거) |")
    md.append("")
    return "\n".join(md)


def _copy_project(slug: str, num: int, short: str, conclusion: str, acc: bool) -> dict:
    src, dst = ROOT / slug, OUT / slug
    dst.mkdir(parents=True, exist_ok=True)
    date = _report_date(src / "REPORT.md")

    # 차트는 최신본만 둔다. 날짜별로 쌓으면 저장소가 감당이 안 된다.
    charts = sorted((src / "charts").glob("*.png"))
    if charts:
        cdir = dst / "charts"
        cdir.mkdir(exist_ok=True)
        for png in charts:
            shutil.copy2(png, cdir / png.name)

    index = src / "site" / "index.html"
    if index.exists():
        shutil.copy2(index, dst / "index.html")

    name = f"REPORT{num} - {date.replace('-', '')}.md" if (acc and date) else "REPORT.md"
    # 축적 대상이 된 프로젝트에 예전 무날짜 REPORT.md 가 남아 있으면 지운다.
    # 반대 방향(축적 -> 고정)은 지우지 않는다 — 이미 쌓인 기록을 없애면 안 된다.
    if acc and date and (dst / "REPORT.md").exists():
        (dst / "REPORT.md").unlink()
    (dst / name).write_text(_compose(slug, num, short, conclusion, acc, date),
                            encoding="utf-8")

    kept = sorted(p.name for p in dst.glob("REPORT*.md"))
    return {"charts": len(charts), "site": index.exists(),
            "latest": name, "n_reports": len(kept), "date": date}


def _index_md(rows: list) -> str:
    lines = [
        "# 결과물", "",
        "StelLive 데이터 분석 포트폴리오 **11개 프로젝트의 결과물만** 모았습니다.",
        "각 리포트는 **결론이 맨 위**에 있고 근거·차트·상세분석이 아래로 이어집니다 —",
        "파일 하나만 열면 됩니다.", "",
        "수집할 때마다 숫자가 바뀌는 프로젝트는 `REPORT1 - 20260818.md` 처럼 날짜를 붙여",
        "날짜별로 쌓습니다. 잘 안 바뀌는 프로젝트는 `REPORT.md` 하나입니다.", "",
        "| # | 프로젝트 | 최신 리포트 | 기준일 | 축적 | 차트 | 대시보드 |",
        "|---|---|---|---|---|---|---|",
    ]
    for slug, num, short, acc, got in rows:
        link = f"[{got['latest']}]({slug}/{got['latest'].replace(' ', '%20')})"
        acc_s = f"{got['n_reports']}개" if acc else "—"
        ch = f"[{got['charts']}종]({slug}/charts/)" if got["charts"] else "—"
        site = f"[index.html]({slug}/index.html)" if got["site"] else "—"
        lines.append(f"| {num} | {short} | {link} | {got['date'] or '—'} | {acc_s} | {ch} | {site} |")

    total_ch = sum(r[4]["charts"] for r in rows)
    lines += [
        "",
        f"프로젝트 {len(rows)}개 · 차트 {total_ch}종 · 대시보드 "
        f"{sum(1 for r in rows if r[4]['site'])}건.", "",
        "## 대시보드 여는 법", "",
        "`index.html` 은 CSS·데이터를 안에 품은 자체완결 파일이라 그냥 브라우저로 열면 됩니다",
        "(GitHub 웹에서는 HTML 이 렌더링되지 않으니 내려받아서 열어야 합니다).", "",
        "## 차트 시점", "",
        "차트는 **최신 실행 기준 한 벌만** 둡니다. 날짜별로 쌓으면 67종 × 날짜 수로",
        "저장소가 급격히 커지기 때문입니다. 그래서 지난 날짜의 리포트를 열면 본문 숫자와",
        "차트 시점이 다를 수 있습니다 — 각 리포트의 차트 절에 어느 시점 기준인지 적어뒀습니다.", "",
        "> 이 폴더는 `youtube_analyze_all/scripts/build_deliverables.py` 가 생성합니다.",
        "> 직접 고치면 다음 실행에서 덮어써집니다 — 원본을 고치고 스크립트를 다시 도세요.", "",
    ]
    return "\n".join(lines)


def main() -> int:
    # 통째로 지우지 않는다 — 날짜별로 쌓인 지난 리포트를 보존해야 한다.
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for slug, num, short, acc, conclusion in PROJECTS:
        if not (ROOT / slug).is_dir():
            print(f"  ! {slug} 없음 — 건너뜀")
            continue
        got = _copy_project(slug, num, short, conclusion, acc)
        rows.append((slug, num, short, acc, got))
        print(f"  ✓ {slug:32} {got['latest']:28} 리포트 {got['n_reports']}개")

    (OUT / "README.md").write_text(_index_md(rows), encoding="utf-8")
    print(f"\n결과물 -> {OUT}  (프로젝트 {len(rows)}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
