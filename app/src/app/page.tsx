import Badge from "@/components/Badge";
import Card from "@/components/Card";
import Section from "@/components/Section";
import StatTile from "@/components/StatTile";
import data01 from "@/data/01.json";
import data02 from "@/data/02.json";
import data03 from "@/data/03.json";
import data04 from "@/data/04.json";
import data05 from "@/data/05.json";
import data06 from "@/data/06.json";
import data08 from "@/data/08.json";
import type { Data01, Data02, Data03, Data04, Data05, Data06, Data08 } from "@/data/types";
import { overlapLine } from "@/lib/overlap";
import styles from "./page.module.css";

// M3 파트 2 — 01뿐이던 레퍼런스 연결을 나머지 6개(02~06, 08)까지 넓혔다. 07은
// PRD 4절 "앱에서 제외" 대상이라 Next.js 데이터 계약에 없다 — 허브에서는
// 기존 정적 HTML로 외부 링크만 건다.
const project01 = data01 as Data01;
const project02 = data02 as Data02;
const project03 = data03 as Data03;
const project04 = data04 as Data04;
const project05 = data05 as Data05;
const project06 = data06 as Data06;
const project08 = data08 as Data08;

const project01TotalSubscribers = project01.members.reduce((sum, m) => sum + m.subscribers, 0);

const ALL_FETCHED_AT = [
  project01.meta.fetched_at,
  project02.meta.fetched_at,
  project03.meta.fetched_at,
  project04.meta.fetched_at,
  project05.meta.fetched_at,
  project06.meta.fetched_at,
  project08.meta.fetched_at,
];
const oldestFetchedAt = ALL_FETCHED_AT.reduce((oldest, cur) => (new Date(cur) < new Date(oldest) ? cur : oldest));

const peakCcuValues = project08.members
  .map((m) => m.peak_ccu)
  .filter((v): v is number => v !== null);
const maxPeakCcu = peakCcuValues.length > 0 ? Math.max(...peakCcuValues) : null;

type Insight = {
  headline: string;
  detail: string;
};

// 인사이트 3개는 전부 실제 데이터에서 계산한다 — M1 골격 단계에 있던 자리표시자
// 문구(예: "커버곡 조회수는 발매 후 72시간에 절반이 몰린다", "동시시청자는 방송
// 시작 10분 안에 정점을 찍는다")는 근거 데이터가 없는 주장이라 M3에서 제거했다.
// 02는 조회수 기반 시계열 데이터가 없고, 08은 아직 세션 자체가 FR-5 기준 미만이라
// 그런 행태 패턴을 결론 낼 수 없다 — 채용 심사자에게 보여줄 첫 화면에서부터
// 검증 안 된 주장을 하지 않는다는 원칙을 지킨다.
// 멤버 이름을 붙인 "1위" 대신 상위 3명이 겹치는지로 쓴다(공개 화면이라 멤버 비교 문구를 만들지 않는다).
const insight01 = overlapLine(project01.members, (m) => m.subscribers, (m) => m.recent_avg_engagement_rate, "구독자", "참여율");
const insight02 = overlapLine(project02.members, (m) => m.total_views, (m) => m.avg_engagement_rate, "커버곡 조회수", "참여율");

const INSIGHTS: Insight[] = [
  {
    headline: "팔로워 규모와 팬덤 밀도는 다른 지표다",
    detail: `${insight01} — 01 채널 성과`,
  },
  {
    headline: insight02,
    detail: `커버곡 수(cover_count)는 ${project02.meta.method_changed_at}부터 업로드 재생목록 전량 열거로 수집한다 — 그 이전 스냅샷과는 비교할 수 없다 — 02 커버곡 랭킹`,
  },
  {
    headline: project08.enough_coverage
      ? "동시시청자 데이터가 결론을 낼 만큼 쌓였다"
      : "동시시청자는 아직 결론을 낼 만큼 데이터가 쌓이지 않았다",
    // 세션 수는 sessions.length 다. coverage.n_live_rows 는 라이브 스냅샷 '행' 수라 훨씬 크다.
    // 판단 기준은 span_hours(달력 시간)가 아니라 observed_hours(실제 찍은 시간)다.
    detail: `실관측 ${project08.coverage.observed_hours}시간 · 세션 ${project08.sessions.length}건(기준 24시간·5세션) · 커버리지 ${Math.round(project08.coverage.coverage_ratio * 100)}% — FR-5 커버리지 가드가 이 상태를 그대로 UI에 반영한다 — 08 동시시청자`,
  },
];

type ProjectCadence = "10min" | "daily" | "weekly" | "quarterly" | "static";

const CADENCE_LABEL: Record<ProjectCadence, string> = {
  "10min": "10분마다 갱신",
  daily: "일 1회 갱신",
  weekly: "주 1회 갱신",
  quarterly: "분기 1회 갱신",
  static: "정적 · 외부 페이지",
};

const CADENCE_TONE: Record<ProjectCadence, "primary" | "positive" | "neutral" | "cautionary"> = {
  "10min": "primary",
  daily: "positive",
  weekly: "neutral",
  quarterly: "neutral",
  static: "cautionary",
};

type Project = {
  no: string;
  title: string;
  href: string;
  cadence: ProjectCadence;
  statLabel: string;
  statValue: string;
  statUnit?: string;
  highlight?: boolean;
  /** 07처럼 Next.js 앱 라우트 밖(기존 정적 HTML)으로 나가는 카드. */
  external?: boolean;
};

