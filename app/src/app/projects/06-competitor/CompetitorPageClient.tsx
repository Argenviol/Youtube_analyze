"use client";

import { useMemo } from "react";
import Badge from "@/components/Badge";
import Card from "@/components/Card";
import FilterBar from "@/components/FilterBar";
import Freshness from "@/components/Freshness";
import MemberDetail from "@/components/MemberDetail";
import Section from "@/components/Section";
import StatTile from "@/components/StatTile";
import Table, { type TableColumn } from "@/components/Table";
import BarChart, { type BarDatum } from "@/components/charts/BarChart";
import ScatterPlot, { type ScatterDatum } from "@/components/charts/ScatterPlot";
import data06 from "@/data/06.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import { UNIT_LABEL_KO } from "@/data/roster";
import type { Data06, Member06 } from "@/data/types";
import { useFilters } from "@/lib/useFilters";
import styles from "./page.module.css";

const data = data06 as Data06;

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

function groupTone(group: string): "primary" | "neutral" {
  return group === "StelLive" ? "primary" : "neutral";
}

export default function CompetitorPageClient() {
  const { members: memberFilter, units: unitFilter, detail, openDetail, closeDetail } = useFilters();

  // 06은 18행 중 12행(홀로라이브 6 + 이세계아이돌 6)이 unit: null이다 — 설계상 정상
  // (그 12명은 StelLive 유닛 체계에 속하지 않고, 대신 group으로 소속을 구분한다).
  // useFilters().matchesFilters를 그대로 쓰면 유닛 칩을 하나라도 고르는 순간 이
  // 12행이 "unit이 없다"는 이유만으로 조용히 사라진다 — 경쟁사 비교가 이 페이지의
  // 핵심이므로 그건 허용할 수 없다. 그래서 unit이 null인 행(경쟁사)은 유닛·멤버
  // 필터와 무관하게 항상 통과시키고, StelLive 6행에만 일반 필터 규칙을 적용한다.
  const filteredMembers = useMemo(
    () =>
      data.members.filter((m) => {
        if (m.unit === null) return true;
        if (unitFilter.length > 0 && !unitFilter.includes(m.unit)) return false;
        if (memberFilter.length > 0 && !memberFilter.includes(m.name_en)) return false;
        return true;
      }),
    [memberFilter, unitFilter]
  );

  // 그룹이 하나뿐인 코호트는 비교 상대가 없다. 막대를 그리면 비교한 것처럼 보이므로 뺀다.
  const comparableCohorts = useMemo(() => {
    const byCohort = new Map<string, Set<string>>();
    for (const c of data.cohorts) {
      if (!byCohort.has(c.cohort)) byCohort.set(c.cohort, new Set());
      byCohort.get(c.cohort)!.add(c.group);
    }
    return [...byCohort.entries()].filter(([, g]) => g.size >= 2).map(([c]) => c).sort();
  }, []);

  // 구독자는 누적 지표라 코호트를 섞으면 안 된다. 라벨에 코호트를 붙여 같은
  // 코호트끼리만 견주도록 강제한다.
  const cohortBarData: BarDatum[] = useMemo(
    () =>
      data.cohorts
        .filter((c) => comparableCohorts.includes(c.cohort))
        .sort(
          (a, b) =>
            a.cohort.localeCompare(b.cohort) || b.median_subscribers - a.median_subscribers
        )
        .map((c) => ({
          name_en: `${c.cohort}/${c.group}`,
          label: `${c.cohort} · ${c.group}`,
          value: c.median_subscribers,
        })),
    [comparableCohorts]
  );

  const scatterData: ScatterDatum[] = useMemo(
    () =>
      filteredMembers.map((m) => ({
        name_en: m.name_en,
        label: m.name_ko,
        x: m.recent_avg_views,
        y: m.reach_ratio,
        size: m.subscribers,
      })),
    [filteredMembers]
  );

  const columns: TableColumn<Member06>[] = [
    {
      key: "rank_in_cohort",
      header: "코호트 내 순위",
      accessor: (r) => r.rank_in_cohort,
      align: "right",
      render: (r) => (r.rank_in_cohort ? r.rank_in_cohort : "—"),
    },
    {
      key: "cohort",
      header: "데뷔 코호트",
      accessor: (r) => r.cohort ?? "",
      render: (r) => (r.cohort ? <Badge tone="neutral">{r.cohort}</Badge> : "구간 밖"),
    },
    {
      key: "months_since_debut",
      header: "데뷔 후 개월",
      accessor: (r) => r.months_since_debut ?? 0,
      align: "right",
      render: (r) => (r.months_since_debut == null ? "—" : Math.round(r.months_since_debut)),
    },
    {
      key: "group",
      header: "그룹",
      accessor: (r) => r.group,
      render: (r) => <Badge tone={groupTone(r.group)}>{r.group}</Badge>,
    },
    { key: "name_ko", header: "채널", accessor: (r) => r.name_ko },
    {
      key: "unit",
      header: "유닛",
      accessor: (r) => r.unit ?? "",
      render: (r) => (r.unit ? UNIT_LABEL_KO[r.unit] : "해당없음"),
    },
    {
      key: "subscribers",
      header: "구독자",
      accessor: (r) => r.subscribers,
      align: "right",
      render: (r) => r.subscribers.toLocaleString("ko-KR"),
    },
    {
      key: "recent_avg_views",
      header: "최근 평균 조회수",
      accessor: (r) => r.recent_avg_views,
      align: "right",
      render: (r) => Math.round(r.recent_avg_views).toLocaleString("ko-KR"),
    },
    {
      key: "recent_avg_engagement_rate",
      header: "참여율",
      accessor: (r) => r.recent_avg_engagement_rate,
      align: "right",
      render: (r) => pct(r.recent_avg_engagement_rate),
    },
    {
      key: "subs_per_month",
      header: "월평균 구독자 획득",
      accessor: (r) => r.subs_per_month ?? 0,
      align: "right",
      render: (r) =>
        r.subs_per_month == null ? "—" : Math.round(r.subs_per_month).toLocaleString("ko-KR"),
    },
    { key: "uploads_per_week", header: "주당 업로드", accessor: (r) => r.uploads_per_week, align: "right" },
    {
      key: "reach_ratio",
      header: "도달률",
      accessor: (r) => r.reach_ratio,
      align: "right",
      render: (r) => pct(r.reach_ratio),
    },
  ];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 06</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>경쟁사 비교</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["06"]} cadenceLabel={REFRESH_LABEL["06"]} />
        </div>
        <p className={styles.subhead}>
          {data.meta.sampling} — 채널 {data.meta.n_channels}개 · 영상 {data.meta.n_videos}건 기준.
          데뷔 시기가 겹치는 <strong>기수 전원</strong>이며 그룹 전체가 아니다.
        </p>
      </header>

      <Card padding="lg" className={styles.insightCard}>
        <Badge tone="cautionary">읽는 법</Badge>
        <p className={styles.insightText}>
          <strong>구독자는 누적 지표다.</strong> 데뷔 시기가 다르면 그 차이의 대부분은 실력이 아니라 활동
          기간이다. 그래서 그룹 비교는 <strong>같은 데뷔 코호트 안에서만</strong> 한다. 코호트를 넘어 견줄 수
          있는 것은 최근 영상 기준 지표(도달률·참여율)이고, 월평균 구독자 획득은 데뷔 직후 급증이 섞여
          신생 채널에 유리하므로 보조 지표로만 본다.
          {comparableCohorts.length < data.cohorts.length ? (
            <> 비교군이 없는 코호트는 그룹 비교 차트에서 제외했고, 표에는 그대로 남겨 뒀다.</>
          ) : null}
        </p>
        <p className={styles.insightText}>
          홀로라이브·이세계아이돌 채널은 StelLive 유닛 체계에 속하지 않아 <code>unit: null</code>이다(설계상
          정상). <strong>유닛·멤버 필터는 그 행들에 적용되지 않는다</strong> — 필터를 켜도 경쟁사는 계속
          표시된다. 소속은 유닛 대신 <strong>그룹 배지</strong>로 구분한다.
        </p>
      </Card>

      <Section eyebrow="Filters" title="필터" description="StelLive 멤버에만 적용된다 — 경쟁사 채널은 항상 표시." />
      <FilterBar />

      <Section
        eyebrow="Charts"
        title="데뷔 코호트별 구독자 중앙값"
        description="같은 시기에 데뷔한 기수끼리만 묶어 비교한다. 코호트가 다른 막대끼리 견주면 안 된다."
      />
      <Card padding="md">
        <BarChart data={cohortBarData} title="데뷔 코호트 × 그룹 구독자 중앙값" />
      </Card>

      <Section
        eyebrow="Charts"
        title="최근 평균 조회수 대비 도달률"
        description="x: 최근 평균 조회수 · y: 도달률(최근 평균 조회수/구독자) · 버블 크기: 구독자 수. 점을 클릭하면 상세 패널이 열린다."
      />
      {scatterData.length > 0 ? (
        <Card padding="md">
          <ScatterPlot
            data={scatterData}
            title="최근 평균 조회수 대비 도달률"
            xLabel="최근 평균 조회수"
            yLabel="도달률"
            yFormat={pct}
            onSelect={openDetail}
            selected={detail}
          />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 채널이 없다.</p>
        </Card>
      )}

      <Section eyebrow="Table" title="전체 채널" description="열 제목을 클릭하면 정렬된다. 행을 클릭하면 상세 패널이 열린다." />
      <Table
        columns={columns}
        rows={filteredMembers}
        getRowKey={(r) => r.name_en}
        initialSortKey="subscribers"
        initialSortDir="desc"
        caption={`프로젝트 06 · 경쟁사 비교 (${data.meta.n_channels}개 채널, 데뷔 코호트 매칭)`}
        onRowClick={(r) => openDetail(r.name_en)}
      />

      <div className={styles.statRow}>
        {data.cohorts
          .filter((c) => comparableCohorts.includes(c.cohort))
          .map((c) => (
            <StatTile
              key={`${c.cohort}/${c.group}`}
              label={`${c.cohort} · ${c.group} 참여율`}
              value={pct(c.avg_engagement_rate)}
              caption={`${c.n_members}명 · 데뷔 후 ${Math.round(c.avg_months_since_debut)}개월 · 구독자 중앙값 ${Math.round(c.median_subscribers).toLocaleString("ko-KR")}명 · 도달률 ${pct(c.avg_reach_ratio)}`}
            />
          ))}
      </div>

      {detail ? <MemberDetail nameEn={detail} onClose={closeDetail} /> : null}
    </div>
  );
}
