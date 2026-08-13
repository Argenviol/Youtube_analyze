"use client";

/**
 * 프로젝트 10 · 호요버스 (Phase 2).
 *
 * 캐릭터 단위 프로젝트라 `members[]`가 없다 — 09와 같은 이유로 01~06·08의
 * page.tsx + Suspense + `*PageClient.tsx` 골격을 쓰지 않는다. `useSearchParams`를
 * 쓰지 않으므로(게임·희귀도 필터는 로컬 `useState`) `<Suspense>`도 필요 없다.
 * 전역 멤버/유닛 필터(FR-1)도 걸지 않는다 — 조인 키가 멤버가 아니라 캐릭터
 * (char_id)다.
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
import data10 from "@/data/10.json";
import { REFRESH_INTERVAL_MIN, REFRESH_LABEL } from "@/data/refresh";
import type { Character10, Data10 } from "@/data/types";
import styles from "./page.module.css";

const data = data10 as Data10;

const GAME_NAME_KO = new Map(data.app_summary.map((a) => [a.game, a.name_ko]));
function gameLabel(game: string): string {
  return GAME_NAME_KO.get(game) ?? game;
}

function stars(rank: number): string {
  return "★".repeat(Math.max(0, Math.min(5, Math.round(rank))));
}

function dateOnly(iso: string): string {
  return iso.slice(0, 10);
}

function signedFixed(v: number | null | undefined, digits = 2): string {
  if (v === null || v === undefined) return "—";
  return `${v >= 0 ? "+" : ""}${v.toFixed(digits)}`;
}

function monthX(month: string): number {
  const [y, m] = month.split("-").map(Number);
  return y * 12 + m;
}

const MONTH_LABEL = new Map<number, string>(data.monthly_sentiment.map((m) => [monthX(m.month), m.month]));
function monthXFormat(v: number): string {
  return MONTH_LABEL.get(Math.round(v)) ?? String(v);
}

const MONTHLY_SENTIMENT_SERIES: LineSeriesDatum[] = (() => {
  const byGame = new Map<string, { x: number; y: number }[]>();
  for (const m of data.monthly_sentiment) {
    if (!byGame.has(m.game)) byGame.set(m.game, []);
    byGame.get(m.game)!.push({ x: monthX(m.month), y: m.avg_score });
  }
  return [...byGame.entries()].map(([game, points]) => ({ name_en: game, label: gameLabel(game), points }));
})();

const GAMES = data.meta.games;
const RANKS = [5, 4];

function buildCharacterColumns(): TableColumn<Character10>[] {
  return [
    { key: "game", header: "게임", accessor: (r) => gameLabel(r.game) },
    { key: "name_ko", header: "캐릭터", accessor: (r) => r.name_ko },
    { key: "rank", header: "희귀도", accessor: (r) => r.rank, align: "right", render: (r) => stars(r.rank) },
    { key: "element", header: "원소/커맨드", accessor: (r) => r.element },
    {
      key: "mention_count",
      header: "리뷰 언급수",
      accessor: (r) => r.mention_count ?? -1,
      align: "right",
      render: (r) => (r.mention_count !== null ? r.mention_count.toLocaleString("ko-KR") : "—"),
    },
    {
      key: "mention_rate_per_10k",
      header: "언급률(만 건당)",
      accessor: (r) => r.mention_rate_per_10k ?? -1,
      align: "right",
      render: (r) => (r.mention_rate_per_10k !== null ? r.mention_rate_per_10k.toFixed(2) : "—"),
    },
    {
      key: "sentiment_vs_baseline",
      header: "평점 편차",
      accessor: (r) => r.sentiment_vs_baseline ?? -Infinity,
      align: "right",
      render: (r) => signedFixed(r.sentiment_vs_baseline),
    },
    {
      key: "push_rank",
      header: "푸시 순위(프록시)",
      accessor: (r) => r.push_rank ?? Infinity,
      align: "right",
      render: (r) => r.push_rank ?? "—",
    },
    {
      key: "audience_rank",
      header: "반응 순위",
      accessor: (r) => r.audience_rank ?? Infinity,
      align: "right",
      render: (r) => r.audience_rank ?? "—",
    },
  ];
}

function rankedColumns(rankKey: "push_rank" | "audience_rank", rankLabel: string): TableColumn<Character10>[] {
  return [
    { key: rankKey, header: rankLabel, accessor: (r) => r[rankKey] ?? Infinity, align: "right" },
    { key: "game", header: "게임", accessor: (r) => gameLabel(r.game) },
    { key: "name_ko", header: "캐릭터", accessor: (r) => r.name_ko },
    { key: "rank", header: "희귀도", accessor: (r) => r.rank, align: "right", render: (r) => stars(r.rank) },
    { key: "release_date", header: "출시일", accessor: (r) => r.release_date, render: (r) => dateOnly(r.release_date) },
    {
      key: "mention_count",
      header: "리뷰 언급수",
      accessor: (r) => r.mention_count ?? -1,
      align: "right",
      render: (r) => (r.mention_count !== null ? r.mention_count.toLocaleString("ko-KR") : "—"),
    },
  ];
}

const CHARACTER_COLUMNS = buildCharacterColumns();
const PUSH_COLUMNS = rankedColumns("push_rank", "푸시 순위");
const AUDIENCE_COLUMNS = rankedColumns("audience_rank", "반응 순위");

const gapColumns: TableColumn<Character10>[] = [
  { key: "name_ko", header: "캐릭터", accessor: (r) => r.name_ko },
  { key: "game", header: "게임", accessor: (r) => gameLabel(r.game) },
  { key: "push_rank", header: "푸시 순위", accessor: (r) => r.push_rank ?? Infinity, align: "right" },
  { key: "audience_rank", header: "반응 순위", accessor: (r) => r.audience_rank ?? Infinity, align: "right" },
  { key: "gap", header: "격차", accessor: (r) => r.gap ?? 0, align: "right", render: (r) => signedFixed(r.gap, 0) },
];

export default function Page() {
  const [gameFilter, setGameFilter] = useState<string[]>([]);
  const [rankFilter, setRankFilter] = useState<number[]>([]);

  const toggleGame = (g: string) => setGameFilter((cur) => (cur.includes(g) ? cur.filter((x) => x !== g) : [...cur, g]));
  const toggleRank = (r: number) => setRankFilter((cur) => (cur.includes(r) ? cur.filter((x) => x !== r) : [...cur, r]));
  const resetFilters = () => {
    setGameFilter([]);
    setRankFilter([]);
  };
  const hasActiveFilters = gameFilter.length > 0 || rankFilter.length > 0;

  const filteredCharacters = useMemo(
    () =>
      data.characters.filter(
        (c) =>
          (gameFilter.length === 0 || gameFilter.includes(c.game)) &&
          (rankFilter.length === 0 || rankFilter.includes(c.rank))
      ),
    [gameFilter, rankFilter]
  );

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Project 10</p>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>호요버스</h1>
          <Freshness fetchedAt={data.meta.fetched_at} intervalMinutes={REFRESH_INTERVAL_MIN["10"]} cadenceLabel={REFRESH_LABEL["10"]} />
        </div>
        <p className={styles.subhead}>
          원신·붕괴: 스타레일 캐릭터 {data.characters.length}종(플레이어 아바타 {data.meta.n_playable_avatars_excluded}
          종 제외) × 앱스토어 리뷰 {data.meta.n_reviews.toLocaleString("ko-KR")}건 기준. Zenless Zone Zero는 작동하는
          데이터 소스가 없어 수집 대상에서 제외했다.
        </p>
        {data.characters.length !== data.meta.n_characters ? (
          <p className={styles.subhead}>
            참고: meta.n_characters는 {data.meta.n_characters}종이라고 적혀 있지만 실제 characters 배열은{" "}
            {data.characters.length}종이다 — 아래 표는 실제 배열 기준(더 신뢰할 수 있는 쪽)으로 센다. 소스
            파이프라인(10_hoyoverse/analyze.py)의 카운트 로직에 차이가 있는 것으로 보인다.
          </p>
        ) : null}
      </header>

      <Card padding="lg" className={styles.warnCard}>
        <Badge tone="negative">데이터 소스 폐기 — Google Trends 미사용</Badge>
        <p className={styles.insightText}>
          Google Trends 비공식 클라이언트({data.trends_status.library})가 매 실행마다 즉시 실패한다:{" "}
          <code>{data.trends_status.error}</code>. {data.trends_status.note}
        </p>
      </Card>

      <Card padding="lg" className={styles.warnCard}>
        <Badge tone="cautionary">프록시 지표 — &quot;공식 푸시&quot; 순위</Badge>
        <p className={styles.insightText}>
          실제 가챠 배너 노출 데이터는 공개돼 있지 않다. 아래 &quot;푸시 순위&quot;는 5★ 캐릭터의{" "}
          <strong>출시 최신성</strong>으로 근사한 값이다(1위 = 가장 최근 출시) — 실측 배너율이 아니라 근사치라는
          점을 표·차트 라벨에 그대로 남긴다.
        </p>
      </Card>

      <Section
        eyebrow="Apps"
        title="앱스토어 요약"
        description="구글 플레이 기준 평점·평가 수. 리뷰 본문의 캐릭터 이름 언급으로 유저 반응을 근사한다."
      />
      <div className={styles.statRow}>
        {data.app_summary.map((a) => (
          <StatTile
            key={a.game}
            label={`${a.name_ko} 평점`}
            value={a.score.toFixed(2)}
            caption={`평가 ${a.ratings.toLocaleString("ko-KR")}개 · 스토어 리뷰 ${a.reviews_total.toLocaleString("ko-KR")}건 · ${a.installs}`}
          />
        ))}
        <StatTile
          label="매칭 신뢰도 낮음"
          value={data.n_matchable_low_confidence}
          unit="명"
          caption="이름이 짧거나 흔해 리뷰 매칭이 불확실한 캐릭터 수"
        />
      </div>

      <Section eyebrow="Charts" title="월별 평균 평점 추이" description="게임별 앱스토어 리뷰 월간 평균 평점." />
      <Card padding="md">
        <LineChart
          series={MONTHLY_SENTIMENT_SERIES}
          title="월별 평균 평점 추이"
          xFormat={monthXFormat}
          yFormat={(v) => v.toFixed(2)}
        />
      </Card>

      <Section eyebrow="Filters" title="필터" description="게임·희귀도로 아래 표를 좁힌다 (멤버/유닛 필터 아님 — 이 프로젝트는 캐릭터 단위)." />
      <div className={styles.filterBar} role="group" aria-label="게임·희귀도 필터">
        <div className={styles.filterRow}>
          <span className={styles.filterRowLabel}>게임</span>
          <div className={styles.chips}>
            {GAMES.map((g) => (
              <FilterChip key={g} label={gameLabel(g)} active={gameFilter.includes(g)} onClick={() => toggleGame(g)} />
            ))}
          </div>
        </div>
        <div className={styles.filterRow}>
          <span className={styles.filterRowLabel}>희귀도</span>
          <div className={styles.chips}>
            {RANKS.map((r) => (
              <FilterChip key={r} label={`${r}★`} active={rankFilter.includes(r)} onClick={() => toggleRank(r)} />
            ))}
          </div>
        </div>
        <button type="button" className={styles.reset} onClick={resetFilters} disabled={!hasActiveFilters}>
          필터 초기화
        </button>
      </div>

      <Section
        eyebrow="Table"
        title="푸시 순위 상위 15명 (프록시)"
        description="5★ 캐릭터의 출시 최신성 기준 — 실제 배너율 데이터 아님."
      />
      <Table columns={PUSH_COLUMNS} rows={data.push_top} getRowKey={(r) => r.char_id} initialSortKey="push_rank" initialSortDir="asc" />

      <Section eyebrow="Table" title="반응 순위 상위 15명" description="리뷰 언급률(mention_rate_per_10k) 기준." />
      <Table
        columns={AUDIENCE_COLUMNS}
        rows={data.audience_top}
        getRowKey={(r) => r.char_id}
        initialSortKey="audience_rank"
        initialSortDir="asc"
      />

      <Section
        eyebrow="Table"
        title="과대 푸시 vs 숨은 인기"
        description="왼쪽: 많이 밀었는데 반응이 적은 캐릭터. 오른쪽: 덜 밀었는데 반응이 큰(숨은 인기) 캐릭터."
      />
      <div className={styles.gapGrid}>
        <div>
          <p className={styles.gapLabel}>과대 푸시 (push는 상위인데 반응은 하위)</p>
          <Table columns={gapColumns} rows={data.gap_overpushed} getRowKey={(r) => r.char_id} initialSortKey="gap" initialSortDir="desc" />
        </div>
        <div>
          <p className={styles.gapLabel}>숨은 인기 (push는 하위인데 반응은 상위)</p>
          <Table columns={gapColumns} rows={data.gap_sleeper} getRowKey={(r) => r.char_id} initialSortKey="gap" initialSortDir="asc" />
        </div>
      </div>

      <Section eyebrow="Table" title="전체 캐릭터" description="열 제목을 클릭하면 정렬된다." />
      <Table
        columns={CHARACTER_COLUMNS}
        rows={filteredCharacters}
        getRowKey={(r) => r.char_id}
        initialSortKey="mention_count"
        initialSortDir="desc"
        caption={`프로젝트 10 · 캐릭터 전체 (${filteredCharacters.length}명)`}
      />
    </div>
  );
}
