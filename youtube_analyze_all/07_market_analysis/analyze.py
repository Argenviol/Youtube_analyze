"""
프로젝트7 · 분석 단계
버추얼 크리에이터 시장 분석. Claude 웹서치로 수집한 시장 통계(data/market_facts.csv,
stellive_milestones.csv) + 프로젝트1·6에서 만든 자체 데이터를 결합해 SQL/차트/사이트를 만든다.

  python 07_market_analysis/analyze.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config, db, viz
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = HERE / "data"
SQL = HERE / "sql"
CHARTS = HERE / "charts"
SITE = HERE / "site"


def load_own_data():
    """프로젝트1(자체 채널 지표)·6(경쟁사 비교)의 산출물을 재사용.

    06 은 2026-09-18 부터 그룹 평균(group_summary) 대신 **코호트 × 그룹**
    요약(cohort_summary)을 만든다. 데뷔 시기가 4~6년 차이 나는 채널을 한 평균에
    섞으면 그 평균이 활동 기간을 재는 값이 되기 때문이다. 07 은 그 구조를 그대로
    따라간다 — 여기서 다시 코호트를 뭉개면 06 을 고친 의미가 없다.
    """
    p1 = ROOT / "01_member_channel_performance" / "data" / "channel_metrics.csv"
    p6 = ROOT / "06_competitor_comparison" / "data" / "cohort_summary.csv"
    metrics = pd.read_csv(p1) if p1.exists() else pd.DataFrame()
    groups = pd.read_csv(p6) if p6.exists() else pd.DataFrame()
    return metrics, groups


def build_sql(facts, milestones, metrics, groups):
    SQL.mkdir(parents=True, exist_ok=True)
    tables = {"market_facts": facts, "stellive_milestones": milestones}
    if not groups.empty:
        tables["cohort_summary"] = groups
    db.write_sqlite(SQL / "market.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables)
    for name, df in tables.items():
        db.dump_insert_sql(SQL / f"{name}.sql", name, df)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")
    md = ["# 시장 분석 쿼리 결과\n", "`sql/market.db`(SQLite) 실행 결과. 원천: Claude 웹서치 + 프로젝트1·6 자체 데이터.\n"]
    for title, q in NAMED_QUERIES:
        try:
            res = db.run_query(SQL / "market.db", q)
        except Exception as e:
            continue
        md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n"); md.append(res.to_markdown(index=False)); md.append("\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


def build_charts(facts, milestones, metrics, groups):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    S = config.PALETTE["series"]

    # 1. 글로벌 VTuber 시장 규모 전망 (2개 리서치사 비교)
    ms = facts[facts["category"] == "market_size"].copy()
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    for i, src in enumerate(ms["source_name"].unique()):
        d = ms[ms["source_name"] == src].sort_values("year")
        ax.plot(d["year"], d["value"]/1000, marker="o", color=S[i], linewidth=2.4,
               markersize=8, label=src, zorder=3)
        for _, r in d.iterrows():
            ax.annotate(f"${r['value']/1000:.1f}B", (r["year"], r["value"]/1000),
                       fontsize=9, xytext=(6, 6), textcoords="offset points", color=config.INK["text"])
    ax.set_title("글로벌 VTuber 시장 규모 전망 (리서치사별)")
    ax.set_ylabel("시장 규모 (십억 달러)"); ax.grid(zorder=0); ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(CHARTS / "01_market_size_forecast.png", dpi=140); plt.close(fig)

    # 2. 매출원/지역 구성
    rev = facts[facts["category"].isin(["revenue_share", "region_share"])]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    bars = ax.bar(rev["metric"], rev["value"], color=S[:len(rev)], zorder=3)
    ax.set_title("VTuber 시장 구조 (매출원·지역 비중, %)"); ax.set_ylabel("%")
    ax.grid(axis="y", zorder=0); plt.setp(ax.get_xticklabels(), rotation=18, ha="right")
    for b, v in zip(bars, rev["value"]):
        ax.annotate(f"{v:.1f}%", (b.get_x()+b.get_width()/2, v), ha="center", va="bottom",
                    fontsize=10, color=config.INK["text"], xytext=(0, 3), textcoords="offset points")
    fig.tight_layout(); fig.savefig(CHARTS / "02_market_structure.png", dpi=140); plt.close(fig)

    # 3. 치지직 플랫폼 KPI
    pk = facts[facts["category"] == "platform_kpi"]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    labels = ["MAU\n(백만명)", "월 시청시간\n(억분)", "LCK 뷰어십\n(백만명)"]
    vals = [pk.iloc[0]["value"]/1e6, pk.iloc[1]["value"]/1e8, pk.iloc[2]["value"]/1e6]
    bars = ax.bar(labels, vals, color=S[3], zorder=3, width=0.55)
    ax.set_title("치지직(Chzzk) 핵심 지표 (2026)"); ax.grid(axis="y", zorder=0)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:.1f}", (b.get_x()+b.get_width()/2, v), ha="center", va="bottom",
                    fontsize=10, color=config.INK["text"], xytext=(0, 3), textcoords="offset points")
    fig.tight_layout(); fig.savefig(CHARTS / "03_chzzk_kpi.png", dpi=140); plt.close(fig)

    # 4. StelLive 성장 타임라인 (마일스톤) — 실제 날짜가 아닌 균등 간격 배치로 겹침 방지
    fig, ax = plt.subplots(figsize=(13, 5.2))
    milestones["dt"] = pd.to_datetime(milestones["date"])
    cat_color = {"origin": config.INK["muted"], "launch": S[0], "investment": S[1], "milestone": S[2]}
    m = milestones.sort_values("dt").reset_index(drop=True)
    xs = range(len(m))
    y0 = 0
    ax.axhline(y0, color=config.INK["grid"], lw=1.5, zorder=1)
    offsets = [0.7, -0.7, 0.7, -0.7, 0.7, -0.7, 0.7, -0.7]
    for i, (x, (_, r)) in enumerate(zip(xs, m.iterrows())):
        yoff = offsets[i % len(offsets)]
        ax.scatter([x], [y0], s=90, color=cat_color.get(r["category"], S[0]), zorder=3)
        ax.plot([x, x], [y0, yoff*0.82], color=config.INK["grid"], lw=1, zorder=2)
        wrapped = r["event"] if len(r["event"]) <= 16 else r["event"][:16] + "\n" + r["event"][16:32]
        ax.annotate(f"{r['date']}\n{wrapped}", (x, yoff), ha="center",
                   va="bottom" if yoff > 0 else "top", fontsize=8.6, color=config.INK["text"], linespacing=1.4)
    ax.set_xlim(-0.6, len(m)-0.4)
    ax.set_ylim(-1.5, 1.5); ax.set_yticks([]); ax.set_xticks([])
    ax.set_title("StelLive 성장 타임라인 (균등 간격 배치, 날짜순)")
    for spine in ("top", "left", "right", "bottom"): ax.spines[spine].set_visible(False)
    handles = [plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=c, markersize=9, label=k)
               for k, c in cat_color.items()]
    ax.legend(handles=handles, labels=["창립", "런칭", "투자", "성과"], frameon=False,
              loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=4)
    fig.tight_layout(); fig.savefig(CHARTS / "04_stellive_timeline.png", dpi=140); plt.close(fig)

    # 5. 시장 포지션 (프로젝트6 자체 데이터 재사용)
    #    점 하나 = 그룹이 아니라 **코호트 × 그룹**이다. 그룹을 하나로 뭉쳐 찍으면
    #    데뷔 2년차와 7년차가 한 점이 되어 위치가 아무 의미도 갖지 못한다.
    if not groups.empty:
        gc = {"StelLive": S[0], "홀로라이브": S[1], "이세계아이돌": S[2]}
        fig, ax = plt.subplots(figsize=(8.5, 6))
        for _, r in groups.iterrows():
            x, y = r["median_subscribers"], r["avg_reach_ratio"]*100
            ax.scatter(x, y, s=max(40, r["avg_recent_views"]/2000),
                      color=gc.get(r["group"], S[3]), alpha=0.8,
                      edgecolors="white", linewidths=1.5, zorder=3)
            ax.annotate(f"{r['group']}\n{r['cohort']}", (x, y),
                       fontsize=9, xytext=(8, 6), textcoords="offset points",
                       color=config.INK["text"])
        ax.set_xscale("log")
        ax.set_title("시장 포지션: 규모 vs 도달효율 (점=데뷔 코호트별 그룹, 버블=평균조회수)")
        ax.set_xlabel("구독자 중앙값 (log)"); ax.set_ylabel("도달 효율 (%)")
        ax.grid(True, zorder=0)
        fig.tight_layout(); fig.savefig(CHARTS / "05_market_position.png", dpi=140); plt.close(fig)

    print(f"차트 -> {CHARTS}")


def _stel_position(groups: pd.DataFrame) -> str:
    """StelLive 의 시장 포지션 한 줄 — 하드코딩하지 않고 06 산출물에서 계산한다.

    예전에는 "도달 효율(60%)이 압도적" 처럼 숫자를 본문에 박아 뒀다. 06 이 매일
    갱신되는 동안 이 문장만 옛날 값에 머물러 두 리포트가 서로 다른 숫자를 말했다.
    """
    if groups.empty or "cohort" not in groups.columns:
        return "비교 데이터 없음 — 프로젝트6을 먼저 실행하세요."
    shared = [c for c, g in groups.groupby("cohort")
              if {"StelLive", "홀로라이브"} <= set(g["group"])]
    if not shared:
        return ("같은 시기에 데뷔한 비교군이 아직 없어 그룹 비교를 하지 않았습니다 "
                "(프로젝트6 참고).")
    parts = []
    for c in sorted(shared):
        g = groups[groups["cohort"] == c].set_index("group")
        s, h = g.loc["StelLive"], g.loc["홀로라이브"]
        parts.append(
            f"**{c}** 코호트에서 구독자 중앙값은 {s['median_subscribers']:,.0f} 대 "
            f"{h['median_subscribers']:,.0f}, 도달 효율은 {s['avg_reach_ratio']*100:.0f}% 대 "
            f"{h['avg_reach_ratio']*100:.0f}%")
    return ("; ".join(parts) +
            " — 규모가 아니라 구독자 대비 실제 시청 비율에서 위치를 잡는 구조입니다.")


def build_outputs(facts, milestones, metrics, groups):
    # 데이터 계약(PRD 7): 공통 스키마는 meta.fetched_at을 요구한다.
    # 07은 외부 리서치 기반 정적 페이지라 "수집"이 아니라 "빌드"이므로 기존 built_at은
    # 유지하고, 신선도 배지 등 공통 UI가 그대로 쓸 수 있도록 fetched_at을 같은 값으로 추가한다.
    now = pd.Timestamp.now(tz="UTC").isoformat()
    meta = dict(built_at=now, fetched_at=now,
                source="Claude 웹서치(시장 통계) + 프로젝트1·6 자체 수집 데이터",
                n_facts=len(facts), n_milestones=len(milestones))
    site_data = dict(
        meta=meta,
        facts=json.loads(facts.to_json(orient="records", force_ascii=False)),
        milestones=json.loads(milestones.drop(columns=["dt"], errors="ignore").to_json(orient="records", force_ascii=False)),
        groups=json.loads(groups.to_json(orient="records", force_ascii=False)) if not groups.empty else [],
    )
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # data/_meta.json 도 같이 남긴다. 다른 프로젝트는 collect.py 가 만들지만 07은
    # 자체 수집이 없어 이 파일이 없었고, 그래서 결과물 리포트의 기준일이 계속 "—"
    # 였다. 갱신된 날짜를 모르면 독자는 이 페이지가 언제 것인지 알 수 없다.
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                     encoding="utf-8")

    md = f"""# 프로젝트 7 · 버추얼 크리에이터 시장 분석

