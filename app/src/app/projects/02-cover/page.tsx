import { Suspense } from "react";
import CoverPageClient from "./CoverPageClient";
import styles from "./page.module.css";

/**
 * 프로젝트 02 · 커버곡 성과 랭킹.
 *
 * 01의 골격(`page.tsx`가 서버 컴포넌트로 `<Suspense>` 경계를 두고, 실제
 * 상태는 `useSearchParams`를 쓰는 클라이언트 컴포넌트에서 처리)을 그대로
 * 따른다 — 정적 export 빌드가 "Missing Suspense boundary" 에러 없이
 * 통과하려면 이 구조가 필수다.
 */
export default function Page() {
  return (
    <Suspense fallback={<div className={styles.fallback}>불러오는 중…</div>}>
      <CoverPageClient />
    </Suspense>
  );
}
