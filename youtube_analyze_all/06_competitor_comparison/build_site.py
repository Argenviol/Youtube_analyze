"""프로젝트6 · 사이트 빌드 — 데뷔 코호트 매칭 비교 대시보드."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE / "site"


def build():
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    html = TEMPLATE.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    (SITE / "index.html").write_text(html, encoding="utf-8")
    style = html[html.index("<style>"):html.index("</style>") + len("</style>")]
    body_inner = html[html.index("<body>") + len("<body>"):html.index("</body>")]
    (SITE / "artifact.html").write_text(style + "\n" + body_inner, encoding="utf-8")
    print(f"사이트 -> {SITE / 'index.html'}  (+ artifact.html)")


TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StelLive 경쟁사 비교 — 데뷔 코호트 매칭</title>
<style>
:root{
  --bg:#F7F7F8; --surface:#ffffff; --text:#171719; --text2:#37383C; --muted:#70737C;
  --grid:#E1E2E4; --border:rgba(112,115,124,.22);
  --g1:#2a78d6; --g2:#eb6834; --g3:#1baf7a;
  --s1:#005EEB; --s2:#F55A00; --s3:#009632; --s4:#D17600; --s5:#E846CD; --s6:#429E00; --s7:#5B37ED; --s8:#E52222;
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --bg:#0F0F10; --surface:#212225; --text:#F7F7F8; --text2:#C2C4C8; --muted:#70737C;
  --grid:#37383C; --border:rgba(112,115,124,.32);
  --g1:#3987e5; --g2:#d95926; --g3:#199e70;
  --s1:#3385FF; --s2:#FF7B2E; --s3:#1ED45A; --s4:#FF9200; --s5:#FA73E3; --s6:#429E00; --s7:#7D5EF7; --s8:#FF6363;
}}
:root[data-theme=dark]{
  --bg:#0F0F10; --surface:#212225; --text:#F7F7F8; --text2:#C2C4C8; --muted:#70737C;
  --grid:#37383C; --border:rgba(112,115,124,.32);
  --g1:#3987e5; --g2:#d95926; --g3:#199e70;
  --s1:#3385FF; --s2:#FF7B2E; --s3:#1ED45A; --s4:#FF9200; --s5:#FA73E3; --s6:#429E00; --s7:#7D5EF7; --s8:#FF6363;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:Pretendard,"Pretendard Variable",-apple-system,BlinkMacSystemFont,"Malgun Gothic","Noto Sans KR",system-ui,sans-serif;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
header h1{font-size:26px;margin:0 0 4px}
header p{color:var(--text2);margin:0 0 6px}
.tag{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--border);border-radius:999px;padding:2px 10px;margin-right:6px}
section{margin:34px 0}
h2{font-size:18px;margin:0 0 4px}
.sub{color:var(--text2);font-size:13.5px;margin:0 0 16px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px}
.gcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:26px 0}
.gcard{background:var(--surface);border:1px solid var(--border);border-top:4px solid var(--gc);border-radius:14px;padding:18px 20px}
.gcard h3{margin:0 0 10px;font-size:16px}
.gcard .row{display:flex;justify-content:space-between;font-size:13px;padding:4px 0;border-bottom:1px solid var(--border)}
.gcard .row:last-child{border-bottom:none}
.gcard .row b{font-variant-numeric:tabular-nums}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{padding:9px 10px;text-align:right;border-bottom:1px solid var(--border);font-variant-numeric:tabular-nums}
th:first-child,td:first-child{text-align:left;font-variant-numeric:normal}
th{color:var(--text2);font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
th.active{color:var(--text)}
tbody tr:hover{background:color-mix(in srgb,var(--s1) 8%,transparent)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
.gpill{font-size:11px;color:var(--text2);border:1px solid var(--border);border-radius:6px;padding:1px 7px}
.chart-svg{width:100%;height:auto;display:block;overflow:visible}
.gridline{stroke:var(--grid);stroke-width:1}
.axis,.axis text{fill:var(--muted);font-size:11px}
.mlabel{fill:var(--text2);font-size:12px}
.legend{display:flex;gap:16px;font-size:12.5px;color:var(--text2);margin-top:10px}
.legend span{display:flex;align-items:center}
.tip{position:fixed;pointer-events:none;background:var(--text);color:var(--bg);font-size:12px;padding:6px 9px;border-radius:8px;opacity:0;transition:opacity .1s;z-index:10;white-space:nowrap}
.foot{color:var(--muted);font-size:12px;margin-top:40px;border-top:1px solid var(--border);padding-top:16px}
.toggle{float:right;background:var(--surface);border:1px solid var(--border);color:var(--text2);border-radius:999px;padding:5px 12px;font-size:12.5px;cursor:pointer}
</style>
</head>
<body>
<div class="wrap">
<button class="toggle" onclick="toggleTheme()">◐ 테마</button>
<header>
  <h1>StelLive 경쟁사 비교 — 데뷔 코호트 매칭</h1>
  <p>StelLive vs 홀로라이브(Hololive) vs 이세계아이돌(이세돌) — <b>데뷔 시기가 겹치는 기수끼리만</b> 비교합니다. 기수 전원 표본.</p>
  <div id="tags"></div>
</header>

<div class="gcards" id="gcards"></div>

<section>
  <h2>구독자 vs 참여율 (로그 스케일)</h2>
  <p class="sub">참여율은 최근 영상 기준이라 데뷔 시기 영향이 가장 작은 지표다 — 코호트가 달라도 이 축은 견줄 수 있다.</p>
  <div class="card"><svg id="scatter" class="chart-svg" viewBox="0 0 720 440"></svg></div>
  <div class="legend" id="glegend"></div>
</section>

<section>
  <h2>전체 멤버 상세 비교</h2>
  <p class="sub">열 제목 클릭 시 정렬. 구독자는 같은 코호트끼리만 비교하세요.</p>
  <div class="card" style="overflow-x:auto"><table id="tbl"></table></div>
</section>

<div class="foot" id="foot"></div>
</div>
<div class="tip" id="tip"></div>

<script>
const DATA = /*__DATA__*/null;
const GC={'StelLive':'--g1','홀로라이브':'--g2','이세계아이돌':'--g3'};
const cssv=v=>getComputedStyle(document.body).getPropertyValue(v).trim();
const fmt=n=>n>=1e6?(n/1e6).toFixed(2)+'M':n>=1e3?(n/1e3).toFixed(0)+'K':(''+n);
const fmtN=n=>Number(n).toLocaleString('ko-KR');
const tip=document.getElementById('tip');
const showTip=(e,h)=>{tip.innerHTML=h;tip.style.opacity=1;tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY+12)+'px';};
const hideTip=()=>tip.style.opacity=0;
const svgEl=(t,a)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e;};

document.getElementById('tags').innerHTML =
  `<span class="tag">수집 ${DATA.meta.fetched_at.slice(0,10)}</span>`+
  `<span class="tag">데뷔 코호트 매칭</span>`+
  `<span class="tag">${DATA.meta.n_channels}채널 · 기수 전원</span>`+
  `<span class="tag">최근 ${DATA.meta.recent_per_channel}영상</span>`+
  `<span class="tag">YouTube Data API v3</span>`;

// 그룹이 하나뿐인 코호트는 비교 상대가 없다 — 카드로 만들면 비교한 것처럼 보이므로 뺀다.
const COHORT_N = {};
DATA.cohorts.forEach(c=>{ COHORT_N[c.cohort]=(COHORT_N[c.cohort]||0)+1; });
const CMP = DATA.cohorts.filter(c=>COHORT_N[c.cohort]>=2);
const LONELY = DATA.cohorts.filter(c=>COHORT_N[c.cohort]<2);

document.getElementById('gcards').innerHTML = CMP.map(g=>`
  <div class="gcard" style="--gc:${cssv(GC[g.group])}">
    <h3>${g.cohort}<br><span class="gpill">${g.group} · ${g.n_members}명</span></h3>
    <div class="row"><span>데뷔 후 경과</span><b>${g.avg_months_since_debut.toFixed(1)}개월</b></div>
    <div class="row"><span>구독자 중앙값</span><b>${fmt(g.median_subscribers)}</b></div>
    <div class="row"><span>월평균 구독자 획득</span><b>${fmt(Math.round(g.median_subs_per_month))}</b></div>
    <div class="row"><span>평균 최근 조회수</span><b>${fmt(g.avg_recent_views)}</b></div>
    <div class="row"><span>평균 참여율</span><b>${(g.avg_engagement_rate*100).toFixed(1)}%</b></div>
    <div class="row"><span>주간 업로드</span><b>${g.avg_uploads_per_week.toFixed(1)}회</b></div>
    <div class="row"><span>도달 효율</span><b>${(g.avg_reach_ratio*100).toFixed(0)}%</b></div>
  </div>`).join('');

document.getElementById('glegend').innerHTML = Object.entries(GC).map(([g,c])=>
  `<span><i class="dot" style="background:${cssv(c)}"></i>${g}</span>`).join('');

function drawScatter(){
  const svg=document.getElementById('scatter');svg.innerHTML='';
  const W=720,H=440,ml=70,mr=30,mt=16,mb=44,list=DATA.members;
  const xs=list.map(m=>Math.log10(m.subscribers)),ys=list.map(m=>m.recent_avg_engagement_rate*100);
  const xmin=Math.min(...xs)-0.08,xmax=Math.max(...xs)+0.08,ymin=0,ymax=Math.max(...ys)*1.15;
  const X=v=>ml+(v-xmin)/(xmax-xmin)*(W-ml-mr),Y=v=>H-mb-(v-ymin)/(ymax-ymin)*(H-mt-mb);
  for(let i=0;i<=4;i++){const gy=mt+i/4*(H-mt-mb);svg.appendChild(svgEl('line',{x1:ml,x2:W-mr,y1:gy,y2:gy,class:'gridline'}));
    const t=svgEl('text',{x:ml-8,y:gy+4,'text-anchor':'end',class:'axis'});t.textContent=(ymax-(i/4)*(ymax-ymin)).toFixed(1)+'%';svg.appendChild(t);}
  [1e5,2e5,5e5,1e6,2e6,5e6,1e7].forEach(v=>{const lx=Math.log10(v);if(lx<xmin||lx>xmax)return;
    const gx=X(lx);const t=svgEl('text',{x:gx,y:H-mb+18,'text-anchor':'middle',class:'axis'});t.textContent=fmt(v);svg.appendChild(t);
    svg.appendChild(svgEl('line',{x1:gx,x2:gx,y1:mt,y2:H-mb,class:'gridline'}));});
  svg.appendChild(svgEl('text',{x:(ml+W-mr)/2,y:H-6,'text-anchor':'middle',class:'axis'})).textContent='구독자 (log)';
  list.forEach(m=>{
    const cx=X(Math.log10(m.subscribers)),cy=Y(m.recent_avg_engagement_rate*100);
    const c=svgEl('circle',{cx,cy,r:9,fill:cssv(GC[m.group]),opacity:.82,stroke:cssv('--surface'),'stroke-width':2});
    c.addEventListener('mousemove',e=>showTip(e,`<b>${m.name_ko}</b> (${m.group})<br>구독 ${fmt(m.subscribers)}<br>참여율 ${(m.recent_avg_engagement_rate*100).toFixed(1)}%`));
    c.addEventListener('mouseleave',hideTip);svg.appendChild(c);
  });
}

const COLS=[
  ['name_ko','멤버',r=>`<i class="dot" style="background:${cssv(GC[r.group])}"></i>${r.name_ko} <span class="gpill">${r.group}</span>`],
  ['cohort','코호트',r=>r.cohort||'—'],
  ['months_since_debut','경과개월',r=>r.months_since_debut==null?'—':r.months_since_debut.toFixed(0)],
  ['subscribers','구독자',r=>fmtN(r.subscribers)],
  ['subs_per_month','월평균획득',r=>r.subs_per_month==null?'—':fmtN(Math.round(r.subs_per_month))],
  ['recent_avg_views','평균조회수',r=>fmtN(Math.round(r.recent_avg_views))],
  ['recent_avg_engagement_rate','참여율',r=>(r.recent_avg_engagement_rate*100).toFixed(1)+'%'],
  ['uploads_per_week','주간업로드',r=>r.uploads_per_week.toFixed(1)],
  ['reach_ratio','도달효율',r=>(r.reach_ratio*100).toFixed(0)+'%'],
];
let sk='subscribers',sd=-1;
const rows=()=>[...DATA.members].sort((a,b)=>(a[sk]>b[sk]?1:-1)*sd);
function drawTable(){const t=document.getElementById('tbl');
  t.innerHTML='<thead><tr>'+COLS.map(c=>`<th class="${c[0]===sk?'active':''}" onclick="setSk('${c[0]}')">${c[1]}${c[0]===sk?(sd<0?' ▾':' ▴'):''}</th>`).join('')+'</tr></thead>'+
  '<tbody>'+rows().map(r=>'<tr>'+COLS.map(c=>`<td>${c[2](r)}</td>`).join('')+'</tr>').join('')+'</tbody>';}
function setSk(k){if(sk===k)sd*=-1;else{sk=k;sd=-1;}drawTable();}

document.getElementById('foot').innerHTML=
  `표본: 데뷔 시기가 겹치는 <b>기수 전원</b>입니다. 그룹 전체 평균이 아니므로 홀로라이브 전사 지표로 읽으면 안 됩니다.<br>`+
  (LONELY.length? `비교군 없는 코호트: ${LONELY.map(c=>c.cohort+'('+c.group+' '+c.n_members+'명)').join(', ')} — 그룹 비교에서 제외했습니다.<br>`:'')+
  `구독자는 누적 지표라 코호트가 다르면 비교가 성립하지 않습니다. 코호트 간 비교는 참여율·도달 효율을 보세요.<br>`+
  `데이터 출처: YouTube Data API v3 · 지표는 수집 시점 스냅샷입니다.`;

function toggleTheme(){const r=document.documentElement;
  const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  r.setAttribute('data-theme',cur==='dark'?'light':'dark');drawAll();}
function drawAll(){drawScatter();drawTable();}
drawAll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
