"use client";

import { ROSTER, UNITS, UNIT_LABEL_KO } from "@/data/roster";
import { useFilters } from "@/lib/useFilters";
import FilterChip from "./FilterChip";
import styles from "./FilterBar.module.css";

export type PeriodOption = { value: string; label: string };

type FilterBarProps = {
  /** 이 프로젝트가 기간 필터를 지원할 때만 넘긴다 — 넘기지 않으면 기간 행이 아예 렌더되지 않는다. */
  periodOptions?: PeriodOption[];
};

/**
 * 전역 필터 바(FR-1) — 멤버(11) · 유닛(4) · (선택) 기간.
 * 로스터는 `@/data/roster`가 유일한 정본이라 여기서 멤버 목록을 새로 적지 않는다.
 * 선택 상태는 `useFilters()`를 거쳐 URL 쿼리에 그대로 반영된다.
 */
export default function FilterBar({ periodOptions }: FilterBarProps) {
  const { members, units, period, toggleMember, toggleUnit, setPeriod, resetFilters, hasActiveFilters } =
    useFilters();

  return (
    <div className={styles.bar} role="group" aria-label="전역 필터">
      <div className={styles.row}>
        <span className={styles.rowLabel}>유닛</span>
        <div className={styles.chips}>
          {UNITS.map((unit) => (
            <FilterChip
              key={unit}
              label={UNIT_LABEL_KO[unit]}
              active={units.includes(unit)}
              onClick={() => toggleUnit(unit)}
            />
          ))}
        </div>
      </div>

      <div className={styles.row}>
        <span className={styles.rowLabel}>멤버</span>
        <div className={styles.chips}>
          {ROSTER.map((member) => (
            <FilterChip
              key={member.name_en}
              label={member.name_ko}
              active={members.includes(member.name_en)}
              onClick={() => toggleMember(member.name_en)}
            />
          ))}
        </div>
      </div>

      {periodOptions && periodOptions.length > 0 ? (
        <div className={styles.row}>
          <span className={styles.rowLabel}>기간</span>
          <div className={styles.chips}>
            {periodOptions.map((opt) => (
              <FilterChip
                key={opt.value}
                label={opt.label}
                active={period === opt.value}
                onClick={() => setPeriod(period === opt.value ? null : opt.value)}
              />
            ))}
          </div>
        </div>
      ) : null}

      <button type="button" className={styles.reset} onClick={resetFilters} disabled={!hasActiveFilters}>
        필터 초기화
      </button>
    </div>
  );
}
