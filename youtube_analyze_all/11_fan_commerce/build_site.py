"""
프로젝트11 · 사이트 빌드
site/data.json → site/index.html (인터랙티브 대시보드).

  python 11_fan_commerce/build_site.py

외부 CDN을 쓰지 않고 SVG를 직접 그린다(오프라인에서도 열림).
이 프로젝트는 회사/플랫폼 단위 분석이라(07·09·10과 동일한 이유) `members` 배열이 없다.
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
C_OFFICIAL, C_FANMADE = PAL[2], PAL[4]
C_PARABLE, C_SANDBOX = PAL[3], PAL[6]


def _fmt_won(v) -> str:
    return f"{v:,.0f}원" if v is not None else "—"


def _fmt_eok(v) -> str:
    return f"{v/1e8:,.1f}억원" if v is not None else "—"


def _price_bar_rows(rows: list[dict], highlight_url: str) -> str:
    if not rows:
        return '<p class="empty">가격 데이터가 없습니다.</p>'
    top = max(r["avg_price"] for r in rows) or 1
    out = []
    for r in rows:
        pct = r["avg_price"] / top * 100
        hl = r["creator_url"] == highlight_url
        color = PAL[1] if hl else PAL[0]
        label = r["nickname"] + (" ⭐" if hl else "")
        out.append(
            f'<div class="row"><span class="nm">{label}</span>'
            f'<span class="track"><span class="fill" style="width:{pct:.1f}%;'
            f'background:{color}"></span></span>'
            f'<span class="val">{r["avg_price"]:,.0f}원</span></div>'
        )
    return "\n".join(out)


def _crowdfunding_row(r: dict) -> str:
    badge_cls = "pill-ok" if r["category"] == "공식 굿즈 펀딩" else "pill-warn"
    return (
        f'<tr><td>{r["project_name"]}</td>'
        f'<td><span class="pill {badge_cls}">{r["category"]}</span></td>'
        f'<td>{r["raised_krw"]:,}원</td><td>{r["backers"]:,}명</td>'
        f'<td>{r["achievement_pct"]:,.0f}%</td><td>{r["per_backer_krw"]:,}원</td></tr>'
    )


def _financials_row(r: dict) -> str:
    op = r.get("operating_income")
    op_cls = "pill-no" if (op is not None and op < 0) else "pill-ok"
    op_label = f'{op/1e8:+,.1f}억원' if op is not None else "—"
    return (
        f'<tr><td>{r["corp_name"]}</td><td>{r["bsns_year"]:.0f}</td><td>{r["fs_div"]}</td>'
        f'<td>{_fmt_eok(r.get("revenue"))}</td>'
        f'<td><span class="pill {op_cls}">{op_label}</span></td>'
        f'<td>{(r["operating_margin"]*100):.1f}%</td></tr>'
    )


def _trend_svg(financials: list[dict], corp: str, color: str, width=780, height=280, pad=46):
    """회사 1곳의 연도별 매출(막대 대신 선) + 영업이익(선) — 두 스케일이 겹치므로
    각각 첫 연도를 0으로 맞춘 증감(억원) 그래프로 겹쳐 그린다."""
    rows = sorted([r for r in financials if r["corp_name"] == corp], key=lambda r: r["bsns_year"])
    if not rows:
        return '<p class="empty">재무 데이터가 없습니다.</p>'
    years = [int(r["bsns_year"]) for r in rows]
    rev = [r["revenue"] / 1e8 for r in rows]
    op = [r["operating_income"] / 1e8 for r in rows]
    vmax = max(rev + op); vmin = min(rev + op + [0])
    yspan = max(1.0, vmax - vmin)
    xi = {y: i for i, y in enumerate(years)}
    span = max(1, len(years) - 1)

    def x(y):
        return pad + xi[y] / span * (width - pad * 2)

    def y(v):
        return height - pad - (v - vmin) / yspan * (height - pad * 2)

    def path(vals, c, dash=""):
        d = " ".join(("M" if i == 0 else "L") + f"{x(yy):.1f},{y(v):.1f}" for i, (yy, v) in enumerate(zip(years, vals)))
        style = f'stroke-dasharray="{dash}"' if dash else ""
        dots = "".join(f'<circle cx="{x(yy):.1f}" cy="{y(v):.1f}" r="3.2" fill="{c}"><title>{yy}: {v:,.1f}억원</title></circle>'
                        for yy, v in zip(years, vals))
        return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.2" {style}/>' + dots

    grid = "".join(
        f'<line x1="{pad}" y1="{y(vmin+yspan*f):.1f}" x2="{width-pad}" y2="{y(vmin+yspan*f):.1f}" '
        f'stroke="var(--grid)" stroke-width="1"/>'
        f'<text x="{pad-8}" y="{y(vmin+yspan*f)+4:.1f}" text-anchor="end" class="ax">{vmin+yspan*f:,.0f}</text>'
        for f in (0, .25, .5, .75, 1)
    )
    zero_line = (f'<line x1="{pad}" y1="{y(0):.1f}" x2="{width-pad}" y2="{y(0):.1f}" '
                 f'stroke="var(--negative)" stroke-width="1" stroke-dasharray="3,3"/>')
    xlabels = "".join(
        f'<text x="{x(yy):.1f}" y="{height-pad+18}" text-anchor="middle" class="ax">{yy}</text>' for yy in years
    )
    legend = (f'<div class="legend"><span class="lg"><i style="background:{color}"></i>매출(억원)</span>'
              f'<span class="lg"><i style="background:{config.INK["text"]}"></i>영업이익(억원, 점선)</span></div>')
    return (f'<svg viewBox="0 0 {width} {height}" class="chart">{grid}{zero_line}{xlabels}'
            + path(rev, color) + path(op, config.INK["text"], dash="5,3") + "</svg>" + legend)


def build():
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    meta = data["meta"]
    fanding = data["fanding"]
    cf = data["crowdfunding"]
    fin = data["financials"]

    stats = fanding["stats"]
    top_creators = sorted(fanding["creator_summary"], key=lambda r: -r["avg_price"])[:12]
    official = [r for r in cf if r["category"] == "공식 굿즈 펀딩"]
    fanmade = [r for r in cf if r["category"] == "팬메이드 광고 펀딩"]

    parable_latest = max([r for r in fin if r["corp_name"] == "패러블엔터테인먼트"],
                          key=lambda r: r["bsns_year"], default=None)
    sandbox_years = [r for r in fin if r["corp_name"] == "샌드박스네트워크"]
    sandbox_loss_years = sum(1 for r in sandbox_years if (r.get("operating_income") or 0) < 0)

    html = f"""<!doctype html>
