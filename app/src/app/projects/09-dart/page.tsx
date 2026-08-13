"use client";

/**
 * 프로젝트 09 · DART 재무 (Phase 2).
 *
 * 회사 단위 프로젝트라 `members[]`가 없다 — 01~06·08의 page.tsx + Suspense +
 * `*PageClient.tsx` 골격을 그대로 베끼지 않는다. 이 페이지는 `useSearchParams`를
 * 쓰지 않아서(회사·연도 필터는 로컬 `useState`) `<Suspense>` 경계가 애초에
 * 필요 없다 — `/methodology`가 순수 서버 컴포넌트로 남는 것과 같은 이유
 * (methodology/page.tsx 상단 주석 참고). 다만 이 페이지는 필터·정렬 같은
 * 클라이언트 상태가 있어 "use client" 단일 파일로 충분하다.
 *
 * 전역 멤버/유닛 필터(FR-1, `<FilterBar />`/`useFilters()`)는 의도적으로 쓰지
 * 않는다 — 이 프로젝트의 조인 키는 멤버가 아니라 회사×회계연도다.
 */
import { useMemo, useState } from "react";
import Badge from "@/components/Badge";
import Card from "@/components/Card";
import FilterChip from "@/components/FilterChip";
import Freshness from "@/components/Freshness";
import Section from "@/components/Section";
import StatTile from "@/components/StatTile";
import Table, { type TableColumn } from "@/components/Table";
import LineChart, { type LineSeriesDatum } from "@/components/charts/LineChart";
import ScatterPlot, { type ScatterDatum } from "@/components/charts/ScatterPlot";
import { memberColor } from "@/components/charts/chartUtils";
import data09 from "@/data/09.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import type { Company09, Data09, TargetSearch09 } from "@/data/types";
import styles from "./page.module.css";

const data = data09 as Data09;

function eok(v: number): string {
  return `${Math.round(v / 100_000_000).toLocaleString("ko-KR")}억`;
}

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

function pctYoy(v: number | null): string {
  if (v === null) return "—";
  return `${v >= 0 ? "+" : ""}${(v * 100).toFixed(1)}%`;
}

const COMPANIES = Array.from(new Set(data.companies.map((c) => c.corp_name)));
const YEARS = Array.from(new Set(data.companies.map((c) => c.bsns_year))).sort((a, b) => a - b);

const parableRows = data.companies
  .filter((c) => c.corp_name === "패러블엔터테인먼트")
  .sort((a, b) => a.bsns_year - b.bsns_year);
const sandboxRows = data.companies.filter((c) => c.corp_name === "샌드박스네트워크");
const sandboxAlwaysLoss = sandboxRows.length > 0 && sandboxRows.every((c) => c.operating_income < 0);

