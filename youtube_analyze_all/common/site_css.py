"""
대시보드 공통 스타일시트 — Montage 토큰 기반.

프로젝트마다 CSS를 따로 쓰면 8개 사이트가 조금씩 달라진다. 여기 한 곳에서만
만들어 전 프로젝트가 같은 것을 쓴다. 외부 CDN을 부르지 않으므로 오프라인에서도 열린다.
"""
from __future__ import annotations

from . import montage


def stylesheet() -> str:
    return montage.css_variables() + """
* { box-sizing: border-box; }

html { color-scheme: light dark; }

body {
  margin: 0;
  background: var(--bg-alt);
  color: var(--label);
  font-family: var(--font);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.wrap { max-width: 1000px; margin: 0 auto; padding: 48px 20px 80px; }

/* ---- 타이포 ---- */
h1 { font-size: 28px; font-weight: 700; letter-spacing: -0.02em; margin: 0 0 6px; }
h2 {
  font-size: 18px; font-weight: 700; letter-spacing: -0.01em;
  margin: 40px 0 16px; color: var(--label);
}
.sub { color: var(--label-alt); font-size: 14px; margin-bottom: 32px; }
.eyebrow {
  display: inline-block; font-size: 12px; font-weight: 600;
  color: var(--primary); letter-spacing: 0.02em; margin-bottom: 8px;
}

/* ---- 카드 ---- */
.cards {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}
.card {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  box-shadow: var(--shadow-xsmall);
}
.card .k { color: var(--label-alt); font-size: 12px; font-weight: 500; }
.card .v {
  font-size: 24px; font-weight: 700; letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums; margin-top: 2px;
}

/* ---- 뱃지(상태 표시) ---- */
.pill {
  display: inline-block; font-size: 11.5px; font-weight: 600;
  padding: 3px 9px; border-radius: var(--radius-full, 999px);
  white-space: nowrap;
}
.pill-ok { background: color-mix(in srgb, var(--positive) 16%, transparent); color: var(--positive); }
.pill-warn { background: color-mix(in srgb, var(--cautionary) 16%, transparent); color: var(--cautionary); }
.pill-no { background: color-mix(in srgb, var(--negative) 16%, transparent); color: var(--negative); }

/* ---- 알림 ---- */
.warn {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-left: 3px solid var(--cautionary);
  border-radius: var(--radius-md);
  padding: 14px 18px; font-size: 14px; margin: 24px 0;
  color: var(--label-neutral);
}
.warn strong { color: var(--label); }

/* ---- 바 리스트 ---- */
.row { display: flex; align-items: center; gap: 12px; margin: 6px 0; font-size: 14px; }
.nm { width: 108px; flex: none; color: var(--label-neutral); }
.track {
  flex: 1; height: 18px; background: var(--fill);
  border-radius: var(--radius-sm); overflow: hidden;
}
.fill { display: block; height: 100%; border-radius: var(--radius-sm); }
.val {
  width: 84px; text-align: right; flex: none;
  font-variant-numeric: tabular-nums; font-weight: 600;
}

/* ---- 차트 ---- */
.chart-box {
  background: var(--bg-elevated); border: 1px solid var(--line);
  border-radius: var(--radius-lg); padding: 20px;
  overflow-x: auto;
}
.chart { width: 100%; height: auto; display: block; }
.ax { fill: var(--label-assistive); font-size: 11px; }
.legend {
  display: flex; flex-wrap: wrap; gap: 14px; font-size: 12px;
  color: var(--label-alt); margin-top: 12px;
}
.lg i {
  display: inline-block; width: 10px; height: 10px;
  border-radius: var(--radius-sm); margin-right: 6px; vertical-align: -1px;
}

/* ---- 표 ---- */
.table-box {
  background: var(--bg-elevated); border: 1px solid var(--line);
  border-radius: var(--radius-lg); overflow: hidden; overflow-x: auto;
}
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td {
  text-align: right; padding: 10px 14px;
  border-bottom: 1px solid var(--line-alt);
  font-variant-numeric: tabular-nums;
}
th:first-child, td:first-child { text-align: left; font-variant-numeric: normal; }
th {
  color: var(--label-alt); font-weight: 600; font-size: 12px;
  background: var(--bg-alt); border-bottom: 1px solid var(--line);
}
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: var(--fill); }

/* ---- 기타 ---- */
.empty { color: var(--label-assistive); font-size: 14px; padding: 24px 0; }
.note {
  color: var(--label-alt); font-size: 13px; margin-top: 40px;
  padding-top: 20px; border-top: 1px solid var(--line);
}
.note strong { color: var(--label-neutral); }
code {
  background: var(--fill); border-radius: var(--radius-sm);
  padding: 1px 5px; font-size: 0.92em;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }

@media (max-width: 640px) {
  .wrap { padding: 32px 16px 56px; }
  h1 { font-size: 23px; }
  .nm { width: 84px; }
  .val { width: 68px; }
}
"""


def head(title: str) -> str:
    """<head> 공통 블록. 각 build_site.py에서 재사용한다."""
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{stylesheet()}</style>"""
