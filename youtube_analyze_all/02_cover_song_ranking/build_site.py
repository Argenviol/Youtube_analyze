"""
프로젝트2 · 사이트 빌드 — site/data.json 인라인 임베드 자체완결 대시보드.
  python 02_cover_song_ranking/build_site.py
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
<title>StelLive 커버곡 성과 랭킹</title>
<style>
:root{
  --bg:#F7F7F8; --surface:#ffffff; --text:#171719; --text2:#37383C; --muted:#70737C;
  --grid:#E1E2E4; --border:rgba(112,115,124,.22);
  --s1:#005EEB; --s2:#F55A00; --s3:#009632; --s4:#D17600; --s5:#E846CD; --s6:#429E00; --s7:#5B37ED; --s8:#E52222;
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --bg:#0F0F10; --surface:#212225; --text:#F7F7F8; --text2:#C2C4C8; --muted:#70737C;
  --grid:#37383C; --border:rgba(112,115,124,.32);
  --s1:#3385FF; --s2:#FF7B2E; --s3:#1ED45A; --s4:#FF9200; --s5:#FA73E3; --s6:#429E00; --s7:#7D5EF7; --s8:#FF6363;
}}
:root[data-theme=dark]{
  --bg:#0F0F10; --surface:#212225; --text:#F7F7F8; --text2:#C2C4C8; --muted:#70737C;
  --grid:#37383C; --border:rgba(112,115,124,.32);
  --s1:#3385FF; --s2:#FF7B2E; --s3:#1ED45A; --s4:#FF9200; --s5:#FA73E3; --s6:#429E00; --s7:#7D5EF7; --s8:#FF6363;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:Pretendard,"Pretendard Variable",-apple-system,BlinkMacSystemFont,"Malgun Gothic","Noto Sans KR",system-ui,sans-serif;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
header h1{font-size:26px;margin:0 0 4px}
header p{color:var(--text2);margin:0 0 6px}
.tag{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--border);
  border-radius:999px;padding:2px 10px;margin-right:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:26px 0}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 18px}
.kpi .v{font-size:26px;font-weight:700;letter-spacing:-.5px}
.kpi .l{font-size:12.5px;color:var(--text2);margin-top:3px}
.kpi .s{font-size:12px;color:var(--muted);margin-top:2px}
section{margin:34px 0}
h2{font-size:18px;margin:0 0 4px}
.sub{color:var(--text2);font-size:13.5px;margin:0 0 16px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px}
.chart-svg{width:100%;height:auto;display:block;overflow:visible}
.axis text{fill:var(--muted);font-size:11px}
.gridline{stroke:var(--grid);stroke-width:1}
.blabel{fill:var(--text);font-size:11px;font-variant-numeric:tabular-nums}
.mlabel{fill:var(--text2);font-size:12px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{padding:9px 10px;text-align:right;border-bottom:1px solid var(--border);font-variant-numeric:tabular-nums}
th:first-child,td:first-child{text-align:left;font-variant-numeric:normal}
th{color:var(--text2);font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
th.active{color:var(--text)}
td.song{text-align:left;font-variant-numeric:normal;max-width:440px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
tbody tr:hover{background:color-mix(in srgb,var(--s3) 8%,transparent)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
.rankn{color:var(--muted);font-variant-numeric:tabular-nums;width:26px;display:inline-block}
.tip{position:fixed;pointer-events:none;background:var(--text);color:var(--bg);font-size:12px;
  padding:6px 9px;border-radius:8px;opacity:0;transition:opacity .1s;z-index:10;white-space:nowrap}
.foot{color:var(--muted);font-size:12px;margin-top:40px;border-top:1px solid var(--border);padding-top:16px}
.toggle{float:right;background:var(--surface);border:1px solid var(--border);color:var(--text2);
  border-radius:999px;padding:5px 12px;font-size:12.5px;cursor:pointer}
</style>
</head>
<body>
<div class="wrap">
<button class="toggle" onclick="toggleTheme()">◐ 테마</button>
<header>
  <h1>StelLive 커버곡 성과 랭킹</h1>
  <p>스텔라이브 멤버들의 유튜브 커버곡 조회수·좋아요·참여율 비교</p>
  <div id="tags"></div>
</header>

<div class="kpis" id="kpis"></div>

<section>
  <h2>멤버별 커버 성과</h2>
  <p class="sub">열 제목 클릭 시 정렬. 총 조회수는 각 멤버 커버곡의 합입니다.</p>
  <div class="card" style="overflow-x:auto"><table id="tbl"></table></div>
</section>

<section>
  <h2>커버 수 vs 곡당 평균 조회수</h2>
  <p class="sub">버블 크기 = 총 조회수. 오른쪽=다작, 위쪽=곡당 파괴력. 둘 다 높으면 최상위.</p>
  <div class="card"><svg id="scatter" class="chart-svg" viewBox="0 0 720 440"></svg></div>
</section>

<section>
  <h2>커버곡 조회수 TOP 20</h2>
  <div class="card" style="overflow-x:auto"><table id="topcovers"></table></div>
</section>

<div class="foot" id="foot"></div>
</div>
<div class="tip" id="tip"></div>

<script>
const DATA = /*__DATA__*/null;
const SERIES=['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'];
const cssv=v=>getComputedStyle(document.body).getPropertyValue(v).trim();
const fmt=n=>n>=1e6?(n/1e6).toFixed(1)+'M':n>=1e3?(n/1e3).toFixed(0)+'K':(''+n);
const fmtN=n=>Number(n).toLocaleString('ko-KR');
const mcolor={}; DATA.members.forEach((m,i)=>mcolor[m.name_en]=SERIES[i%SERIES.length]);
const tip=document.getElementById('tip');
const showTip=(e,h)=>{tip.innerHTML=h;tip.style.opacity=1;tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY+12)+'px';};
const hideTip=()=>tip.style.opacity=0;

document.getElementById('tags').innerHTML =
  `<span class="tag">수집 ${DATA.meta.fetched_at.slice(0,10)}</span>`+
  `<span class="tag">커버 ${DATA.meta.n_covers}곡</span>`+
  `<span class="tag">멤버 ${DATA.meta.n_members}명</span>`+
  `<span class="tag">YouTube Data API v3</span>`;

const totCovers=DATA.members.reduce((a,m)=>a+m.cover_count,0);
const totViews=DATA.members.reduce((a,m)=>a+m.total_views,0);
const king=[...DATA.members].sort((a,b)=>b.total_views-a.total_views)[0];
const topCover=DATA.top_covers[0];
document.getElementById('kpis').innerHTML=[
  ['총 커버곡',fmtN(totCovers)+'곡','11명 채널 합산'],
  ['합산 조회수',fmt(totViews),'모든 커버곡 조회수 합'],
  ['총 조회수 1위',king.name_ko,fmt(king.total_views)+' · '+king.cover_count+'곡'],
  ['최고 조회 커버',topCover.name_ko,fmt(topCover.views)+' 조회'],
].map(k=>`<div class="kpi"><div class="v">${k[1]}</div><div class="l">${k[0]}</div><div class="s">${k[2]}</div></div>`).join('');

const COLS=[
  ['name_ko','멤버',r=>`<i class="dot" style="background:${cssv(mcolor[r.name_en])}"></i>${r.name_ko}`],
  ['cover_count','곡수',r=>r.cover_count],
  ['total_views','총 조회수',r=>fmtN(r.total_views)],
  ['avg_views','평균 조회수',r=>fmtN(Math.round(r.avg_views))],
  ['max_views','최고 조회',r=>fmtN(r.max_views)],
  ['avg_engagement_rate','참여율',r=>(r.avg_engagement_rate*100).toFixed(1)+'%'],
];
let sortKey='total_views',sortDir=-1;
function rows(){return [...DATA.members].sort((a,b)=>(a[sortKey]>b[sortKey]?1:-1)*sortDir);}
function drawTable(){
  const t=document.getElementById('tbl');
  t.innerHTML='<thead><tr>'+COLS.map(c=>
    `<th class="${c[0]===sortKey?'active':''}" onclick="setSort('${c[0]}')">${c[1]}${c[0]===sortKey?(sortDir<0?' ▾':' ▴'):''}</th>`).join('')+'</tr></thead>'+
    '<tbody>'+rows().map(r=>'<tr>'+COLS.map(c=>`<td>${c[2](r)}</td>`).join('')+'</tr>').join('')+'</tbody>';
}
function setSort(k){if(sortKey===k)sortDir*=-1;else{sortKey=k;sortDir=-1;}drawTable();}

function svgEl(t,a){const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e;}
function drawScatter(){
  const svg=document.getElementById('scatter');svg.innerHTML='';
  const W=720,H=440,ml=64,mr=40,mt=16,mb=44,list=DATA.members;
  const xs=list.map(m=>m.cover_count),ys=list.map(m=>m.avg_views/1e6);
  const xmin=0,xmax=Math.max(...xs)*1.08,ymin=0,ymax=Math.max(...ys)*1.1;
  const X=v=>ml+(v-xmin)/(xmax-xmin)*(W-ml-mr);
  const Y=v=>H-mb-(v-ymin)/(ymax-ymin)*(H-mt-mb);
  for(let i=0;i<=4;i++){const gy=mt+i/4*(H-mt-mb);
    svg.appendChild(svgEl('line',{x1:ml,x2:W-mr,y1:gy,y2:gy,class:'gridline'}));
    const t=svgEl('text',{x:ml-8,y:gy+4,'text-anchor':'end',class:'axis'});t.textContent=(ymax-(i/4)*(ymax-ymin)).toFixed(1)+'M';svg.appendChild(t);}
  for(let i=0;i<=5;i++){const gx=ml+i/5*(W-ml-mr);
    const t=svgEl('text',{x:gx,y:H-mb+18,'text-anchor':'middle',class:'axis'});t.textContent=Math.round(xmin+(i/5)*(xmax-xmin));svg.appendChild(t);}
  svg.appendChild(svgEl('text',{x:(ml+W-mr)/2,y:H-6,'text-anchor':'middle',class:'axis'})).textContent='커버곡 수';
  const maxTV=Math.max(...list.map(m=>m.total_views));
  list.forEach(m=>{
    const r=8+Math.sqrt(m.total_views/maxTV)*20,cx=X(m.cover_count),cy=Y(m.avg_views/1e6);
    const c=svgEl('circle',{cx,cy,r,fill:cssv(mcolor[m.name_en]),opacity:.82,stroke:cssv('--surface'),'stroke-width':2});
    c.addEventListener('mousemove',e=>showTip(e,`<b>${m.name_ko}</b><br>${m.cover_count}곡 · 총 ${fmt(m.total_views)}<br>평균 ${fmt(Math.round(m.avg_views))}`));
    c.addEventListener('mouseleave',hideTip);svg.appendChild(c);
    const right=cx+r+58>W-mr;
    const tx=svgEl('text',{x:right?cx-r-4:cx+r+4,y:cy+4,class:'mlabel','text-anchor':right?'end':'start'});
    tx.textContent=m.name_ko;svg.appendChild(tx);
  });
}

const tc=document.getElementById('topcovers');
tc.innerHTML='<thead><tr><th>#</th><th>멤버</th><th style="text-align:left">곡</th><th>조회수</th><th>좋아요</th></tr></thead>'+
  '<tbody>'+DATA.top_covers.map((v,i)=>`<tr><td><span class="rankn">${i+1}</span></td>`+
  `<td>${v.name_ko}</td><td class="song">${v.title}</td>`+
  `<td>${fmtN(v.views)}</td><td>${v.likes==null?'-':fmtN(v.likes)}</td></tr>`).join('')+'</tbody>';

document.getElementById('foot').innerHTML=
  `커버 식별: 채널 내 "cover / 커버 / 歌ってみた" 검색 후 제목 필터. 콜라보 곡은 소유 채널 기준 집계.<br>`+
  `데이터 출처: YouTube Data API v3 · 지표는 수집 시점 스냅샷입니다.`;

function toggleTheme(){const r=document.documentElement;
  const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  r.setAttribute('data-theme',cur==='dark'?'light':'dark');drawAll();}
function drawAll(){drawTable();drawScatter();}
drawAll();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
