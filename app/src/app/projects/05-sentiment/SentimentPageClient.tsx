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
import HeatMap from "@/components/charts/HeatMap";
import ScatterPlot, { type ScatterDatum } from "@/components/charts/ScatterPlot";
import data05 from "@/data/05.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import { UNIT_LABEL_KO } from "@/data/roster";
import { normalizeHeatmap05, type Data05, type Member05 } from "@/data/types";
import { useFilters } from "@/lib/useFilters";
import styles from "./page.module.css";

const data = data05 as Data05;

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

export default function SentimentPageClient() {
  const { detail, openDetail, closeDetail, matchesFilters } = useFilters();

  const filteredMembers = useMemo(() => data.members.filter((m) => matchesFilters(m)), [matchesFilters]);

  // 05의 heatmap.members는 name_ko 배열이다. normalizeHeatmap05()로 name_en을 뽑아
  // 조인/선택 상태(useFilters의 detail 등)는 name_en으로만 유지하고, 화면 표시는
  // 원본 name_ko 라벨을 그대로 쓴다.
  const normalizedHeatmap = useMemo(() => normalizeHeatmap05(data), []);

  const barData: BarDatum[] = useMemo(
    () =>
      [...filteredMembers]
        .sort((a, b) => b.sentiment_score - a.sentiment_score)
        .map((m) => ({ name_en: m.name_en, label: m.name_ko, value: m.sentiment_score })),
    [filteredMembers]
  );

  const scatterData: ScatterDatum[] = useMemo(
    () =>
      filteredMembers.map((m) => ({
        name_en: m.name_en,
        label: m.name_ko,
        x: m.n_comments,
        y: m.sentiment_score,
        size: m.avg_likes,
      })),
    [filteredMembers]
  );

  const columns: TableColumn<Member05>[] = [
    { key: "rank", header: "순위", accessor: (r) => r.rank, align: "right" },
    { key: "name_ko", header: "멤버", accessor: (r) => r.name_ko },
    {
      key: "unit",
      header: "유닛",
      accessor: (r) => r.unit ?? "",
      render: (r) => (r.unit ? UNIT_LABEL_KO[r.unit] : "—"),
    },
    { key: "n_comments", header: "분석 댓글 수", accessor: (r) => r.n_comments, align: "right" },
    {
      key: "sentiment_score",
      header: "여론 점수",
      accessor: (r) => r.sentiment_score,
      align: "right",
      render: (r) => r.sentiment_score.toFixed(3),
    },
    {
      key: "positive_share",
      header: "긍정 비율",
      accessor: (r) => r.positive_share,
      align: "right",
      render: (r) => pct(r.positive_share),
    },
    {
      key: "negative_share",
      header: "부정 비율",
      accessor: (r) => r.negative_share,
      align: "right",
      render: (r) => pct(r.negative_share),
    },
    { key: "top_topic", header: "주요 화제", accessor: (r) => r.top_topic },
    {
      key: "avg_likes",
      header: "평균 좋아요",
      accessor: (r) => r.avg_likes,
      align: "right",
      render: (r) => Math.round(r.avg_likes).toLocaleString("ko-KR"),
    },
  ];

  const totalComments = data.overall_sentiment.positive + data.overall_sentiment.neutral + data.overall_sentiment.negative;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 05</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>댓글 여론 분석</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["05"]} cadenceLabel={REFRESH_LABEL["05"]} />
        </div>
        <p className={styles.subhead}>
          영상 {data.meta.n_videos}건에서 수집한 댓글 {data.meta.n_comments.toLocaleString("ko-KR")}건(멤버당 영상{" "}
          {data.meta.videos_per_member}건 × 영상당 댓글 {data.meta.comments_per_video}건, order=relevance) 기준
          감성 분석 결과.
        </p>
      </header>

      <Section eyebrow="Filters" title="필터" description="멤버·유닛으로 아래 차트와 표를 함께 좁힌다." />
      <FilterBar />

      <Section eyebrow="Charts" title="멤버별 여론 점수" description="막대나 이름을 클릭하면 상세 패널이 열린다." />
      {barData.length > 0 ? (
        <Card padding="md">
          <BarChart data={barData} title="멤버별 여론 점수" valueFormat={(v) => v.toFixed(3)} onSelect={openDetail} selected={detail} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section
        eyebrow="Charts"
        title="멤버 × 화제 히트맵"
        description="칸이 진할수록 그 멤버 댓글에서 그 화제가 자주 언급됐다는 뜻. 행을 클릭하면 상세 패널이 열린다."
      />
      <Card padding="md">
        <HeatMap
          title="멤버별 화제 언급 빈도"
          rowLabels={data.heatmap.members}
          rowKeys={normalizedHeatmap.members}
          colLabels={data.heatmap.topics}
          values={data.heatmap.values}
          cellWidth={46}
          cellHeight={28}
          rowLabelWidth={104}
          colLabelHeight={62}
          rotateColLabels
          onSelectRow={openDetail}
          selected={detail}
        />
      </Card>

      <Section
        eyebrow="Charts"
        title="댓글 수 대비 여론 점수"
        description="x: 분석 댓글 수 · y: 여론 점수 · 버블 크기: 평균 좋아요 수"
      />
      {scatterData.length > 0 ? (
        <Card padding="md">
          <ScatterPlot
            data={scatterData}
            title="댓글 수 대비 여론 점수"
            xLabel="분석 댓글 수"
            yLabel="여론 점수"
            onSelect={openDetail}
            selected={detail}
          />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section eyebrow="Highlights" title="좋아요 상위 댓글 Top 5" description="수집된 댓글 중 좋아요 수 기준." />
      <Card padding="md">
        <ol className={styles.topList}>
          {data.top_liked.slice(0, 5).map((c, i) => (
            <li key={`${c.name_ko}-${i}`} className={styles.topListItem}>
              <span className={styles.topListRank}>{i + 1}</span>
              <div className={styles.topListBody}>
                <span className={styles.topListTitle}>
                  {c.name_ko} · {c.text}
                </span>
                <span className={styles.topListMeta}>
                  좋아요 {c.like_count.toLocaleString("ko-KR")} · {c.sentiment} · {c.topic_ko}
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
        initialSortKey="sentiment_score"
        initialSortDir="desc"
        caption="프로젝트 05 · 댓글 여론 분석"
        onRowClick={(r) => openDetail(r.name_en)}
      />

      <div className={styles.statRow}>
        <StatTile
          label="전체 긍정 비율"
          value={totalComments > 0 ? pct(data.overall_sentiment.positive / totalComments) : "—"}
          caption={`긍정 ${data.overall_sentiment.positive} · 중립 ${data.overall_sentiment.neutral} · 부정 ${data.overall_sentiment.negative}`}
        />
        <StatTile
          label="최다 화제"
          value={data.topic_totals[0]?.topic ?? "—"}
          caption={`${(data.topic_totals[0]?.count ?? 0).toLocaleString("ko-KR")}건`}
        />
      </div>

      {detail ? <MemberDetail nameEn={detail} onClose={closeDetail} /> : null}
    </div>
  );
}
