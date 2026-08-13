"use client";

import { useMemo } from "react";
import Card from "@/components/Card";
import FilterBar from "@/components/FilterBar";
import Freshness from "@/components/Freshness";
import MemberDetail from "@/components/MemberDetail";
import Section from "@/components/Section";
import StatTile from "@/components/StatTile";
import Table, { type TableColumn } from "@/components/Table";
import BarChart, { type BarDatum } from "@/components/charts/BarChart";
import ScatterPlot, { type ScatterDatum } from "@/components/charts/ScatterPlot";
import data04 from "@/data/04.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import { UNIT_LABEL_KO, nameKoToEn } from "@/data/roster";
import type { ClipChannel04, Data04, Member04 } from "@/data/types";
import { useFilters } from "@/lib/useFilters";
import styles from "./page.module.css";

const data = data04 as Data04;

export default function KirinukiPageClient() {
  const { detail, openDetail, closeDetail, matchesFilters } = useFilters();

  const filteredMembers = useMemo(() => data.members.filter((m) => matchesFilters(m)), [matchesFilters]);

  const barData: BarDatum[] = useMemo(
    () =>
      [...filteredMembers]
        .sort((a, b) => b.clip_count - a.clip_count)
        .map((m) => ({ name_en: m.name_en, label: m.name_ko, value: m.clip_count })),
    [filteredMembers]
  );

  const scatterData: ScatterDatum[] = useMemo(
    () =>
      filteredMembers.map((m) => ({
        name_en: m.name_en,
        label: m.name_ko,
        x: m.total_clip_views,
        y: m.fan_channels,
        size: m.avg_clip_views,
      })),
    [filteredMembers]
  );

  const specializationBar: BarDatum[] = useMemo(
    () =>
      data.specialization
        .slice()
        .sort((a, b) => a.members - b.members)
        .map((s) => ({ name_en: `spec-${s.members}`, label: `${s.members}명 전담`, value: s.channels })),
    []
  );

  const topChannels = useMemo(() => [...data.channels].sort((a, b) => b.total_views - a.total_views).slice(0, 10), []);

  const memberColumns: TableColumn<Member04>[] = [
    { key: "rank", header: "순위", accessor: (r) => r.rank, align: "right" },
    { key: "name_ko", header: "멤버", accessor: (r) => r.name_ko },
    {
      key: "unit",
      header: "유닛",
      accessor: (r) => r.unit ?? "",
      render: (r) => (r.unit ? UNIT_LABEL_KO[r.unit] : "—"),
    },
    { key: "clip_count", header: "클립 수", accessor: (r) => r.clip_count, align: "right" },
    {
      key: "total_clip_views",
      header: "클립 총 조회수",
      accessor: (r) => r.total_clip_views,
      align: "right",
      render: (r) => r.total_clip_views.toLocaleString("ko-KR"),
    },
    {
      key: "avg_clip_views",
      header: "클립 평균 조회수",
      accessor: (r) => r.avg_clip_views,
      align: "right",
      render: (r) => Math.round(r.avg_clip_views).toLocaleString("ko-KR"),
    },
    { key: "fan_channels", header: "팬 클립 채널 수", accessor: (r) => r.fan_channels, align: "right" },
    { key: "top_channel", header: "대표 클립 채널", accessor: (r) => r.top_channel },
  ];

  const channelColumns: TableColumn<ClipChannel04>[] = [
    { key: "rank", header: "순위", accessor: (r) => r.rank, align: "right" },
    { key: "clip_channel_title", header: "클립 채널", accessor: (r) => r.clip_channel_title },
    { key: "subs", header: "구독자", accessor: (r) => r.subs, align: "right", render: (r) => r.subs.toLocaleString("ko-KR") },
    { key: "clip_count", header: "클립 수", accessor: (r) => r.clip_count, align: "right" },
    {
      key: "total_views",
      header: "총 조회수",
      accessor: (r) => r.total_views,
      align: "right",
      render: (r) => r.total_views.toLocaleString("ko-KR"),
    },
    { key: "members_covered", header: "다루는 멤버 수", accessor: (r) => r.members_covered, align: "right" },
    { key: "primary_member", header: "주력 멤버", accessor: (r) => r.primary_member },
  ];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 04</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>키리누키 생태계</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["04"]} cadenceLabel={REFRESH_LABEL["04"]} />
        </div>
        <p className={styles.subhead}>
          팬 클립(키리누키) {data.meta.n_clips}건, 클립 채널 {data.meta.n_clip_channels}개 기준. 대부분의 클립
          채널은 멤버 한 명만 전담한다 — 아래 히스토그램에서 바로 확인할 수 있다.
        </p>
      </header>

      <Section eyebrow="Filters" title="필터" description="멤버·유닛으로 아래 차트와 표를 함께 좁힌다." />
      <FilterBar />

      <Section
        eyebrow="Charts"
        title="멤버별 클립 수"
        description="막대나 이름을 클릭하면 상세 패널이 열린다."
      />
      {barData.length > 0 ? (
        <Card padding="md">
          <BarChart data={barData} title="멤버별 팬 클립 수" valueFormat={(v) => `${v.toLocaleString("ko-KR")}개`} onSelect={openDetail} selected={detail} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section
        eyebrow="Charts"
        title="클립 총 조회수 대비 팬 채널 수"
        description="x: 클립 총 조회수 · y: 그 멤버를 다루는 팬 클립 채널 수 · 버블 크기: 클립 평균 조회수"
      />
      {scatterData.length > 0 ? (
        <Card padding="md">
          <ScatterPlot
            data={scatterData}
            title="클립 총 조회수 대비 팬 채널 수"
            xLabel="클립 총 조회수"
            yLabel="팬 클립 채널 수"
            onSelect={openDetail}
            selected={detail}
          />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section
        eyebrow="Charts"
        title="클립 채널 전문화 정도"
        description="한 클립 채널이 몇 명의 멤버를 다루는지 — 채널 대부분이 한 멤버만 전담한다(멤버별 데이터 아님)."
      />
      <Card padding="md">
        <BarChart data={specializationBar} title="전담 멤버 수별 클립 채널 개수" valueFormat={(v) => `${v.toLocaleString("ko-KR")}개`} />
      </Card>

      <Section eyebrow="Table" title="멤버별 지표" description="열 제목을 클릭하면 정렬된다. 행을 클릭하면 상세 패널이 열린다." />
      <Table
        columns={memberColumns}
        rows={filteredMembers}
        getRowKey={(r) => r.name_en}
        initialSortKey="clip_count"
        initialSortDir="desc"
        caption="프로젝트 04 · 멤버별 팬 클립 지표"
        onRowClick={(r) => openDetail(r.name_en)}
      />

      <Section
        eyebrow="Table"
        title="클립 채널 랭킹 Top 10"
        description="총 조회수 기준 상위 클립 채널. 행을 클릭하면 그 채널의 주력 멤버 상세 패널이 열린다(로스터에 있는 경우)."
      />
      <Table
        columns={channelColumns}
        rows={topChannels}
        getRowKey={(r) => r.clip_channel_id}
        initialSortKey="total_views"
        initialSortDir="desc"
        caption="프로젝트 04 · 팬 클립 채널 랭킹(상위 10개)"
        onRowClick={(r) => {
          const nameEn = nameKoToEn(r.primary_member);
          if (nameEn) openDetail(nameEn);
        }}
      />

      <div className={styles.statRow}>
        <StatTile label="수집된 클립" value={data.meta.n_clips.toLocaleString("ko-KR")} unit="건" />
        <StatTile label="활성 클립 채널" value={data.meta.n_clip_channels.toLocaleString("ko-KR")} unit="개" />
      </div>

      {detail ? <MemberDetail nameEn={detail} onClose={closeDetail} /> : null}
    </div>
  );
}
