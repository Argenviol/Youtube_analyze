/**
 * Montage (Wanted Lab Design System for Web) 디자인 토큰.
 *
 * 출처: https://github.com/wanteddev/montage-web (MIT)
 *       packages/wds-theme/src/theme/{atomic,semantic,spacing}
 *
 * `@wanteddev/wds`는 GitHub Packages 전용으로 배포되어 무인증 접근 시 401이
 * 발생한다 (PRD 8절 참고). 그래서 컴포넌트 라이브러리를 설치하는 대신,
 * `youtube_analyze_all/common/montage.py`에 이미 추출된 실제 토큰 값을
 * 이 파일로 그대로 옮겨 왔다. 값의 원본(source of truth)은 montage.py이며,
 * 이 파일과 `app/src/app/globals.css`의 CSS 변수 블록은 그 값과 반드시
 * 일치해야 한다.
 *
 * 컴포넌트에서 하드코딩 hex를 쓰지 않고, 이 파일의 값(또는 globals.css가
 * 정의하는 동일한 값의 CSS 변수 `var(--*)`)만 사용한다.
 */

// ---------------------------------------------------------------------------
// Atomic — 원자 팔레트 (wds-theme/src/theme/atomic)
// ---------------------------------------------------------------------------
export const coolNeutral = {
  5: "#0F0F10",
  7: "#141415",
  10: "#171719",
  15: "#1B1C1E",
  17: "#212225",
  20: "#292A2D",
  22: "#2E2F33",
  23: "#333438",
  25: "#37383C",
  30: "#46474C",
  40: "#5A5C63",
  50: "#70737C",
  60: "#878A93",
  70: "#989BA2",
  80: "#AEB0B6",
  90: "#C2C4C8",
  95: "#DBDCDF",
  96: "#E1E2E4",
  97: "#EAEBEC",
  98: "#F4F4F5",
  99: "#F7F7F8",
} as const;

export const blue = { 40: "#0054D1", 45: "#005EEB", 50: "#0066FF", 55: "#1A75FF", 60: "#3385FF" } as const;
export const red = { 40: "#E52222", 50: "#FF4242", 60: "#FF6363" } as const;
export const redOrange = { 48: "#F55A00", 50: "#FF5E00", 60: "#FF7B2E" } as const;
export const orange = { 39: "#D17600", 50: "#FF9200", 60: "#FFA938" } as const;
export const lime = { 37: "#429E00", 50: "#58CF04", 60: "#6BE016" } as const;
export const green = { 40: "#009632", 50: "#00BF40", 60: "#1ED45A" } as const;
export const cyan = { 40: "#0098B2", 50: "#00BDDE", 60: "#28D0ED" } as const;
export const lightBlue = { 40: "#008DCF", 50: "#00AEFF", 60: "#3DC2FF" } as const;
export const violet = { 45: "#5B37ED", 50: "#6541F2", 60: "#7D5EF7" } as const;
export const purple = { 40: "#AD36E3", 50: "#CB59FF", 60: "#D478FF" } as const;
export const pink = { 46: "#E846CD", 50: "#F553DA", 60: "#FA73E3" } as const;

export const white = "#ffffff";
export const black = "#000000";

// ---------------------------------------------------------------------------
// Semantic — 라이트/다크 (wds-theme/src/theme/semantic)
//   Montage 원본은 알파 합성(addHexOpacity)을 쓰지만, 여기서는 montage.py와
//   동일하게 불투명 근사값으로 평탄화했다.
// ---------------------------------------------------------------------------
export const light = {
  primary: blue[50],
  primaryStrong: blue[45],
  bg: white, // background.normal.normal
  bgAlt: coolNeutral[99], // background.normal.alternative
  bgElevated: white,
  label: coolNeutral[10], // label.normal
  labelStrong: black,
  labelNeutral: coolNeutral[25],
  labelAlt: coolNeutral[50], // label.alternative
  labelAssistive: coolNeutral[70],
  line: coolNeutral[96], // line.solid.normal
  lineNeutral: coolNeutral[97],
  lineAlt: coolNeutral[98],
  fill: coolNeutral[98],
  positive: green[50],
  cautionary: orange[50],
  negative: red[50],
} as const;

