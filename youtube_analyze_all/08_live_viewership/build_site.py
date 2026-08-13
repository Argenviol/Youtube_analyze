"""
프로젝트8 · 사이트 빌드
site/data.json → site/index.html (인터랙티브 대시보드).

  python 08_live_viewership/build_site.py

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


def _member_color(i: int) -> str:
    return PAL[i % len(PAL)]


def _bar_rows(members, key, fmt="{:+,}"):
    vals = [m.get(key) for m in members if m.get(key) is not None]
    if not vals:
        return '<p class="empty">아직 데이터가 없습니다.</p>'
    top = max(abs(v) for v in vals) or 1
    out = []
    for i, m in enumerate(members):
        v = m.get(key)
        if v is None:
            continue
        pct = abs(v) / top * 100
        out.append(
            f'<div class="row"><span class="nm">{m["name_ko"]}</span>'
            f'<span class="track"><span class="fill" style="width:{pct:.1f}%;'
            f'background:{_member_color(i)}"></span></span>'
            f'<span class="val">{fmt.format(v)}</span></div>'
        )
    return "\n".join(out)


def _member_row(m: dict) -> str:
    """멤버 1행. 라이브 관측이 없으면 해당 칸은 —로 비운다."""
    peak = f'{m["peak_ccu"]:,}' if m.get("peak_ccu") else "—"
    dens = f'{m["ccu_per_1k_followers"]:.1f}' if m.get("ccu_per_1k_followers") else "—"
    return (
        f'<tr><td>{m["name_ko"]}</td><td>{m["unit"]}</td>'
        f'<td>{m["followers"]:,}</td><td>{m["follower_delta"]:+,}</td>'
        f'<td>{m["n_sessions"]}</td><td>{peak}</td><td>{dens}</td></tr>'
    )


def _ccu_svg(series: dict, width=880, height=320, pad=44):
    if not series:
        return '<p class="empty">라이브 스냅샷이 아직 없습니다. 방송 중에 수집되면 채워집니다.</p>'
    pts = [(t, v) for s in series.values() for t, v in s["points"]]
    times = sorted({t for t, _ in pts})
    vmax = max(v for _, v in pts) or 1
    xi = {t: i for i, t in enumerate(times)}
    span = max(1, len(times) - 1)

    def x(t):
        return pad + xi[t] / span * (width - pad * 2)

    def y(v):
        return height - pad - (v / vmax) * (height - pad * 2)

    paths, legend = [], []
    for i, (en, s) in enumerate(series.items()):
        c = _member_color(i)
        d = " ".join(
            ("M" if j == 0 else "L") + f"{x(t):.1f},{y(v):.1f}"
            for j, (t, v) in enumerate(s["points"])
        )
        paths.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2"/>')
        legend.append(f'<span class="lg"><i style="background:{c}"></i>{s["name_ko"]}</span>')

    grid = "".join(
        f'<line x1="{pad}" y1="{y(vmax*f):.1f}" x2="{width-pad}" y2="{y(vmax*f):.1f}" '
        f'stroke="var(--grid)" stroke-width="1"/>'
        f'<text x="{pad-8}" y="{y(vmax*f)+4:.1f}" text-anchor="end" class="ax">'
        f'{int(vmax*f):,}</text>'
        for f in (0, .25, .5, .75, 1)
    )
    return (f'<svg viewBox="0 0 {width} {height}" class="chart">{grid}'
            + "".join(paths) + "</svg>"
            + f'<div class="legend">{"".join(legend)}</div>')


def build():
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    cov, members = data["coverage"], data["members"]
    enough = data.get("enough_coverage", False)

    warn = "" if enough else (
        '<div class="warn"><strong>라이브 분석 커버리지 미달.</strong> '
        f'관측 {cov["span_hours"]:.1f}시간 · 세션 {len(data["sessions"])}건. '
        '동시시청자는 소급 수집이 불가능해 직접 쌓는 중이며, 기준(24시간·5세션)에 도달하면 '
        '아래 섹션이 자동으로 채워집니다.</div>'
    )

    html = f"""<!doctype html>
<html lang="ko"><head>
{site_css.head("StelLive 동시시청자 시계열 · 프로젝트 8")}
</head><body><div class="wrap">

<div class="eyebrow">PROJECT 08</div>
<h1>StelLive 동시시청자 시계열</h1>
<div class="sub">치지직 10분 간격 자체 수집 ·
관측 {cov["first"][:16]} ~ {cov["last"][:16]} (UTC)</div>

<div class="cards">
  <div class="card"><div class="k">관측 시간</div><div class="v">{cov["span_hours"]:.1f}h</div></div>
  <div class="card"><div class="k">스냅샷</div><div class="v">{cov["n_snapshots"]:,}</div></div>
  <div class="card"><div class="k">수집 시점</div><div class="v">{cov["n_timepoints"]:,}</div></div>
  <div class="card"><div class="k">멤버</div><div class="v">{cov["members"]}</div></div>
  <div class="card"><div class="k">관측 세션</div><div class="v">{len(data["sessions"])}</div></div>
</div>

{warn}

<h2>동시시청자 시계열</h2>
<div class="chart-box">{_ccu_svg(data["ccu_series"])}</div>

<h2>관측 구간 팔로워 증감</h2>
{_bar_rows(sorted(members, key=lambda m: -(m.get("follower_delta") or 0)), "follower_delta")}

<h2>멤버 지표</h2>
<div class="table-box"><table><thead><tr>
<th>멤버</th><th>유닛</th><th>팔로워</th><th>증감</th><th>세션</th><th>피크 동시솔</th><th>밀도</th>
</tr></thead><tbody>
{"".join(_member_row(m) for m in members)}
</tbody></table></div>

<div class="note">
<strong>데이터 함정.</strong> 치지직은 방송이 꺼져 있어도 <code>concurrentUserCount</code>에
직전 방송 값을 그대로 돌려줍니다. 수집 단계에서 <code>status</code>를 확인해 라이브 지표를
비우고 잔존값은 <code>last_*</code>로 분리했습니다. 이 처리를 건너뛰면 오프라인 구간이
&ldquo;시청자가 계속 있는 평지&rdquo;로 찍혀 그래프가 통째로 거짓이 됩니다.
<br><br>
<strong>왜 별도 프로젝트인가.</strong> 프로젝트3(방송 패턴)은 VOD 다시보기로 과거를 소급
수집할 수 있지만, 동시시청자는 소급이 불가능합니다. 직접 찍어 쌓은 것만이 유일한 출처입니다.
</div>

</div></body></html>"""

    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"사이트 -> {SITE / 'index.html'}")


if __name__ == "__main__":
    build()
