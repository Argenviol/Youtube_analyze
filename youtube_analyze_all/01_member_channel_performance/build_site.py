"""
프로젝트1 · 사이트 빌드
site/data.json 을 인라인 임베드한 자체완결 HTML 대시보드(site/index.html) 생성.
외부 리소스/네트워크 요청 없음 → 파일 하나로 열람 가능, Artifact 게시 가능.

  python 01_member_channel_performance/build_site.py
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

    # Artifact 게시용 fragment (플랫폼이 head/body를 감싸므로 wrapper 제거)
    style = html[html.index("<style>"):html.index("</style>") + len("</style>")]
    body_inner = html[html.index("<body>") + len("<body>"):html.index("</body>")]
    (SITE / "artifact.html").write_text(style + "\n" + body_inner, encoding="utf-8")
    print(f"사이트 -> {SITE / 'index.html'}  (+ artifact.html)")


TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StelLive 멤버 채널 성과 분석</title>
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
tbody tr:hover{background:color-mix(in srgb,var(--s1) 8%,transparent)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
.unit-chip{font-size:11px;color:var(--text2);border:1px solid var(--border);border-radius:6px;padding:1px 7px}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.filters button{background:var(--surface);border:1px solid var(--border);color:var(--text2);
  border-radius:999px;padding:5px 14px;font-size:13px;cursor:pointer}
.filters button.on{background:var(--text);color:var(--bg);border-color:var(--text)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:720px){.two{grid-template-columns:1fr}}
.tip{position:fixed;pointer-events:none;background:var(--text);color:var(--bg);font-size:12px;
  padding:6px 9px;border-radius:8px;opacity:0;transition:opacity .1s;z-index:10;white-space:nowrap}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:var(--text2);margin-top:10px}
.legend span{display:flex;align-items:center}
.foot{color:var(--muted);font-size:12px;margin-top:40px;border-top:1px solid var(--border);padding-top:16px}
.toggle{float:right;background:var(--surface);border:1px solid var(--border);color:var(--text2);
  border-radius:999px;padding:5px 12px;font-size:12.5px;cursor:pointer}
a{color:var(--s1)}
</style>
</head>
<body>
<div class="wrap">
<button class="toggle" onclick="toggleTheme()">◐ 테마</button>
<header>
  <h1>StelLive 멤버별 유튜브 채널 성과 분석</h1>
  <p>스텔라이브 탤런트 10명의 채널 지표 · 최근 영상 성과 비교</p>
  <div id="tags"></div>
</header>

<div class="kpis" id="kpis"></div>

<section>
  <h2>멤버 랭킹</h2>
  <p class="sub">열 제목을 클릭하면 정렬됩니다. 도달 효율 = 최근 평균 조회수 ÷ 구독자.</p>
  <div class="filters" id="filters"></div>
  <div class="card" style="overflow-x:auto"><table id="tbl"></table></div>
  <div class="legend" id="unitlegend"></div>
</section>

<section>
  <h2>구독자 vs 최근 평균 조회수</h2>
  <p class="sub">버블 크기 = 참여율. 점선은 회귀선(추세). 오른쪽 위일수록 규모·조회수 모두 높음.</p>
  <div class="card"><svg id="scatter" class="chart-svg" viewBox="0 0 720 440"></svg></div>
</section>

<section class="two">
  <div>
    <h2>도달 효율</h2>
    <p class="sub">구독자 대비 실제 조회수 도달률(%). 팬 참여도가 높을수록 큼.</p>
    <div class="card"><svg id="reach" class="chart-svg" viewBox="0 0 480 460"></svg></div>
  </div>
  <div>
    <h2>참여율</h2>
    <p class="sub">(좋아요+댓글) ÷ 조회수, 최근 영상 평균 %.</p>
    <div class="card"><svg id="engage" class="chart-svg" viewBox="0 0 480 460"></svg></div>
  </div>
</section>

<section>
  <h2>최고 조회수 영상 TOP 15</h2>
  <div class="card" style="overflow-x:auto"><table id="topvids"></table></div>
</section>

<div class="foot" id="foot"></div>
</div>
<div class="tip" id="tip"></div>

<script>
const DATA = /*__DATA__*/null;
const SERIES=['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'];
const cssv=v=>getComputedStyle(document.body).getPropertyValue(v).trim();
const fmt=n=>n>=1e6?(n/1e6).toFixed(2)+'M':n>=1e3?(n/1e3).toFixed(0)+'K':(''+n);
const fmtN=n=>Number(n).toLocaleString('ko-KR');
const UNITCOLORS={EVERYS:'--s1',UNIVERSE:'--s2',CLICHE:'--s3',STELLIVE:'--muted'};
// 멤버 고정색
const mcolor={}; DATA.members.forEach((m,i)=>mcolor[m.name_en]=SERIES[i%SERIES.length]);
const tip=document.getElementById('tip');
function showTip(e,html){tip.innerHTML=html;tip.style.opacity=1;
  tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY+12)+'px';}
function hideTip(){tip.style.opacity=0;}

// tags
document.getElementById('tags').innerHTML =
  `<span class="tag">수집 ${DATA.meta.fetched_at.slice(0,10)}</span>`+
  `<span class="tag">채널 ${DATA.meta.n_channels}개</span>`+
  `<span class="tag">영상 ${DATA.meta.n_videos}개</span>`+
  `<span class="tag">YouTube Data API v3</span>`;

// KPIs
const talents=DATA.members.filter(m=>m.role==='talent');
const sumSubs=talents.reduce((a,m)=>a+m.subscribers,0);
const avgViews=Math.round(talents.reduce((a,m)=>a+m.recent_avg_views,0)/talents.length);
const avgEng=(talents.reduce((a,m)=>a+m.recent_avg_engagement_rate,0)/talents.length*100).toFixed(1);
const topReach=[...talents].sort((a,b)=>b.reach_ratio-a.reach_ratio)[0];
const kpis=[
  ['탤런트 합산 구독자',fmt(sumSubs),'탤런트 10명'],
  ['평균 조회수(최근)',fmtN(avgViews),'채널당 최근 50영상'],
  ['평균 참여율',avgEng+'%','좋아요+댓글/조회수'],
  ['도달 효율 1위',topReach.name_ko,(topReach.reach_ratio*100).toFixed(0)+'% · 조회수/구독자'],
];
document.getElementById('kpis').innerHTML=kpis.map(k=>
  `<div class="kpi"><div class="v">${k[1]}</div><div class="l">${k[0]}</div><div class="s">${k[2]}</div></div>`).join('');

// unit legend
document.getElementById('unitlegend').innerHTML=Object.entries(UNITCOLORS).map(([u,c])=>
  `<span><i class="dot" style="background:${cssv(c)}"></i>${u}</span>`).join('');

// table
const COLS=[
  ['name_ko','멤버',r=>`<i class="dot" style="background:${cssv(mcolor[r.name_en])}"></i>${r.name_ko} `+
      `<span class="unit-chip">${r.unit}</span>`],
  ['subscribers','구독자',r=>fmtN(r.subscribers)],
  ['recent_avg_views','평균조회수',r=>fmtN(Math.round(r.recent_avg_views))],
  ['uploads_per_week','주간업로드',r=>r.uploads_per_week.toFixed(1)],
  ['recent_avg_engagement_rate','참여율',r=>(r.recent_avg_engagement_rate*100).toFixed(1)+'%'],
  ['reach_ratio','도달효율',r=>(r.reach_ratio*100).toFixed(0)+'%'],
  ['shorts_share','쇼츠',r=>(r.shorts_share*100).toFixed(0)+'%'],
];
let sortKey='subscribers',sortDir=-1,unitFilter='ALL';
function rows(){let r=DATA.members.filter(m=>unitFilter==='ALL'||m.unit===unitFilter);
  return r.sort((a,b)=>(a[sortKey]>b[sortKey]?1:-1)*sortDir);}
function drawTable(){
  const t=document.getElementById('tbl');
  t.innerHTML='<thead><tr>'+COLS.map(c=>
    `<th class="${c[0]===sortKey?'active':''}" onclick="setSort('${c[0]}')">${c[1]}${c[0]===sortKey?(sortDir<0?' ▾':' ▴'):''}</th>`).join('')+'</tr></thead>'+
    '<tbody>'+rows().map(r=>'<tr>'+COLS.map(c=>`<td>${c[2](r)}</td>`).join('')+'</tr>').join('')+'</tbody>';
}
function setSort(k){if(sortKey===k)sortDir*=-1;else{sortKey=k;sortDir=-1;}drawTable();}
// filters
const units=['ALL',...new Set(DATA.members.map(m=>m.unit))];
document.getElementById('filters').innerHTML=units.map(u=>
  `<button class="${u==='ALL'?'on':''}" data-u="${u}" onclick="setFilter('${u}')">${u==='ALL'?'전체':u}</button>`).join('');
function setFilter(u){unitFilter=u;
  document.querySelectorAll('#filters button').forEach(b=>b.classList.toggle('on',b.dataset.u===u));
  drawTable();drawScatter();}

// ---- SVG helpers ----
function svgEl(tag,attrs){const e=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for(const k in attrs)e.setAttribute(k,attrs[k]);return e;}

function hbarChart(id,list,valfn,labelfn,colorfn){
  const svg=document.getElementById(id);svg.innerHTML='';
  const W=480,H=460,ml=96,mr=54,mt=10,mb=24;
  const data=[...list].sort((a,b)=>valfn(a)-valfn(b));
  const max=Math.max(...data.map(valfn))*1.02;
  const bh=(H-mt-mb)/data.length;
  const x=v=>ml+(v/max)*(W-ml-mr);
  // gridlines
  for(let i=0;i<=4;i++){const gx=ml+i/4*(W-ml-mr);
    svg.appendChild(svgEl('line',{x1:gx,x2:gx,y1:mt,y2:H-mb,class:'gridline'}));}
  data.forEach((r,i)=>{
    const y=mt+i*bh, val=valfn(r), col=cssv(colorfn(r));
    const bar=svgEl('rect',{x:ml,y:y+bh*0.18,width:Math.max(1,x(val)-ml),height:bh*0.64,
      rx:4,fill:col});
    bar.addEventListener('mousemove',e=>showTip(e,`<b>${r.name_ko}</b><br>${labelfn(r)}`));
    bar.addEventListener('mouseleave',hideTip);
    svg.appendChild(bar);
    const t1=svgEl('text',{x:ml-8,y:y+bh/2+4,'text-anchor':'end',class:'mlabel'});t1.textContent=r.name_ko;
    svg.appendChild(t1);
    const t2=svgEl('text',{x:x(val)+6,y:y+bh/2+4,class:'blabel'});t2.textContent=labelfn(r);
    svg.appendChild(t2);
  });
}
function drawReach(){hbarChart('reach',talents,m=>m.reach_ratio,
  m=>(m.reach_ratio*100).toFixed(0)+'%',m=>mcolor[m.name_en]);}
function drawEngage(){hbarChart('engage',talents,m=>m.recent_avg_engagement_rate,
  m=>(m.recent_avg_engagement_rate*100).toFixed(1)+'%',m=>mcolor[m.name_en]);}

function drawScatter(){
  const svg=document.getElementById('scatter');svg.innerHTML='';
  const W=720,H=440,ml=64,mr=34,mt=16,mb=44;
  const list=talents;
  const xs=list.map(m=>m.subscribers),ys=list.map(m=>m.recent_avg_views);
  const xmin=Math.min(...xs)*0.9,xmax=Math.max(...xs)*1.05;
  const ymin=Math.min(...ys)*0.8,ymax=Math.max(...ys)*1.08;
  const X=v=>ml+(v-xmin)/(xmax-xmin)*(W-ml-mr);
  const Y=v=>H-mb-(v-ymin)/(ymax-ymin)*(H-mt-mb);
  // grid + axes
  for(let i=0;i<=4;i++){const gy=mt+i/4*(H-mt-mb);
    svg.appendChild(svgEl('line',{x1:ml,x2:W-mr,y1:gy,y2:gy,class:'gridline'}));
    const val=ymax-(i/4)*(ymax-ymin);
    const tl=svgEl('text',{x:ml-8,y:gy+4,'text-anchor':'end',class:'axis'});tl.textContent=fmt(Math.round(val));
    svg.appendChild(tl);}
  for(let i=0;i<=4;i++){const gx=ml+i/4*(W-ml-mr);const val=xmin+(i/4)*(xmax-xmin);
    const tl=svgEl('text',{x:gx,y:H-mb+18,'text-anchor':'middle',class:'axis'});tl.textContent=fmt(Math.round(val));
    svg.appendChild(tl);}
  svg.appendChild(svgEl('text',{x:(ml+W-mr)/2,y:H-6,'text-anchor':'middle',class:'axis'})).textContent='구독자';
  // regression line
  const n=list.length,sx=xs.reduce((a,b)=>a+b),sy=ys.reduce((a,b)=>a+b);
  const sxy=list.reduce((a,m)=>a+m.subscribers*m.recent_avg_views,0);
  const sxx=xs.reduce((a,b)=>a+b*b,0);
  const slope=(n*sxy-sx*sy)/(n*sxx-sx*sx),inter=(sy-slope*sx)/n;
  svg.appendChild(svgEl('line',{x1:X(xmin),y1:Y(slope*xmin+inter),x2:X(xmax),y2:Y(slope*xmax+inter),
    stroke:cssv('--muted'),'stroke-width':1.2,'stroke-dasharray':'5 4'}));
  // points
  const highlight=unitFilter==='ALL'?null:unitFilter;
  list.forEach(m=>{
    const r=Math.max(7,Math.min(22,5+Math.sqrt(m.recent_avg_engagement_rate)*52));
    const faded=highlight&&m.unit!==highlight;
    const cx=X(m.subscribers),cy=Y(m.recent_avg_views);
    const c=svgEl('circle',{cx:cx,cy:cy,r:r,
      fill:cssv(mcolor[m.name_en]),opacity:faded?0.18:0.82,stroke:cssv('--surface'),'stroke-width':2});
    c.addEventListener('mousemove',e=>showTip(e,
      `<b>${m.name_ko}</b><br>구독 ${fmtN(m.subscribers)}<br>평균조회 ${fmtN(Math.round(m.recent_avg_views))}<br>참여율 ${(m.recent_avg_engagement_rate*100).toFixed(1)}%`));
    c.addEventListener('mouseleave',hideTip);
    svg.appendChild(c);
    if(!faded){
      const rightEdge=cx+r+64>W-mr;   // 오른쪽 끝이면 라벨을 왼쪽으로
      const tx=svgEl('text',{x:rightEdge?cx-r-4:cx+r+4,y:cy+4,class:'mlabel',
        'text-anchor':rightEdge?'end':'start'});
      tx.textContent=m.name_ko;svg.appendChild(tx);}
  });
}

// top videos
const tv=document.getElementById('topvids');
tv.innerHTML='<thead><tr><th>멤버</th><th style="text-align:left">영상</th><th>조회수</th><th>좋아요</th><th>댓글</th></tr></thead>'+
  '<tbody>'+DATA.top_videos.map(v=>`<tr><td>${v.name_ko}</td>`+
  `<td style="text-align:left;max-width:420px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${v.title}</td>`+
  `<td>${fmtN(v.views)}</td><td>${v.likes==null?'-':fmtN(v.likes)}</td><td>${v.comments==null?'-':fmtN(v.comments)}</td></tr>`).join('')+'</tbody>';

// foot
const c=DATA.correlations;
document.getElementById('foot').innerHTML=
  `상관관계(탤런트): 구독자↔평균조회수 r=${c.subs_vs_avgviews} · 업로드빈도↔구독자 r=${c.cadence_vs_subs} · `+
  `도달효율↔구독자 r=${c.reach_vs_subs}<br>데이터 출처: YouTube Data API v3 · 지표는 수집 시점 스냅샷입니다.`;

function toggleTheme(){const r=document.documentElement;
  const cur=r.getAttribute('data-theme')|| (matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  r.setAttribute('data-theme',cur==='dark'?'light':'dark');
  drawAll();}
function drawAll(){drawTable();drawScatter();drawReach();drawEngage();}
drawAll();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
