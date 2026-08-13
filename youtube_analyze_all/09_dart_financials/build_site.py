"""
프로젝트9 · 사이트 빌드
site/data.json → site/index.html (인터랙티브 대시보드).

  python 09_dart_financials/build_site.py

외부 CDN을 쓰지 않고 SVG를 직접 그린다(오프라인에서도 열림).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config, site_css

HERE = Path(__file__).resolve().parent
SITE = HERE / "site"

PAL = config.PALETTE["series"]
C_NAVER, C_SOOP = PAL[0], PAL[1]
C_FOUND, C_MISSING = PAL[2], PAL[7]
_COMPANY_ORDER = ["NAVER", "SOOP", "샌드박스네트워크", "패러블엔터테인먼트"]
_AUDIT_PATH_COMPANIES = {"샌드박스네트워크", "패러블엔터테인먼트"}


def _fmt_eok(v):
    return f"{v/1e8:,.0f}억원" if v is not None else "—"


def _search_row(r: dict, fin_companies: set) -> str:
    if r["matched"]:
        if r["category"] == "동명이인":
            badge = '<span class="pill pill-warn">동명이인 — 분석 제외</span>'
        elif r["corp_name"] in fin_companies and r["corp_name"] in ("SOOP", "NAVER"):
            badge = '<span class="pill pill-ok">재무제표 확보(정기보고서 XBRL)</span>'
        elif r["corp_name"] in fin_companies:
            badge = '<span class="pill pill-ok">재무제표 확보(감사보고서 원문 파싱)</span>'
        elif r["corp_name"] == "팬딩":
            badge = '<span class="pill pill-warn">기업코드만 확인(공시 없음)</span>'
        else:
            badge = '<span class="pill pill-warn">기업코드만 확인</span>'
        code = f'{r["corp_name"]} · {r["corp_code"]}'
    else:
        badge = '<span class="pill pill-no">DART 미등재</span>'
        code = "—"
    return (f'<tr><td>{r["label"]}</td><td>{r["category"]}</td><td>{badge}</td>'
            f'<td>{code}</td><td style="text-align:left;color:var(--label-alt);font-size:12.5px">'
            f'{r["note"]}</td></tr>')


def _metrics_table(companies: list[dict]) -> str:
    rows = sorted(companies, key=lambda c: (c["corp_name"], c["bsns_year"]))
    out = []
    for r in rows:
        out.append(
            "<tr><td>{corp}</td><td>{year}</td><td>{fs}</td><td>{rev}</td>"
            "<td>{op}</td><td>{opm}</td><td>{at}</td></tr>".format(
                corp=r["corp_name"], year=r["bsns_year"], fs=r["fs_div"],
                rev=_fmt_eok(r["revenue"]), op=_fmt_eok(r["operating_income"]),
                opm=f'{r["operating_margin"]*100:.1f}%' if r.get("operating_margin") is not None else "—",
                at=f'{r["asset_turnover"]:.2f}배' if r.get("asset_turnover") is not None else "—",
            )
        )
    return "\n".join(out)


def _revenue_svg(companies: list[dict], width=820, height=320, pad=48):
    """연도별 매출 성장 지수(첫 연도=100) SVG. companies는 이미 analyze.py의 pick_primary()가
    회사×연도별로 연결(CFS) 우선·별도(OFS) 보완을 끝낸 결과라 fs_div로 다시 거를 필요는 없다
    (거르면 항상 OFS인 패러블엔터테인먼트가 통째로 빠진다)."""
    by_corp = {}
    for r in companies:
        if r["revenue"] is None:
            continue
        by_corp.setdefault(r["corp_name"], []).append((r["bsns_year"], r["revenue"]))
    for k in by_corp:
        by_corp[k].sort()

    if not by_corp:
        return '<p class="empty">재무제표를 확보한 회사가 없습니다.</p>'

    years = sorted({y for pts in by_corp.values() for y, _ in pts})
    idx_series = {}
    for corp, pts in by_corp.items():
        base = pts[0][1]
        idx_series[corp] = [(y, v / base * 100) for y, v in pts]

    vmax = max(v for s in idx_series.values() for _, v in s)
    vmin = min(100, min(v for s in idx_series.values() for _, v in s))
    yspan = max(1.0, vmax - vmin)
    xi = {y: i for i, y in enumerate(years)}
    span = max(1, len(years) - 1)

    def x(y):
        return pad + xi[y] / span * (width - pad * 2)

    def y(v):
        return height - pad - (v - vmin) / yspan * (height - pad * 2)

    cmap = {corp: PAL[i % len(PAL)] for i, corp in enumerate(_COMPANY_ORDER)}
    paths, legend, dots = [], [], []
    for corp, pts in idx_series.items():
        c = cmap.get(corp, "#888")
        d = " ".join(("M" if i == 0 else "L") + f"{x(yy):.1f},{y(vv):.1f}" for i, (yy, vv) in enumerate(pts))
        paths.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.5"/>')
        legend.append(f'<span class="lg"><i style="background:{c}"></i>{corp}</span>')
        for yy, vv in pts:
            dots.append(f'<circle cx="{x(yy):.1f}" cy="{y(vv):.1f}" r="3.5" fill="{c}"><title>'
                        f'{corp} {yy} {vv:.0f}</title></circle>')

    grid = "".join(
        f'<line x1="{pad}" y1="{y(vmin+yspan*f):.1f}" x2="{width-pad}" y2="{y(vmin+yspan*f):.1f}" '
        f'stroke="var(--grid)" stroke-width="1"/>'
        f'<text x="{pad-8}" y="{y(vmin+yspan*f)+4:.1f}" text-anchor="end" class="ax">'
        f'{vmin+yspan*f:.0f}</text>'
        for f in (0, .25, .5, .75, 1)
    )
    xlabels = "".join(
        f'<text x="{x(yy):.1f}" y="{height-pad+18}" text-anchor="middle" class="ax">{yy}</text>'
        for yy in years
    )
    return (f'<svg viewBox="0 0 {width} {height}" class="chart">{grid}{xlabels}'
            + "".join(paths) + "".join(dots) + "</svg>"
            + f'<div class="legend">{"".join(legend)}</div>')


def build():
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    meta = data["meta"]
    search = data["target_search"]
    companies = data["companies"]
    fandom = data.get("fandom_context", {})

    n_total = len(search)
    n_matched = sum(1 for r in search if r["matched"])
    fin_companies = {r["corp_name"] for r in companies}
    n_fin = len(fin_companies)

    latest_year = max(r["bsns_year"] for r in companies) if companies else None
    latest = [r for r in companies if r["bsns_year"] == latest_year and r["fs_div"] == "CFS"]
    naver_latest = next((r for r in latest if r["corp_name"] == "NAVER"), None)
    soop_latest = next((r for r in latest if r["corp_name"] == "SOOP"), None)

    kpi_scale = ""
    if naver_latest and soop_latest and soop_latest["revenue"]:
        kpi_scale = f'{naver_latest["revenue"]/soop_latest["revenue"]:.0f}배'

    p1 = fandom.get("project01")
    p8 = fandom.get("project08")

    html = f"""<!doctype html>
