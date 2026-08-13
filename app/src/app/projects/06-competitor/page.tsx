import { Suspense } from "react";
import CompetitorPageClient from "./CompetitorPageClient";
import styles from "./page.module.css";

/** 프로젝트 06 · 경쟁사 비교. 01의 page.tsx + Suspense 골격을 그대로 따른다. */
export default function Page() {
  return (
    <Suspense fallback={<div className={styles.fallback}>불러오는 중…</div>}>
      <CompetitorPageClient />
    </Suspense>
  );
}
