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
import data02 from "@/data/02.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import { UNIT_LABEL_KO } from "@/data/roster";
import type { Data02, Member02 } from "@/data/types";
import { useFilters } from "@/lib/useFilters";
import styles from "./page.module.css";

const data = data02 as Data02;

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

export default function CoverPageClient() {
  const { detail, openDetail, closeDetail, matchesFilters } = useFilters();

  const filteredMembers = useMemo(() => data.members.filter((m) => matchesFilters(m)), [matchesFilters]);

  const barData: BarDatum[] = useMemo(
    () =>
      [...filteredMembers]
        .sort((a, b) => b.total_views - a.total_views)
        .map((m) => ({ name_en: m.name_en, label: m.name_ko, value: m.total_views })),
    [filteredMembers]
  );

  const scatterData: ScatterDatum[] = useMemo(
    () =>
      filteredMembers.map((m) => ({
        name_en: m.name_en,
        label: m.name_ko,
        x: m.avg_views,
        y: m.avg_engagement_rate,
        size: m.cover_count,
      })),
    [filteredMembers]
  );

  const topCovers = useMemo(() => [...data.top_covers].sort((a, b) => b.views - a.views).slice(0, 5), []);

  const columns: TableColumn<Member02>[] = [
    { key: "rank", header: "순위", accessor: (r) => r.rank, align: "right" },
    { key: "name_ko", header: "멤버", accessor: (r) => r.name_ko },
    {
      key: "unit",
      header: "유닛",
      accessor: (r) => r.unit ?? "",
      render: (r) => (r.unit ? UNIT_LABEL_KO[r.unit] : "—"),
    },
    {
      key: "cover_count",
      header: "커버곡 수",
      accessor: (r) => r.cover_count,
      align: "right",
      render: (r) => `${r.cover_count.toLocaleString("ko-KR")}곡`,
    },
    {
      key: "total_views",
      header: "총 조회수",
      accessor: (r) => r.total_views,
      align: "right",
      render: (r) => r.total_views.toLocaleString("ko-KR"),
    },
    {
      key: "avg_views",
      header: "평균 조회수",
      accessor: (r) => r.avg_views,
      align: "right",
      render: (r) => Math.round(r.avg_views).toLocaleString("ko-KR"),
    },
    {
      key: "avg_engagement_rate",
      header: "평균 참여율",
      accessor: (r) => r.avg_engagement_rate,
      align: "right",
      render: (r) => pct(r.avg_engagement_rate),
    },
    {
      key: "collab_share",
      header: "합방 비율",
      accessor: (r) => r.collab_share,
      align: "right",
      render: (r) => pct(r.collab_share),
    },
    { key: "best_cover", header: "대표 커버곡", accessor: (r) => r.best_cover },
  ];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 02</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>커버곡 성과 랭킹</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["02"]} cadenceLabel={REFRESH_LABEL["02"]} />
        </div>
        <p className={styles.subhead}>
          제목 필터 <code>{data.meta.title_filter}</code> 기준 커버곡 {data.meta.n_covers}건. 멤버{" "}
          {data.meta.n_members}명의 커버곡 조회수·참여율을 비교한다.
        </p>
      </header>

      <Card padding="lg" className={styles.insightCard}>
        <Badge tone="cautionary">데이터 주의 — 수집 방식이 바뀌었다</Badge>
        <p className={styles.insightText}>
          이 페이지의 <strong>커버곡 수(cover_count)</strong>는 {data.meta.method_changed_at}부터 업로드
          재생목록을 전량 열거하는 방식(<code>{data.meta.method}</code>)으로 수집한다. 그 전에는 YouTube{" "}
          <code>search.list</code>를 <code>order=&quot;relevance&quot;</code>로 호출해 쿼리당 최대 40건만 가져왔는데,
          이 &quot;relevance 상위 40건 창&quot;은 실행마다 흔들렸다 — 실제로 영상이 한 편도 삭제되지 않았는데도
          재실행 한 번으로 어떤 멤버는 34곡 → 29곡으로 줄어든 사례가 있었다. 전량 열거로 바뀐 지금은 그 문제가
          해소됐지만, <strong>{data.meta.method_changed_at} 이전에 기록해 둔 값과는 여전히 비교할 수 없다</strong>{" "}
          — 수집 방식 자체가 달라졌기 때문이다. 이 앱은 스냅샷을 따로 저장하지 않고 최신 수집 결과만 보여주므로,
          지금 화면의 cover_count는 신뢰할 수 있는 절대값이지만 과거에 메모해 둔 값과의 비교(성장 추이)에는 쓰지
          말 것.
        </p>
        <p className={styles.noteText}>{data.meta.method_note}</p>
      </Card>

      <Section eyebrow="Filters" title="필터" description="멤버·유닛으로 아래 차트와 표를 함께 좁힌다." />
      <FilterBar />

      <Section
        eyebrow="Charts"
        title="커버곡 총 조회수"
        description="멤버별 수집된 커버곡의 총 조회수. 막대나 이름을 클릭하면 상세 패널이 열린다."
      />
      {barData.length > 0 ? (
        <Card padding="md">
          <BarChart data={barData} title="멤버별 커버곡 총 조회수" onSelect={openDetail} selected={detail} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section
        eyebrow="Charts"
        title="평균 조회수 대비 참여율"
        description="x: 커버곡 평균 조회수 · y: 평균 참여율 · 버블 크기: 수집된 커버곡 수(표본, 시계열 비교 불가)"
      />
      {scatterData.length > 0 ? (
        <Card padding="md">
          <ScatterPlot
            data={scatterData}
            title="평균 조회수 대비 참여율"
            xLabel="평균 조회수"
            yLabel="평균 참여율"
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

      <Section eyebrow="Highlights" title="조회수 상위 커버곡 Top 5" description="전체 수집 커버곡 중 조회수 기준." />
      <Card padding="md">
        <ol className={styles.topList}>
          {topCovers.map((c, i) => (
            <li key={`${c.name_ko}-${c.title}`} className={styles.topListItem}>
              <span className={styles.topListRank}>{i + 1}</span>
              <div className={styles.topListBody}>
                <span className={styles.topListTitle}>
                  {c.name_ko} · {c.title}
                </span>
                <span className={styles.topListMeta}>
                  조회수 {c.views.toLocaleString("ko-KR")} · 좋아요 {c.likes.toLocaleString("ko-KR")}
                </span>
              </div>
            </li>
          ))}
        </ol>
      </Card>

      <Section eyebrow="Table" title="전체 지표" description="열 제목을 클릭하면 정렬된다. 행을 클릭하면 상세 패널이 열린다." />
      <Table
        columns={columns}
        rows={filteredMembers}
        getRowKey={(r) => r.name_en}
        initialSortKey="total_views"
        initialSortDir="desc"
        caption={`프로젝트 02 · 커버곡 성과 랭킹 (수집 방식: ${data.meta.method}, ${data.meta.method_changed_at}부터 — 그 이전 스냅샷과 커버곡 수 비교 불가)`}
        onRowClick={(r) => openDetail(r.name_en)}
      />

      <div className={styles.statRow}>
        <StatTile label="수집된 커버곡" value={data.meta.n_covers.toLocaleString("ko-KR")} unit="건" caption="업로드 재생목록 전량 열거" />
        <StatTile
          label="최고 참여율"
          value={pct(Math.max(...data.members.map((m) => m.avg_engagement_rate)))}
          caption={data.members.reduce((a, b) => (a.avg_engagement_rate > b.avg_engagement_rate ? a : b)).name_ko}
        />
      </div>

      {detail ? <MemberDetail nameEn={detail} onClose={closeDetail} /> : null}
    </div>
  );
}
