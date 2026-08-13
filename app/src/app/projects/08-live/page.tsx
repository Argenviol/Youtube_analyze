import { Suspense } from "react";
import LivePageClient from "./LivePageClient";
import styles from "./page.module.css";

/** 프로젝트 08 · 동시시청자(FR-5 커버리지 가드). 01의 page.tsx + Suspense 골격을 그대로 따른다. */
export default function Page() {
  return (
    <Suspense fallback={<div className={styles.fallback}>불러오는 중…</div>}>
      <LivePageClient />
    </Suspense>
  );
}
