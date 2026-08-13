"""
프로젝트10 · 사이트 빌드
site/data.json → site/index.html (인터랙티브 대시보드).

  python 10_hoyoverse/build_site.py

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
C_GAME = {"genshin": PAL[0], "starrail": PAL[1]}


def _c(game: str) -> str:
    return C_GAME.get(game, "#888")


def _push_rows(push_top: list[dict]) -> str:
    out = []
    for r in push_top:
        out.append(
            f'<tr><td>{int(r["push_rank"])}</td>'
            f'<td><span style="display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle;background:{_c(r['game'])}"></span>{r["name_ko"]}</td>'
            f'<td>{r["name_ko_game"]}</td><td>{"5성" if r["rank"]==5 else "4성"}</td>'
            f'<td>{str(r["release_date"])[:10]}</td></tr>'
        )
    return "\n".join(out)


def _audience_rows(audience_top: list[dict]) -> str:
    if not audience_top:
        return '<p class="empty">언급된 캐릭터가 없습니다.</p>'
    top = max((r["mention_count"] or 0) for r in audience_top) or 1
    out = []
    for r in audience_top:
        pct = (r["mention_count"] or 0) / top * 100
        amb = ' <span class="pill pill-warn">2글자 이하·상한값</span>' if r.get("name_ambiguous") else ""
        out.append(
            f'<div class="row"><span class="nm">{r["name_ko"]}<br>'
            f'<small style="color:var(--label-alt)">{r["name_ko_game"]}{amb}</small></span>'
            f'<span class="track"><span class="fill" style="width:{pct:.1f}%;'
            f'background:{_c(r["game"])}"></span></span>'
            f'<span class="val">{int(r["mention_count"])}건'
            f'{" · " + str(r["avg_mention_score"]) + "점" if r.get("avg_mention_score") else ""}</span></div>'
        )
    return "\n".join(out)


def _gap_rows(rows: list[dict]) -> str:
    out = []
    for r in rows:
        out.append(
            f'<tr><td><span style="display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle;background:{_c(r['game'])}"></span>{r["name_ko"]}</td>'
            f'<td>{r["name_ko_game"]}</td><td>{int(r["push_rank"])}</td>'
            f'<td>{int(r["audience_rank"])}</td><td>{int(r["gap"]):+d}</td></tr>'
        )
    return "\n".join(out)


def _rank_scatter_svg(characters: list[dict], width=760, height=560, pad=54):
    pts = [c for c in characters if c.get("push_rank") is not None and c.get("audience_rank") is not None]
    if not pts:
        return '<p class="empty">두 랭킹에 모두 포함된 캐릭터가 없습니다.</p>'
    xmax = max(c["push_rank"] for c in pts)
    ymax = max(c["audience_rank"] for c in pts)
    lim = max(xmax, ymax) + 2

    def x(v):
        return pad + v / lim * (width - pad * 2)

    def y(v):
        return pad + v / lim * (height - pad * 2)

    diag = f'<line x1="{x(0):.1f}" y1="{y(0):.1f}" x2="{x(lim):.1f}" y2="{y(lim):.1f}" stroke="var(--line)" stroke-width="1.5" stroke-dasharray="5,4"/>'
    grid, xl, yl = [], [], []
    for f in (0, .25, .5, .75, 1):
        v = lim * f
        grid.append(f'<line x1="{pad}" y1="{y(v):.1f}" x2="{width-pad}" y2="{y(v):.1f}" stroke="var(--grid)" stroke-width="1"/>')
        yl.append(f'<text x="{pad-8}" y="{y(v)+4:.1f}" text-anchor="end" class="ax">{v:.0f}</text>')
        xl.append(f'<text x="{x(v):.1f}" y="{height-pad+18}" text-anchor="middle" class="ax">{v:.0f}</text>')
    dots = []
    for c in pts:
        cx, cy = x(c["push_rank"]), y(c["audience_rank"])
        dots.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="{_c(c["game"])}" opacity="0.85" '
            f'stroke="var(--bg-elevated)" stroke-width="1.5"><title>{c["name_ko"]} ({c["name_ko_game"]}) '
            f'푸시순위 {int(c["push_rank"])} / 반응순위 {int(c["audience_rank"])}</title></circle>'
        )
        if c["push_rank"] <= 20 or c["audience_rank"] <= 20:
            dots.append(f'<text x="{cx+7:.1f}" y="{cy+3:.1f}" class="mlabel">{c["name_ko"]}</text>')
    return (
        f'<svg viewBox="0 0 {width} {height}" class="chart">{"".join(grid)}{diag}'
        f'<text x="{pad-36}" y="{pad-16}" class="ax">반응 순위(언급 많음=1)</text>'
        f'<text x="{width-pad-90}" y="{height-pad+38}" class="ax">푸시 순위(최근 출시=1)</text>'
        f'{"".join(xl)}{"".join(yl)}{"".join(dots)}</svg>'
    )


def _monthly_svg(monthly: list[dict], width=820, height=300, pad=48):
    by_game: dict[str, list[tuple[str, float]]] = {}
    for r in monthly:
        by_game.setdefault(r["game"], []).append((r["month"], r["avg_score"]))
    for k in by_game:
        by_game[k].sort()
    months = sorted({m for pts in by_game.values() for m, _ in pts})
    if not months:
        return '<p class="empty">월별 데이터가 없습니다.</p>'
    xi = {m: i for i, m in enumerate(months)}
    span = max(1, len(months) - 1)
    vmin, vmax = 1, 5

    def x(m):
        return pad + xi[m] / span * (width - pad * 2)

    def y(v):
        return height - pad - (v - vmin) / (vmax - vmin) * (height - pad * 2)

    paths = []
    for game, pts in by_game.items():
        c = _c(game)
        d = " ".join(("M" if i == 0 else "L") + f"{x(m):.1f},{y(v):.1f}" for i, (m, v) in enumerate(pts))
        paths.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.4"/>')
    grid = "".join(
        f'<line x1="{pad}" y1="{y(v):.1f}" x2="{width-pad}" y2="{y(v):.1f}" stroke="var(--grid)" stroke-width="1"/>'
        f'<text x="{pad-8}" y="{y(v)+4:.1f}" text-anchor="end" class="ax">{v}</text>'
        for v in (1, 2, 3, 4, 5)
    )
    xlabels = "".join(
        f'<text x="{x(m):.1f}" y="{height-pad+18}" text-anchor="middle" class="ax">{m}</text>'
        for i, m in enumerate(months) if i % 2 == 0
    )
    return (f'<svg viewBox="0 0 {width} {height}" class="chart">{grid}{xlabels}'
            + "".join(paths) + "</svg>"
            + f'<div class="legend">'
            + "".join(f'<span class="lg"><i style="background:{_c(g)}"></i>{("원신" if g=="genshin" else "붕괴:스타레일")}</span>' for g in by_game)
            + "</div>")


def build():
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    meta, trends = data["meta"], data["trends_status"]
    chars = data["characters"]
    push_top, audience_top = data["push_top"], data["audience_top"]
    overpushed, sleeper = data["gap_overpushed"], data["gap_sleeper"]

    n_gacha = len(chars)
    n_zero = sum(1 for c in chars if c.get("matchable") and (c.get("mention_count") or 0) == 0)

    html = f"""<!doctype html>
