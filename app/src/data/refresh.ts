/**
 * 프로젝트별 예상 갱신 주기 (PRD §4 "앱에 포함" 표). FR-4 신선도 배지가
 * `meta.fetched_at`과 이 값을 비교해 경고 여부를 판단한다.
 */
import type { ProjectId } from "./types";

/**
 * 09·10·11(Phase 2)은 멤버/유닛 필터가 걸리는 01~06·08과 성격이 달라
 * `ProjectId`(member-level 8개) 자체는 넓히지 않고, 신선도 표시에만 쓰는
 * 이 파일 로컬 타입으로 확장한다 — `projects.ts`/`aggregate.ts`(멤버 드릴다운
 * 전용)는 그대로 두어도 된다.
 */
export type ExtendedProjectId = ProjectId | "09" | "10" | "11";

// ⚠ 01~06·08 값은 youtube_analyze_all/scripts/refresh.py 의 GROUPS 와 반드시
//   일치해야 한다. 그쪽이 실제 수집 스케줄이고 여기는 표시용이다. 한쪽만
//   고치면 화면이 거짓말을 한다.
//   02는 2026-08-12 수집 방식을 search.list(3,300 units)에서 업로드 재생목록 전량 열거
//   (~173 units)로 바꾸면서 weekly → daily 로 옮겼다.
//
//   09·10·11은 아직 scripts/refresh.py의 GROUPS에 없다(Phase 2 구현 세션에서
//   추가됨, refresh.py 자체는 이 세션의 스코프 밖) — 값은 PRD Phase 2 편입
//   지시(09 분기·10/11 주 1회)를 그대로 반영해뒀고, refresh.py에 그룹이
//   추가되는 대로 이 주석을 지운다.
export const REFRESH_INTERVAL_MIN: Record<ExtendedProjectId, number> = {
  "01": 24 * 60, // daily
  "02": 24 * 60, // daily (전량 열거로 전환 후 비용이 낮아짐)
  "03": 24 * 60, // daily
  "04": 7 * 24 * 60, // weekly — search.list 의존, 33회 × 100 units
  "05": 7 * 24 * 60, // weekly
  "06": 24 * 60, // daily
  "08": 10, // live
  "09": 90 * 24 * 60, // quarterly — DART 공시(감사보고서·정기보고서) 주기
  "10": 7 * 24 * 60, // weekly
  "11": 7 * 24 * 60, // weekly
};

export const REFRESH_LABEL: Record<ExtendedProjectId, string> = {
  "01": "일 1회",
  "02": "일 1회",
  "03": "일 1회",
  "04": "주 1회",
  "05": "주 1회",
  "06": "일 1회",
  "08": "10분",
  "09": "분기 1회",
  "10": "주 1회",
  "11": "주 1회",
};