<html lang="ko"><head>
{site_css.head("팬 커머스 분석 · 프로젝트 11")}
</head><body><div class="wrap">

<div class="eyebrow">PROJECT 11</div>
<h1>팬 커머스 분석 — 팬덤은 얼마를 쓰고, 그 돈은 회사에 남는가?</h1>
<div class="sub">팬딩(Fanding) 가격 구조 · 텀블벅(Tumblbug) 실제 지출(정적 큐레이션) ·
09_dart_financials 감사보고서 재사용 · 수집 {meta['fetched_at'][:10]}</div>

<div class="cards">
  <div class="card"><div class="k">팬딩 VTuber 크리에이터</div><div class="v">{meta['n_fanding_creators']}명</div></div>
  <div class="card"><div class="k">멤버십 티어 확보</div><div class="v">{meta['n_fanding_tiers']}건</div></div>
  <div class="card"><div class="k">크라우드펀딩 프로젝트</div><div class="v">{meta['n_crowdfunding_projects']}건</div></div>
  <div class="card"><div class="k">재무 확보 회사</div><div class="v">2곳</div></div>
</div>

<div class="warn">
<strong>텀블벅 실제 지출 레이어는 자동 수집이 불가능하다.</strong> 텀블벅
<code>robots.txt</code>가 <code>Disallow: /api/</code>를 명시하는데, 모금액·후원자 수·달성률
등 모든 수치는 그 경로에서만 온다(상세 페이지 HTML 자체는 빈 껍데기). 그래서 이 레이어는
언론 보도·텀블벅 자체 발표·프로젝트 페이지 1회성 열람으로 확보한 <strong>정적 큐레이션</strong>이다 —
재실행해도 갱신되지 않는다. 아래 표의 <code>source_type</code> 열에 각 수치의 출처를 남긴다.
</div>

<h2>레이어 1 · 팬딩 VTuber 멤버십 가격 (자동 수집)</h2>
<p class="sub">팬딩 VTuber 카테고리 크리에이터 {meta['n_fanding_creators']}명의 공개 멤버십 페이지를
전수 조사. 가격을 매긴 크리에이터 {stats['n_creators_with_tiers']}명, 티어 {stats['n_tiers']}건.
범위 {stats['min_price']:,}~{stats['max_price']:,}원(중앙값 {stats['median_price']:,}원). ⭐ = 스텔라이브
(하위 {stats.get('stellive_percentile', 0):.0f}%ile — 더 저렴한 티어가 그만큼 있다는 뜻).</p>
<div class="chart-box">
{_price_bar_rows(top_creators, "stellive")}
</div>
<div class="note">가격 ≠ 매출. 팬딩은 구독자 수를 공개하지 않아 이 표만으로 실제 수입을 추정할 수 없다 —
여기서는 "팬이 얼마를 요구받는가"만 다룬다.</div>

