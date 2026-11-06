/**
 * 프로젝트별 예상 갱신 주기 (PRD §4 표). FR-4 신선도 배지가
 * `meta.fetched_at`과 이 값을 비교해 경고 여부를 판단한다.
 */
import type { ProjectId } from "./types";

export type ExtendedProjectId = ProjectId;

// ⚠ 이 값은 youtube_analyze_all/scripts/refresh.py 의 GROUPS(live 10분 · daily · weekly)와
//   반드시 일치해야 한다. 그쪽이 실제 수집 스케줄이고 여기는 표시용이다. 한쪽만 고치면 화면이 거짓말을 한다.
export const REFRESH_INTERVAL_MIN: Record<ExtendedProjectId, number> = {
  "01": 24 * 60, // daily
  "02": 24 * 60, // daily (전량 열거로 전환 후 비용이 낮아짐)
  "03": 24 * 60, // daily
  "04": 7 * 24 * 60, // weekly — search.list 의존, 45회 × 100 units
  "05": 7 * 24 * 60, // weekly
  "06": 24 * 60, // daily
  "08": 10, // live
};

export const REFRESH_LABEL: Record<ExtendedProjectId, string> = {
  "01": "일 1회",
  "02": "일 1회",
  "03": "일 1회",
  "04": "주 1회",
  "05": "주 1회",
  "06": "일 1회",
  "08": "10분",
};
