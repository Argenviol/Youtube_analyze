/**
 * 드릴다운(FR-2)용 크로스 프로젝트 집계.
 *
 * `<MemberDetail />`은 `name_en` 하나를 받아 동기화된 모든 프로젝트
 * (01~06, 08 — 07은 앱 미포함)에서 그 멤버의 대표 지표를 모아 보여줘야 한다.
 * 이 모듈이 그 조인을 담당한다: 각 프로젝트 JSON을 읽고, contract.md가
 * "대표 지표"로 표시한 필드만 뽑아 프로젝트 공통 모양(`MemberMetricGroup`)으로
 * 맞춘다.
 *
 * 08(동시시청자)은 FR-5 커버리지 가드를 그대로 계승한다 — `enough_coverage`가
 * false면 숫자 대신 "데이터 수집 중" 상태를 반환한다.
 */
import data01 from "./01.json";
import data02 from "./02.json";
import data03 from "./03.json";
import data04 from "./04.json";
import data05 from "./05.json";
import data06 from "./06.json";
import data08 from "./08.json";
import { PROJECT_HREF, PROJECT_TITLE } from "./projects";
import type { Data01, Data02, Data03, Data04, Data05, Data06, Data08, ProjectId } from "./types";

export type MetricValue = { label: string; value: string; note?: string };

export type MemberMetricGroup = {
  projectId: ProjectId;
  title: string;
  href: string;
  fetchedAt: string;
  /** 데이터가 결론을 내기엔 아직 얇을 때(FR-5) 숫자 대신 이 메시지를 보여준다. */
  pending?: string;
  metrics: MetricValue[];
};

function fmtInt(n: number): string {
  return Math.round(n).toLocaleString("ko-KR");
}

function fmtPercent(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

function fmtDecimal(n: number, digits = 1): string {
  return n.toLocaleString("ko-KR", { maximumFractionDigits: digits });
}

export function getMemberMetricGroups(nameEn: string): MemberMetricGroup[] {
  const groups: MemberMetricGroup[] = [];

  const d01 = data01 as Data01;
  const m01 = d01.members.find((m) => m.name_en === nameEn);
  if (m01) {
    groups.push({
      projectId: "01",
      title: PROJECT_TITLE["01"],
      href: PROJECT_HREF["01"],
      fetchedAt: d01.meta.fetched_at,
      metrics: [
        { label: "구독자", value: `${fmtInt(m01.subscribers)}명` },
        { label: "최근 평균 조회수", value: `${fmtInt(m01.recent_avg_views)}회` },
        { label: "도달률(reach ratio)", value: fmtPercent(m01.reach_ratio) },
      ],
    });
  }

  const d02 = data02 as Data02;
  const m02 = d02.members.find((m) => m.name_en === nameEn);
  if (m02) {
    groups.push({
      projectId: "02",
      title: PROJECT_TITLE["02"],
      href: PROJECT_HREF["02"],
      fetchedAt: d02.meta.fetched_at,
      metrics: [
        { label: "커버곡 수", value: `${fmtInt(m02.cover_count)}곡` },
        { label: "커버곡 총 조회수", value: `${fmtInt(m02.total_views)}회` },
        { label: "평균 참여율", value: fmtPercent(m02.avg_engagement_rate) },
      ],
    });
  }

  const d03 = data03 as Data03;
  const m03 = d03.members.find((m) => m.name_en === nameEn);
  if (m03) {
    groups.push({
      projectId: "03",
      title: PROJECT_TITLE["03"],
      href: PROJECT_HREF["03"],
      fetchedAt: d03.meta.fetched_at,
      metrics: [
        { label: "방송 횟수", value: `${fmtInt(m03.stream_count)}건` },
        { label: "주당 방송 시간", value: `${fmtDecimal(m03.hours_per_week)}시간` },
        { label: "평균 시작 시각", value: `${fmtDecimal(m03.avg_start_hour)}시` },
      ],
    });
  }

  const d04 = data04 as Data04;
  const m04 = d04.members.find((m) => m.name_en === nameEn);
  if (m04) {
    groups.push({
      projectId: "04",
      title: PROJECT_TITLE["04"],
      href: PROJECT_HREF["04"],
      fetchedAt: d04.meta.fetched_at,
      metrics: [
        { label: "팬 클립 수", value: `${fmtInt(m04.clip_count)}개` },
        { label: "클립 총 조회수", value: `${fmtInt(m04.total_clip_views)}회` },
        { label: "팬 클립 채널 수", value: `${fmtInt(m04.fan_channels)}개` },
      ],
    });
  }

  const d05 = data05 as Data05;
  const m05 = d05.members.find((m) => m.name_en === nameEn);
  if (m05) {
    groups.push({
      projectId: "05",
      title: PROJECT_TITLE["05"],
      href: PROJECT_HREF["05"],
      fetchedAt: d05.meta.fetched_at,
      metrics: [
        { label: "여론 점수(sentiment)", value: fmtDecimal(m05.sentiment_score, 2) },
        { label: "긍정 비율", value: fmtPercent(m05.positive_share) },
        { label: "주요 화제", value: m05.top_topic },
      ],
    });
  }

  const d06 = data06 as Data06;
  const m06 = d06.members.find((m) => m.name_en === nameEn);
  if (m06) {
    groups.push({
      projectId: "06",
      title: PROJECT_TITLE["06"],
      href: PROJECT_HREF["06"],
      fetchedAt: d06.meta.fetched_at,
      metrics: [
        { label: "구독자(경쟁사 비교 표본)", value: `${fmtInt(m06.subscribers)}명` },
        { label: "도달률(reach ratio)", value: fmtPercent(m06.reach_ratio) },
        { label: "비교 그룹", value: m06.group },
      ],
    });
  }

  const d08 = data08 as Data08;
  const m08 = d08.members.find((m) => m.name_en === nameEn);
  if (m08) {
    if (!d08.enough_coverage || m08.peak_ccu === null) {
      groups.push({
        projectId: "08",
        title: PROJECT_TITLE["08"],
        href: PROJECT_HREF["08"],
        fetchedAt: d08.meta.fetched_at,
        // 세션 수는 sessions.length. coverage.n_live_rows 는 라이브 스냅샷 '행' 수라 다르다.
        pending: `데이터 수집 중 — 실관측 ${fmtDecimal(d08.coverage.observed_hours, 1)}시간 · 세션 ${d08.sessions.length}건 (기준: 24시간·5세션 이상)`,
        metrics: [{ label: "팔로워", value: `${fmtInt(m08.followers)}명` }],
      });
    } else {
      groups.push({
        projectId: "08",
        title: PROJECT_TITLE["08"],
        href: PROJECT_HREF["08"],
        fetchedAt: d08.meta.fetched_at,
        metrics: [
          { label: "최고 동시시청자", value: `${fmtInt(m08.peak_ccu)}명` },
          { label: "평균 동시시청자", value: m08.avg_ccu !== null ? `${fmtInt(m08.avg_ccu)}명` : "—" },
          { label: "팔로워 1천 명당 CCU", value: m08.ccu_per_1k_followers !== null ? fmtDecimal(m08.ccu_per_1k_followers, 2) : "—" },
        ],
      });
    }
  }

  return groups;
}