<html lang="ko"><head>
{site_css.head("DART 재무 분석 · 프로젝트 9")}
</head><body><div class="wrap">

<div class="eyebrow">PROJECT 09</div>
<h1>DART 재무 분석 — 팬덤과 재무 사이의 간극</h1>
<div class="sub">Open DART(전자공시시스템) Open API · 조사 대상 {n_total}곳 중 기업코드 확인 {n_matched}곳,
구조화된 재무제표 확보 {n_fin}곳 · 수집 {meta['fetched_at'][:10]}</div>

<div class="cards">
  <div class="card"><div class="k">조사 대상</div><div class="v">{n_total}곳</div></div>
  <div class="card"><div class="k">DART 기업코드 확인</div><div class="v">{n_matched}곳</div></div>
  <div class="card"><div class="k">재무제표 확보</div><div class="v">{n_fin}곳</div></div>
  <div class="card"><div class="k">NAVER/SOOP 매출 규모차</div><div class="v">{kpi_scale or "—"}</div></div>
</div>

<div class="warn">
<strong>이 프로젝트가 유일하게 다루는 것: 감사받은 법정 재무제표.</strong> 정기보고서 XBRL
(<code>fnlttSinglAcntAll</code>) 경로로는 <strong>NAVER·SOOP 2곳</strong>만 나왔지만, 비상장
법인이 내는 <strong>감사보고서 원문(document.xml)을 직접 파싱하는 경로</strong>를 추가해
<strong>샌드박스네트워크·패러블엔터테인먼트</strong>까지 확보했다. 스텔라이브 본체·Brave
group·팬딩은 여전히 확보하지 못했다 — 스텔라이브/Brave group은 DART 기업코드 자체가 없고,
팬딩은 기업코드는 있지만 공시 이력이 단 한 건도 없다. "없다"는 것도 이 프로젝트의 결과다.
</div>