export default function Page() {
  const [companyFilter, setCompanyFilter] = useState<string[]>([]);
  const [yearFilter, setYearFilter] = useState<number[]>([]);

  const toggleCompany = (name: string) =>
    setCompanyFilter((cur) => (cur.includes(name) ? cur.filter((c) => c !== name) : [...cur, name]));
  const toggleYear = (year: number) =>
    setYearFilter((cur) => (cur.includes(year) ? cur.filter((y) => y !== year) : [...cur, year]));
  const resetFilters = () => {
    setCompanyFilter([]);
    setYearFilter([]);
  };
  const hasActiveFilters = companyFilter.length > 0 || yearFilter.length > 0;

  const filteredCompanies = useMemo(
    () =>
      data.companies.filter(
        (c) =>
          (companyFilter.length === 0 || companyFilter.includes(c.corp_name)) &&
          (yearFilter.length === 0 || yearFilter.includes(c.bsns_year))
      ),
    [companyFilter, yearFilter]
  );

  const revenueSeries: LineSeriesDatum[] = useMemo(() => {
    const byCompany = new Map<string, { x: number; y: number }[]>();
    for (const c of filteredCompanies) {
      if (!byCompany.has(c.corp_name)) byCompany.set(c.corp_name, []);
      byCompany.get(c.corp_name)!.push({ x: c.bsns_year, y: c.revenue });
    }
    return [...byCompany.entries()].map(([name, points]) => ({ name_en: name, label: name, points }));
  }, [filteredCompanies]);

  const marginSeries: LineSeriesDatum[] = useMemo(() => {
    const byCompany = new Map<string, { x: number; y: number }[]>();
    for (const c of filteredCompanies) {
      if (!byCompany.has(c.corp_name)) byCompany.set(c.corp_name, []);
      byCompany.get(c.corp_name)!.push({ x: c.bsns_year, y: c.operating_margin });
    }
    return [...byCompany.entries()].map(([name, points]) => ({ name_en: name, label: name, points }));
  }, [filteredCompanies]);

  const latestScatter: ScatterDatum[] = useMemo(() => {
    const latestByCompany = new Map<string, Company09>();
    for (const c of filteredCompanies) {
      const cur = latestByCompany.get(c.corp_name);
      if (!cur || c.bsns_year > cur.bsns_year) latestByCompany.set(c.corp_name, c);
    }
    return [...latestByCompany.values()].map((c) => ({
      name_en: c.corp_name,
      label: `${c.corp_name} · ${c.bsns_year}`,
      x: c.revenue,
      y: c.operating_margin,
      size: c.assets,
    }));
  }, [filteredCompanies]);

  const companyColumns: TableColumn<Company09>[] = [
    { key: "corp_name", header: "회사", accessor: (r) => r.corp_name },
    { key: "bsns_year", header: "연도", accessor: (r) => r.bsns_year, align: "right" },
    { key: "fs_div", header: "재무제표", accessor: (r) => r.fs_div },
    { key: "revenue", header: "매출", accessor: (r) => r.revenue, align: "right", render: (r) => eok(r.revenue) },
    {
      key: "operating_income",
      header: "영업이익",
      accessor: (r) => r.operating_income,
      align: "right",
      render: (r) => eok(r.operating_income),
    },
    {
      key: "operating_margin",
      header: "영업이익률",
      accessor: (r) => r.operating_margin,
      align: "right",
      render: (r) => pct(r.operating_margin),
    },
    {
      key: "net_margin",
      header: "순이익률",
      accessor: (r) => r.net_margin,
      align: "right",
      render: (r) => pct(r.net_margin),
    },
    {
      key: "debt_to_equity",
      header: "부채비율",
      accessor: (r) => r.debt_to_equity,
      align: "right",
      render: (r) => r.debt_to_equity.toFixed(2),
    },
    {
      key: "revenue_yoy",
      header: "매출 YoY",
      accessor: (r) => r.revenue_yoy ?? -Infinity,
      align: "right",
      render: (r) => pctYoy(r.revenue_yoy),
    },
  ];

  const searchColumns: TableColumn<TargetSearch09>[] = [
    { key: "label", header: "검색 대상", accessor: (r) => r.label },
    { key: "category", header: "구분", accessor: (r) => r.category },
    {
      key: "matched",
      header: "매칭",
      accessor: (r) => (r.matched ? 1 : 0),
      render: (r) => <Badge tone={r.matched ? "positive" : "negative"}>{r.matched ? "매칭됨" : "미매칭"}</Badge>,
    },
    { key: "corp_name", header: "DART 법인명", accessor: (r) => r.corp_name ?? "—" },
    { key: "corp_code", header: "기업코드", accessor: (r) => r.corp_code ?? "—" },
    { key: "note", header: "비고", accessor: (r) => r.note },
  ];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 09</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>DART 재무</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["09"]} cadenceLabel={REFRESH_LABEL["09"]} />
        </div>
        <p className={styles.subhead}>
          DART(전자공시시스템) 법인코드 마스터 {data.meta.corp_master_total.toLocaleString("ko-KR")}개 중{" "}
          {data.meta.n_targets}개 법인을 검색해 {data.meta.n_matched}개를 찾았고, 그중 재무 수치를 확보한 곳은{" "}
          {data.meta.n_with_financials + data.meta.n_with_audit_report_financials}곳이다. 회사·유닛이 아니라{" "}
          <strong>회사×회계연도</strong>가 조인 키라 멤버/유닛 필터는 이 페이지에 걸지 않는다.
        </p>
      </header>

      <Card padding="lg" className={styles.insightCard}>
        <Badge tone="negative">핵심 발견</Badge>
        <p className={styles.insightText}>
          스텔라이브 본체와 일본 모기업 Brave group은 법인코드 마스터{" "}
          {data.meta.corp_master_total.toLocaleString("ko-KR")}개 전체에서 검색되지 않는다. 팬딩은 기업코드는
          있지만(감사보고서 매년 제출 의무가 있음에도) 실제 제출된 필링이 0건이다. 재무 수치를 얻은 곳은
          NAVER·SOOP(XBRL 정기보고서) 2곳과, 감사보고서 원문을 직접 파싱해 확보한 샌드박스네트워크·패러블엔터테인먼트
          2곳뿐이다 — 경위는 <a href="/methodology">/methodology</a>의 &quot;DART XBRL 커버리지 한계&quot; 카드에
          있다.
        </p>
      </Card>

      {parableRows.length >= 2 ? (
        <Card padding="lg" className={styles.insightCard}>
          <Badge tone="cautionary">주목할 수치</Badge>
          <p className={styles.insightText}>
            패러블엔터테인먼트(이세계아이돌 소속사)는 {parableRows[0].bsns_year}→{parableRows[1].bsns_year}년 매출이{" "}
            {eok(parableRows[0].revenue)}에서 {eok(parableRows[1].revenue)}으로 늘었지만, 영업이익은{" "}
            {eok(parableRows[0].operating_income)}에서 {eok(parableRows[1].operating_income)}으로 흑자에서 적자로
            돌아섰다. 자산은 {eok(parableRows[0].assets)}에서 {eok(parableRows[1].assets)}으로{" "}
            {parableRows[1].assets / parableRows[0].assets < 0.6 ? "거의 반토막났다" : "줄었다"}.
          </p>
        </Card>
      ) : null}

      {sandboxRows.length > 0 ? (
        <Card padding="lg" className={styles.insightCard}>
          <Badge tone={sandboxAlwaysLoss ? "negative" : "neutral"}>비교군 참고</Badge>
          <p className={styles.insightText}>
            샌드박스네트워크는 확보된 {sandboxRows[0].bsns_year}~{sandboxRows[sandboxRows.length - 1].bsns_year}년{" "}
            {sandboxRows.length}개 연도{" "}
            {sandboxAlwaysLoss
              ? "전부 영업손실을 기록했다 — 매출은 커졌지만 흑자로 전환한 해가 한 번도 없다."
              : "중 일부 연도에서 영업손실을 기록했다."}
          </p>
        </Card>
      ) : null}

      <Card padding="lg" className={styles.warnCard}>
        <Badge tone="neutral">상관계수를 계산하지 않은 이유</Badge>
        <p className={styles.insightText}>
          재무 수치를 확보한 회사는 2~4곳뿐이고, 회사마다 확보된 회계연도 범위도 다르다(NAVER·SOOP는{" "}
          {data.meta.years[0]}~{data.meta.years[1]}년, 샌드박스네트워크·패러블엔터테인먼트는 그보다 짧다). 이
          표본으로는 상관계수가 통계적으로 의미가 없어 계산하지 않았다. 프로젝트 01(구독자 {" "}
          {data.fandom_context.project01.total_subscribers.toLocaleString("ko-KR")}명)·08(동시시청자, 팔로워 증감{" "}
          {data.fandom_context.project08.total_follower_delta.toLocaleString("ko-KR")}) 수치도 참고용으로만
          병기한다 — {data.fandom_context.note}
        </p>
      </Card>

      <Section
        eyebrow="Search"
        title="검색 대상과 매칭 결과"
        description="9개 법인을 DART에서 검색한 원본 결과 — 무엇을 찾았고 무엇을 못 찾았는지 투명하게 남긴다."
      />
      <Table
        columns={searchColumns}
        rows={data.target_search}
        getRowKey={(r) => r.query}
        initialSortKey="matched"
        initialSortDir="desc"
        caption="프로젝트 09 · DART 법인 검색 결과 (9건)"
      />

      <Section
        eyebrow="Filters"
        title="필터"
        description="회사·연도로 아래 차트와 표를 함께 좁힌다 (멤버/유닛 필터 아님 — 이 프로젝트는 회사 단위)."
      />
      <div className={styles.filterBar} role="group" aria-label="회사·연도 필터">
        <div className={styles.filterRow}>
          <span className={styles.filterRowLabel}>회사</span>
          <div className={styles.chips}>
            {COMPANIES.map((name) => (
              <FilterChip key={name} label={name} active={companyFilter.includes(name)} onClick={() => toggleCompany(name)} />
            ))}
          </div>
        </div>
        <div className={styles.filterRow}>
          <span className={styles.filterRowLabel}>연도</span>
          <div className={styles.chips}>
            {YEARS.map((year) => (
              <FilterChip key={year} label={String(year)} active={yearFilter.includes(year)} onClick={() => toggleYear(year)} />
            ))}
          </div>
        </div>
        <button type="button" className={styles.reset} onClick={resetFilters} disabled={!hasActiveFilters}>
          필터 초기화
        </button>
      </div>

      <Section eyebrow="Charts" title="회사별 매출 추이" description="x: 회계연도 · y: 매출. 회사마다 확보된 연도 범위가 다르다." />
      {revenueSeries.length > 0 ? (
        <Card padding="md">
          <LineChart series={revenueSeries} title="회사별 매출 추이" xFormat={(v) => String(Math.round(v))} yFormat={eok} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 데이터가 없다.</p>
        </Card>
      )}

      <Section eyebrow="Charts" title="회사별 영업이익률 추이" description="0% 아래는 영업손실 구간이다." />
      {marginSeries.length > 0 ? (
        <Card padding="md">
          <LineChart series={marginSeries} title="회사별 영업이익률 추이" xFormat={(v) => String(Math.round(v))} yFormat={pct} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 데이터가 없다.</p>
        </Card>
      )}

      <Section
        eyebrow="Charts"
        title="최신 연도 스냅샷 — 매출 대비 영업이익률"
        description="x: 매출 · y: 영업이익률 · 버블 크기: 자산. 회사마다 확보된 최신 연도만 1점씩."
      />
      {latestScatter.length > 0 ? (
        <Card padding="md">
          <ScatterPlot
            data={latestScatter}
            title="최신 연도 스냅샷"
            xLabel="매출"
            yLabel="영업이익률"
            xFormat={eok}
            yFormat={pct}
          />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 데이터가 없다.</p>
        </Card>
      )}

      <Section eyebrow="Table" title="전체 재무 지표" description="열 제목을 클릭하면 정렬된다." />
      <Table
        columns={companyColumns}
        rows={filteredCompanies}
        getRowKey={(r) => `${r.corp_name}-${r.bsns_year}-${r.fs_div}`}
        initialSortKey="bsns_year"
        initialSortDir="desc"
        caption={`프로젝트 09 · 회사×회계연도 재무 (${filteredCompanies.length}행)`}
      />

      <div className={styles.statRow}>
        <StatTile label="검색 대상" value={data.meta.n_targets} unit="개 법인" />
        <StatTile label="DART 매칭" value={data.meta.n_matched} unit="개 법인" />
        <StatTile label="XBRL로 확보" value={data.meta.n_with_financials} unit="개 법인" caption="NAVER·SOOP" />
        <StatTile
          label="감사보고서 원문 파싱으로 확보"
          value={data.meta.n_with_audit_report_financials}
          unit="개 법인"
          caption="샌드박스네트워크·패러블엔터테인먼트"
        />
      </div>

      <div className={styles.legendRow}>
        {COMPANIES.map((name) => (
          <span key={name} className={styles.legendItem}>
            <span className={styles.legendSwatch} style={{ background: memberColor(name) }} />
            {name}
          </span>
        ))}
      </div>
    </div>
  );
}
