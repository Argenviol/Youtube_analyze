/** 차트 3종이 공유하는 자잘한 헬퍼. */
import { accentVar } from "@/design/tokens";
import { accentIndexFor } from "@/data/roster";

/** 멤버(name_en) 하나에 항상 같은 accent 색을 준다 — 어느 차트에서도 동일. */
export function memberColor(nameEn: string): string {
  return accentVar(accentIndexFor(nameEn));
}

export function defaultValueFormat(v: number): string {
  if (Number.isInteger(v)) return v.toLocaleString("ko-KR");
  return v.toLocaleString("ko-KR", { maximumFractionDigits: 1 });
}

/** 0 나눗셈 방지용 안전한 최댓값. */
export function safeMax(values: number[], fallback = 1): number {
  const max = Math.max(...values, 0);
  return max > 0 ? max : fallback;
}
