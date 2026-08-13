"""프로젝트7 · 사이트 빌드 — 시장 분석 대시보드."""
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
<title>버추얼 크리에이터 시장 분석</title>
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
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:26px 0}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 18px}
.kpi .v{font-size:23px;font-weight:700;letter-spacing:-.5px}
.kpi .l{font-size:12.5px;color:var(--text2);margin-top:3px}
.kpi .s{font-size:11.5px;color:var(--muted);margin-top:2px}
section{margin:34px 0}
h2{font-size:18px;margin:0 0 4px}
.sub{color:var(--text2);font-size:13.5px;margin:0 0 16px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px}
.chart-svg{width:100%;height:auto;display:block;overflow:visible}
.gridline{stroke:var(--grid);stroke-width:1}
.axis,.axis text{fill:var(--muted);font-size:11px}
.mlabel{fill:var(--text2);font-size:12px}
.timeline{position:relative;padding:50px 10px 60px}
.tl-line{position:absolute;left:0;right:0;top:50%;height:2px;background:var(--grid)}
.tl-items{display:flex;justify-content:space-between;position:relative}
.tl-item{flex:1;text-align:center;position:relative;padding:0 4px}
.tl-dot{width:14px;height:14px;border-radius:50%;margin:0 auto;position:relative;z-index:2;border:3px solid var(--surface)}
.tl-date{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums;margin-top:6px}
.tl-event{font-size:12px;color:var(--text);margin-top:2px;line-height:1.35}
.tl-item.up .tl-content{position:absolute;bottom:calc(50% + 16px);left:50%;transform:translateX(-50%);width:150px}
.tl-item.down .tl-content{position:absolute;top:calc(50% + 16px);left:50%;transform:translateX(-50%);width:150px}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:var(--text2);margin-top:16px;justify-content:center}
.legend span{display:flex;align-items:center}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--border)}
th{color:var(--text2);font-weight:600}
a{color:var(--s1)}
.foot{color:var(--muted);font-size:12px;margin-top:40px;border-top:1px solid var(--border);padding-top:16px}
.toggle{float:right;background:var(--surface);border:1px solid var(--border);color:var(--text2);border-radius:999px;padding:5px 12px;font-size:12.5px;cursor:pointer}
.note{background:color-mix(in srgb,var(--s4) 12%,transparent);border:1px solid var(--border);border-radius:12px;padding:14px 16px;font-size:13px;color:var(--text2);margin-top:16px}
</style>
</head>
<body>
<div class="wrap">
<button class="toggle" onclick="toggleTheme()">◐ 테마</button>
<header>
  <h1>버추얼 크리에이터 시장 분석</h1>
  <p>글로벌 VTuber 시장 · 한국 스트리밍 생태계(치지직) · StelLive의 시장 포지션 — Claude 웹서치 기반</p>
  <div id="tags"></div>
</header>

<div class="kpis" id="kpis"></div>

<section>
  <h2>글로벌 VTuber 시장 규모 전망</h2>
  <p class="sub">리서치사별 추정치 비교 — 방법론 차이로 편차가 있어 범위로 해석 권장.</p>
  <div class="card"><svg id="market" class="chart-svg" viewBox="0 0 640 430"></svg></div>
</section>

<section>
  <h2>StelLive 성장 타임라인</h2>
  <p class="sub">창립부터 브레이브 그룹 인수·첫 콘서트까지.</p>
  <div class="card">
    <div class="timeline" id="timeline"></div>
    <div class="legend" id="tllegend"></div>
  </div>
</section>

<section>
  <h2>시장 구조 &amp; 한국 스트리밍 현황</h2>
  <div class="card" id="factstable"></div>
</section>

<div class="note">
  시장 규모 추정치는 리서치사별 방법론 차이로 편차가 크며, 절대값보다 <b>성장 추세와 구조적 신호</b>로
  해석하는 것을 권장합니다. 모든 수치는 출처 링크를 포함합니다.
</div>

<div class="foot" id="foot"></div>
</div>

<script>
const DATA = /*__DATA__*/null;
const cssv=v=>getComputedStyle(document.body).getPropertyValue(v).trim();
const svgEl=(t,a)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e;};

document.getElementById('tags').innerHTML =
  `<span class="tag">시장통계: Claude 웹서치</span>`+
  `<span class="tag">자체데이터: 프로젝트1·6</span>`+
  `<span class="tag">${DATA.meta.n_facts}개 지표</span>`;

const f = m => DATA.facts.find(x=>x.metric===m);
const marketSize2026 = f('글로벌 VTuber 시장 규모(2026)');
const chzzkMau = f('치지직 월간활성이용자(MAU)');
const apac = f('아시아태평양 지역 점유율');
const krRevenue = f('한국 크리에이터 산업 매출액');
document.getElementById('kpis').innerHTML=[
  ['글로벌 시장(2026)','$'+(marketSize2026.value/1000).toFixed(1)+'B','VTuber 시장 규모 추정'],
  ['치지직 MAU',Math.round(chzzkMau.value/10000)+'만명','2026.7 · YoY +17%'],
  ['APAC 점유율',apac.value.toFixed(0)+'%','글로벌 VTuber 시장 지역 비중'],
  ['한국 크리에이터 매출',(krRevenue.value/1e6).toFixed(2)+'조원','2025 KMCC 산업조사'],
].map(k=>`<div class="kpi"><div class="v">${k[1]}</div><div class="l">${k[0]}</div><div class="s">${k[2]}</div></div>`).join('');

