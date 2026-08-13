"""
프로젝트9 · 분석 단계
DART 재무제표 원자료(XBRL 경로 + 감사보고서 원문 파싱 경로) → 핵심 재무지표 → SQL → 차트 →
사이트 → 리포트.

  python 09_dart_financials/analyze.py

이 프로젝트는 포트폴리오에서 유일하게 "인기 프록시"가 아니라 감사받은 법정 재무제표를
다룬다. 처음엔 XBRL 경로(`fnlttSinglAcntAll`)로 플랫폼 2곳(SOOP·NAVER)만 확보했지만,
비상장 법인이 내는 **감사보고서 원문(document.xml)을 직접 파싱하는 경로**를 추가해
샌드박스네트워크·패러블엔터테인먼트까지 확보했다(자세한 방법은 REPORT.md 참고). 스텔라이브
본체·Brave group·팬딩은 여전히 확보하지 못했다 — 스텔라이브/Brave group은 DART 기업코드
자체가 없고, 팬딩은 기업코드는 있지만 공시 이력이 단 한 건도 없다(`data/corp_search.csv`·
`data/financials_status.csv`·`data/financials_audit_status.csv`에 그대로 남아 있다). 그래서
이 분석은 "스텔라이브 팬덤 vs 스텔라이브 재무" 직접 비교가 아니라 "확보 가능했던 크리에이터
인접 기업·플랫폼들의 재무 체력"과 "그 위에서 프로젝트1·8이 관측한 스텔라이브 팬덤 스냅샷을
나란히 참고용으로 놓는" 정도로 정직하게 범위를 좁힌다.
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

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SQL = HERE / "sql"
CHARTS = HERE / "charts"
SITE = HERE / "site"

# 이 프로젝트가 참조하는 다른 프로젝트의 산출물 (읽기 전용 — 여긴 수정하지 않는다)
ROOT = HERE.parent
PROJECT01_DATA = ROOT / "01_member_channel_performance" / "site" / "data.json"
PROJECT08_DATA = ROOT / "08_live_viewership" / "site" / "data.json"

KEY_ACCOUNTS = {
    "assets": ("Assets", "재무상태표"),
    "liabilities": ("Liabilities", "재무상태표"),
    "equity": ("Equity", "재무상태표"),
    "revenue": ("Revenue", "포괄손익계산서"),
    "operating_income": ("OperatingIncomeLoss", "포괄손익계산서"),
    "net_income": ("ProfitLoss", "포괄손익계산서"),
}


def load_raw(search_df: pd.DataFrame) -> pd.DataFrame:
    """XBRL 경로(financials_raw.csv) + 감사보고서 경로(financials_audit_raw.csv)를 합친다.
    두 경로 모두 account_id가 "네임스페이스_로컬명" 형태(예: ifrs-full_Revenue,
    dart-audit_OperatingIncomeLoss)라 이후 처리(build_metrics)는 동일하게 탄다."""
    df = pd.read_csv(DATA / "financials_raw.csv", dtype={"corp_code": str})
    df["source"] = "xbrl"

    audit_path = DATA / "financials_audit_raw.csv"
    if audit_path.exists():
        audit_df = pd.read_csv(audit_path, dtype={"corp_code": str})
        if len(audit_df):
            # "동명이인 주의"(브레이브엔터테인먼트, K-pop 걸그룹 소속사)는 corp_code는
            # 확인되지만 이 프로젝트가 다루는 VTuber Brave group과 무관하다고 이미 결론
            # 내렸다(README 참고). 감사보고서 경로가 일반화되어 있어 이 법인도 데이터가
            # 나오지만, 혼동을 막기 위해 분석에서는 계속 제외한다.
            excluded = set(search_df.loc[search_df["category"] == "동명이인", "corp_name"].dropna())
            audit_df = audit_df[~audit_df["corp_name"].isin(excluded)].copy()
            df = pd.concat([df, audit_df], ignore_index=True, sort=False)

    # account_id는 "네임스페이스_로컬명" 형태(예: ifrs-full_Revenue, dart_OperatingIncomeLoss).
    # 계정명(account_nm) 표기가 연도마다 달라("영업이익"/"영업이익(손실)") account_id로 매칭한다.
    df["localname"] = df["account_id"].astype(str).str.split("_", n=1).str[-1]
    return df


def build_metrics(raw: pd.DataFrame) -> pd.DataFrame:
    """회사×연도×fs_div 단위 와이드 재무지표. 연결(CFS) 우선, 없으면 별도(OFS)로 보완."""
    rows = []
    for (corp, year, fs_div), g in raw.groupby(["corp_name", "bsns_year", "fs_div"]):
        vals = {}
        for key, (localname, sj_nm) in KEY_ACCOUNTS.items():
            hit = g[(g["localname"] == localname) & (g["sj_nm"] == sj_nm)]
            vals[key] = float(hit["thstrm_amount"].iloc[0]) if len(hit) else None
        rows.append(dict(corp_name=corp, bsns_year=int(year), fs_div=fs_div, **vals))
    wide = pd.DataFrame(rows)

    def ratio(a, b):
        return np.where((wide[b].notna()) & (wide[b] != 0), wide[a] / wide[b], np.nan)

    wide["operating_margin"] = ratio("operating_income", "revenue")
    wide["net_margin"] = ratio("net_income", "revenue")
    wide["asset_turnover"] = ratio("revenue", "assets")
    wide["equity_ratio"] = ratio("equity", "assets")
    wide["debt_to_equity"] = ratio("liabilities", "equity")

    wide = wide.sort_values(["corp_name", "fs_div", "bsns_year"]).reset_index(drop=True)
    wide["revenue_yoy"] = wide.groupby(["corp_name", "fs_div"])["revenue"].pct_change()
    wide["operating_income_yoy"] = wide.groupby(["corp_name", "fs_div"])["operating_income"].pct_change()
    return wide


def pick_primary(wide: pd.DataFrame) -> pd.DataFrame:
    """회사×연도 1행. 연결재무제표(CFS)를 우선하고 없으면 별도(OFS)를 쓴다."""
    out = []
    for (corp, year), g in wide.groupby(["corp_name", "bsns_year"]):
        row = g[g["fs_div"] == "CFS"]
        if row.empty:
            row = g[g["fs_div"] == "OFS"]
        if not row.empty:
            out.append(row.iloc[0].to_dict())
    df = pd.DataFrame(out).sort_values(["corp_name", "bsns_year"]).reset_index(drop=True)
    return df


def load_fandom_context() -> dict:
    """프로젝트1(채널 성과)·8(동시시청자)의 site/data.json에서 요약 스냅샷만 참고용으로 가져온다.
    ⚠ 시계열이 아니라 수집 시점(2026-08) 단일 스냅샷이며, DART 연간 재무제표(~FY2025)와
    기간이 겹치지 않는다 — 상관관계를 계산하지 않고 나란히 보여주기만 한다."""
    ctx = {"note": "프로젝트1·8은 2026-08 수집 시점의 단일 스냅샷이다. DART 재무제표는 회계연도(~FY2025, "
                    "2026년 3월 제출) 단위라 기간이 겹치지 않는다. 상관계수를 계산하지 않고 참고 수치로만 병기한다."}
    if PROJECT01_DATA.exists():
        d1 = json.loads(PROJECT01_DATA.read_text(encoding="utf-8"))
        members = d1.get("members", [])
        ctx["project01"] = dict(
            fetched_at=d1.get("meta", {}).get("fetched_at"),
            n_members=len(members),
            total_subscribers=int(sum(m.get("subscribers", 0) for m in members)),
            total_recent_avg_views=int(sum(m.get("recent_avg_views", 0) for m in members)),
        )
    if PROJECT08_DATA.exists():
        d8 = json.loads(PROJECT08_DATA.read_text(encoding="utf-8"))
        members = d8.get("members", [])
        ctx["project08"] = dict(
            fetched_at=d8.get("meta", {}).get("fetched_at"),
            coverage=d8.get("coverage"),
            enough_coverage=d8.get("enough_coverage"),
            total_follower_delta=int(sum(m.get("follower_delta", 0) or 0 for m in members)),
        )
    return ctx


def build_sql(raw, status_df, search_df, wide, primary, audit_status_df):
    SQL.mkdir(parents=True, exist_ok=True)
    tables = {
        "corp_search": search_df,
        "financials_status": status_df,
        "financials_audit_status": audit_status_df,
        "financials_raw": raw.drop(columns=["localname"]),
        "company_metrics": wide,
    }
    db.write_sqlite(SQL / "dart.db", tables)
    db.dump_schema_sql(SQL / "schema.sql", tables)
    db.dump_insert_sql(SQL / "company_metrics.sql", "company_metrics", wide)
    db.dump_insert_sql(SQL / "corp_search.sql", "corp_search", search_df)
    (SQL / "analysis_queries.sql").write_text(ANALYSIS_QUERIES, encoding="utf-8")

    # tabulate(to_markdown)는 "01921913"처럼 숫자로만 이뤄진 문자열 ID를 과학적 표기 float로
    # 잘못 해석한다(예: 1.92191e+06). 기업코드 열만 콕 집어 숫자 파싱을 꺼서 원문 그대로 낸다.
    id_cols = {"기업코드", "corp_code"}

    def _to_md(res: pd.DataFrame) -> str:
        disable = [i for i, c in enumerate(res.columns) if c in id_cols]
        if disable:
            return res.to_markdown(index=False, disable_numparse=disable)
        return res.to_markdown(index=False)

    md = ["# DART 재무 분석 쿼리 결과\n", "`sql/dart.db`(SQLite) 실행 결과.\n"]
    for title, q in NAMED_QUERIES:
        try:
            res = db.run_query(SQL / "dart.db", q)
            md.append(f"## {title}\n\n```sql\n{q.strip()}\n```\n")
            md.append(_to_md(res)); md.append("\n")
        except Exception as e:
            md.append(f"## {title}\n\n(실행 불가: {e})\n")
    (SQL / "query_results.md").write_text("\n".join(md), encoding="utf-8")
    print(f"SQL -> {SQL}")


_COMPANY_ORDER = ["NAVER", "SOOP", "샌드박스네트워크", "패러블엔터테인먼트"]


def _colors(companies):
    pal = config.PALETTE["series"]
    return {corp: pal[i % len(pal)] for i, corp in enumerate(companies)}


def build_charts(primary: pd.DataFrame, search_df: pd.DataFrame) -> list[str]:
    CHARTS.mkdir(parents=True, exist_ok=True)
    viz.apply_style()
    made = []
    present = set(primary["corp_name"].unique())
    companies = [c for c in _COMPANY_ORDER if c in present] + \
        sorted(present - set(_COMPANY_ORDER))
    cmap = _colors(companies)

    # 1. 매출(영업수익) 추이 — 회사 간 스케일 차이가 커서(NAVER 12조원 vs 패러블 200억원)
    # 회사별 별도 서브플롯으로 그린다.
    ncols = min(len(companies), 2)
    nrows = -(-len(companies) // ncols)  # ceil
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 4.6 * nrows), sharex=False)
    axes = np.atleast_1d(axes).ravel()
    for ax in axes[len(companies):]:
        ax.axis("off")
    for ax, corp in zip(axes, companies):
        d = primary[primary["corp_name"] == corp].sort_values("bsns_year")
        ax.plot(d["bsns_year"], d["revenue"] / 1e8, marker="o", color=cmap[corp], linewidth=2)
        ax.set_title(f"{corp} 매출(영업수익) 추이")
        ax.set_ylabel("억원")
        ax.grid(True, zorder=0)
    fig.suptitle("연도별 매출 추이 (연결재무제표 기준, 단위: 억원)")
    fig.tight_layout()
    fig.savefig(CHARTS / "01_revenue_trend.png", dpi=140); plt.close(fig)
    made.append("01_revenue_trend.png")

    # 2. 매출 성장 지수 (첫 연도=100) — 스케일 무관 비교
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for corp in companies:
        d = primary[primary["corp_name"] == corp].sort_values("bsns_year")
        base = d["revenue"].iloc[0]
        idx = d["revenue"] / base * 100
        ax.plot(d["bsns_year"], idx, marker="o", color=cmap[corp], linewidth=2, label=corp)
    ax.axhline(100, color=config.INK["grid"], linewidth=1, linestyle="--")
    ax.set_title(f"매출 성장 지수 ({primary['bsns_year'].min()}년=100)")
    ax.set_ylabel("지수"); ax.legend(frameon=False); ax.grid(True, zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "02_revenue_index.png", dpi=140); plt.close(fig)
    made.append("02_revenue_index.png")

    # 3. 영업이익률 추이
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for corp in companies:
        d = primary[primary["corp_name"] == corp].sort_values("bsns_year")
        ax.plot(d["bsns_year"], d["operating_margin"] * 100, marker="o", color=cmap[corp],
                linewidth=2, label=corp)
    ax.set_title("영업이익률 추이"); ax.set_ylabel("%"); ax.legend(frameon=False); ax.grid(True, zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "03_operating_margin.png", dpi=140); plt.close(fig)
    made.append("03_operating_margin.png")

    # 4. 자산 대비 매출 효율(자산회전율)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for corp in companies:
        d = primary[primary["corp_name"] == corp].sort_values("bsns_year")
        ax.plot(d["bsns_year"], d["asset_turnover"], marker="o", color=cmap[corp],
                linewidth=2, label=corp)
    ax.set_title("자산 대비 매출 효율 (매출/자산총계)"); ax.set_ylabel("배")
    ax.legend(frameon=False); ax.grid(True, zorder=0)
    fig.tight_layout(); fig.savefig(CHARTS / "04_asset_turnover.png", dpi=140); plt.close(fig)
    made.append("04_asset_turnover.png")

    # 5. 대상 법인 DART 커버리지 — "없다"도 결과라는 걸 보여주는 차트.
    # 재무제표를 실제로 어느 경로로 확보했는지(XBRL 정기보고서 vs 감사보고서 원문 파싱)까지
    # 구분해서 보여준다 — "기업코드가 있다"≠"재무제표가 있다"는 이 프로젝트의 핵심 발견이다.
    d = search_df.copy()
    d["status"] = np.where(d["matched"], "기업코드 있음", "기업코드 없음")
    order = d.sort_values(["matched", "label"], ascending=[False, True])
    colors_map = {"기업코드 있음": config.PALETTE["series"][2], "기업코드 없음": config.PALETTE["series"][7]}
    fig, ax = plt.subplots(figsize=(9, 6))
    y = range(len(order))
    ax.barh(y, [1] * len(order), color=[colors_map[s] for s in order["status"]], height=0.6, zorder=3)
    ax.set_yticks(list(y)); ax.set_yticklabels(order["label"], fontsize=9)
    ax.set_xticks([])
    ax.set_title("대상 법인 DART 등재 여부 및 재무제표 확보 경로")
    xbrl_companies = {"NAVER", "SOOP"}
    audit_companies = present - xbrl_companies
    for i, (_, r) in enumerate(order.iterrows()):
        if r["corp_name"] in xbrl_companies:
            note = "재무제표 확보(정기보고서 XBRL)"
        elif r["corp_name"] in audit_companies:
            note = "재무제표 확보(감사보고서 원문 파싱)"
        elif r.get("category") == "동명이인":
            note = "확보했으나 동명이인이라 제외"
        elif r["matched"]:
            note = "기업코드만 확인(공시 없음)" if r["corp_name"] == "팬딩" else "기업코드만 확인"
        else:
            note = "미등재"
        ax.annotate(note, (1.02, i), va="center", fontsize=8.5, color=config.INK["muted"])
    ax.set_xlim(0, 2.9)
    fig.tight_layout(); fig.savefig(CHARTS / "05_coverage.png", dpi=140); plt.close(fig)
    made.append("05_coverage.png")

    print(f"차트 {len(made)}종 -> {CHARTS}")
    return made


def build_outputs(raw, status_df, search_df, wide, primary, charts, fandom_ctx, audit_status_df):
    wide.to_csv(DATA / "company_metrics_wide.csv", index=False)
    primary.to_csv(DATA / "company_metrics.csv", index=False)

    meta = json.loads((DATA / "_meta.json").read_text(encoding="utf-8"))
    SITE.mkdir(parents=True, exist_ok=True)

    companies_json = json.loads(primary.replace({np.nan: None}).to_json(orient="records"))
    search_json = json.loads(search_df.replace({np.nan: None}).to_json(orient="records"))
    status_summary = {}
    for corp, g in status_df.groupby("corp_name"):
        counts = g["status"].astype(str).str.zfill(3).value_counts()
        status_summary[str(corp)] = {str(k): int(v) for k, v in counts.items()}
    audit_status_summary = {}
    if len(audit_status_df):
        for corp, g in audit_status_df.groupby("corp_name"):
            counts = g["status"].astype(str).value_counts()
            audit_status_summary[str(corp)] = {str(k): int(v) for k, v in counts.items()}

    site_data = dict(
        meta=meta,
        target_search=search_json,
        companies=companies_json,
        status_summary=status_summary,
        audit_status_summary=audit_status_summary,
        fandom_context=fandom_ctx,
    )
    (SITE / "data.json").write_text(json.dumps(site_data, ensure_ascii=False, indent=2), encoding="utf-8")

    n_total = len(search_df)
    n_matched = int(search_df["matched"].sum())
    n_fin = primary["corp_name"].nunique()
    not_matched = search_df[~search_df["matched"]]
    matched_no_fin = search_df[search_df["matched"] & ~search_df["corp_name"].isin(primary["corp_name"].unique())]
    # 팬딩은 감사보고서 경로까지 확장한 뒤에도 filings.csv에 단 한 건도 없다 — corp_code는
    # 있지만 DART에 어떤 보고서도 낸 적이 없는 유일한 매칭 법인.
    matched_no_filings = matched_no_fin[matched_no_fin["corp_name"] == "팬딩"]
    matched_audit_only_no_data = matched_no_fin[matched_no_fin["corp_name"] != "팬딩"]

    naver = primary[primary["corp_name"] == "NAVER"].sort_values("bsns_year")
    soop = primary[primary["corp_name"] == "SOOP"].sort_values("bsns_year")
    sandbox = primary[primary["corp_name"] == "샌드박스네트워크"].sort_values("bsns_year")
    parable = primary[primary["corp_name"] == "패러블엔터테인먼트"].sort_values("bsns_year")

    lines = [
        "# 프로젝트 9 · DART 재무 분석 — 스텔라이브 팬덤과 실제 재무 사이의 간극\n",
        "- 데이터 소스: Open DART(전자공시시스템) Open API — `corpCode.xml`, `company.json`, "
        "`list.json`, `fnlttSinglAcntAll.json`(정기보고서 XBRL), `document.xml`(감사보고서 원문)",
        f"- 수집 시각: {meta['fetched_at'][:19]} UTC · 조사 대상 {n_total}곳 · "
        f"기업코드 확인 {n_matched}곳 · **구조화된 재무제표 확보 {n_fin}곳**\n",
        "## 이 프로젝트가 다른 이유\n",
        "01~06·08은 조회수·구독자·동시시청자 같은 **인기 프록시**를 측정한다. 09는 포트폴리오에서",
        "유일하게 **감사받은 법정 공시 데이터**(재무제표)를 다룬다. 처음에는 XBRL 경로",
        "(`fnlttSinglAcntAll`)로 NAVER·SOOP 2곳만 확보했지만, 이후 **감사보고서 원문",
        "(`document.xml`)을 직접 파싱하는 두 번째 경로**를 추가해 샌드박스네트워크·",
        "패러블엔터테인먼트까지 확보했다 — 자세한 내용은 아래 '감사보고서 원문 파싱' 절 참고.\n",
        "## 무엇을 찾지 못했는가 (핵심 발견)\n",
    ]
    for _, r in not_matched.iterrows():
        lines.append(f"- **{r['label']}** — {r['note']}")
    if len(matched_no_filings):
        lines.append("")
        lines.append("기업코드는 확인되지만 **감사보고서를 포함해 DART에 낸 공시가 단 한 건도 없는** 법인:")
        for _, r in matched_no_filings.iterrows():
            lines.append(f"- **{r['label']}** ({r['corp_name']}, {r['corp_code']}) — "
                          "`list.json`을 `pblntf_ty` 제한 없이·1999년부터 전체 기간으로 조회해도 0건. "
                          "감사보고서 경로를 추가한 뒤에도 마찬가지다(`data/filings.csv` 참고).")
    if len(matched_audit_only_no_data):
        lines.append("")
        lines.append("아래 법인은 분석에서 의도적으로 제외했다(재무 수치가 없어서가 아니다):")
        for _, r in matched_audit_only_no_data.iterrows():
            if r["category"] == "동명이인":
                lines.append(
                    f"- **{r['label']}** ({r['corp_name']}, {r['corp_code']}) — 감사보고서 원문 파싱은 "
                    "정상적으로 됐다(재무 수치 확보). 다만 이 법인은 K-pop 걸그룹 '브레이브걸스' 소속사이고, "
                    "이 프로젝트가 다루는 VTuber Brave group과는 이름만 같은 별개 법인이다 — 혼동을 막기 위해 "
                    "결과 통합·차트·리포트에서 계속 제외한다.")
            else:
                lines.append(f"- **{r['label']}** ({r['corp_name']}, {r['corp_code']})")
    lines += [
        "",
        "**왜 XBRL 경로만으로는 부족한가.** `fnlttSinglAcntAll.json`은 XBRL이 태깅된 **정기보고서**",
        "(사업보고서·반기보고서·분기보고서)만 파싱한다. 이건 사실상 상장사 + 일부 대형 비상장사의",
        "몫이다. 샌드박스네트워크·패러블엔터테인먼트·팬딩·브레이브엔터테인먼트는 「외부감사법」에",
        "따라 **감사보고서**만 금융감독원에 제출하면 되고, 이 감사보고서는 이 API가 파싱하는",
        "XBRL 재무제표 세트에 포함되지 않는다 — 그래서 corp_code가 있어도 013(데이터 없음)이",
        "정상 결과로 나온다. 이 한계 자체는 여전히 유효한 발견이다.\n",
        "스텔라이브(주식회사 스텔라이브, 2023.4 설립) 자체와 Brave group(일본 모기업) 한국법인은",
        "기업코드 마스터(118,701개 법인)에서조차 검색되지 않았다 — 아직 DART에 어떤 보고서도",
        "낸 적이 없다는 뜻이다(외부감사 대상 요건 미달 또는 감사보고서 제출 이전 시점일 가능성).",
        "감사보고서 경로를 추가해도 애초에 없는 필링을 만들어낼 수는 없으므로 이 결론은 그대로다.\n",
        "## 감사보고서 원문 파싱: 013을 넘어서다\n",
        "`fnlttSinglAcntAll`이 013을 반환하는 법인도 실제로는 `list.json`을 `pblntf_ty=F`",
        "(외부감사관련)로 조회하면 감사보고서/연결감사보고서 이력이 나온다. 그 공시의",
        "`rcept_no`로 `document.xml`을 요청하면 ZIP이 오는데, 압축을 풀면 DART 자체 DTD",
        "(`dart3.xsd`/`dart4.xsd`)로 작성된 XML이 나온다 — XBRL이 아니라 DART의 전자공시 뷰어가",
        "직접 렌더링하는 원본 서식이다. 실제로 확인한 구조:",
        "",
        "- 별도재무제표(OFS): `<TITLE>재 무 상 태 표</TITLE>` 같은 제목 태그 뒤에 표준",
        "  계정코드(`ACODE`, 예: 자산총계=`11500000010000`, 매출액=`12100000010000`)가 붙은",
        "  `<TE>` 셀로 이루어진 표.",
        "- 연결재무제표(CFS): `<TITLE>` 태그 없이 일반 `<TD>` 셀 + \"과목/주석/당기/전기\" 헤더만",
        "  있는 표 — ACODE가 없어 계정과목 **텍스트**(\"자산총계\", \"영업수익\" 등)로 매칭해야 한다.",
        "- 오래된 필링(2019~2021년경)은 XML 선언에 `encoding=\"utf-8\"`이라고 적혀 있어도 실제",
        "  바이트는 EUC-KR인 경우가 있었다 — 선언을 믿지 않고 utf-8 → euc-kr 순으로 디코딩",
        "  시도해서 처리했다.",
        "- \"영업이익(손실)\"처럼 이익/손실을 한 라벨에 합쳐 괄호로 부호를 표시하는 경우와,",
        "  \"영업손실\"처럼 별도 라벨로 나오되 값 자체는 부호 없는 양수(손실 크기)로 찍히는",
        "  경우가 **같은 회사, 다른 연도**에 둘 다 나타났다 — 손실 전용 라벨은 항상 음수로",
        "  강제(`-abs`)해서 통일했다.",
        "",
        "**단위 검증.** 재무상태표·손익계산서 본표는 표 제목 옆에 `(단위 : 원)`이 명시돼 있고,",
        "실제로 모든 표본에서 원(KRW) 단위였다. 반면 뒤쪽 **주석(Notes)** 표는 종종",
        "`(단위: 천원)`을 쓴다 — 주석까지 잘못 읽으면 1,000배 오차가 난다. 이를 피하려고",
        "각 재무제표 제목 뒤에 나오는 **첫 번째** 데이터 표만 쓰고 이후 표는 보지 않는다.",
        "",
        "**교차검증 (실제로 수행한 방법).** 인접 연도의 감사보고서는 당기·전기 비교치를 함께",
        "싣는다. 예를 들어 샌드박스네트워크 연결재무제표 기준 2024년 자산총계는 "
        "'연결감사보고서 (2024.12)' 파일의 **당기**란과 '연결감사보고서 (2025.12)' 파일의",
        "**전기**란에 각각 독립적으로 인쇄돼 있는데, 파싱 결과 두 값이 정확히",
        "32,389,420,968원으로 일치했다(원문 XML을 직접 열어 `(87,891,190,875)` 같은",
        "괄호-음수 표기까지 육안으로 대조). 10개 필링에 걸쳐 이런 당기/전기 값이 어긋난",
        "사례는 없었다.\n",
    ]
    audit_targets = [("샌드박스네트워크", sandbox), ("패러블엔터테인먼트", parable)]
    for name, d in audit_targets:
        if not len(d):
            continue
        last = d.iloc[-1]
        fs_label = "연결" if last["fs_div"] == "CFS" else "별도"
        lines.append(
            f"- **{name}** ({int(d['bsns_year'].min())}~{int(d['bsns_year'].max())}년, {fs_label} 우선): "
            f"{int(last['bsns_year'])}년 매출 {last['revenue']/1e8:,.1f}억원, "
            f"영업이익 {last['operating_income']/1e8:,.1f}억원, "
            f"당기순이익 {last['net_income']/1e8:,.1f}억원, "
            f"자산총계 {last['assets']/1e8:,.1f}억원"
            + (f" (자본총계 {last['equity']/1e8:,.1f}억원 — 자본잠식)" if last["equity"] < 0 else "")
        )
    lines.append("")
    lines.append(
        "**팬딩(Fanding)은 이 경로로도 데이터가 없다.** `list.json`을 `pblntf_ty` 제한 없이 "
        "전체 기간(1999~현재)으로 조회해도 팬딩(`01921913`)의 공시 이력은 0건이다 — "
        "`company.json`으로 법인 자체는 확인되지만(2018.9 설립, 대표 엄세현), 감사보고서를 "
        "포함해 DART에 어떤 보고서도 제출한 적이 없다. **프로젝트 11(팬 커머스)이 이 프로젝트의 "
        "DART 데이터로 팬딩의 매출·손익을 확인할 수는 없다** — 이 결론은 XBRL 경로에서도, "
        "감사보고서 경로에서도 동일하다."
    )
    lines += [
        "",
        "인건비 비중은 여전히 산출하지 못했다: 두 경로 모두 재무제표 본표(재무상태표·손익계산서·",
        "현금흐름표·자본변동표)에는 인건비가 별도 계정으로 없다(기능별 표시 손익계산서라",
        "'영업비용' 한 줄로 뭉쳐 있음). 인건비는 감사보고서 **주석**에만 나오는데, 주석 표는",
        "단위가 '천원'으로 바뀌는 경우가 많고 표 구조도 회사·연도마다 제각각이라 이번 파싱",
        "범위에서 의도적으로 제외했다 — 억지로 추정치를 만들지 않고 '산출 불가'로 남긴다.\n",
        "## 확보한 데이터로 본 것 (연결재무제표 우선)\n",
    ]
    if len(naver) and len(soop):
        n_last, s_last = naver.iloc[-1], soop.iloc[-1]
        lines += [
            f"- **{int(n_last['bsns_year'])}년 매출**: NAVER {n_last['revenue']/1e8:,.0f}억원 vs "
            f"SOOP {s_last['revenue']/1e8:,.0f}억원 (약 {n_last['revenue']/s_last['revenue']:.0f}배 규모차)",
            f"- **영업이익률**: NAVER {n_last['operating_margin']*100:.1f}% vs SOOP {s_last['operating_margin']*100:.1f}%",
            f"- **자산 대비 매출 효율**: NAVER {n_last['asset_turnover']:.2f}배 vs SOOP {s_last['asset_turnover']:.2f}배",
        ]
        rev_start_year = int(naver['bsns_year'].iloc[0])
        n_cagr = (n_last['revenue'] / naver.iloc[0]['revenue']) ** (1 / (len(naver) - 1)) - 1
        s_cagr = (s_last['revenue'] / soop.iloc[0]['revenue']) ** (1 / (len(soop) - 1)) - 1
        lines.append(
            f"- **{rev_start_year}~{int(n_last['bsns_year'])}년 매출 CAGR**: NAVER {n_cagr*100:.1f}%/년 "
            f"vs SOOP {s_cagr*100:.1f}%/년"
        )
    if len(sandbox):
        s_last = sandbox.iloc[-1]
        lines.append(
            f"- **샌드박스네트워크**: {int(s_last['bsns_year'])}년 매출 {s_last['revenue']/1e8:,.0f}억원, "
            f"영업이익률 {s_last['operating_margin']*100:.1f}% — 2024~2025년 연결기준 자본총계가 "
            f"음수(완전자본잠식)로 전환됐다(우선주 관련 부채 재분류 등 회계상 사유 가능성, 이 데이터만으로는 "
            f"원인을 특정할 수 없다)."
        )
    if len(parable):
        p_last = parable.iloc[-1]
        lines.append(
            f"- **패러블엔터테인먼트**: {int(p_last['bsns_year'])}년 매출 {p_last['revenue']/1e8:,.0f}억원"
            + (f"으로 전년({parable.iloc[0]['revenue']/1e8:,.0f}억원) 대비 소폭 증가했지만 "
               f"영업이익은 {p_last['operating_income']/1e8:,.0f}억원 적자로 전환됐다(전년 흑자 "
               f"{parable.iloc[0]['operating_income']/1e8:,.0f}억원)." if len(parable) > 1 else ".")
        )
    lines += [
        "",
        "## 팬덤 지표와 나란히 놓아보면\n",
    ]
    p1 = fandom_ctx.get("project01"); p8 = fandom_ctx.get("project08")
    if p1:
        lines.append(f"- 프로젝트1(2026-08 스냅샷): 스텔라이브 11명 합산 구독자 {p1['total_subscribers']:,}명")
    if p8:
        lines.append(f"- 프로젝트8(2026-08 스냅샷): 관측 {p8['coverage']['span_hours']:.1f}시간, "
                      f"팔로워 증감 합계 {p8['total_follower_delta']:+,}명")
    lines += [
        "",
        "**상관관계는 계산하지 않았다.** ① 스텔라이브 자체의 재무제표가 없어 '팬덤 지표 ↔ 자사",
        "재무'라는 원래 질문 자체가 이 데이터로는 답이 안 나온다(패러블엔터테인먼트는 이세계아이돌",
        "소속사이지만 스텔라이브와는 다른 법인이다). ② NAVER·SOOP는 플랫폼 전체 실적이라",
        "스텔라이브라는 개별 크리에이터 그룹의 기여분을 분리할 수 없다. ③ 재무제표는 회계연도",
        "단위이고 팬덤 지표는 2026-08 시점 스냅샷이라 기간도 어긋난다. 숫자 몇 개로 인과관계를",
        "만드는 대신, 이 세 가지 이유를 그대로 남기는 쪽을 택했다.\n",
        "## 산출물",
        "- `data/corp_search.csv` 대상 법인 검색 결과(찾음/못찾음 사유 포함)",
        "- `data/company_overview.csv`·`data/filings.csv` 기업 개요·공시 이력(기업코드 확보분)",
        "- `data/financials_status.csv` XBRL(정기보고서) 재무제표 API 호출 로그(013 포함)",
        "- `data/financials_raw.csv` XBRL 경로로 확보된 재무제표 원자료(SOOP·NAVER, 계정별 롱포맷)",
        "- `data/financials_audit_status.csv` 감사보고서(document.xml) 파싱 시도 로그(필링별)",
        "- `data/financials_audit_raw.csv` 감사보고서 원문에서 파싱한 재무제표 원자료(계정별 롱포맷)",
        "- `data/company_metrics.csv` 회사×연도 핵심 지표(두 경로 통합, 연결 우선)",
        "- `sql/` 스키마·INSERT·분석쿼리·SQLite·실행결과",
        f"- `charts/` 차트 {len(charts)}종(매출 추이·성장 지수·영업이익률·자산회전율·DART 커버리지)",
        "- `site/index.html` 대시보드",
    ]
    (HERE / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"리포트/사이트 데이터 -> {HERE}")


NAMED_QUERIES = [
    ("대상 법인 검색 결과", """
