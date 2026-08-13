"use client";

/**
 * 프로젝트 11 · 팬 커머스 (Phase 2).
 *
 * 플랫폼/회사 단위 프로젝트라 `members[]`가 없다 — 09·10과 같은 이유로 01~06·08의
 * page.tsx + Suspense + `*PageClient.tsx` 골격을 쓰지 않는다. `useSearchParams`를
 * 쓰지 않으므로(플랫폼·카테고리 필터는 로컬 `useState`) `<Suspense>`도 필요
 * 없다. 전역 멤버/유닛 필터(FR-1)도 걸지 않는다.
 *
 * 이 프로젝트는 다른 세션이 동시에 만들고 있었다 — 이 페이지를 쓰는 세션
 * 도중 `youtube_analyze_all/11_fan_commerce/site/data.json`이 도착해서 실제
 * 데이터로 만들었다(허브의 "준비 중" 플레이스홀더 분기는 데이터가 다시
 * 없어지는 경우를 대비해 그대로 남겨둔다 — `isData11Ready()` 참고).
 */
import { useMemo, useState } from "react";
import Badge from "@/components/Badge";
import Card from "@/components/Card";
import FilterChip from "@/components/FilterChip";
import Freshness from "@/components/Freshness";
import Section from "@/components/Section";
import StatTile from "@/components/StatTile";
import Table, { type TableColumn } from "@/components/Table";
import BarChart, { type BarDatum } from "@/components/charts/BarChart";
import data11 from "@/data/11.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import {
  isData11Ready,
  type Company09,
  type Crowdfunding11,
  type Data11,
  type Data11Ready,
  type FandingCreator11,
} from "@/data/types";
import styles from "./page.module.css";

const data = data11 as Data11;

function money(v: number): string {
  const abs = Math.abs(v);
  if (abs >= 100_000_000) return `${(v / 100_000_000).toLocaleString("ko-KR", { maximumFractionDigits: 1 })}억`;
  if (abs >= 10_000) return `${Math.round(v / 10_000).toLocaleString("ko-KR")}만`;
  return `${v.toLocaleString("ko-KR")}원`;
}

function pct1(v: number): string {
  return `${v.toLocaleString("ko-KR", { maximumFractionDigits: 1 })}%`;
}

export default function Page() {
  if (!isData11Ready(data)) {
    return (
      <div className={styles.page}>
        <header className={styles.header}>
          <p className={styles.eyebrow}>Project 11</p>
          <h1 className={styles.title}>팬 커머스</h1>
        </header>
        <Card padding="lg" className={styles.warnCard}>
          <Badge tone="cautionary">준비 중</Badge>
          <p className={styles.insightText}>{data.note}</p>
        </Card>
      </div>
    );
  }

  return <Ready data={data} />;
}

