/**
 * "지표 A 상위 k명과 지표 B 상위 k명이 겹치는가" 문장 — 멤버 이름을 붙인 1위 대신 쓴다.
 * 공개 저장소라 "○○ 1위" 문구는 멤버끼리의 비교로 퍼진다(2026-10-18 결정).
 * 파이썬 리포트의 `common/summary.py` `overlap_line`과 같은 문장을 만든다.
 */
export function overlapLine<T extends { name_en: string }>(
  rows: T[],
  a: (r: T) => number,
  b: (r: T) => number,
  labelA: string,
  labelB: string,
  k = 3,
): string {
  const n0 = Math.min(k, rows.length);
  if (n0 === 0) return `${labelA}·${labelB}를 함께 비교할 값이 없다`;
  const top = (f: (r: T) => number) =>
    new Set([...rows].sort((x, y) => f(y) - f(x)).slice(0, n0).map((r) => r.name_en));
  const ta = top(a);
  const n = [...top(b)].filter((x) => ta.has(x)).length;
  if (n === 0) return `${labelA} 상위 ${n0}명과 ${labelB} 상위 ${n0}명은 한 명도 겹치지 않는다`;
  if (n === n0) return `${labelA} 상위 ${n0}명과 ${labelB} 상위 ${n0}명이 같다`;
  return `${labelA} 상위 ${n0}명과 ${labelB} 상위 ${n0}명 중 겹치는 멤버는 ${n}명이다`;
}
