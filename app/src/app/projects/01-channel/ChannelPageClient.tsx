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
import data01 from "@/data/01.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import { UNIT_LABEL_KO } from "@/data/roster";
import type { Data01, Member01 } from "@/data/types";
import { useFilters } from "@/lib/useFilters";
import styles from "./page.module.css";

const data = data01 as Data01;

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

export default function ChannelPageClient() {
  const { detail, openDetail, closeDetail, matchesFilters } = useFilters();

  const filteredMembers = useMemo(() => data.members.filter((m) => matchesFilters(m)), [matchesFilters]);

  const { topSubscriber, topEngagement } = useMemo(() => {
    const bySubs = [...data.members].sort((a, b) => b.subscribers - a.subscribers)[0];
    const byEng = [...data.members].sort((a, b) => b.recent_avg_engagement_rate - a.recent_avg_engagement_rate)[0];
    return { topSubscriber: bySubs, topEngagement: byEng };
  }, []);

  const barData: BarDatum[] = useMemo(
    () =>
      [...filteredMembers]
        .sort((a, b) => b.subscribers - a.subscribers)
        .map((m) => ({ name_en: m.name_en, label: m.name_ko, value: m.subscribers })),
    [filteredMembers]
  );

  const scatterData: ScatterDatum[] = useMemo(
    () =>
      filteredMembers.map((m) => ({
        name_en: m.name_en,
        label: m.name_ko,
        x: m.subscribers,
        y: m.recent_avg_engagement_rate,
        size: m.recent_avg_views,
      })),
    [filteredMembers]
  );

  const columns: TableColumn<Member01>[] = [
    { key: "rank_subs", header: "순위", accessor: (r) => r.rank_subs, align: "right" },
    { key: "name_ko", header: "멤버", accessor: (r) => r.name_ko },
    {
      key: "unit",
      header: "유닛",
      accessor: (r) => r.unit ?? "",
      render: (r) => (r.unit ? UNIT_LABEL_KO[r.unit] : "—"),
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
      key: "uploads_per_week",
      header: "주당 업로드",
      accessor: (r) => r.uploads_per_week,
      align: "right",
    },
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
        <p className={styles.eyebrow}>Project 01</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>멤버 채널 성과</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["01"]} cadenceLabel={REFRESH_LABEL["01"]} />
        </div>
        <p className={styles.subhead}>
          유튜브 채널 {data.meta.n_channels}개 · 최근 영상 {data.meta.n_videos}건 기준. 구독자 규모와 참여율은
          서로 다른 사람이 1위를 차지한다 — 아래 산점도에서 바로 확인할 수 있다.
        </p>
      </header>

      {topSubscriber.name_en !== topEngagement.name_en ? (
        <Card padding="lg" className={styles.insightCard}>
          <Badge tone="primary">핵심 발견</Badge>
          <p className={styles.insightText}>
            구독자 1위는 <strong>{topSubscriber.name_ko}</strong>({topSubscriber.subscribers.toLocaleString("ko-KR")}명)지만,
            최근 참여율 1위는 <strong>{topEngagement.name_ko}</strong>({pct(topEngagement.recent_avg_engagement_rate)})다.
            팔로워 규모와 팬덤 밀도는 다른 지표다.
          </p>
        </Card>
      ) : null}

      <Section eyebrow="Filters" title="필터" description="멤버·유닛으로 아래 차트와 표를 함께 좁힌다." />
      <FilterBar />

      <Section eyebrow="Charts" title="구독자 순위" description="멤버별 구독자 수. 막대나 이름을 클릭하면 상세 패널이 열린다." />
      {barData.length > 0 ? (
        <Card padding="md">
          <BarChart data={barData} title="멤버별 구독자 수" onSelect={openDetail} selected={detail} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section
        eyebrow="Charts"
        title="구독자 대비 참여율"
        description="x: 구독자 수 · y: 최근 평균 참여율 · 버블 크기: 최근 평균 조회수"
      />
      {scatterData.length > 0 ? (
        <Card padding="md">
          <ScatterPlot
            data={scatterData}
            title="구독자 대비 참여율"
            xLabel="구독자 수"
            yLabel="최근 평균 참여율"
            yFormat={pct}
            onSelect={openDetail}
            selected={detail}
          />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section eyebrow="Table" title="전체 지표" description="열 제목을 클릭하면 정렬된다. 행을 클릭하면 상세 패널이 열린다." />
      <Table
        columns={columns}
        rows={filteredMembers}
        getRowKey={(r) => r.name_en}
        initialSortKey="subscribers"
        initialSortDir="desc"
        caption="프로젝트 01 · 멤버 채널 성과"
        onRowClick={(r) => openDetail(r.name_en)}
      />

      <div className={styles.statRow}>
        <StatTile
          label="구독자-최근 평균 조회수 상관계수"
          value={data.correlations.subs_vs_avgviews.toFixed(3)}
          caption="Pearson r"
        />
        <StatTile
          label="업로드 빈도-참여율 상관계수"
          value={data.correlations.cadence_vs_avgviews.toFixed(3)}
          caption="Pearson r"
        />
      </div>

      {detail ? <MemberDetail nameEn={detail} onClose={closeDetail} /> : null}
    </div>
  );
}
