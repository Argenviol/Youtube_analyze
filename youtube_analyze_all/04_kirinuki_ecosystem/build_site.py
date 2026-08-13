"""프로젝트4 · 사이트 빌드 — 키리누키 생태계 대시보드."""
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
<title>StelLive 키리누키 생태계</title>
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
body{margin:0;background:var(--bg);color:var(--text);font-family:Pretendard,"Pretendard Variable",-apple-system,BlinkMacSystemFont,"Malgun Gothic","Noto Sans KR",system-ui,sans-serif;line-height:1.5}
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
td.name{text-align:left;font-variant-numeric:normal;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
tbody tr:hover{background:color-mix(in srgb,var(--s5) 8%,transparent)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
.rankn{color:var(--muted);font-variant-numeric:tabular-nums;width:22px;display:inline-block}
.chart-svg{width:100%;height:auto;display:block;overflow:visible}
.gridline{stroke:var(--grid);stroke-width:1}
.mlabel{fill:var(--text2);font-size:12px}
.axis,.axis text{fill:var(--muted);font-size:11px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:760px){.two{grid-template-columns:1fr}}
.tip{position:fixed;pointer-events:none;background:var(--text);color:var(--bg);font-size:12px;padding:6px 9px;border-radius:8px;opacity:0;transition:opacity .1s;z-index:10;white-space:nowrap}
.foot{color:var(--muted);font-size:12px;margin-top:40px;border-top:1px solid var(--border);padding-top:16px}
.toggle{float:right;background:var(--surface);border:1px solid var(--border);color:var(--text2);border-radius:999px;padding:5px 12px;font-size:12.5px;cursor:pointer}
.specrow{display:grid;grid-template-columns:70px 1fr 40px;align-items:center;gap:10px;font-size:13px;margin-bottom:7px}
.specrow .bar{height:16px;border-radius:4px;background:var(--s3)}
.specrow .n{text-align:right;color:var(--text2);font-variant-numeric:tabular-nums}
</style>
</head>
<body>
<div class="wrap">
<button class="toggle" onclick="toggleTheme()">◐ 테마</button>
<header>
  <h1>StelLive 키리누키(2차창작) 생태계</h1>
  <p>스텔라이브 멤버들의 팬 제작 클립 채널·조회수 지도 (공식 채널 제외)</p>
  <div id="tags"></div>
</header>

<div class="kpis" id="kpis"></div>

<section>
  <h2>멤버별 팬 클립 생태계</h2>
  <p class="sub">팬채널수 = 해당 멤버 클립을 올리는 서로 다른 채널 수(= 창작 관심도). 열 클릭 시 정렬.</p>
  <div class="card" style="overflow-x:auto"><table id="mtbl"></table></div>
</section>

<section class="two">
  <div>
    <h2>클립 수 vs 총 조회수</h2>
    <p class="sub">버블=팬채널 수. 오른쪽=많이, 위쪽=많이 봄.</p>
    <div class="card"><svg id="scatter" class="chart-svg" viewBox="0 0 460 380"></svg></div>
  </div>
  <div>
    <h2>팬채널 전문성</h2>
    <p class="sub">한 채널이 다루는 멤버 수 분포. 1이면 특정 멤버 전문(오시).</p>
    <div class="card"><div id="spec"></div></div>
  </div>
</section>

<section>
  <h2>상위 키리누키 채널 TOP 20</h2>
  <div class="card" style="overflow-x:auto"><table id="ctbl"></table></div>
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
const svgEl=(t,a)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e;};

document.getElementById('tags').innerHTML =
  `<span class="tag">수집 ${DATA.meta.fetched_at.slice(0,10)}</span>`+
  `<span class="tag">클립 ${DATA.meta.n_clips}개</span>`+
  `<span class="tag">팬채널 ${DATA.meta.n_clip_channels}개</span>`+
  `<span class="tag">YouTube Data API</span>`;

const totClips=DATA.members.reduce((a,m)=>a+m.clip_count,0);
const totViews=DATA.members.reduce((a,m)=>a+m.total_clip_views,0);
const hot=[...DATA.members].sort((a,b)=>b.total_clip_views-a.total_clip_views)[0];
const mostCh=[...DATA.members].sort((a,b)=>b.fan_channels-a.fan_channels)[0];
document.getElementById('kpis').innerHTML=[
  ['총 클립(표본)',fmtN(totClips)+'개','공식 제외 팬 제작'],
  ['합산 조회수',fmt(totViews),'표본 클립 총합'],
  ['클립 조회 1위',hot.name_ko,fmt(hot.total_clip_views)],
  ['최다 창작 관심',mostCh.name_ko,mostCh.fan_channels+'개 팬채널'],
].map(k=>`<div class="kpi"><div class="v">${k[1]}</div><div class="l">${k[0]}</div><div class="s">${k[2]}</div></div>`).join('');

const MCOLS=[
  ['name_ko','멤버',r=>`<i class="dot" style="background:${cssv(mcolor[r.name_en])}"></i>${r.name_ko}`],
  ['clip_count','클립수',r=>r.clip_count],
  ['total_clip_views','총 조회수',r=>fmtN(r.total_clip_views)],
  ['avg_clip_views','평균 조회',r=>fmtN(Math.round(r.avg_clip_views))],
  ['fan_channels','팬채널수',r=>r.fan_channels],
  ['top_channel','최다 클립 채널',r=>`<span style="color:var(--text2)">${r.top_channel}</span>`],
];
let sk='total_clip_views',sd=-1;
const mrows=()=>[...DATA.members].sort((a,b)=>(a[sk]>b[sk]?1:-1)*sd);
function drawM(){const t=document.getElementById('mtbl');
  t.innerHTML='<thead><tr>'+MCOLS.map(c=>`<th class="${c[0]===sk?'active':''}" onclick="setSk('${c[0]}')">${c[1]}${c[0]===sk?(sd<0?' ▾':' ▴'):''}</th>`).join('')+'</tr></thead>'+
  '<tbody>'+mrows().map(r=>'<tr>'+MCOLS.map(c=>`<td${c[0]==='top_channel'?' class="name"':''}>${c[2](r)}</td>`).join('')+'</tr>').join('')+'</tbody>';}
function setSk(k){if(sk===k)sd*=-1;else{sk=k;sd=-1;}drawM();}

// channel table
const ct=document.getElementById('ctbl');
ct.innerHTML='<thead><tr><th>#</th><th>채널</th><th>구독자</th><th>클립수</th><th>총 조회수</th><th>주력멤버</th><th>다루는멤버</th></tr></thead>'+
  '<tbody>'+DATA.channels.map((c,i)=>`<tr><td><span class="rankn">${i+1}</span></td>`+
  `<td class="name">${c.clip_channel_title}</td><td>${c.subs==null?'-':fmtN(c.subs)}</td>`+
  `<td>${c.clip_count}</td><td>${fmtN(c.total_views)}</td><td>${c.primary_member}</td><td>${c.members_covered}명</td></tr>`).join('')+'</tbody>';

// specialization
const maxSpec=Math.max(...DATA.specialization.map(s=>s.channels));
document.getElementById('spec').innerHTML=DATA.specialization.map(s=>
  `<div class="specrow"><span>${s.members}명 다룸</span>`+
  `<span class="bar" style="width:${(s.channels/maxSpec*100).toFixed(1)}%"></span>`+
  `<span class="n">${s.channels}</span></div>`).join('');

function drawScatter(){
  const svg=document.getElementById('scatter');svg.innerHTML='';
  const W=460,H=380,ml=44,mr=30,mt=14,mb=40,list=DATA.members;
  const xs=list.map(m=>m.clip_count),ys=list.map(m=>m.total_clip_views/1e6);
  const xmin=0,xmax=Math.max(...xs)*1.08,ymin=0,ymax=Math.max(...ys)*1.1;
  const X=v=>ml+(v-xmin)/(xmax-xmin)*(W-ml-mr),Y=v=>H-mb-(v-ymin)/(ymax-ymin)*(H-mt-mb);
  for(let i=0;i<=4;i++){const gy=mt+i/4*(H-mt-mb);svg.appendChild(svgEl('line',{x1:ml,x2:W-mr,y1:gy,y2:gy,class:'gridline'}));
    const t=svgEl('text',{x:ml-8,y:gy+4,'text-anchor':'end',class:'axis'});t.textContent=(ymax-(i/4)*(ymax-ymin)).toFixed(1)+'M';svg.appendChild(t);}
  for(let i=0;i<=4;i++){const gx=ml+i/4*(W-ml-mr);const t=svgEl('text',{x:gx,y:H-mb+18,'text-anchor':'middle',class:'axis'});t.textContent=Math.round(xmin+(i/4)*(xmax-xmin));svg.appendChild(t);}
  svg.appendChild(svgEl('text',{x:(ml+W-mr)/2,y:H-4,'text-anchor':'middle',class:'axis'})).textContent='클립 수';
  list.forEach(m=>{
    const r=7+Math.sqrt(m.fan_channels)*3.4,cx=X(m.clip_count),cy=Y(m.total_clip_views/1e6);
    const c=svgEl('circle',{cx,cy,r,fill:cssv(mcolor[m.name_en]),opacity:.8,stroke:cssv('--surface'),'stroke-width':2});
    c.addEventListener('mousemove',e=>showTip(e,`<b>${m.name_ko}</b><br>${m.clip_count}클립 · ${fmt(m.total_clip_views)}<br>팬채널 ${m.fan_channels}개`));
    c.addEventListener('mouseleave',hideTip);svg.appendChild(c);
    const right=cx+r+50>W-mr;
    const tx=svgEl('text',{x:right?cx-r-4:cx+r+4,y:cy+4,class:'mlabel','text-anchor':right?'end':'start'});tx.textContent=m.name_ko;svg.appendChild(tx);
  });
}

document.getElementById('foot').innerHTML=
  `방법론: 멤버명+키리누키/클립/切り抜き 검색 표본 → 공식 채널 제외 → 제목·채널명 클립 토큰 필터.<br>`+
  `유튜브 검색 상위 표본이라 전수가 아닌 대표 표본입니다 · 지표는 수집 시점 스냅샷.`;

function toggleTheme(){const r=document.documentElement;
  const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  r.setAttribute('data-theme',cur==='dark'?'light':'dark');drawAll();}
function drawAll(){drawM();drawScatter();}
drawAll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