Claude 웹서치로 수집한 공개 시장 통계(출처 명시)와, 프로젝트1(멤버별 채널 성과)·
프로젝트6(경쟁사 비교)에서 이미 만든 자체 데이터를 결합한 종합 시장 리포트입니다.

## 글로벌 시장

- VTuber 시장 규모: **2026년 약 31.3억 달러** (SkyQuest), 2031년 49.4억 달러 전망(CAGR 9.56%).
  다른 리서치사(Global Growth Insights)는 2026년 33.1억 달러 → 2032년 82.4억 달러(CAGR 16.3%)로 추정 —
  리서치사별 편차가 커서 **범위로 이해**하는 것이 안전합니다.
- 매출 구조: 구독+후원(수퍼챗 등)이 **52.67%**, YouTube 플랫폼이 **49.73%** — 후원 기반 수익모델이 견고.
- 지역 편중: **아시아태평양이 65.14%** — 한중일 시장이 여전히 핵심 축.

## 한국 시장 (치지직 중심)

- 치지직 MAU **242만 명**(2026.7 기준, YoY +17%), 월 시청시간 **8.47억 분**(YoY +91%) — 트위치 철수 이후
  독주 체제 굳히는 중.
- e스포츠 중계권(EWC) 확보로 LCK 뷰어십 점유율 **60%+**, SOOP(구 아프리카TV) 대비 우위.
- 한국 크리에이터 산업 전체: 사업체 11,089개, 매출 5조 5,503억 원, 종사자 43,717명(2025, KMCC).

