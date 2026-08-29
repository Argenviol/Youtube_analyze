"""
프로젝트12 · 사이트 빌드
site/data.json → site/index.html (이벤트 타임라인 대시보드).

  python 12_event_impact/build_site.py

외부 CDN을 쓰지 않는다(오프라인에서도 열림).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import site_css  # noqa: E402

HERE = Path(__file__).resolve().parent
SITE = HERE / "site"

TYPE_COLOR = {"합방": "#0066FF", "커버곡": "#7C3AED", "콘서트": "#E52222",
              "오리지널곡": "#009632", "오프라인": "#F59E0B"}


def _chip(t: str) -> str:
    c = TYPE_COLOR.get(t, "#70737C")
    return (f'<span class="chip" style="border-color:{c};color:{c}">{t}</span>')


def _collab_rows(rows: list[dict]) -> str:
    if not rows:
        return '<p class="empty">아직 측정된 합방이 없습니다.</p>'
    top = max(r["views_multiple"] for r in rows) or 1
    out = []
    for r in rows:
        pct = r["views_multiple"] / top * 100
        out.append(
            f'<div class="row"><span class="nm">{r["title"][:28]}'
            f'<i>{r["date"]}</i></span>'
            f'<span class="bar"><b style="width:{pct:.1f}%"></b></span>'
            f'<span class="val">{r["views_multiple"]:.2f}배</span></div>')
    return "".join(out)


def _impact_rows(rows: list[dict]) -> str:
    if not rows:
        return ('<p class="empty">이벤트 후 창이 찰 때까지 기다리는 중입니다. '
                '측정 가능한 건이 생기면 여기에 쌓입니다.</p>')
    out = []
    for r in rows:
        ch = r.get("change_pct")
        cls = "up" if ch and ch > 0 else ("dn" if ch and ch < 0 else "zero")
        out.append(
            f'<tr><td>{r["date"]}</td><td>{str(r["title"])[:30]}</td>'
            f'<td>{r["name_ko"]}</td><td>{r["metric"]}</td>'
            f'<td>{r["before_per_day"]:+,.0f}</td><td>{r["after_per_day"]:+,.0f}</td>'
            f'<td class="{cls}">{ch:+.1f}%</td></tr>')
    return "".join(out)


def build() -> None:
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    by_type = data.get("by_type", {})
    chips = "".join(_chip(f"{k} {v}건") for k, v in by_type.items())
    span = " ~ ".join(data.get("span", ["", ""]))

    html = f"""{site_css.head("프로젝트12 · 이벤트 임팩트")}
<div class="wrap">
<h1>이벤트 임팩트 분석</h1>
<p class="sub">대규모 합방·커버곡 발매·콘서트를 자동으로 찾아 기억하고, 그 전후로
팔로워·구독자·동시시청자가 어떻게 움직였는지 붙입니다.</p>
<p class="sub">{span} · 총 {data.get('n_events', 0)}건 &nbsp; {chips}</p>

<h2>합방 효과 — 이벤트 방송 조회수 ÷ 평소 방송</h2>
<p class="sub">치지직 VOD 조회수는 과거분이 남아 있어 <b>일일 수집 이전 이벤트도
크기는 잴 수 있습니다.</b> 1.0 = 평소와 같음.</p>
<div class="bars">{_collab_rows(data.get('top_collabs', []))}</div>

<h2>이벤트 전후 변화</h2>
<div class="table-box"><table><thead><tr>
<th>날짜</th><th>이벤트</th><th>멤버</th><th>지표</th>
<th>이전(일평균)</th><th>이후(일평균)</th><th>변화</th>
</tr></thead><tbody>
{_impact_rows(data.get('impact', []))}
</tbody></table></div>

<div class="note">
<strong>수익은 잴 수 없습니다.</strong> 치지직 후원·구독 수익도, 유튜브 광고 수익도
공개되지 않습니다. 추정치를 지어내는 대신 플랫폼이 실제로 수익을 매기는 축인
<b>노출량(동시시청자 피크·조회수)</b>을 대리 지표로 냅니다. 회사 단위 실제 수익성은
프로젝트9(DART 감사보고서)가 연 단위로 답합니다.
<br><br>
<strong>측정 가능 시점이 지표마다 다릅니다.</strong> 조회수 배수는 2025-04부터 소급
가능하지만, 팔로워·구독자·동시시청자 전후 비교는 일일 수집이 시작된 <b>2026-08-12
이후 이벤트</b>만 가능합니다. 그 이전은 기준선이 없어 계산하지 않습니다 —
0%가 아니라 측정 불가입니다.
<br><br>
<strong>자동 감지의 한계.</strong> 합방은 치지직 방송이 있어야 잡힙니다. 유튜브 전용
합방·오프라인 행사·오리지널곡 발매는 <code>data/events_manual.csv</code>에 손으로
등록해야 합니다.
</div>

</div></body></html>"""

    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"사이트 -> {SITE / 'index.html'}")


if __name__ == "__main__":
    build()
