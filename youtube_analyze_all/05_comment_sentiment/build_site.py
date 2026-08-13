"""프로젝트5 · 사이트 빌드 — 댓글 감성 대시보드."""
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
<title>StelLive 댓글 여론 분석</title>
<style>
:root{
  --bg:#F7F7F8; --surface:#ffffff; --text:#171719; --text2:#37383C; --muted:#70737C;
  --grid:#E1E2E4; --border:rgba(112,115,124,.22);
  --pos:#00BF40; --neu:#70737C; --neg:#FF4242;
  --s1:#005EEB; --s2:#F55A00; --s3:#009632; --s4:#D17600; --s5:#E846CD; --s6:#429E00; --s7:#5B37ED; --s8:#E52222;
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --bg:#0F0F10; --surface:#212225; --text:#F7F7F8; --text2:#C2C4C8; --muted:#70737C;
  --grid:#37383C; --border:rgba(112,115,124,.32);
  --pos:#1ED45A; --neu:#989BA2; --neg:#FF6363;
  --s1:#3385FF; --s2:#FF7B2E; --s3:#1ED45A; --s4:#FF9200; --s5:#FA73E3; --s6:#429E00; --s7:#7D5EF7; --s8:#FF6363;
}}
:root[data-theme=dark]{
  --bg:#0F0F10; --surface:#212225; --text:#F7F7F8; --text2:#C2C4C8; --muted:#70737C;
  --grid:#37383C; --border:rgba(112,115,124,.32);
  --pos:#1ED45A; --neu:#989BA2; --neg:#FF6363;
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
tbody tr:hover{background:color-mix(in srgb,var(--pos) 8%,transparent)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
.bar-outer{background:var(--grid);border-radius:5px;overflow:hidden;height:18px;display:flex}
.bar-seg{height:100%}
.senti-row{display:grid;grid-template-columns:100px 1fr 120px;align-items:center;gap:10px;font-size:13px;margin-bottom:9px}
.senti-nums{font-size:11.5px;color:var(--text2);text-align:right;font-variant-numeric:tabular-nums}
.comment-card{border:1px solid var(--border);border-radius:12px;padding:12px 14px;margin-bottom:10px;background:var(--bg)}
.comment-card .meta{font-size:12px;color:var(--muted);display:flex;justify-content:space-between;margin-bottom:5px}
.pill{font-size:10.5px;border-radius:999px;padding:1px 8px;font-weight:600}
.pill.positive{background:color-mix(in srgb,var(--pos) 20%,transparent);color:var(--pos)}
.pill.neutral{background:color-mix(in srgb,var(--neu) 20%,transparent);color:var(--text2)}
.pill.negative{background:color-mix(in srgb,var(--neg) 20%,transparent);color:var(--neg)}
.chart-svg{width:100%;height:auto;display:block;overflow:visible}
.gridline{stroke:var(--grid);stroke-width:1}
.axis,.axis text{fill:var(--muted);font-size:11px}
.foot{color:var(--muted);font-size:12px;margin-top:40px;border-top:1px solid var(--border);padding-top:16px}
.toggle{float:right;background:var(--surface);border:1px solid var(--border);color:var(--text2);border-radius:999px;padding:5px 12px;font-size:12.5px;cursor:pointer}
.two{display:grid;grid-template-columns:1.1fr 0.9fr;gap:20px}
@media(max-width:760px){.two{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<button class="toggle" onclick="toggleTheme()">◐ 테마</button>
<header>
  <h1>StelLive 댓글 여론/감성 분석</h1>
  <p>인기 영상 상위 댓글 표본을 Claude가 직접 읽고 감성·토픽으로 분류했습니다</p>
  <div id="tags"></div>
</header>

<div class="kpis" id="kpis"></div>

<section>
  <h2>멤버별 감성 구성</h2>
  <p class="sub">긍정(초록)·중립(회색)·부정(빨강) 비율. 표본은 각 멤버 좋아요 상위 30개 댓글.</p>
  <div class="card" id="sentibars"></div>
</section>

<section class="two">
  <div>
    <h2>전체 토픽 분포</h2>
    <p class="sub">댓글이 가장 많이 언급하는 주제.</p>
    <div class="card"><svg id="topics" class="chart-svg" viewBox="0 0 460 320"></svg></div>
  </div>
  <div>
    <h2>가장 좋아요 많은 댓글</h2>
    <p class="sub">상위 8개, 감성·토픽 라벨 포함.</p>
    <div class="card" id="topcomments"></div>
  </div>
</section>

<section>
  <h2>멤버별 상세</h2>
  <div class="card" style="overflow-x:auto"><table id="tbl"></table></div>
</section>

<div class="foot" id="foot"></div>
</div>

<script>
const DATA = /*__DATA__*/null;
const cssv=v=>getComputedStyle(document.body).getPropertyValue(v).trim();
const fmtN=n=>Number(n).toLocaleString('ko-KR');
const svgEl=(t,a)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e;};

document.getElementById('tags').innerHTML =
  `<span class="tag">수집 ${DATA.meta.fetched_at.slice(0,10)}</span>`+
  `<span class="tag">원천 댓글 ${DATA.meta.n_comments}개</span>`+
  `<span class="tag">라벨링 표본 330개</span>`+
  `<span class="tag">분류: Claude</span>`;

const os=DATA.overall_sentiment, totS=os.positive+os.neutral+os.negative;
const best=[...DATA.members].sort((a,b)=>b.sentiment_score-a.sentiment_score)[0];
document.getElementById('kpis').innerHTML=[
  ['긍정 비율',(os.positive/totS*100).toFixed(0)+'%',os.positive+'개 / '+totS+'개'],
  ['중립 비율',(os.neutral/totS*100).toFixed(0)+'%',os.neutral+'개'],
  ['부정 비율',(os.negative/totS*100).toFixed(0)+'%',os.negative+'개'],
  ['감성 점수 1위',best.name_ko,'+'+ (best.sentiment_score*100).toFixed(0)+'점'],
].map(k=>`<div class="kpi"><div class="v">${k[1]}</div><div class="l">${k[0]}</div><div class="s">${k[2]}</div></div>`).join('');

const byScore=[...DATA.members].sort((a,b)=>b.sentiment_score-a.sentiment_score);
document.getElementById('sentibars').innerHTML = byScore.map(m=>`
  <div class="senti-row">
    <span>${m.name_ko}</span>
    <span class="bar-outer">
      <span class="bar-seg" style="width:${(m.positive_share*100).toFixed(1)}%;background:${cssv('--pos')}"></span>
      <span class="bar-seg" style="width:${(m.neutral_share*100).toFixed(1)}%;background:${cssv('--neu')}"></span>
      <span class="bar-seg" style="width:${(m.negative_share*100).toFixed(1)}%;background:${cssv('--neg')}"></span>
    </span>
    <span class="senti-nums">${(m.positive_share*100).toFixed(0)}% / ${(m.negative_share*100).toFixed(0)}%</span>
  </div>`).join('');

function drawTopics(){
  const svg=document.getElementById('topics');svg.innerHTML='';
  const W=460,H=320,ml=100,mr=30,mt=10,mb=10;
  const data=[...DATA.topic_totals].sort((a,b)=>a.count-b.count);
  const max=Math.max(...data.map(d=>d.count));
  const bh=(H-mt-mb)/data.length;
  const X=v=>ml+(v/max)*(W-ml-mr);
  const SER=['--s1','--s2','--s3','--s4','--s5','--s6','--s7'];
  data.forEach((d,i)=>{
    const y=mt+i*bh;
    svg.appendChild(svgEl('rect',{x:ml,y:y+bh*0.2,width:Math.max(1,X(d.count)-ml),height:bh*0.6,rx:4,fill:cssv(SER[i%SER.length])}));
    const t1=svgEl('text',{x:ml-8,y:y+bh/2+4,'text-anchor':'end',class:'axis'});t1.textContent=d.topic;svg.appendChild(t1);
    const t2=svgEl('text',{x:X(d.count)+6,y:y+bh/2+4,class:'axis'});t2.textContent=d.count;svg.appendChild(t2);
  });
}

const SENTI_KO={positive:'긍정',neutral:'중립',negative:'부정'};
document.getElementById('topcomments').innerHTML = DATA.top_liked.slice(0,8).map(c=>`
  <div class="comment-card">
    <div class="meta"><span>${c.name_ko} · ${c.topic_ko}</span>
      <span class="pill ${c.sentiment}">${SENTI_KO[c.sentiment]} · ♥${fmtN(c.like_count)}</span></div>
    <div>${c.text}</div>
  </div>`).join('');

const COLS=[
  ['name_ko','멤버',r=>r.name_ko],
  ['n_comments','표본수',r=>r.n_comments],
  ['positive_share','긍정',r=>(r.positive_share*100).toFixed(0)+'%'],
  ['negative_share','부정',r=>(r.negative_share*100).toFixed(0)+'%'],
  ['sentiment_score','감성점수',r=>(r.sentiment_score>=0?'+':'')+(r.sentiment_score*100).toFixed(0)],
  ['top_topic','주요토픽',r=>r.top_topic],
  ['avg_likes','평균좋아요',r=>fmtN(Math.round(r.avg_likes))],
];
let sk='sentiment_score',sd=-1;
const rows=()=>[...DATA.members].sort((a,b)=>(a[sk]>b[sk]?1:-1)*sd);
function drawTable(){const t=document.getElementById('tbl');
  t.innerHTML='<thead><tr>'+COLS.map(c=>`<th class="${c[0]===sk?'active':''}" onclick="setSk('${c[0]}')">${c[1]}${c[0]===sk?(sd<0?' ▾':' ▴'):''}</th>`).join('')+'</tr></thead>'+
  '<tbody>'+rows().map(r=>'<tr>'+COLS.map(c=>`<td>${c[2](r)}</td>`).join('')+'</tr>').join('')+'</tbody>';}
function setSk(k){if(sk===k)sd*=-1;else{sk=k;sd=-1;}drawTable();}

document.getElementById('foot').innerHTML=
  `표본: 멤버별 인기 영상 상위(추천순) 댓글 중 좋아요 상위 30개(총 330개). 라벨링은 Claude가 문맥을 읽고 직접 분류(반어법·팬덤 용어 고려).<br>`+
  `추천순 상위 댓글은 긍정 편향이 있을 수 있음 · 지표는 수집 시점 스냅샷입니다.`;

function toggleTheme(){const r=document.documentElement;
  const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  r.setAttribute('data-theme',cur==='dark'?'light':'dark');drawAll();}
function drawAll(){drawTopics();drawTable();}
drawAll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