SELECT label AS 대상, category AS 구분, matched AS 기업코드확인, corp_name AS 법인명,
       corp_code AS 기업코드, note AS 비고
FROM corp_search ORDER BY matched DESC, category;"""),
    ("재무제표 확보 현황 (연도별 status)", """
SELECT corp_name AS 법인명, bsns_year AS 사업연도, fs_div AS 재무제표구분,
       status AS 상태코드, status_msg AS 상태, n_rows AS 계정수
FROM financials_status ORDER BY corp_name, bsns_year, fs_div;"""),
    ("연도별 매출·영업이익 (연결/별도 혼합, company_metrics)", """
SELECT corp_name AS 법인명, bsns_year AS 사업연도, fs_div AS 구분,
       ROUND(revenue/1e8,0) AS 매출_억원, ROUND(operating_income/1e8,0) AS 영업이익_억원,
       ROUND(operating_margin*100,1) AS 영업이익률_pct
FROM company_metrics WHERE revenue IS NOT NULL ORDER BY corp_name, bsns_year;"""),
    ("자산 대비 매출 효율 랭킹 (연도×회사)", """
SELECT corp_name AS 법인명, bsns_year AS 사업연도, ROUND(asset_turnover,2) AS 자산회전율,
       ROUND(equity_ratio*100,1) AS 자기자본비율_pct