function drawMarket(){
  const svg=document.getElementById('market');svg.innerHTML='';
  const W=640,H=400,ml=54,mr=30,mt=20,mb=40,legendY=430;
  const ms=DATA.facts.filter(f=>f.category==='market_size');
  const sources=[...new Set(ms.map(f=>f.source_name))];
  const years=[...new Set(ms.map(f=>f.year))].sort((a,b)=>a-b);
  const xmin=Math.min(...years),xmax=Math.max(...years);
  const ymax=Math.max(...ms.map(f=>f.value))/1000*1.15;
  const X=v=>ml+(v-xmin)/(xmax-xmin)*(W-ml-mr),Y=v=>H-mb-(v/ymax)*(H-mt-mb);
  for(let i=0;i<=4;i++){const gy=mt+i/4*(H-mt-mb);svg.appendChild(svgEl('line',{x1:ml,x2:W-mr,y1:gy,y2:gy,class:'gridline'}));
    const t=svgEl('text',{x:ml-8,y:gy+4,'text-anchor':'end',class:'axis'});t.textContent='$'+(ymax-(i/4)*ymax).toFixed(1)+'B';svg.appendChild(t);}
  years.forEach(y=>{const gx=X(y);const t=svgEl('text',{x:gx,y:H-mb+18,'text-anchor':'middle',class:'axis'});t.textContent=y;svg.appendChild(t);});
  const SER=['--s1','--s2'];
  sources.forEach((src,i)=>{
    const d=ms.filter(f=>f.source_name===src).sort((a,b)=>a.year-b.year);
    const pts=d.map(f=>`${X(f.year)},${Y(f.value/1000)}`).join(' ');
    svg.appendChild(svgEl('polyline',{points:pts,fill:'none',stroke:cssv(SER[i]),'stroke-width':2.5}));
    d.forEach((f,j)=>{
      svg.appendChild(svgEl('circle',{cx:X(f.year),cy:Y(f.value/1000),r:6,fill:cssv(SER[i]),stroke:cssv('--surface'),'stroke-width':2}));
      // 시작점(첫 연도)은 두 시리즈가 겹치므로 세로로 살짝 벌려서 라벨 배치
      const dy = (j===0) ? (i===0? 16 : -8) : -10;
      const t=svgEl('text',{x:X(f.year)+8,y:Y(f.value/1000)+dy,class:'mlabel'});t.textContent='$'+(f.value/1000).toFixed(1)+'B';svg.appendChild(t);
    });
  });
  // 범례: 차트 아래
  const ly=legendY-6;
  sources.forEach((src,i)=>{
    const lx=ml + i*260;
    svg.appendChild(svgEl('circle',{cx:lx,cy:ly,r:5,fill:cssv(SER[i])}));
    const lt=svgEl('text',{x:lx+10,y:ly+4,class:'mlabel'});lt.textContent=src;svg.appendChild(lt);
  });
}

const CAT_LABEL={origin:'창립',launch:'런칭',investment:'투자',milestone:'성과'};
const CAT_COLOR={origin:'--muted',launch:'--s1',investment:'--s2',milestone:'--s3'};
function drawTimeline(){
  const el=document.getElementById('timeline');
  const items=DATA.milestones;
  el.innerHTML='<div class="tl-line"></div><div class="tl-items">'+
    items.map((m,i)=>{
      const dir=i%2===0?'up':'down';
      return `<div class="tl-item ${dir}">
        <div class="tl-content">
          ${dir==='up'?`<div class="tl-event">${m.event}</div><div class="tl-date">${m.date}</div>`:''}
        </div>
        <div class="tl-dot" style="background:${cssv(CAT_COLOR[m.category])}"></div>
        <div class="tl-content">
          ${dir==='down'?`<div class="tl-date">${m.date}</div><div class="tl-event">${m.event}</div>`:''}
        </div>
      </div>`;
    }).join('')+'</div>';
  document.getElementById('tllegend').innerHTML = Object.entries(CAT_LABEL).map(([k,v])=>
    `<span><i class="dot" style="background:${cssv(CAT_COLOR[k])}"></i>${v}</span>`).join('');
}

function drawFacts(){
  const rows = DATA.facts.filter(f=>['revenue_share','region_share','platform_kpi','industry_kr'].includes(f.category));
  const fmtVal=f=>{
    if(f.unit==='pct') return f.value.toFixed(1)+'%';
    if(f.unit==='users') return (f.value/1e6).toFixed(2)+'M';
    if(f.unit==='minutes') return (f.value/1e8).toFixed(1)+'억분';
    if(f.unit==='million_krw') return (f.value/1e6).toFixed(2)+'조원';
    if(f.unit==='count') return f.value.toLocaleString('ko-KR')+'개';
    return f.value;
  };
  document.getElementById('factstable').innerHTML = '<table><thead><tr><th>지표</th><th>값</th><th>출처</th><th>비고</th></tr></thead><tbody>'+
    rows.map(f=>`<tr><td>${f.metric}</td><td><b>${fmtVal(f)}</b></td>`+
    `<td><a href="${f.source_url}" target="_blank" rel="noopener">${f.source_name}</a></td>`+
    `<td style="color:var(--text2)">${f.note||''}</td></tr>`).join('')+'</tbody></table>';
}

document.getElementById('foot').innerHTML=
  `시장 통계는 Claude가 웹서치로 수집한 공개 리서치·보도자료 기반이며, 리서치사별 추정 방법론 차이로 편차가 있습니다.<br>`+
  `StelLive 자체 포지션 데이터는 프로젝트1(멤버별 채널 성과)·프로젝트6(경쟁사 비교)의 실측 데이터를 재사용했습니다.`;

function toggleTheme(){const r=document.documentElement;
  const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  r.setAttribute('data-theme',cur==='dark'?'light':'dark');drawAll();}
function drawAll(){drawMarket();drawTimeline();drawFacts();}
drawAll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
