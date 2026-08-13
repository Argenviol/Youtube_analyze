/**
 * 멤버 로스터 정본(canonical roster) — 단일 모듈.
 *
 * 값의 원본(source of truth)은 `youtube_analyze_all/common/config.py`의
 * `MEMBERS`다. Python 쪽을 Next.js가 직접 import할 수 없어서(정적 export,
 * 언어 경계) 여기 TypeScript로 그대로 미러링한다 — `tokens.ts`가
 * `montage.py`를 미러링하는 것과 같은 패턴이다.
 *
 * 페이지마다 멤버/유닛 목록을 따로 하드코딩하지 말 것. 필터 UI, 드릴다운,
 * accent 색 배정은 전부 이 모듈을 거친다.
 */
import type { Role, Unit } from "./types";

export type RosterMember = {
  name_ko: string;
  name_en: string;
  unit: Unit;
  role: Role;
};

/** `common/config.py`의 `MEMBERS` 순서 그대로 — accent 색 인덱스가 이 순서에 대응한다. */
export const ROSTER: readonly RosterMember[] = [
  { name_ko: "강지", name_en: "Kangji", unit: "STELLIVE", role: "founder" },
  { name_ko: "아야츠노 유니", name_en: "Ayatsuno Yuni", unit: "EVERYS", role: "talent" },
  { name_ko: "사키하네 후야", name_en: "Sakihane Huya", unit: "EVERYS", role: "talent" },
  { name_ko: "시라유키 히나", name_en: "Shirayuki Hina", unit: "UNIVERSE", role: "talent" },
  { name_ko: "네네코 마시로", name_en: "Neneko Mashiro", unit: "UNIVERSE", role: "talent" },
  { name_ko: "아카네 리제", name_en: "Akane Lize", unit: "UNIVERSE", role: "talent" },
  { name_ko: "아라하시 타비", name_en: "Arahashi Tabi", unit: "UNIVERSE", role: "talent" },
  { name_ko: "텐코 시부키", name_en: "Tenko Shibuki", unit: "CLICHE", role: "talent" },
  { name_ko: "아오쿠모 린", name_en: "Aokumo Rin", unit: "CLICHE", role: "talent" },
  { name_ko: "하나코 나나", name_en: "Hanako Nana", unit: "CLICHE", role: "talent" },
  { name_ko: "유즈하 리코", name_en: "Yuzuha Riko", unit: "CLICHE", role: "talent" },
] as const;

export const UNITS: readonly Unit[] = ["STELLIVE", "EVERYS", "UNIVERSE", "CLICHE"] as const;

export const UNIT_LABEL_KO: Record<Unit, string> = {
  STELLIVE: "창립자",
  EVERYS: "EVERYS",
  UNIVERSE: "UNIVERSE",
  CLICHE: "CLICHE",
};

const NAME_EN_TO_INDEX = new Map(ROSTER.map((m, i) => [m.name_en, i]));
const NAME_KO_TO_EN = new Map(ROSTER.map((m) => [m.name_ko, m.name_en]));
const NAME_EN_TO_MEMBER = new Map(ROSTER.map((m) => [m.name_en, m]));

/** 로스터 상 인덱스. 못 찾으면 -1(경쟁사 등 로스터 밖 인물). */
export function rosterIndex(nameEn: string): number {
  return NAME_EN_TO_INDEX.get(nameEn) ?? -1;
}

/** `name_ko → name_en` 조인. 05의 heatmap 정규화 등에 쓴다. */
export function nameKoToEn(nameKo: string): string | undefined {
  return NAME_KO_TO_EN.get(nameKo);
}

export function rosterMember(nameEn: string): RosterMember | undefined {
  return NAME_EN_TO_MEMBER.get(nameEn);
}

/**
 * 차트 accent 색 인덱스. 로스터에 없는 인물(06의 경쟁사 12명 등)은 안정적인
 * 문자열 해시로 0~10 범위에 배정해 그래도 매번 같은 색을 받게 한다(단, 어느
 * 로스터 멤버와도 겹칠 수 있음 — 로스터 밖 인물이라 허용 가능한 손실).
 */
export function accentIndexFor(nameEn: string): number {
  const idx = rosterIndex(nameEn);
  if (idx >= 0) return idx;
  let hash = 0;
  for (let i = 0; i < nameEn.length; i += 1) {
    hash = (hash * 31 + nameEn.charCodeAt(i)) % 997;
  }
  return hash % 11;
}