<h2>레이어 2 · 텀블벅 크라우드펀딩 — 실제 지출</h2>
<p class="sub">공식 굿즈 펀딩(이세계아이돌·패러블엔터테인먼트 소속)과 팬메이드 광고 펀딩(스텔라이브
멤버 개인, 비공식·팬 운영)을 구분했다. 표본은 검색으로 발견된 프로젝트만 포함해 생존자 편향이 있다.</p>
<div class="table-box"><table><thead><tr>
<th>프로젝트</th><th>구분</th><th>모인금액</th><th>후원자</th><th>달성률</th><th>1인당 평균</th>
</tr></thead><tbody>
{"".join(_crowdfunding_row(r) for r in sorted(cf, key=lambda r: -r["raised_krw"]))}
</tbody></table></div>
<div class="note">
<strong>팬메이드 광고 펀딩은 회사 매출이 아니다.</strong> '유니버스 데뷔 3주년 기념 광고' 창작자는
정산액 34,114,780원(수수료 차감 후)을 전액 광고비·일러스트레이터 외주비로 지출했다고 직접
공개했다 — 이 돈은 스텔라이브 회사 매출로 잡히지 않고 팬 커뮤니티 내부에서 돌 뿐이다.
</div>

<h2>레이어 3 · 회사에 남는 것 (09_dart_financials 재사용)</h2>
<p class="sub">DART 감사보고서 원문 파싱으로 확보한 재무제표(09에서 재사용, DART 재수집 없음).
팬딩은 여전히 DART 공시가 0건이라 이 레이어에 팬딩 자체는 없다.</p>
<div class="cards">
  <div class="chart-box">
    <div class="sub" style="margin-bottom:8px">패러블엔터테인먼트(이세계아이돌 소속사)</div>
    {_trend_svg(fin, "패러블엔터테인먼트", C_PARABLE)}
  </div>
</div>
<div class="chart-box" style="margin-top:12px">
  <div class="sub" style="margin-bottom:8px">샌드박스네트워크 (2018~2025년 전 연도 영업손실
  {sandbox_loss_years}/{len(sandbox_years)}년)</div>
  {_trend_svg(fin, "샌드박스네트워크", C_SANDBOX)}
</div>
<div class="table-box" style="margin-top:16px"><table><thead><tr>
<th>법인</th><th>연도</th><th>구분</th><th>매출</th><th>영업이익</th><th>영업이익률</th>
</tr></thead><tbody>
{"".join(_financials_row(r) for r in sorted(fin, key=lambda r: (r["corp_name"], r["bsns_year"])))}
</tbody></table></div>

<h2>세 레이어를 나란히 놓아보면 (관찰 — 증명 아님)</h2>
<div class="note">
이세계아이돌 굿즈 펀딩 두 건은 41억원·88억원이라는 국내 크라우드펀딩 역대 최고 기록을 냈다.
같은 기간 그 IP의 실제 관리사로 보도된 패러블엔터테인먼트의 감사보고서는 매출이
{"210억→218억원" if parable_latest else "—"}으로 늘었는데도 영업이익은 +12억→-91억원으로
무너졌다. 팬덤이 쓰는 돈이 늘어난다고 회사에 남는 돈이 늘어난다는 보장은 없다 —
샌드박스네트워크는 관측된 전 연도({len(sandbox_years)}개 연도) 모두 영업손실을 기록했다.
<br><br>
<strong>이건 증명이 아니라 관찰이다.</strong>
① 크라우드펀딩 IP 소유자(이세계아이돌)와 감사보고서 법인(패러블엔터테인먼트)은 '실제 관리사'라는
언론 보도로만 연결돼 있어 펀딩 수익이 재무제표에 정확히 얼마나 반영되는지는 알 수 없다.
② 재무 표본이 회사 2곳뿐이라 상관계수를 계산하지 않았다.
③ 회계연도(연 1회)와 크라우드펀딩 캠페인(특정 시점)은 기간이 정확히 겹치지 않는다.
④ 팬딩 가격 레이어는 이 두 회사와 무관한 제3의 플랫폼 데이터라 세 레이어를 하나의 숫자로
합칠 수 없다 — 그래서 병렬로만 제시하고 억지로 잇지 않았다.
</div>

</div></body></html>"""

    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"사이트 -> {SITE / 'index.html'}")


if __name__ == "__main__":
    build()