## StelLive의 시장 포지션

- 2025년 7월 **브레이브 그룹(Brave Group)에 인수합병** — 일본계 버추얼 기획사 자본 편입으로 해외 확장 발판.
- 2025년 12월 **첫 단체 콘서트** 개최로 오프라인 IP 확장 시작.
- 프로젝트6 자체 데이터 기준(데뷔 시기를 맞춘 코호트 비교): {_stel_position(groups)}

## 산출물
- `data/market_facts.csv` 시장 통계(출처·URL 포함), `stellive_milestones.csv` 성장 타임라인
- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과 (프로젝트6 cohort_summary 재사용 포함)
- `charts/` 차트 5종(시장규모 전망·시장구조·치지직KPI·타임라인·시장포지션)
- `site/index.html` 인터랙티브 대시보드

## 출처
{chr(10).join(f"- [{r['source_name']}]({r['source_url']})" for r in facts.drop_duplicates('source_name').to_dict('records'))}

> 시장 규모 추정치는 리서치사별 방법론 차이로 편차가 크며, 특정 수치를 절대값이 아닌
> **성장 추세와 구조적 신호**로 해석하는 것을 권장합니다.
"""
    (HERE / "REPORT.md").write_text(md, encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("시장 규모 전망 (리서치사별)", """
