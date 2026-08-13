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
import HeatMap from "@/components/charts/HeatMap";
import ScatterPlot, { type ScatterDatum } from "@/components/charts/ScatterPlot";
import data03 from "@/data/03.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import { UNIT_LABEL_KO } from "@/data/roster";
import type { Data03, Member03 } from "@/data/types";
import { useFilters } from "@/lib/useFilters";
import styles from "./page.module.css";

const data = data03 as Data03;

const DAY_LABELS = ["일", "월", "화", "수", "목", "금", "토"];
const HOUR_LABELS = Array.from({ length: 24 }, (_, h) => String(h));

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

function hourLabel(v: number): string {
  return `${Math.round(v)}시`;
}

export default function StreamPageClient() {
  const { detail, openDetail, closeDetail, matchesFilters } = useFilters();

  const filteredMembers = useMemo(() => data.members.filter((m) => matchesFilters(m)), [matchesFilters]);

  const busiestHour = useMemo(() => {
    let maxIdx = 0;
    data.hour_dist.forEach((v, i) => {
      if (v > data.hour_dist[maxIdx]) maxIdx = i;
    });
    return maxIdx;
  }, []);

  const barData: BarDatum[] = useMemo(
    () =>
      [...filteredMembers]
        .sort((a, b) => b.hours_per_week - a.hours_per_week)
        .map((m) => ({ name_en: m.name_en, label: m.name_ko, value: m.hours_per_week })),
    [filteredMembers]
  );

  const scatterData: ScatterDatum[] = useMemo(
    () =>
      filteredMembers.map((m) => ({
        name_en: m.name_en,
        label: m.name_ko,
        x: m.avg_start_hour,
        y: m.night_share,
        size: m.hours_per_week,
      })),
    [filteredMembers]
  );

  const columns: TableColumn<Member03>[] = [
    { key: "rank", header: "순위", accessor: (r) => r.rank, align: "right" },
    { key: "name_ko", header: "멤버", accessor: (r) => r.name_ko },
    {
      key: "unit",
      header: "유닛",
      accessor: (r) => r.unit ?? "",
      render: (r) => (r.unit ? UNIT_LABEL_KO[r.unit] : "—"),
    },
    { key: "stream_count", header: "방송 횟수", accessor: (r) => r.stream_count, align: "right" },
    {
      key: "hours_per_week",
      header: "주당 방송 시간",
      accessor: (r) => r.hours_per_week,
      align: "right",
      render: (r) => `${r.hours_per_week.toLocaleString("ko-KR")}h`,
    },
    {
      key: "avg_start_hour",
      header: "평균 시작 시각",
      accessor: (r) => r.avg_start_hour,
      align: "right",
      render: (r) => hourLabel(r.avg_start_hour),
    },
    {
      key: "night_share",
      header: "심야 방송 비율",
      accessor: (r) => r.night_share,
      align: "right",
      render: (r) => pct(r.night_share),
    },
    {
      key: "game_share",
      header: "게임 방송 비율",
      accessor: (r) => r.game_share,
      align: "right",
      render: (r) => pct(r.game_share),
    },
    { key: "top_category", header: "주요 카테고리", accessor: (r) => r.top_category },
    {
      key: "avg_vod_views",
      header: "평균 VOD 조회수",
      accessor: (r) => r.avg_vod_views,
      align: "right",
      render: (r) => Math.round(r.avg_vod_views).toLocaleString("ko-KR"),
    },
  ];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 03</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>치지직 방송 패턴</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["03"]} cadenceLabel={REFRESH_LABEL["03"]} />
        </div>
        <p className={styles.subhead}>
          치지직(비공식 API) 방송 {data.meta.n_streams}건, 멤버 {data.meta.n_members}명 기준 (기준 시간대{" "}
          {data.meta.tz}). 채널 조인 키가 없어 <code>name_en</code>으로만 다른 프로젝트와 연결된다.
        </p>
      </header>

      <Card padding="lg" className={styles.insightCard}>
        <Badge tone="primary">핵심 발견</Badge>
        <p className={styles.insightText}>
          전체 방송 시작 시각 분포(hour_dist)를 보면 <strong>{hourLabel(busiestHour)}</strong>대에 방송이 가장 많이
          시작된다 — 요일×시간 히트맵에서 어느 요일이 그 시간대를 주도하는지 바로 확인할 수 있다.
        </p>
      </Card>

      <Section eyebrow="Filters" title="필터" description="멤버·유닛으로 아래 차트와 표를 함께 좁힌다." />
      <FilterBar />

      <Section
        eyebrow="Charts"
        title="주당 방송 시간"
        description="멤버별 주당 방송 시간(시간). 막대나 이름을 클릭하면 상세 패널이 열린다."
      />
      {barData.length > 0 ? (
        <Card padding="md">
          <BarChart data={barData} title="멤버별 주당 방송 시간" valueFormat={(v) => `${v.toLocaleString("ko-KR")}h`} onSelect={openDetail} selected={detail} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section
        eyebrow="Charts"
        title="요일 × 시간 방송 빈도"
        description="칸이 진할수록 그 요일·시간에 방송이 자주 시작됐다는 뜻이다. 숫자는 실제 방송 시작 건수."
      />
      <Card padding="md">
        <HeatMap
          title="요일별 시간대 방송 빈도"
          rowLabels={DAY_LABELS}
          colLabels={HOUR_LABELS}
          values={data.heatmap}
          cellWidth={26}
          cellHeight={26}
          rowLabelWidth={40}
        />
      </Card>

      <Section
        eyebrow="Charts"
        title="시작 시각 대비 심야 방송 비율"
        description="x: 평균 시작 시각(시) · y: 심야(00~06시) 방송 비율 · 버블 크기: 주당 방송 시간"
      />
      {scatterData.length > 0 ? (
        <Card padding="md">
          <ScatterPlot
            data={scatterData}
            title="시작 시각 대비 심야 방송 비율"
            xLabel="평균 시작 시각"
            yLabel="심야 방송 비율"
            xFormat={hourLabel}
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
        initialSortKey="hours_per_week"
        initialSortDir="desc"
        caption="프로젝트 03 · 치지직 방송 패턴"
        onRowClick={(r) => openDetail(r.name_en)}
      />

      <div className={styles.statRow}>
        <StatTile label="수집 방송 건수" value={data.meta.n_streams.toLocaleString("ko-KR")} unit="건" caption={`채널당 최대 ${data.meta.max_items}건`} />
        <StatTile
          label="가장 활발한 카테고리"
          value={data.top_categories[0]?.name ?? "—"}
          caption={`${(data.top_categories[0]?.count ?? 0).toLocaleString("ko-KR")}건`}
        />
      </div>

      {detail ? <MemberDetail nameEn={detail} onClose={closeDetail} /> : null}
    </div>
  );
}