export const dark = {
  primary: blue[60],
  primaryStrong: blue[55],
  bg: coolNeutral[15],
  bgAlt: coolNeutral[5],
  bgElevated: coolNeutral[17],
  label: coolNeutral[99],
  labelStrong: white,
  labelNeutral: coolNeutral[90],
  labelAlt: coolNeutral[80],
  labelAssistive: coolNeutral[70],
  line: coolNeutral[25],
  lineNeutral: coolNeutral[23],
  lineAlt: coolNeutral[22],
  fill: coolNeutral[22],
  positive: green[60],
  cautionary: orange[60],
  negative: red[60],
} as const;

export type SemanticTokenKey = keyof typeof light;

// ---------------------------------------------------------------------------
// Accent — 카테고리(멤버) 식별용 시리즈 색
//   Montage semantic.accent.foreground 순서 그대로.
//
//   경고: 11색 카테고리는 색각 이상 사용자가 완전히 구분하기 어렵다. 이건
//   Montage의 한계가 아니라 "11개 계열을 색으로만 구분"하려는 설계 자체의
//   한계다. 차트에서 색에만 의존하지 말고 직접 라벨을 함께 붙인다.
// ---------------------------------------------------------------------------
export const accentLight = [
  blue[45], redOrange[48], green[40], orange[39], pink[46], lime[37],
  violet[45], red[40], cyan[40], purple[40], lightBlue[40],
] as const;

export const accentDark = [
  blue[60], redOrange[60], green[60], orange[50], pink[60], lime[50],
  violet[60], red[60], cyan[60], purple[60], lightBlue[60],
] as const;

// ---------------------------------------------------------------------------
// Spacing / Radius / Shadow / Typography
// ---------------------------------------------------------------------------
export const spacing = [0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 32, 40, 48, 56, 64, 72, 80] as const;

export const radius = {
  sm: "4px",
  md: "8px",
  lg: "12px",
  xl: "16px",
  full: "9999px",
} as const;

export const shadow = {
  xsmall: "0px 1px 2px -1px rgba(23,23,23,0.10)",
  small: "0px 2px 4px -2px rgba(23,23,23,0.06), 0px 4px 6px -1px rgba(23,23,23,0.06)",
  medium: "0px 4px 6px -2px rgba(23,23,23,0.07), 0px 10px 15px -3px rgba(23,23,23,0.07)",
  large: "0px 6px 10px -4px rgba(23,23,23,0.08), 0px 16px 24px -6px rgba(23,23,23,0.08)",
} as const;

// Montage는 Pretendard를 표준 서체로 쓴다. 설치돼 있지 않을 수 있으므로
// 한글이 깨지지 않는 시스템 서체로 폴백한다.
export const fontStack =
  'Pretendard, "Pretendard Variable", -apple-system, BlinkMacSystemFont, ' +
  '"Malgun Gothic", "Noto Sans KR", system-ui, sans-serif';

// ---------------------------------------------------------------------------
// CSS 변수 헬퍼 — globals.css가 정의하는 변수명과 1:1 대응.
// 컴포넌트는 하드코딩 hex 대신 이 함수들이 돌려주는 var(--*) 참조를 쓴다.
// ---------------------------------------------------------------------------
const kebab = (key: string) => key.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase();

export function semanticVar(key: SemanticTokenKey): string {
  return `var(--${kebab(key)})`;
}

export function accentVar(index: number): string {
  return `var(--accent-${index % accentLight.length})`;
}

export function radiusVar(key: keyof typeof radius): string {
  return `var(--radius-${key})`;
}

export function shadowVar(key: keyof typeof shadow): string {
  return `var(--shadow-${key})`;
}

export const spacingVar = (index: number): string => `var(--space-${index})`;