SELECT source_name AS 출처, year AS 연도, value AS 규모_백만달러
FROM market_facts WHERE category='market_size' ORDER BY source_name, year;"""),
    ("매출원·지역 구조", """
SELECT metric AS 지표, value AS 비율_pct, source_name AS 출처
FROM market_facts WHERE category IN ('revenue_share','region_share');"""),
    ("치지직 핵심 지표", """
SELECT metric AS 지표, value AS 값, unit AS 단위, note AS 비고
FROM market_facts WHERE category='platform_kpi';"""),
    ("StelLive 성장 타임라인", """
SELECT date AS 날짜, event AS 이벤트, category AS 구분
FROM stellive_milestones ORDER BY date;"""),
]
ANALYSIS_QUERIES = "-- 버추얼 크리에이터 시장 분석 쿼리 (SQLite: sql/market.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    facts = pd.read_csv(DATA / "market_facts.csv")
    milestones = pd.read_csv(DATA / "stellive_milestones.csv")
    metrics, groups = load_own_data()
    build_sql(facts, milestones, metrics, groups)
    build_charts(facts, milestones, metrics, groups)
    build_outputs(facts, milestones, metrics, groups)
    print(f"\n시장 팩트 {len(facts)}건, 마일스톤 {len(milestones)}건 처리 완료")


if __name__ == "__main__":
    main()