FROM company_metrics WHERE asset_turnover IS NOT NULL
ORDER BY 자산회전율 DESC LIMIT 10;"""),
    ("013(데이터 없음) 비중 — XBRL(정기보고서) 경로의 한계 정량화", """
SELECT corp_name AS 법인명,
       SUM(CASE WHEN status='000' THEN 1 ELSE 0 END) AS 성공,
       SUM(CASE WHEN status='013' THEN 1 ELSE 0 END) AS 데이터없음,
       COUNT(*) AS 전체시도
FROM financials_status GROUP BY corp_name ORDER BY 성공 DESC;"""),
    ("감사보고서 원문 파싱 경로 — 필링별 확보 현황", """
SELECT corp_name AS 법인명, bsns_year AS 사업연도, fs_div AS 재무제표구분,
       report_nm AS 공시명, status AS 상태코드, n_rows AS 추출계정수
FROM financials_audit_status ORDER BY corp_name, bsns_year, fs_div;"""),
    ("비상장 팬덤 인접 기업 재무 (감사보고서 원문 파싱으로 확보, 연결 우선)", """
SELECT corp_name AS 법인명, bsns_year AS 사업연도, fs_div AS 구분,
       ROUND(revenue/1e8,1) AS 매출_억원, ROUND(operating_income/1e8,1) AS 영업이익_억원,
       ROUND(net_income/1e8,1) AS 당기순이익_억원, ROUND(assets/1e8,1) AS 자산총계_억원
