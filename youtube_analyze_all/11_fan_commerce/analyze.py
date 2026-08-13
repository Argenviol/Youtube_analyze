"""
프로젝트11 · 분석 단계
가격 구조(팬딩) + 실제 지출(텀블벅) + 회사 재무(09 재사용) → 지표 → SQL → 차트 → 사이트 → 리포트.

  python 11_fan_commerce/analyze.py

"팬덤은 얼마를 쓰고, 그 돈은 회사에 남는가?"를 검증하되, 표본이 작다는 것도 그대로
남긴다 — 재무 데이터는 회사 2곳 × 몇 개 연도뿐이라 상관관계·인과관계는 계산하지 않는다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import config, db, viz
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SQL = HERE / "sql"
CHARTS = HERE / "charts"
SITE = HERE / "site"

STELLIVE_URL = "stellive"


# ---------------------------------------------------------------------------
# 지표
# ---------------------------------------------------------------------------
def build_fanding_metrics(tiers: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    if tiers.empty:
        return tiers, {}
    summary = (tiers.groupby(["creator_url", "nickname"])["price_krw"]
               .agg(n_tiers="count", min_price="min", max_price="max", avg_price="mean")
               .reset_index())
    summary["avg_price"] = summary["avg_price"].round(0).astype(int)
    summary = summary.sort_values("avg_price", ascending=False).reset_index(drop=True)

    prices = tiers["price_krw"]
    stellive_prices = tiers.loc[tiers["creator_url"] == STELLIVE_URL, "price_krw"].tolist()
    stats = dict(
        n_tiers=int(len(tiers)), n_creators_with_tiers=int(tiers["creator_url"].nunique()),
        min_price=int(prices.min()), max_price=int(prices.max()),
        median_price=int(prices.median()), mean_price=round(float(prices.mean()), 0),
        stellive_prices=stellive_prices,
        stellive_percentile=round(float((prices < stellive_prices[0]).mean() * 100), 1) if stellive_prices else None,
    )
    return summary, stats


def build_crowdfunding_metrics(cf: pd.DataFrame) -> pd.DataFrame:
    return cf.sort_values("raised_krw", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# SQL
# ---------------------------------------------------------------------------
def build_sql(tiers, fanding_summary, cf, fin):
    SQL.mkdir(parents=True, exist_ok=True)
    tables = {
        "fanding_tiers": tiers,
        "fanding_creator_summary": fanding_summary,
        "crowdfunding_projects": cf.drop(columns=["source_url", "source_type", "note"]),
        "company_financials": fin,
    }
    db.write_sqlite(SQL / "fan_commerce.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables)
    db.dump_insert_sql(SQL / "fanding_tiers.sql", "fanding_tiers", tiers)
    db.dump_insert_sql(SQL / "crowdfunding_projects.sql", "crowdfunding_projects",
                        tables["crowdfunding_projects"])
    db.dump_insert_sql(SQL / "company_financials.sql", "company_financials", fin)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")

    md = ["# 팬 커머스 분석 쿼리 결과\n", "`sql/fan_commerce.db`(SQLite) 실행 결과.\n"]
    for title, q in NAMED_QUERIES:
        try:
            res = db.run_query(SQL / "fan_commerce.db", q)
            md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n")
            md.append(res.to_markdown(index=False)); md.append("\n")
        except Exception as e:
            md.append(f"## {title}\n\n(실행 불가: {e})\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


# ---------------------------------------------------------------------------
# 차트
# ---------------------------------------------------------------------------
def build_charts(tiers, fanding_stats, cf, fin):
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    pal = config.PALETTE["series"]
    made = []

    # 1. 팬딩 VTuber 카테고리 멤버십 가격 분포 (로그 스케일 히스토그램, 스텔라이브 위치 표시)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    prices = tiers["price_krw"].values
    bins = np.logspace(np.log10(max(prices.min(), 500)), np.log10(prices.max() * 1.05), 16)
    ax.hist(prices, bins=bins, color=pal[0], zorder=3, edgecolor="white", linewidth=0.6)
    ax.set_xscale("log")
    for p in fanding_stats.get("stellive_prices", []):
        ax.axvline(p, color=pal[1], linewidth=2, linestyle="--", zorder=4)
        ax.annotate(f"스텔라이브 {p:,}원", (p, ax.get_ylim()[1] * 0.92), color=pal[1],
                    fontsize=9, ha="left", xytext=(6, 0), textcoords="offset points")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_title(f"팬딩 VTuber 카테고리 멤버십 가격 분포 (티어 {len(tiers)}건, "
                 f"크리에이터 {fanding_stats['n_creators_with_tiers']}명)")
    ax.set_xlabel("월 가격(원, 로그 스케일)"); ax.set_ylabel("티어 수")
    fig.tight_layout(); fig.savefig(CHARTS / "01_fanding_price_dist.png", dpi=140); plt.close(fig)
    made.append("01_fanding_price_dist.png")

    # 2. 크라우드펀딩 프로젝트별 달성률 (로그 스케일 — 282%~44,112%로 편차가 크다)
    d = cf.sort_values("achievement_pct")
    colors = [pal[2] if c == "공식 굿즈 펀딩" else pal[4] for c in d["category"]]
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(d["project_name"], d["achievement_pct"], color=colors, height=0.6, zorder=3)
    ax.set_xscale("log")
    ax.axvline(100, color=config.INK["grid"], linewidth=1.2, linestyle=":", zorder=2)
    ax.annotate("목표 100%", (100, -0.7), color=config.INK["muted"], fontsize=8, ha="center")
    for b, v in zip(bars, d["achievement_pct"]):
        ax.annotate(f"{v:,.0f}%", (b.get_width(), b.get_y() + b.get_height() / 2), va="center",
                    ha="left", fontsize=9, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
    ax.set_title("텀블벅 크라우드펀딩 목표 대비 달성률 (로그 스케일)")
    ax.set_xlabel("달성률(%)"); ax.margins(x=0.18)
    fig.tight_layout(); fig.savefig(CHARTS / "02_crowdfunding_achievement.png", dpi=140); plt.close(fig)
    made.append("02_crowdfunding_achievement.png")

    # 3. 크라우드펀딩 1인당 평균 후원액
    d = cf.sort_values("per_backer_krw")
    colors = [pal[2] if c == "공식 굿즈 펀딩" else pal[4] for c in d["category"]]
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(d["project_name"], d["per_backer_krw"], color=colors, height=0.6, zorder=3)
    for b, v in zip(bars, d["per_backer_krw"]):
        ax.annotate(f"{v:,.0f}원", (b.get_width(), b.get_y() + b.get_height() / 2), va="center",
                    ha="left", fontsize=9, color=config.INK["text"], xytext=(4, 0), textcoords="offset points")
    ax.set_title("텀블벅 크라우드펀딩 1인당 평균 후원액 (모인금액/후원자수)")
    ax.set_xlabel("원"); ax.margins(x=0.2)
    fig.tight_layout(); fig.savefig(CHARTS / "03_crowdfunding_per_backer.png", dpi=140); plt.close(fig)
    made.append("03_crowdfunding_per_backer.png")

    # 4. 패러블엔터테인먼트 매출 vs 영업이익 추이 — 핵심 펀치라인
    _company_trend_chart(fin, "패러블엔터테인먼트", pal[3], CHARTS / "04_parable_revenue_vs_operating.png",
                          "패러블엔터테인먼트(이세계아이돌 소속사) 매출 vs 영업이익")
    made.append("04_parable_revenue_vs_operating.png")

    # 5. 샌드박스네트워크 매출 vs 영업이익 추이
    _company_trend_chart(fin, "샌드박스네트워크", pal[6], CHARTS / "05_sandbox_revenue_vs_operating.png",
                          "샌드박스네트워크 매출 vs 영업이익 (2018~2025)")
    made.append("05_sandbox_revenue_vs_operating.png")

    print(f"차트 {len(made)}종 -> {CHARTS}")
    return made


def _company_trend_chart(fin: pd.DataFrame, corp: str, color: str, path: Path, title: str):
    d = fin[fin["corp_name"] == corp].sort_values("bsns_year")
    fig, ax1 = plt.subplots(figsize=(9, 5.6))
    ax1.bar(d["bsns_year"], d["revenue"] / 1e8, color=color, alpha=0.55, zorder=3, width=0.5,
            label="매출(억원, 좌축)")
    ax1.set_ylabel("매출(억원)"); ax1.set_xlabel("사업연도")
    ax1.set_xticks(d["bsns_year"])
    ax2 = ax1.twinx()
    ax2.plot(d["bsns_year"], d["operating_income"] / 1e8, color=config.INK["text"], marker="o",
              linewidth=2.4, zorder=4, label="영업이익(억원, 우축)")
    ax2.axhline(0, color=config.INK["grid"], linewidth=1, linestyle="--", zorder=2)
    ax2.set_ylabel("영업이익(억원)")
    ax2.grid(False)
    h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, ncol=2, loc="lower center",
               bbox_to_anchor=(0.5, 1.02))
    ax1.set_title(title, pad=34)
    fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


# ---------------------------------------------------------------------------
# 출력물
# ---------------------------------------------------------------------------
def build_outputs(tiers, fanding_summary, fanding_stats, cf, fin, meta, charts):
    SITE.mkdir(parents=True, exist_ok=True)

    site_data = dict(
        meta=meta,
        fanding=dict(
            stats=fanding_stats,
            creator_summary=json.loads(fanding_summary.to_json(orient="records", force_ascii=False)),
            tiers=json.loads(tiers.to_json(orient="records", force_ascii=False)),
        ),
        crowdfunding=json.loads(cf.to_json(orient="records", force_ascii=False)),
        financials=json.loads(fin.replace({np.nan: None}).to_json(orient="records")),
    )
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    parable = fin[fin["corp_name"] == "패러블엔터테인먼트"].sort_values("bsns_year")
    sandbox = fin[fin["corp_name"] == "샌드박스네트워크"].sort_values("bsns_year")
    n_sandbox_loss_years = int((sandbox["operating_income"] < 0).sum())
    official = cf[cf["category"] == "공식 굿즈 펀딩"].sort_values("raised_krw", ascending=False)
    fanmade = cf[cf["category"] == "팬메이드 광고 펀딩"].sort_values("raised_krw", ascending=False)

    lines = [
        "# 프로젝트 11 · 팬 커머스 분석 — 팬덤은 얼마를 쓰고, 그 돈은 회사에 남는가?\n",
        f"- 수집 시각: {meta['fetched_at'][:19]} UTC",
        "- 데이터 소스: 팬딩(Fanding) 공개 REST + 텀블벅(Tumblbug) 공개 결과 정적 큐레이션 + "
        "09_dart_financials 감사보고서 재무제표(읽기 전용 재사용)\n",
        "## 세 레이어, 세 가지 확보 방식\n",
        "이 프로젝트는 '팬덤 지출'을 한 번에 재는 지표가 없어서 세 레이어로 쪼갰다. 각 레이어는",
        "확보 방법이 근본적으로 다르고, 그 차이 자체가 이 프로젝트의 발견이다.\n",
        "### 레이어 1 · 가격 구조 (팬딩) — 자동 수집 성공",
        f"팬딩 VTuber 카테고리 크리에이터 **{meta['n_fanding_creators']}명** 전원의 공개 멤버십 페이지를",
        f"순회해 **{meta['n_fanding_tiers']}개 티어**(가격을 매긴 크리에이터는 {meta['n_fanding_creators_with_tiers']}명)를",
        "확보했다. `robots.txt`가 `/studio/*`(크리에이터 관리자 화면)·`/account-info` 등만 막고",
        "멤버십 페이지 자체는 로그인 없이 공개돼 있어 자동 수집이 가능했다.",
        f"가격 범위는 **{fanding_stats['min_price']:,}원 ~ {fanding_stats['max_price']:,}원**",
        f"(중앙값 {fanding_stats['median_price']:,}원, 평균 {fanding_stats['mean_price']:,.0f}원).",
    ]
    if fanding_stats.get("stellive_prices"):
        p = fanding_stats["stellive_prices"][0]
        lines.append(
            f"스텔라이브 공식 팬클럽(파스텔) 가격은 **{p:,}원/월**로, 표본 내 하위 "
            f"{fanding_stats['stellive_percentile']:.0f}%ile 구간(더 저렴한 티어가 {fanding_stats['stellive_percentile']:.0f}% "
            "있다는 뜻) — 중앙값보다는 높지만 최고가 구간은 아니다."
        )
    lines += [
        "",
        "⚠ **가격 ≠ 매출.** 팬딩은 구독자 수를 공개하지 않으므로 이 레이어만으로 실제 수입을 ",
        "추정할 수 없다. 여기서는 '팬이 얼마를 요구받는가'만 다룬다.\n",
        "### 레이어 2 · 실제 지출 (텀블벅) — 자동 수집이 robots.txt에 막혀 정적 큐레이션으로 대체\n",
        "텀블벅 프로젝트 상세 페이지는 클라이언트 렌더링 SPA라서 모금액·후원자 수·달성률이 전부",
        "`tumblbug.com/api/v2`·`v3` 엔드포인트 호출로만 채워진다. 그런데 텀블벅",
        "`robots.txt`는 `Disallow: /api/`를 명시한다 — 즉 이 프로젝트가 원하는 수치의",
        "**유일한 출처가 로봇배제표준으로 막혀 있다.** `requests`만 쓰는 `collect.py`는 애초에",
        "그 엔드포인트를 요청하지 않으므로 이 규칙을 어길 수 없고(빈 껍데기만 받는다),",
        "헤드리스 브라우저로 렌더링을 우회하는 방법도 검토했지만 그건 매 실행마다 같은",
        "`/api/` 경로를 반복 호출하는 셈이라 규칙의 취지를 어기게 돼 채택하지 않았다.",
        "",
        "대신 이미 공개적으로 발표된 결과(언론 보도, 텀블벅 자체 SNS 발표, 그리고 프로젝트",
        "상세 페이지를 1회성으로 직접 열람해 확인한 수치)를 출처와 함께 정적 데이터셋으로",
        f"기록했다 — 프로젝트 {len(cf)}건. **이 레이어는 재실행해도 갱신되지 않는다**(라이브",
        "API가 아니므로).\n",
        "**공식 굿즈 펀딩 (이세계아이돌 · 패러블엔터테인먼트 소속)**",
    ]
    for _, r in official.iterrows():
        lines.append(
            f"- **{r['project_name']}** ({r['period_start']}~{r['period_end']}): 목표 "
            f"{r['goal_krw']/1e4:,.0f}만원 → 달성 {r['raised_krw']/1e8:,.1f}억원 "
            f"({r['achievement_pct']:,.0f}%), 후원자 {r['backers']:,}명, "
            f"1인당 평균 {r['per_backer_krw']:,}원"
        )
    lines += ["", "**팬메이드 광고 펀딩 (스텔라이브 멤버 개인, 비공식·팬 운영)**"]
    for _, r in fanmade.iterrows():
        lines.append(
            f"- **{r['project_name']}** ({r['period_start']}~{r['period_end']}): 달성 "
            f"{r['raised_krw']:,}원 ({r['achievement_pct']:,.0f}%), 후원자 {r['backers']:,}명, "
            f"1인당 평균 {r['per_backer_krw']:,}원"
        )
    lines += [
        "",
        "⚠ **표본 편향.** 이 목록은 실제로 열린 프로젝트 중에서도 성공/화제가 된 것만 검색으로",
        "발견됐다(생존자 편향). 목표를 못 채우고 조용히 끝난 프로젝트, 애초에 아무도 몰랐던",
        "프로젝트는 이 표본에 없다 — 달성률 분포는 실제보다 낙관적으로 왜곡돼 있을 가능성이 크다.",
        "",
        "⚠ **팬메이드 광고 펀딩은 회사 매출이 아니다.** '유니버스 데뷔 3주년 기념 광고' 창작자는",
        "정산액 34,114,780원(수수료 차감 후)을 전액 광고비·일러스트레이터 외주비로 지출했다고",
        "직접 공개했다 — 이 돈은 스텔라이브 회사 매출로 잡히지 않고 팬 커뮤니티 내부에서",
        "돌 뿐이다. '팬덤이 쓴 돈' 전부가 회사로 흘러간다고 가정하면 안 된다.\n",
        "**와디즈(Wadiz)는 다루지 않았다.** robots.txt는 개별 캠페인 페이지를 막지 않지만",
        "검색으로는 VTuber 카테고리 캠페인을 사실상 찾지 못했다 — 국내 버튜버 크라우드펀딩",
        "수요가 텀블벅에 쏠려 있는 것으로 보인다.\n",
        "### 레이어 3 · 회사에 남는 것 (09_dart_financials 재사용)\n",
        "09가 감사보고서 원문 파싱으로 확보한 재무제표를 그대로 재사용한다(DART 재수집 없음).",
        "**팬딩은 여전히 DART 공시가 0건**이라 이 레이어에 팬딩 자체는 없다 — 09의 결론을 그대로",
        "계승한다.\n",
    ]
    if len(parable) >= 2:
        p0, p1 = parable.iloc[0], parable.iloc[-1]
        lines.append(
            f"- **패러블엔터테인먼트**(이세계아이돌 소속사): 매출 {p0['bsns_year']:.0f}년 "
            f"{p0['revenue']/1e8:,.0f}억원 → {p1['bsns_year']:.0f}년 {p1['revenue']/1e8:,.0f}억원으로 "
            f"증가했지만, 영업이익은 {p0['bsns_year']:.0f}년 {p0['operating_income']/1e8:+,.0f}억원(흑자)에서 "
            f"{p1['bsns_year']:.0f}년 {p1['operating_income']/1e8:+,.0f}억원(적자)으로 전환됐다."
        )
    if len(sandbox):
        s_last = sandbox.iloc[-1]
        lines.append(
            f"- **샌드박스네트워크**: {int(sandbox['bsns_year'].min())}~{int(sandbox['bsns_year'].max())}년 "
            f"{len(sandbox)}개 연도 전부 영업손실({n_sandbox_loss_years}/{len(sandbox)}년 적자). "
            f"{int(s_last['bsns_year'])}년 매출 {s_last['revenue']/1e8:,.0f}억원에도 영업이익률 "
            f"{s_last['operating_margin']*100:.1f}%."
        )
    lines += [
        "",
        "## 세 레이어를 나란히 놓아보면 (펀치라인 — 증명이 아니라 관찰)\n",
        "이세계아이돌 굿즈 펀딩 두 건은 41억원·88억원이라는 국내 크라우드펀딩 역대 최고 기록을",
        "냈다. 같은 기간 그 IP의 실제 관리사로 보도된 패러블엔터테인먼트의 감사보고서는",
        "매출이 210억→218억원으로 늘었는데도 영업이익은 +12억→-91억원으로 무너졌다. 팬덤이",
        "쓰는 돈이 늘어난다고 회사에 남는 돈이 늘어난다는 보장은 없다 — 샌드박스네트워크는",
        f"{int(sandbox['bsns_year'].min())}년부터 {int(sandbox['bsns_year'].max())}년까지 매년",
        "영업손실을 기록했다.\n",
        "⚠ **이건 증명이 아니라 관찰이다.** ① 크라우드펀딩 프로젝트의 IP 소유자(이세계아이돌)와",
        "감사보고서 법인(패러블엔터테인먼트)이 '실제 관리사'라는 언론 보도로만 연결돼 있어 이 펀딩",
        "수익이 그 재무제표에 정확히 얼마나 잡히는지는 알 수 없다(굿즈 원가·제작사·유통사 몫이",
        "따로 있을 수 있다). ② 재무 표본이 회사 2곳뿐이라 상관계수를 계산하지 않았다.",
        "③ 회계연도(연 1회)와 크라우드펀딩 캠페인(특정 시점)은 기간이 정확히 겹치지 않는다.",
        "④ 팬딩 가격 레이어는 이 두 회사와 아예 무관한 제3의 플랫폼 데이터라 세 레이어를 하나의",
        "숫자로 합칠 수 없다 — 그래서 세 레이어를 병렬로만 제시하고 억지로 잇지 않았다.\n",
        "## 산출물",
        "- `data/fanding_creators.csv`·`data/fanding_tiers.csv` 팬딩 VTuber 카테고리 크리에이터·멤버십 티어",
        "- `data/crowdfunding_projects.csv` 텀블벅 VTuber 관련 크라우드펀딩 정적 큐레이션(출처 포함)",
        "- `data/company_financials.csv` 09_dart_financials 재사용(샌드박스네트워크·패러블엔터테인먼트)",
        "- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과",
        f"- `charts/` 차트 {len(charts)}종(가격 분포·달성률·1인당 후원액·회사별 매출-영업이익 추이 2종)",
        "- `site/index.html` 대시보드",
    ]
    (HERE / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("팬딩 VTuber 멤버십 가격 랭킹 (크리에이터별 평균가)", """
