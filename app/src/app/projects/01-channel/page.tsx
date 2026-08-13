import { Suspense } from "react";
import ChannelPageClient from "./ChannelPageClient";
import styles from "./page.module.css";

/**
 * 프로젝트 01 · 멤버 채널 성과 — M3 레퍼런스 페이지.
 *
 * `page.tsx`는 서버 컴포넌트로 남겨두고, 실제 상태(필터/드릴다운)는
 * `useSearchParams`를 쓰는 클라이언트 컴포넌트(`ChannelPageClient`)에서
 * 처리한다. 정적 export 빌드가 "Missing Suspense boundary with
 * useSearchParams"로 실패하지 않으려면 그 클라이언트 컴포넌트를 반드시
 * `<Suspense>`로 감싸야 한다 — 뒤이어 나머지 6개 프로젝트 페이지를 만들 때도
 * 이 골격(`page.tsx` + `*PageClient.tsx`)을 그대로 복제하면 된다.
 */
export default function Page() {
  return (
    <Suspense fallback={<div className={styles.fallback}>불러오는 중…</div>}>
      <ChannelPageClient />
    </Suspense>
  );
}