<h2>대상 법인 검색 결과</h2>
<p class="sub">기업코드는 매 실행마다 DART 기업코드 마스터(11만+ 법인)에서 이름 완전 일치로 검색해 확인한다. 추측 없음.</p>
<div class="table-box"><table><thead><tr>
<th>대상</th><th>구분</th><th>상태</th><th>기업코드</th><th>비고</th>
</tr></thead><tbody>
{"".join(_search_row(r, fin_companies) for r in search)}
</tbody></table></div>

<h2>매출 성장 지수 (첫 확보 연도=100)</h2>
<p class="sub">NAVER·SOOP는 매출 규모가 {kpi_scale or "N배"} 차이나 절대값 대신 지수로 겹쳐 비교한다. 연결재무제표(CFS) 기준.</p>
<div class="chart-box">{_revenue_svg(companies)}</div>

<h2>회사×연도 핵심 지표</h2>
<p class="sub">연도별 매출(영업수익)·영업이익·영업이익률·자산회전율(매출/자산총계). 연결(CFS)·별도(OFS) 모두 표기.</p>
<div class="table-box"><table><thead><tr>
<th>법인</th><th>연도</th><th>구분</th><th>매출</th><th>영업이익</th><th>영업이익률</th><th>자산회전율</th>
</tr></thead><tbody>
{_metrics_table(companies)}
</tbody></table></div>

<h2>팬덤 지표와 나란히 (참고용 — 상관관계 아님)</h2>
<div class="cards">
  <div class="card"><div class="k">프로젝트1 · 구독자 합산 (2026-08 스냅샷)</div>
    <div class="v">{f"{p1['total_subscribers']:,}명" if p1 else "—"}</div></div>
  <div class="card"><div class="k">프로젝트8 · 관측 구간 팔로워 증감 (2026-08 스냅샷)</div>
    <div class="v">{f"{p8['total_follower_delta']:+,}명" if p8 else "—"}</div></div>
</div>
<div class="note">{fandom.get("note", "")}</div>

<div class="note">
<strong>데이터 함정 — 013(데이터 없음)은 "재무제표가 없다"는 뜻이 아니었다.</strong>
<code>fnlttSinglAcntAll.json</code>은 XBRL이 태깅된 <strong>정기보고서</strong>(사업·반기·분기보고서)만
파싱한다. 비상장 소규모 법인은 「외부감사법」에 따라 <strong>감사보고서</strong>만 제출하면 되고,
이 감사보고서 재무제표는 이 API로 조회되지 않는다 — 그래서 013이 나온다. 하지만 감사보고서
자체는 <code>list.json(pblntf_ty=F)</code>로 찾을 수 있고, 그 원문(<code>document.xml</code>, ZIP
안의 DART 자체 DTD XML)을 직접 파싱하면 재무상태표·손익계산서 표를 계정코드(별도재무제표) 또는
계정과목 텍스트(연결재무제표)로 읽어낼 수 있었다. 그렇게 샌드박스네트워크·패러블엔터테인먼트를
추가로 확보했다. 팬딩은 이 경로로도 확인해봤지만 <code>list.json</code>에 어떤 필터로도 단 한 건도
잡히지 않는다 — 감사보고서 자체를 낸 적이 없는 유일한 매칭 법인이다(<code>data/filings.csv</code> 확인).
<br><br>
<strong>인건비 비중을 계획했지만 산출하지 못했다.</strong> 두 경로 모두 재무제표 본표에는 인건비가
별도 계정으로 없다(기능별 표시 손익계산서라 '영업비용' 한 줄로 뭉쳐 있음). 인건비는 감사보고서
주석에만 있는데, 주석 표는 단위가 '천원'으로 바뀌는 경우가 많고 구조도 회사·연도마다 달라 이번
파싱 범위에서 제외했다 — 추정치를 만드는 대신 '산출 불가'로 남겼다.
<br><br>
<strong>왜 상관관계를 계산하지 않았는가.</strong> 스텔라이브 자체 재무제표가 없고(패러블엔터테인먼트는
이세계아이돌 소속사이지만 스텔라이브와는 다른 법인), NAVER·SOOP는 플랫폼 전체 실적이라 개별
크리에이터 그룹 기여분을 분리할 수 없으며, 재무제표(회계연도)와 팬덤 지표(2026-08 스냅샷)의
기간도 어긋난다. 숫자 몇 개로 인과관계를 만들지 않았다.
</div>

</div></body></html>"""

    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"사이트 -> {SITE / 'index.html'}")


if __name__ == "__main__":
    build()