function Ready({ data }: { data: Data11Ready }) {
  const [categoryFilter, setCategoryFilter] = useState<string[]>([]);
  const [platformFilter, setPlatformFilter] = useState<string[]>([]);

  const categories = useMemo(() => Array.from(new Set(data.crowdfunding.map((c) => c.category))), [data.crowdfunding]);
  const platforms = useMemo(() => Array.from(new Set(data.crowdfunding.map((c) => c.platform))), [data.crowdfunding]);

  const toggleCategory = (c: string) =>
    setCategoryFilter((cur) => (cur.includes(c) ? cur.filter((x) => x !== c) : [...cur, c]));
  const togglePlatform = (p: string) =>
    setPlatformFilter((cur) => (cur.includes(p) ? cur.filter((x) => x !== p) : [...cur, p]));
  const resetFilters = () => {
    setCategoryFilter([]);
    setPlatformFilter([]);
  };
  const hasActiveFilters = categoryFilter.length > 0 || platformFilter.length > 0;

  const filteredCrowdfunding = useMemo(
    () =>
      data.crowdfunding.filter(
        (c) =>
          (categoryFilter.length === 0 || categoryFilter.includes(c.category)) &&
          (platformFilter.length === 0 || platformFilter.includes(c.platform))
      ),
    [data.crowdfunding, categoryFilter, platformFilter]
  );

  const officialRows = data.crowdfunding.filter((c) => c.org.includes("패러블엔터테인먼트"));
  const fanmadeRows = data.crowdfunding.filter((c) => c.org.includes("팬 제작"));
  const officialTotalRaised = officialRows.reduce((s, c) => s + c.raised_krw, 0);
  const fanmadeTotalRaised = fanmadeRows.reduce((s, c) => s + c.raised_krw, 0);
  const magnitudeRatio = fanmadeTotalRaised > 0 ? officialTotalRaised / fanmadeTotalRaised : null;

  const crowdfundingBarData: BarDatum[] = useMemo(
    () =>
      [...filteredCrowdfunding]
        .sort((a, b) => b.raised_krw - a.raised_krw)
        .map((c) => ({ name_en: c.slug, label: c.project_name, value: c.raised_krw })),
    [filteredCrowdfunding]
  );

  const fandingBarData: BarDatum[] = useMemo(
    () =>
      [...data.fanding.creator_summary]
        .sort((a, b) => b.avg_price - a.avg_price)
        .slice(0, 15)
        .map((c) => ({ name_en: c.creator_url, label: c.nickname, value: c.avg_price })),
    [data.fanding.creator_summary]
  );

  const crowdfundingColumns: TableColumn<Crowdfunding11>[] = [
    { key: "project_name", header: "프로젝트", accessor: (r) => r.project_name },
    { key: "org", header: "소속", accessor: (r) => r.org },
    {
      key: "category",
      header: "카테고리",
      accessor: (r) => r.category,
      render: (r) => <Badge tone={r.category === "공식 굿즈 펀딩" ? "primary" : "neutral"}>{r.category}</Badge>,
    },
    { key: "platform", header: "플랫폼", accessor: (r) => r.platform },
    {
      key: "goal_krw",
      header: "목표 금액",
      accessor: (r) => r.goal_krw,
      align: "right",
      render: (r) => (
        <>
          {money(r.goal_krw)}
          {r.goal_estimated ? <span className={styles.estimatedMark}> (추정)</span> : null}
        </>
      ),
    },
    { key: "raised_krw", header: "모금액", accessor: (r) => r.raised_krw, align: "right", render: (r) => money(r.raised_krw) },
    { key: "backers", header: "후원자", accessor: (r) => r.backers, align: "right", render: (r) => r.backers.toLocaleString("ko-KR") },
    { key: "achievement_pct", header: "달성률", accessor: (r) => r.achievement_pct, align: "right", render: (r) => pct1(r.achievement_pct) },
    {
      key: "per_backer_krw",
      header: "인당 후원액",
      accessor: (r) => r.per_backer_krw,
      align: "right",
      render: (r) => money(r.per_backer_krw),
    },
    { key: "period_start", header: "기간", accessor: (r) => r.period_start, render: (r) => `${r.period_start} ~ ${r.period_end}` },
  ];

  const fandingColumns: TableColumn<FandingCreator11>[] = [
    {
      key: "nickname",
      header: "크리에이터",
      accessor: (r) => r.nickname,
      render: (r) => (
        <>
          {r.nickname}
          {r.nickname === "스텔라이브" ? (
            <>
              {" "}
              <Badge tone="primary">StelLive 공식</Badge>
            </>
          ) : null}
        </>
      ),
    },
    { key: "n_tiers", header: "티어 수", accessor: (r) => r.n_tiers, align: "right" },
    { key: "min_price", header: "최저가", accessor: (r) => r.min_price, align: "right", render: (r) => money(r.min_price) },
    { key: "max_price", header: "최고가", accessor: (r) => r.max_price, align: "right", render: (r) => money(r.max_price) },
    { key: "avg_price", header: "평균가", accessor: (r) => r.avg_price, align: "right", render: (r) => money(r.avg_price) },
  ];

  const financialsColumns: TableColumn<Company09>[] = [
    { key: "corp_name", header: "회사", accessor: (r) => r.corp_name },
    { key: "bsns_year", header: "연도", accessor: (r) => r.bsns_year, align: "right" },
    { key: "revenue", header: "매출", accessor: (r) => r.revenue, align: "right", render: (r) => money(r.revenue) },
    {
      key: "operating_income",
      header: "영업이익",
      accessor: (r) => r.operating_income,
      align: "right",
      render: (r) => money(r.operating_income),
    },
    {
      key: "operating_margin",
      header: "영업이익률",
      accessor: (r) => r.operating_margin,
      align: "right",
      render: (r) => pct1(r.operating_margin * 100),
    },
  ];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 11</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>팬 커머스</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["11"]} cadenceLabel={REFRESH_LABEL["11"]} />
        </div>
        <p className={styles.subhead}>
          팬딩(멤버십) 크리에이터 {data.meta.n_fanding_creators}명({data.meta.n_fanding_creators_with_tiers}명 유료
          티어 운영, 티어 {data.meta.n_fanding_tiers}개) · 텀블벅 크라우드펀딩 {data.meta.n_crowdfunding_projects}건 ·
          재무 {data.meta.n_financial_company_years}개 회사·연도(09 DART 재무 데이터 재사용, DART 재수집 없음) 기준.
        </p>
      </header>

      <Card padding="lg" className={styles.warnCard}>
        <Badge tone="cautionary">데이터 출처 신뢰 — 텀블벅 robots.txt 준수</Badge>
        <p className={styles.insightText}>
          텀블벅 robots.txt는 <code>{data.meta.tumblbug_robots_rule.split(" ")[0]}</code> 규칙으로 실제 모금액·
          후원자 수가 나오는 경로를 막는다({data.meta.tumblbug_robots_rule}). 이 규칙을 우회하지 않았다 — 공식 굿즈
          펀딩 2건은 언론 보도·나무위키가 사후 집계한 최종 수치를, 팬메이드 광고 펀딩 3건은 프로젝트 페이지를 사람이
          직접 열람해 얻은 수치를 썼다(각 행의 &quot;기간&quot; 옆 표에 출처가 남아 있다). 와디즈는{" "}
          {data.meta.wadiz_note}
        </p>
      </Card>

      <Card padding="lg" className={styles.insightCard}>
        <Badge tone="primary">핵심 발견</Badge>
        <p className={styles.insightText}>
          스텔라이브 공식 팬딩 티어({money(data.fanding.stats.stellive_prices[0] ?? 0)})는 전체{" "}
          {data.fanding.stats.n_tiers}개 티어 가격 분포에서 백분위 {data.fanding.stats.stellive_percentile} —{" "}
          전체 티어의 {data.fanding.stats.stellive_percentile}%보다 비싸다(상위{" "}
          {(100 - data.fanding.stats.stellive_percentile).toFixed(1)}% 구간).{" "}
          {magnitudeRatio !== null
            ? `공식 굿즈 펀딩(패러블엔터테인먼트, ${officialRows.length}건 합계 ${money(officialTotalRaised)})은 같은 텀블벅에서 열린 StelLive 팬메이드 광고 펀딩(${fanmadeRows.length}건 합계 ${money(fanmadeTotalRaised)})보다 약 ${magnitudeRatio.toFixed(0)}배 크다 — 둘은 성격이 다른 자금이라는 점(회사 매출 vs 팬 자발적 모금)에 유의해야 한다.`
            : ""}
        </p>
      </Card>

      <Section
        eyebrow="Filters"
        title="필터"
        description="플랫폼·카테고리로 아래 크라우드펀딩 표·차트를 좁힌다 (멤버/유닛 필터 아님 — 이 프로젝트는 플랫폼/회사 단위)."
      />
      <div className={styles.filterBar} role="group" aria-label="플랫폼·카테고리 필터">
        <div className={styles.filterRow}>
          <span className={styles.filterRowLabel}>플랫폼</span>
          <div className={styles.chips}>
            {platforms.map((p) => (
              <FilterChip key={p} label={p} active={platformFilter.includes(p)} onClick={() => togglePlatform(p)} />
            ))}
          </div>
        </div>
        <div className={styles.filterRow}>
          <span className={styles.filterRowLabel}>카테고리</span>
          <div className={styles.chips}>
            {categories.map((c) => (
              <FilterChip key={c} label={c} active={categoryFilter.includes(c)} onClick={() => toggleCategory(c)} />
            ))}
          </div>
        </div>
        <button type="button" className={styles.reset} onClick={resetFilters} disabled={!hasActiveFilters}>
          필터 초기화
        </button>
      </div>

      <Section eyebrow="Charts" title="크라우드펀딩 모금액" description="프로젝트별 최종 모금액 — 공식 굿즈 펀딩과 팬메이드 광고 펀딩이 섞여 있어 규모 차이가 크다." />
      {crowdfundingBarData.length > 0 ? (
        <Card padding="md">
          <BarChart data={crowdfundingBarData} title="크라우드펀딩 모금액" valueFormat={money} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 프로젝트가 없다.</p>
        </Card>
      )}

      <Section eyebrow="Table" title="크라우드펀딩 전체" description="열 제목을 클릭하면 정렬된다." />
      <Table
        columns={crowdfundingColumns}
        rows={filteredCrowdfunding}
        getRowKey={(r) => r.slug}
        initialSortKey="raised_krw"
        initialSortDir="desc"
        caption={`프로젝트 11 · 텀블벅 크라우드펀딩 (${filteredCrowdfunding.length}건)`}
      />

      <Section eyebrow="Charts" title="팬딩 크리에이터 평균 티어가 상위 15명" description="StelLive 공식 팬딩 티어가 어디쯤 있는지 비교." />
      <Card padding="md">
        <BarChart data={fandingBarData} title="팬딩 크리에이터 평균 티어가 상위 15명" valueFormat={money} />
      </Card>

      <Section eyebrow="Table" title="팬딩 크리에이터 (유료 티어 보유)" description="열 제목을 클릭하면 정렬된다." />
      <Table
        columns={fandingColumns}
        rows={data.fanding.creator_summary}
        getRowKey={(r) => r.creator_url}
        initialSortKey="avg_price"
        initialSortDir="desc"
        caption={`프로젝트 11 · 팬딩 크리에이터 (${data.fanding.creator_summary.length}명)`}
      />

      <Section
        eyebrow="Table"
        title="재무 참고 (09와 동일 데이터)"
        description="샌드박스네트워크·패러블엔터테인먼트 — 커머스 맥락에서 참고용으로 재사용했다. DART 재수집은 하지 않았다."
      />
      <Table
        columns={financialsColumns}
        rows={data.financials}
        getRowKey={(r) => `${r.corp_name}-${r.bsns_year}`}
        initialSortKey="bsns_year"
        initialSortDir="desc"
        caption="프로젝트 09 · DART 재무에서 재사용"
      />

      <div className={styles.statRow}>
        <StatTile label="팬딩 크리에이터" value={data.meta.n_fanding_creators} unit="명" caption={`유료 티어 ${data.meta.n_fanding_creators_with_tiers}명`} />
        <StatTile label="팬딩 티어" value={data.meta.n_fanding_tiers} unit="개" caption={`가격 ${money(data.fanding.stats.min_price)} ~ ${money(data.fanding.stats.max_price)}`} />
        <StatTile label="크라우드펀딩" value={data.meta.n_crowdfunding_projects} unit="건" />
        <StatTile label="StelLive 티어 백분위" value={pct1(data.fanding.stats.stellive_percentile)} caption="전체 티어 가격 분포 기준" />
      </div>
    </div>
  );
}