SELECT nickname AS 크리에이터, n_tiers AS 티어수, min_price AS 최저가,
       max_price AS 최고가, avg_price AS 평균가
FROM fanding_creator_summary ORDER BY avg_price DESC LIMIT 15;"""),
    ("스텔라이브 팬딩 멤버십 티어", """
SELECT nickname AS 크리에이터, tier_title AS 티어명, price_krw AS 가격
FROM fanding_tiers WHERE creator_url = 'stellive';"""),
    ("텀블벅 크라우드펀딩 프로젝트 랭킹 (모금액순)", """
SELECT project_name AS 프로젝트, category AS 구분, goal_krw AS 목표금액,
       raised_krw AS 모인금액, backers AS 후원자수, achievement_pct AS 달성률_pct,
       per_backer_krw AS 인당후원액
FROM crowdfunding_projects ORDER BY raised_krw DESC;"""),
    ("크라우드펀딩 구분별(공식/팬메이드) 평균 지표", """
SELECT category AS 구분, COUNT(*) AS 프로젝트수, ROUND(AVG(achievement_pct),0) AS 평균달성률_pct,
       ROUND(AVG(per_backer_krw),0) AS 평균인당후원액
FROM crowdfunding_projects GROUP BY category;"""),
    ("회사별 최신 연도 매출·영업이익", """