<html lang="ko"><head>
{site_css.head("호요버스 캐릭터 인기도 분석 · 프로젝트 10")}
</head><body><div class="wrap">

<div class="eyebrow">PROJECT 10</div>
<h1>호요버스 캐릭터 인기도 분석</h1>
<div class="sub">게임사가 밀어주는 캐릭터와 유저가 실제로 반응하는 캐릭터는 일치하는가? ·
원신·붕괴:스타레일 · 수집 {meta['fetched_at'][:10]}</div>

<div class="cards">
  <div class="card"><div class="k">가챠 대상 캐릭터</div><div class="v">{n_gacha}명</div></div>
  <div class="card"><div class="k">리뷰 표본</div><div class="v">{meta['n_reviews']:,}건</div></div>
  <div class="card"><div class="k">리뷰 무언급 캐릭터</div><div class="v">{n_zero}명</div></div>
  <div class="card"><div class="k">Google Trends</div><div class="v">사용 불가</div></div>
</div>

<div class="warn">
<strong>Google Trends는 이 프로젝트에서 쓰지 않았다.</strong> 매 시도 즉시
<code>{trends['error']}</code>가 발생했다(재현 로그: <code>data/trends_status.json</code>).
검색 관심도 대신 <strong>앱스토어 리뷰 본문에 캐릭터 이름이 언급된 횟수</strong>로 유저 반응을
근사했다 — 이건 검색량보다 훨씬 거친 대체 지표이고, 리뷰를 남기는 유저층으로 표본이 편향돼 있다.
</div>

