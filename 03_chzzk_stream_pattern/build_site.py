"""
프로젝트3 · 사이트 빌드 — 방송 시작시간 히트맵 포함 자체완결 대시보드.
  python 03_chzzk_stream_pattern/build_site.py
"""
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
<title>StelLive 치지직 방송 패턴</title>
<style>
:root{
  --bg:#f9f9f7; --surface:#fcfcfb; --text:#0b0b0b; --text2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --border:rgba(11,11,11,.10); --heat:74,58,167;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#e87ba4; --s6:#008300; --s7:#4a3aa7; --s8:#e34948;
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --bg:#0d0d0d; --surface:#1a1a19; --text:#fff; --text2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --border:rgba(255,255,255,.10); --heat:144,133,233;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#008300; --s7:#9085e9; --s8:#e66767;
}}
:root[data-theme=dark]{
  --bg:#0d0d0d; --surface:#1a1a19; --text:#fff; --text2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --border:rgba(255,255,255,.10); --heat:144,133,233;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#008300; --s7:#9085e9; --s8:#e66767;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:system-ui,-apple-system,"Segoe UI","Noto Sans KR",sans-serif;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
header h1{font-size:26px;margin:0 0 4px}
header p{color:var(--text2);margin:0 0 6px}
.tag{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--border);border-radius:999px;padding:2px 10px;margin-right:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:26px 0}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 18px}
.kpi .v{font-size:24px;font-weight:700;letter-spacing:-.5px}
.kpi .l{font-size:12.5px;color:var(--text2);margin-top:3px}
.kpi .s{font-size:12px;color:var(--muted);margin-top:2px}
section{margin:34px 0}
h2{font-size:18px;margin:0 0 4px}
.sub{color:var(--text2);font-size:13.5px;margin:0 0 16px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{padding:9px 10px;text-align:right;border-bottom:1px solid var(--border);font-variant-numeric:tabular-nums}
th:first-child,td:first-child{text-align:left;font-variant-numeric:normal}
th{color:var(--text2);font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
th.active{color:var(--text)}
tbody tr:hover{background:color-mix(in srgb,var(--s7) 8%,transparent)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
.chart-svg{width:100%;height:auto;display:block;overflow:visible}
.gridline{stroke:var(--grid);stroke-width:1}
.mlabel{fill:var(--text2);font-size:12px}
.blabel{fill:var(--text);font-size:11px;font-variant-numeric:tabular-nums}
.axis text,.axis{fill:var(--muted);font-size:11px}
.heat-cell{stroke:var(--surface);stroke-width:1.5}
.tip{position:fixed;pointer-events:none;background:var(--text);color:var(--bg);font-size:12px;padding:6px 9px;border-radius:8px;opacity:0;transition:opacity .1s;z-index:10;white-space:nowrap}
.foot{color:var(--muted);font-size:12px;margin-top:40px;border-top:1px solid var(--border);padding-top:16px}
.toggle{float:right;background:var(--surface);border:1px solid var(--border);color:var(--text2);border-radius:999px;padding:5px 12px;font-size:12.5px;cursor:pointer}
.two{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:760px){.two{grid-template-columns:1fr}}
.catbar{display:flex;flex-direction:column;gap:8px}
.catrow{display:grid;grid-template-columns:130px 1fr 44px;align-items:center;gap:10px;font-size:13px}
.catrow .bar{height:16px;border-radius:4px;background:var(--s1)}
.catrow .n{text-align:right;color:var(--text2);font-variant-numeric:tabular-nums}
</style>
</head>
<body>
<div class="wrap">
<button class="toggle" onclick="toggleTheme()">◐ 테마</button>
<header>
  <h1>StelLive 치지직 방송 패턴 분석</h1>
  <p>스텔라이브 멤버들의 방송 빈도·길이·시간대·카테고리 (치지직 다시보기 기반)</p>
  <div id="tags"></div>
</header>

<div class="kpis" id="kpis"></div>

<section>
  <h2>방송 시작 시간 히트맵</h2>
  <p class="sub">요일(세로) × 시각(가로, KST). 진할수록 그 시간대에 방송을 많이 시작. 셀에 마우스를 올리면 방송 수가 보입니다.</p>
  <div class="card"><svg id="heatmap" class="chart-svg" viewBox="0 0 760 250"></svg></div>
</section>

<section>
  <h2>멤버별 방송 패턴</h2>
  <p class="sub">열 제목 클릭 시 정렬. 주간시간 = 수집 구간 기준 주당 방송 시간.</p>
  <div class="card" style="overflow-x:auto"><table id="tbl"></table></div>
</section>

<section class="two">
  <div>
    <h2>인기 방송 카테고리</h2>
    <p class="sub">전체 방송 수 기준 상위 카테고리.</p>
    <div class="card"><div class="catbar" id="cats"></div></div>
  </div>
  <div>
    <h2>방송 빈도 vs 길이</h2>
    <p class="sub">버블=팔로워. 오른쪽=자주, 위쪽=길게.</p>
    <div class="card"><svg id="scatter" class="chart-svg" viewBox="0 0 460 380"></svg></div>
  </div>
</section>

<div class="foot" id="foot"></div>
</div>
<div class="tip" id="tip"></div>

<script>
const DATA = /*__DATA__*/null;
const SERIES=['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'];
const WD=['월','화','수','목','금','토','일'];
const cssv=v=>getComputedStyle(document.body).getPropertyValue(v).trim();
const fmt=n=>n>=1e6?(n/1e6).toFixed(1)+'M':n>=1e3?(n/1e3).toFixed(0)+'K':(''+n);
const fmtN=n=>Number(n).toLocaleString('ko-KR');
const mcolor={}; DATA.members.forEach((m,i)=>mcolor[m.name_en]=SERIES[i%SERIES.length]);
const tip=document.getElementById('tip');
const showTip=(e,h)=>{tip.innerHTML=h;tip.style.opacity=1;tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY+12)+'px';};
const hideTip=()=>tip.style.opacity=0;
const svgEl=(t,a)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e;};

document.getElementById('tags').innerHTML =
  `<span class="tag">수집 ${DATA.meta.fetched_at.slice(0,10)}</span>`+
  `<span class="tag">방송 ${fmtN(DATA.meta.n_streams)}건</span>`+
  `<span class="tag">멤버 ${DATA.meta.n_members}명</span>`+
  `<span class="tag">치지직 API</span>`;

// KPIs
const byHours=[...DATA.members].sort((a,b)=>b.hours_per_week-a.hours_per_week);
const byNight=[...DATA.members].sort((a,b)=>b.night_share-a.night_share)[0];
const byGame=[...DATA.members].sort((a,b)=>b.game_share-a.game_share)[0];
let peakH=0,peakV=-1; DATA.hour_dist.forEach((v,h)=>{if(v>peakV){peakV=v;peakH=h;}});
document.getElementById('kpis').innerHTML=[
  ['방송 시간 1위',byHours[0].name_ko,'주 '+byHours[0].hours_per_week+'시간'],
  ['최다 심야형',byNight.name_ko,(byNight.night_share*100).toFixed(0)+'% · 0~5시 시작'],
  ['최고 게임형',byGame.name_ko,(byGame.game_share*100).toFixed(0)+'% 게임 방송'],
  ['피크 시작 시간',peakH+'시',fmtN(peakV)+'회 (KST)'],
].map(k=>`<div class="kpi"><div class="v">${k[1]}</div><div class="l">${k[0]}</div><div class="s">${k[2]}</div></div>`).join('');

// Heatmap
function drawHeat(){
  const svg=document.getElementById('heatmap');svg.innerHTML='';
  const ml=34,mt=16,cw=(760-ml-6)/24,chh=26,H=DATA.heatmap;
  let max=0; H.forEach(r=>r.forEach(v=>{if(v>max)max=v;}));
  for(let d=0;d<7;d++){
    const t=svgEl('text',{x:ml-8,y:mt+d*chh+chh/2+4,'text-anchor':'end',class:'axis'});t.textContent=WD[d];svg.appendChild(t);
    for(let h=0;h<24;h++){
      const v=H[d][h],a=max?v/max:0;
      const rect=svgEl('rect',{x:ml+h*cw,y:mt+d*chh,width:cw-1.5,height:chh-1.5,rx:3,
        class:'heat-cell',fill:`rgba(${cssv('--heat')},${0.08+a*0.92})`});
      rect.addEventListener('mousemove',e=>showTip(e,`${WD[d]} ${h}시<br><b>${v}</b>회 방송`));
      rect.addEventListener('mouseleave',hideTip);
      svg.appendChild(rect);
    }
  }
  for(let h=0;h<24;h+=2){const t=svgEl('text',{x:ml+h*cw+cw/2,y:mt+7*chh+14,'text-anchor':'middle',class:'axis'});t.textContent=h;svg.appendChild(t);}
}

// table
const COLS=[
  ['name_ko','멤버',r=>`<i class="dot" style="background:${cssv(mcolor[r.name_en])}"></i>${r.name_ko}`],
  ['streams_per_week','주간횟수',r=>r.streams_per_week.toFixed(1)],
  ['avg_duration_h','평균시간',r=>r.avg_duration_h.toFixed(1)+'h'],
  ['hours_per_week','주간시간',r=>r.hours_per_week.toFixed(1)+'h'],
  ['night_share','심야비중',r=>(r.night_share*100).toFixed(0)+'%'],
  ['game_share','게임비중',r=>(r.game_share*100).toFixed(0)+'%'],
  ['top_category','주력',r=>r.top_category],
  ['followers','팔로워',r=>fmt(r.followers)],
];
let sortKey='hours_per_week',sortDir=-1;
const rows=()=>[...DATA.members].sort((a,b)=>(a[sortKey]>b[sortKey]?1:-1)*sortDir);
function drawTable(){
  const t=document.getElementById('tbl');
  t.innerHTML='<thead><tr>'+COLS.map(c=>`<th class="${c[0]===sortKey?'active':''}" onclick="setSort('${c[0]}')">${c[1]}${c[0]===sortKey?(sortDir<0?' ▾':' ▴'):''}</th>`).join('')+'</tr></thead>'+
    '<tbody>'+rows().map(r=>'<tr>'+COLS.map(c=>`<td>${c[2](r)}</td>`).join('')+'</tr>').join('')+'</tbody>';
}
function setSort(k){if(sortKey===k)sortDir*=-1;else{sortKey=k;sortDir=-1;}drawTable();}

// categories
const maxCat=DATA.top_categories[0].count;
document.getElementById('cats').innerHTML=DATA.top_categories.map((c,i)=>
  `<div class="catrow"><span>${c.name}</span>`+
  `<span class="bar" style="width:${(c.count/maxCat*100).toFixed(1)}%;background:${cssv(SERIES[i%SERIES.length])}"></span>`+
  `<span class="n">${c.count}</span></div>`).join('');

// scatter
function drawScatter(){
  const svg=document.getElementById('scatter');svg.innerHTML='';
  const W=460,H=380,ml=44,mr=30,mt=14,mb=40,list=DATA.members;
  const xs=list.map(m=>m.streams_per_week),ys=list.map(m=>m.avg_duration_h);
  const xmin=Math.min(...xs)*0.9,xmax=Math.max(...xs)*1.05,ymin=Math.min(...ys)*0.85,ymax=Math.max(...ys)*1.08;
  const X=v=>ml+(v-xmin)/(xmax-xmin)*(W-ml-mr),Y=v=>H-mb-(v-ymin)/(ymax-ymin)*(H-mt-mb);
  for(let i=0;i<=4;i++){const gy=mt+i/4*(H-mt-mb);svg.appendChild(svgEl('line',{x1:ml,x2:W-mr,y1:gy,y2:gy,class:'gridline'}));
    const t=svgEl('text',{x:ml-8,y:gy+4,'text-anchor':'end',class:'axis'});t.textContent=(ymax-(i/4)*(ymax-ymin)).toFixed(1)+'h';svg.appendChild(t);}
  for(let i=0;i<=4;i++){const gx=ml+i/4*(W-ml-mr);const t=svgEl('text',{x:gx,y:H-mb+18,'text-anchor':'middle',class:'axis'});t.textContent=(xmin+(i/4)*(xmax-xmin)).toFixed(1);svg.appendChild(t);}
  svg.appendChild(svgEl('text',{x:(ml+W-mr)/2,y:H-4,'text-anchor':'middle',class:'axis'})).textContent='주간 방송 횟수';
  const maxF=Math.max(...list.map(m=>m.followers));
  list.forEach(m=>{
    const r=7+Math.sqrt(m.followers/maxF)*14,cx=X(m.streams_per_week),cy=Y(m.avg_duration_h);
    const c=svgEl('circle',{cx,cy,r,fill:cssv(mcolor[m.name_en]),opacity:.8,stroke:cssv('--surface'),'stroke-width':2});
    c.addEventListener('mousemove',e=>showTip(e,`<b>${m.name_ko}</b><br>주 ${m.streams_per_week}회 · ${m.avg_duration_h}h<br>팔로워 ${fmt(m.followers)}`));
    c.addEventListener('mouseleave',hideTip);svg.appendChild(c);
    const right=cx+r+50>W-mr;
    const tx=svgEl('text',{x:right?cx-r-4:cx+r+4,y:cy+4,class:'mlabel','text-anchor':right?'end':'start'});tx.textContent=m.name_ko;svg.appendChild(tx);
  });
}

document.getElementById('foot').innerHTML=
  `방송 데이터: 치지직 다시보기(REPLAY) 기준. 멤버당 최근 최대 ${DATA.meta.max_items}개, 시간은 KST.<br>`+
  `'주간' 지표는 수집된 방송의 실제 기간으로 환산 · 지표는 수집 시점 스냅샷입니다.`;

function toggleTheme(){const r=document.documentElement;
  const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  r.setAttribute('data-theme',cur==='dark'?'light':'dark');drawAll();}
function drawAll(){drawHeat();drawTable();drawScatter();}
drawAll();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