FROM company_metrics
WHERE corp_name IN ('샌드박스네트워크','패러블엔터테인먼트') AND revenue IS NOT NULL
ORDER BY corp_name, bsns_year;"""),
]
ANALYSIS_QUERIES = "-- DART 재무 분석 쿼리 (SQLite: sql/dart.db)\n\n" + \
    "\n\n".join(f"-- {t}{q}" for t, q in NAMED_QUERIES) + "\n"


def main():
    search_df = pd.read_csv(DATA / "corp_search.csv", dtype={"corp_code": str, "stock_code": str})
    raw = load_raw(search_df)
    status_df = pd.read_csv(DATA / "financials_status.csv", dtype={"corp_code": str})
    audit_status_path = DATA / "financials_audit_status.csv"
    audit_status_df = (pd.read_csv(audit_status_path, dtype={"corp_code": str})
                        if audit_status_path.exists() else pd.DataFrame())

    wide = build_metrics(raw)
    primary = pick_primary(wide)
    fandom_ctx = load_fandom_context()

    build_sql(raw, status_df, search_df, wide, primary, audit_status_df)
    charts = build_charts(primary, search_df)
    build_outputs(raw, status_df, search_df, wide, primary, charts, fandom_ctx, audit_status_df)

    print("\n=== 대상 법인 검색 요약 ===")
    print(search_df[["label", "category", "matched", "corp_name", "note"]].to_string(index=False))
    print("\n=== 확보한 회사×연도 핵심 지표 ===")
    cols = ["corp_name", "bsns_year", "fs_div", "revenue", "operating_income",
            "operating_margin", "asset_turnover"]
    with pd.option_context("display.width", 220):
        print(primary[cols].to_string(index=False))


if __name__ == "__main__":
    main()
