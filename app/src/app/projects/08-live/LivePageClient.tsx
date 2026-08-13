"use client";

import { useMemo } from "react";
import Badge from "@/components/Badge";
import Card from "@/components/Card";
import FilterBar, { type PeriodOption } from "@/components/FilterBar";
import Freshness from "@/components/Freshness";
import MemberDetail from "@/components/MemberDetail";
import Section from "@/components/Section";
import StatTile from "@/components/StatTile";
import Table, { type TableColumn } from "@/components/Table";
import BarChart, { type BarDatum } from "@/components/charts/BarChart";
import LineChart, { type LineSeriesDatum } from "@/components/charts/LineChart";
import data08 from "@/data/08.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import { UNIT_LABEL_KO } from "@/data/roster";
import type { Data08, Member08 } from "@/data/types";
import { useFilters } from "@/lib/useFilters";
import styles from "./page.module.css";

const data = data08 as Data08;

type CcuSeriesEntry = { name_ko?: string; points?: [string, number][] };

// `ccu_series`는 계속 자라는 append-only 구조라 types.ts에서 일부러 `Record<string,
// unknown>`으로만 잡아뒀다(엄격한 스키마를 걸면 데몬이 필드를 늘릴 때마다 깨진다).
// 이 페이지에서만 실제 관측된 모양({name_ko, points: [timestamp, ccu][]})으로
// 좁혀 쓴다.
const RAW_CCU_SERIES = (data.ccu_series ?? {}) as Record<string, CcuSeriesEntry>;

const PERIOD_OPTIONS: PeriodOption[] = [
  { value: "10m", label: "최근 10분" },
  { value: "1h", label: "최근 1시간" },
  { value: "6h", label: "최근 6시간" },
  { value: "24h", label: "최근 24시간" },
];

const PERIOD_MINUTES: Record<string, number> = { "10m": 10, "1h": 60, "6h": 360, "24h": 1440 };

/** 세션 타임스탬프("YYYY-MM-DD HH:mm")는 Chzzk 쪽 KST(Asia/Seoul) 벽시계 기준이다. */
function parseKstMs(ts: string): number {
  const t = new Date(`${ts.replace(" ", "T")}:00+09:00`).getTime();
  return Number.isNaN(t) ? 0 : t;
}

function hhmm(ms: number): string {
  return new Date(ms).toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Seoul" });
}

