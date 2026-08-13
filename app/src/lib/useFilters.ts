"use client";

/**
 * 전역 필터(FR-1) + 드릴다운 열림 상태(FR-2) 훅.
 *
 * 상태는 URL 쿼리 문자열에 산다 — `useSearchParams`로 읽고 `router.replace`로
 * 쓴다(뒤로가기 스택을 필터 클릭마다 쌓지 않으려고 push 대신 replace).
 * 그래서 필터가 걸린 화면을 URL 그대로 공유할 수 있다.
 *
 * 쿼리 키:
 *   m      선택된 멤버(name_en) — 콤마 구분, 비어 있으면 "전체"
 *   u      선택된 유닛 — 콤마 구분, 비어 있으면 "전체"
 *   p      기간 필터 — 프로젝트가 시간축 데이터를 가진 경우만 사용(문자열, 프로젝트마다 의미 다름)
 *   detail 드릴다운 패널이 열려 있는 멤버(name_en). 없으면 패널 닫힘.
 *
 * ⚠ 이 훅은 `useSearchParams`를 쓰므로 **`<Suspense>` 경계 안의 클라이언트
 * 컴포넌트에서만** 호출해야 한다 — 그렇지 않으면 정적 export 빌드가
 * "Missing Suspense boundary with useSearchParams" 에러로 실패한다. 각
 * 프로젝트 페이지의 `page.tsx`는 이 훅을 쓰는 클라이언트 컴포넌트를
 * `<Suspense>`로 감싸서 렌더해야 한다.
 */
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo } from "react";
import type { Unit } from "@/data/types";

export type FiltersState = {
  members: string[];
  units: Unit[];
  period: string | null;
  detail: string | null;
};

function parseCsv(value: string | null): string[] {
  if (!value) return [];
  return value
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
}

export function useFilters() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const state: FiltersState = useMemo(
    () => ({
      members: parseCsv(searchParams.get("m")),
      units: parseCsv(searchParams.get("u")) as Unit[],
      period: searchParams.get("p"),
      detail: searchParams.get("detail"),
    }),
    [searchParams]
  );

  const applyPatch = useCallback(
    (patch: Partial<Record<"m" | "u" | "p" | "detail", string | null>>) => {
      const next = new URLSearchParams(searchParams.toString());
      for (const [key, value] of Object.entries(patch)) {
        if (value === null || value === "") next.delete(key);
        else next.set(key, value);
      }
      const query = next.toString();
      router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
    },
    [pathname, router, searchParams]
  );

  const toggleMember = useCallback(
    (nameEn: string) => {
      const current = state.members;
      const nextList = current.includes(nameEn) ? current.filter((n) => n !== nameEn) : [...current, nameEn];
      applyPatch({ m: nextList.length ? nextList.join(",") : null });
    },
    [applyPatch, state.members]
  );

  const toggleUnit = useCallback(
    (unit: Unit) => {
      const current = state.units;
      const nextList = current.includes(unit) ? current.filter((u) => u !== unit) : [...current, unit];
      applyPatch({ u: nextList.length ? nextList.join(",") : null });
    },
    [applyPatch, state.units]
  );

  const setPeriod = useCallback(
    (period: string | null) => {
      applyPatch({ p: period });
    },
    [applyPatch]
  );

  const resetFilters = useCallback(() => {
    applyPatch({ m: null, u: null, p: null });
  }, [applyPatch]);

  const openDetail = useCallback(
    (nameEn: string) => {
      applyPatch({ detail: nameEn });
    },
    [applyPatch]
  );

  const closeDetail = useCallback(() => {
    applyPatch({ detail: null });
  }, [applyPatch]);

  /** 멤버 행이 현재 멤버/유닛 필터를 통과하는지. 06처럼 `unit`이 null인 행(경쟁사)도 다룬다. */
  const matchesFilters = useCallback(
    (row: { name_en: string; unit: Unit | null }): boolean => {
      if (state.units.length > 0 && (!row.unit || !state.units.includes(row.unit))) return false;
      if (state.members.length > 0 && !state.members.includes(row.name_en)) return false;
      return true;
    },
    [state.members, state.units]
  );

  const hasActiveFilters = state.members.length > 0 || state.units.length > 0 || state.period !== null;

  return {
    ...state,
    toggleMember,
    toggleUnit,
    setPeriod,
    resetFilters,
    openDetail,
    closeDetail,
    matchesFilters,
    hasActiveFilters,
  };
}