SELECT corp_name AS 법인, bsns_year AS 사업연도, fs_div AS 구분,
       ROUND(revenue/1e8,1) AS 매출_억원, ROUND(operating_income/1e8,1) AS 영업이익_억원,
       ROUND(operating_margin*100,1) AS 영업이익률_pct
FROM company_financials
WHERE (corp_name, bsns_year) IN (
    SELECT corp_name, MAX(bsns_year) FROM company_financials GROUP BY corp_name
);"""),
    ("샌드박스네트워크 영업손실 연속 연도", """
SELECT bsns_year AS 사업연도, ROUND(revenue/1e8,1) AS 매출_억원,
       ROUND(operating_income/1e8,1) AS 영업이익_억원
FROM company_financials WHERE corp_name = '샌드박스네트워크' ORDER BY bsns_year;"""),
]
ANALYSIS_QUERIES = "-- 팬 커머스 분석 쿼리 (SQLite: sql/fan_commerce.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    tiers = pd.read_csv(DATA / "fanding_tiers.csv")
    cf = pd.read_csv(DATA / "crowdfunding_projects.csv")
    fin = pd.read_csv(DATA / "company_financials.csv")
    meta_in = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))

    fanding_summary, fanding_stats = build_fanding_metrics(tiers)
    cf = build_crowdfunding_metrics(cf)

    build_sql(tiers, fanding_summary, cf, fin)
    charts = build_charts(tiers, fanding_stats, cf, fin)
    build_outputs(tiers, fanding_summary, fanding_stats, cf, fin, meta_in, charts)

    print("\n=== 팬딩 가격 구조 요약 ===")
    print(f"티어 {fanding_stats['n_tiers']}건 / 크리에이터 {fanding_stats['n_creators_with_tiers']}명 / "
          f"{fanding_stats['min_price']:,}~{fanding_stats['max_price']:,}원 "
          f"(중앙값 {fanding_stats['median_price']:,}원)")
    print("\n=== 텀블벅 크라우드펀딩 요약 ===")
    with pd.option_context("display.width", 220):
        print(cf[["project_name", "category", "raised_krw", "backers", "achievement_pct"]].to_string(index=False))
    print("\n=== 회사 재무 요약(최신 연도) ===")
    latest = fin.sort_values("bsns_year").groupby("corp_name").tail(1)
    with pd.option_context("display.width", 220):
        print(latest[["corp_name", "bsns_year", "revenue", "operating_income", "operating_margin"]].to_string(index=False))


if __name__ == "__main__":
    main()