export default function LivePageClient() {
  const { detail, period, openDetail, closeDetail, matchesFilters } = useFilters();

  const filteredMembers = useMemo(() => data.members.filter((m) => matchesFilters(m)), [matchesFilters]);

  // 정적 export라 "지금"을 뷰어의 Date.now()로 잡으면 빌드 시각과 어긋난다
  // (Freshness와 같은 문제). 이 파일이 갱신될 때마다 같이 갱신되는
  // `meta.fetched_at`을 기준 시각으로 써서 빌드/조회 시점 불일치를 원천적으로
  // 피한다.
  const nowMs = useMemo(() => new Date(data.meta.fetched_at).getTime(), []);
  const cutoffMs = period && PERIOD_MINUTES[period] ? nowMs - PERIOD_MINUTES[period] * 60_000 : null;

  const followerBarData: BarDatum[] = useMemo(
    () =>
      [...filteredMembers]
        .sort((a, b) => b.follower_per_day - a.follower_per_day)
        .map((m) => ({ name_en: m.name_en, label: m.name_ko, value: m.follower_per_day })),
    [filteredMembers]
  );

  const previewSeries: LineSeriesDatum[] = useMemo(() => {
    const filteredNameEns = new Set(filteredMembers.map((m) => m.name_en));
    return Object.entries(RAW_CCU_SERIES)
      .filter(([nameEn]) => filteredNameEns.has(nameEn))
      .map(([nameEn, entry]) => ({
        name_en: nameEn,
        label: entry.name_ko ?? nameEn,
        points: (entry.points ?? [])
          .map(([ts, v]) => ({ x: parseKstMs(ts), y: v }))
          .filter((p) => cutoffMs === null || p.x >= cutoffMs),
      }))
      .filter((s) => s.points.length > 0);
  }, [filteredMembers, cutoffMs]);

  const peakCcuBarData: BarDatum[] = useMemo(
    () =>
      filteredMembers
        .filter((m): m is Member08 & { peak_ccu: number } => m.peak_ccu !== null)
        .sort((a, b) => b.peak_ccu - a.peak_ccu)
        .map((m) => ({ name_en: m.name_en, label: m.name_ko, value: m.peak_ccu })),
    [filteredMembers]
  );

  const columns: TableColumn<Member08>[] = [
    { key: "rank", header: "순위", accessor: (r) => r.rank, align: "right" },
    { key: "name_ko", header: "멤버", accessor: (r) => r.name_ko },
    {
      key: "unit",
      header: "유닛",
      accessor: (r) => r.unit ?? "",
      render: (r) => (r.unit ? UNIT_LABEL_KO[r.unit] : "—"),
    },
    {
      key: "followers",
      header: "팔로워",
      accessor: (r) => r.followers,
      align: "right",
      render: (r) => r.followers.toLocaleString("ko-KR"),
    },
    {
      key: "follower_per_day",
      header: "일일 팔로워 증가",
      accessor: (r) => r.follower_per_day,
      align: "right",
      render: (r) => r.follower_per_day.toLocaleString("ko-KR"),
    },
    { key: "n_sessions", header: "관측 세션", accessor: (r) => r.n_sessions, align: "right" },
    {
      key: "peak_ccu",
      header: "최고 동시시청자",
      accessor: (r) => r.peak_ccu ?? -1,
      align: "right",
      render: (r) => (r.peak_ccu !== null ? Math.round(r.peak_ccu).toLocaleString("ko-KR") : "—"),
    },
    {
      key: "avg_ccu",
      header: "평균 동시시청자",
      accessor: (r) => r.avg_ccu ?? -1,
      align: "right",
      render: (r) => (r.avg_ccu !== null ? Math.round(r.avg_ccu).toLocaleString("ko-KR") : "—"),
    },
    {
      key: "ccu_per_1k_followers",
      header: "팔로워 1천명당 CCU",
      accessor: (r) => r.ccu_per_1k_followers ?? -1,
      align: "right",
      render: (r) => (r.ccu_per_1k_followers !== null ? r.ccu_per_1k_followers.toFixed(2) : "—"),
    },
  ];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 08</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>동시시청자</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["08"]} cadenceLabel={REFRESH_LABEL["08"]} />
        </div>
        <p className={styles.subhead}>
          {data.meta.note} 10분 간격 폴링, 스냅샷 {data.meta.n_snapshots}건 누적. 이 프로젝트만 실제
          시계열이라 아래 필터의 기간 옵션이 여기서 의미를 가진다.
        </p>
      </header>

      <Card padding="lg" className={styles.insightCard}>
        <Badge tone={data.enough_coverage ? "positive" : "negative"}>
          {data.enough_coverage ? "커버리지 충분" : "FR-5 커버리지 가드 작동 중"}
        </Badge>
        <p className={styles.insightText}>
          {data.enough_coverage
            ? "관측 시간·세션 수가 기준(24시간·5세션)을 넘어 아래 동시시청자 순위를 결론으로 참고할 수 있다."
            : "동시시청자는 소급 수집이 불가능하다 — 지금부터 쌓이는 것만 관측할 수 있다. 관측 시간이나 세션 수가 " +
              "기준(24시간 이상·5세션 이상)에 못 미치는 동안은 최고/평균 동시시청자 순위를 결론성 지표로 보여주지 " +
              "않는다. 대신 지금까지 실제로 관측된 원시 포인트만 \"미리보기\"로 표시한다."}
        </p>
        <div className={styles.coverageGrid}>
          <div className={styles.coverageStat}>
            <span className={styles.coverageLabel}>실관측 시간</span>
            {/* span_hours(달력 시간)가 아니라 실제로 찍은 시간. PC가 꺼져 있던 구간은 빠진다. */}
            <span className={styles.coverageValue}>{data.coverage.observed_hours.toLocaleString("ko-KR")}시간</span>
          </div>
          <div className={styles.coverageStat}>
            <span className={styles.coverageLabel}>관측 세션</span>
            {/* 세션은 sessions.length. coverage.n_live_rows 는 라이브 스냅샷 '행' 수라 다르다. */}
            <span className={styles.coverageValue}>{data.sessions.length}건</span>
          </div>
          <div className={styles.coverageStat}>
            <span className={styles.coverageLabel}>기준</span>
            <span className={styles.coverageValue}>24시간 · 5세션</span>
          </div>
          <div className={styles.coverageStat}>
            <span className={styles.coverageLabel}>관측 구간</span>
            <span className={styles.coverageValue}>
              {hhmm(new Date(data.coverage.first).getTime())} ~ {hhmm(new Date(data.coverage.last).getTime())}
            </span>
          </div>
        </div>
      </Card>

      <Section
        eyebrow="Filters"
        title="필터"
        description="멤버·유닛에 더해, 기간 필터로 아래 동시시청자 미리보기 시계열의 관측 창을 좁힐 수 있다."
      />
      <FilterBar periodOptions={PERIOD_OPTIONS} />

      <Section
        eyebrow="Charts"
        title="일일 팔로워 증가"
        description="동시시청자 가드와 무관한 지표 — 최근 팔로워 증감 속도. 막대나 이름을 클릭하면 상세 패널이 열린다."
      />
      {followerBarData.length > 0 ? (
        <Card padding="md">
          <BarChart data={followerBarData} title="멤버별 일일 팔로워 증가" onSelect={openDetail} selected={detail} />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터에 해당하는 멤버가 없다.</p>
        </Card>
      )}

      <Section
        eyebrow="Charts"
        title={data.enough_coverage ? "동시시청자 추이" : "동시시청자 미리보기 (결론 아님)"}
        description="실제 관측된 원시 포인트. 위 기간 필터로 시간 창을 좁혀 볼 수 있다."
      />
      {previewSeries.length > 0 ? (
        <Card padding="md">
          <LineChart
            series={previewSeries}
            title="멤버별 동시시청자 추이"
            xFormat={hhmm}
            onSelect={openDetail}
            selected={detail}
          />
        </Card>
      ) : (
        <Card padding="md">
          <p className={styles.empty}>선택한 필터·기간에 해당하는 관측 포인트가 없다 — 데이터가 계속 쌓이는 중이다.</p>
        </Card>
      )}

      {data.enough_coverage ? (
        <>
          <Section
            eyebrow="Charts"
            title="최고 동시시청자 순위"
            description="커버리지가 충분해 결론성 지표로 참고할 수 있다."
          />
          {peakCcuBarData.length > 0 ? (
            <Card padding="md">
              <BarChart data={peakCcuBarData} title="멤버별 최고 동시시청자" onSelect={openDetail} selected={detail} />
            </Card>
          ) : (
            <Card padding="md">
              <p className={styles.empty}>세션이 관측된 멤버가 없다.</p>
            </Card>
          )}
        </>
      ) : null}

      <Section eyebrow="Table" title="전체 지표" description="열 제목을 클릭하면 정렬된다. 행을 클릭하면 상세 패널이 열린다. 커버리지가 부족한 멤버의 동시시청자 값은 '—'로 표시한다." />
      <Table
        columns={columns}
        rows={filteredMembers}
        getRowKey={(r) => r.name_en}
        initialSortKey="followers"
        initialSortDir="desc"
        caption="프로젝트 08 · 동시시청자 (FR-5 커버리지 가드 적용)"
        onRowClick={(r) => openDetail(r.name_en)}
      />

      <div className={styles.statRow}>
        <StatTile label="누적 스냅샷" value={data.meta.n_snapshots.toLocaleString("ko-KR")} unit="건" caption={`${data.meta.interval_min}분 간격`} />
        <StatTile label="관측 세션" value={data.sessions.length.toLocaleString("ko-KR")} unit="건" caption={`라이브 스냅샷 ${data.coverage.n_live_rows}행`} />
      </div>

      {detail ? <MemberDetail nameEn={detail} onClose={closeDetail} /> : null}
    </div>
  );
}