<h2>공식 푸시 TOP 15 <span style="font-weight:400;color:var(--label-alt);font-size:13px">(5성·출시 최신순 — 배너 재출시 이력 API를 찾지 못해 쓴 프록시)</span></h2>
<div class="table-box"><table><thead><tr>
<th>순위</th><th>캐릭터</th><th>게임</th><th>등급</th><th>출시일</th>
</tr></thead><tbody>
{_push_rows(push_top)}
</tbody></table></div>

<h2>유저 반응 TOP 15 <span style="font-weight:400;color:var(--label-alt);font-size:13px">(리뷰 본문 언급 횟수)</span></h2>
{_audience_rows(audience_top)}

<h2>푸시 순위 vs 반응 순위</h2>
<p class="sub">점선(대각선) 위 = 반응이 푸시 순위보다 약함 · 아래 = 반응이 푸시 순위보다 강함(마우스오버로 캐릭터 확인)</p>
<div class="chart-box">{_rank_scatter_svg(chars)}</div>

<h2>간극이 가장 큰 캐릭터</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;flex-wrap:wrap">
<div>
<p class="sub"><strong>많이 밀렸는데 반응은 약함</strong> (반응순위 - 푸시순위, 양수 클수록)</p>
<div class="table-box"><table><thead><tr><th>캐릭터</th><th>게임</th><th>푸시순위</th><th>반응순위</th><th>격차</th></tr></thead>
<tbody>{_gap_rows(overpushed)}</tbody></table></div>
</div>
<div>
<p class="sub"><strong>덜 밀렸는데 반응은 강함</strong> (숨은 인기 캐릭터, 음수 클수록)</p>
<div class="table-box"><table><thead><tr><th>캐릭터</th><th>게임</th><th>푸시순위</th><th>반응순위</th><th>격차</th></tr></thead>
<tbody>{_gap_rows(sleeper)}</tbody></table></div>
</div>

<h2>게임별 월간 평균 리뷰 평점 추이</h2>
<div class="chart-box">{_monthly_svg(data["monthly_sentiment"])}</div>

<div class="note">
<strong>데이터 함정 1 — 배너/재출시 이력이 없다.</strong> 무료·키 불필요 소스 중 호요버스
배너 스케줄 API를 찾지 못했다(ambr.top의 후신 <code>yatta.moe</code>, 대안으로 지정된
<code>hakush.in</code> 모두 확인 — hakush.in은 이 환경에서 DNS 자체가 응답하지 않았다).
그래서 "공식 푸시"는 <strong>5성 캐릭터를 출시 최신순으로 정렬</strong>한 거친 프록시다.
실제로는 재출시(rerun) 빈도가 더 정확한 신호지만 반영하지 못했다.
<br><br>
<strong>데이터 함정 2 — 리뷰 언급 매칭은 부정확하다.</strong> 한글은 리뷰 문장에서 단어
경계가 명시적으로 분리되지 않는다. 이름이 짧을수록(2글자 이하) 다른 단어와 우연히 겹칠
위험이 커진다. 1글자 이름은 매칭에서 아예 제외했고, 2글자 이름은 표에서
<span class="pill pill-warn">2글자 이하·상한값</span> 배지로 표시했다 — 실제 언급 수보다
많게 잡혔을 수 있다는 뜻이다.
<br><br>
<strong>왜 인과를 주장하지 않는가.</strong> 이 페이지의 모든 비교는 관측 상관이다.
"배너를 자주 돌려서 반응이 늘었다"는 식의 인과 문장은 쓰지 않는다. 언급량에는 신캐 출시,
밸런스 논란, 버그, 이벤트 등 여러 원인이 섞여 있다.
</div>

</div></body></html>"""

    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"사이트 -> {SITE / 'index.html'}")


if __name__ == "__main__":
    build()
