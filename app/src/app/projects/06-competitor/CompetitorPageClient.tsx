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

  const groupBarData: BarDatum[] = useMemo(
    () =>
      [...data.groups]
        .sort((a, b) => b.avg_subscribers - a.avg_subscribers)
        .map((g) => ({ name_en: g.group, label: g.group, value: g.avg_subscribers })),
    []
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
    { key: "rank", header: "순위", accessor: (r) => r.rank, align: "right" },
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
          {data.meta.note} — StelLive 6명 · 홀로라이브 6명 · 이세계아이돌 6명, 채널 {data.meta.n_channels}개 ·
          영상 {data.meta.n_videos}건 기준. 전 멤버가 아니라 표본 비교임에 유의.
        </p>
      </header>

      <Card padding="lg" className={styles.insightCard}>
        <Badge tone="cautionary">필터 동작 안내</Badge>
        <p className={styles.insightText}>
          홀로라이브·이세계아이돌 12개 채널은 StelLive 유닛 체계에 속하지 않아 <code>unit: null</code>이다(설계상
          정상). 그래서 <strong>유닛·멤버 필터는 이 12행에 적용되지 않는다</strong> — 필터를 켜도 경쟁사 그룹은
          계속 표시된다(조용히 사라지지 않는다). 소속은 유닛 대신 <strong>그룹 배지</strong>(StelLive / 홀로라이브
          / 이세계아이돌)로 구분한다.
        </p>
      </Card>

      <Section eyebrow="Filters" title="필터" description="StelLive 6명에만 적용된다 — 경쟁사 12명은 항상 표시." />
      <FilterBar />

      <Section
        eyebrow="Charts"
        title="그룹별 평균 구독자"
        description="StelLive · 홀로라이브 · 이세계아이돌 3개 그룹의 평균 구독자 수 비교."
      />
      <Card padding="md">
        <BarChart data={groupBarData} title="그룹별 평균 구독자 수" />
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
        caption="프로젝트 06 · 경쟁사 비교 (18개 채널, 3개 그룹 표본)"
        onRowClick={(r) => openDetail(r.name_en)}
      />

      <div className={styles.statRow}>
        {data.groups.map((g) => (
          <StatTile
            key={g.group}
            label={`${g.group} 평균 참여율`}
            value={pct(g.avg_engagement_rate)}
            caption={`평균 구독자 ${Math.round(g.avg_subscribers).toLocaleString("ko-KR")}명 · 평균 도달률 ${pct(g.avg_reach_ratio)}`}
          />
        ))}
      </div>

      {detail ? <MemberDetail nameEn={detail} onClose={closeDetail} /> : null}
    </div>
  );
}