const PROJECTS: Project[] = [
  {
    no: "01",
    title: "멤버 채널 성과",
    href: "/projects/01-channel",
    cadence: "daily",
    statLabel: "구독자 합계",
    statValue: project01TotalSubscribers.toLocaleString("ko-KR"),
    statUnit: "명",
  },
  {
    no: "02",
    title: "커버곡 랭킹",
    href: "/projects/02-cover",
    cadence: "weekly",
    statLabel: "수집된 커버곡",
    statValue: project02.meta.n_covers.toLocaleString("ko-KR"),
    statUnit: "곡",
  },
  {
    no: "03",
    title: "치지직 방송 패턴",
    href: "/projects/03-stream",
    cadence: "daily",
    statLabel: "수집된 방송",
    statValue: project03.meta.n_streams.toLocaleString("ko-KR"),
    statUnit: "건",
  },
  {
    no: "04",
    title: "키리누키 생태계",
    href: "/projects/04-kirinuki",
    cadence: "weekly",
    statLabel: "활성 클립 채널",
    statValue: project04.meta.n_clip_channels.toLocaleString("ko-KR"),
    statUnit: "개",
  },
  {
    no: "05",
    title: "댓글 여론",
    href: "/projects/05-sentiment",
    cadence: "weekly",
    statLabel: "분석 댓글",
    statValue: project05.meta.n_comments.toLocaleString("ko-KR"),
    statUnit: "건",
  },
  {
    no: "06",
    title: "경쟁사 비교",
    href: "/projects/06-competitor",
    cadence: "daily",
    statLabel: "비교 그룹",
    statValue: project06.meta.groups.length.toLocaleString("ko-KR"),
    statUnit: "팀",
  },
  {
    no: "07",
    title: "시장 분석",
    href: "../../youtube_analyze_all/07_market_analysis/site/index.html",
    cadence: "static",
    statLabel: "외부 리서치 기반",
    statValue: "정적 페이지",
    external: true,
  },
  {
    no: "08",
    title: "동시시청자",
    href: "/projects/08-live",
    cadence: "10min",
    statLabel: "최근 정점 동시시청자",
    statValue: maxPeakCcu !== null ? maxPeakCcu.toLocaleString("ko-KR") : "수집 중",
    statUnit: maxPeakCcu !== null ? "명" : undefined,
    highlight: true,
  },
];

// 아래 문구는 PROJECTS 에서 파생시킨다. 하드코딩해두면 프로젝트가 늘 때 소제목만 남아 거짓말을 한다.
const LIVE_PROJECT_NOS = PROJECTS.filter((p) => !p.external).map((p) => p.no);
const EXTERNAL_PROJECT_NOS = PROJECTS.filter((p) => p.external).map((p) => p.no);

const PROJECTS_SUMMARY = [
  `갱신되는 ${LIVE_PROJECT_NOS.length}개 프로젝트`,
  EXTERNAL_PROJECT_NOS.length > 0
    ? `정적 유지되는 시장 분석 ${EXTERNAL_PROJECT_NOS.length}개(${EXTERNAL_PROJECT_NOS.join("·")}, 외부 링크)`
    : null,
]
  .filter(Boolean)
  .join(" + ");

export default function Home() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>StelLive 팬덤 애널리틱스</p>
          <h1 className={styles.title}>대시보드</h1>
        </div>
        <p className={styles.subhead}>
          데이터 분석가 채용 심사자를 위한 허브 — 발견한 인사이트를 먼저 보여주고,
          관심이 생기면 직접 데이터를 파고들 수 있게 만들었다.
        </p>
      </header>

      <section aria-label="핵심 인사이트" className={styles.insights}>
        {INSIGHTS.map((insight, i) => (
          <Card key={insight.headline} padding="lg" className={styles.insightCard}>
            <span className={styles.insightIndex}>{String(i + 1).padStart(2, "0")}</span>
            <p className={styles.insightHeadline}>{insight.headline}</p>
            <p className={styles.insightDetail}>{insight.detail}</p>
          </Card>
        ))}
      </section>

      <section className={styles.projectsSection}>
        <Section
          eyebrow="Projects"
          title="프로젝트"
          description={PROJECTS_SUMMARY}
        />
        <div className={styles.grid}>
          {PROJECTS.map((project) => (
            <Card
              key={project.no}
              href={project.href}
              external={project.external}
              padding="md"
              className={project.highlight ? styles.highlightCard : undefined}
            >
              <div className={styles.cardTop}>
                <span className={styles.cardNo}>{project.no}</span>
                <Badge tone={CADENCE_TONE[project.cadence]}>{CADENCE_LABEL[project.cadence]}</Badge>
              </div>
              <h3 className={styles.cardTitle}>
                {project.title}
                {project.external ? <span className={styles.externalMark}> ↗</span> : null}
              </h3>
              <StatTile label={project.statLabel} value={project.statValue} unit={project.statUnit} />
            </Card>
          ))}
        </div>
      </section>

      <footer className={styles.freshness}>
        <Badge tone="neutral">데이터 신선도</Badge>
        <span className={styles.freshnessText}>
          {LIVE_PROJECT_NOS.join(" · ")} 총 {LIVE_PROJECT_NOS.length}개 프로젝트가 실데이터에 연결됐다 —
          가장 오래된 수집 시각 {new Date(oldestFetchedAt).toLocaleString("ko-KR")} · 07 시장 분석은 외부
          정적 페이지(갱신 없음)
        </span>
      </footer>
    </div>
  );
}
