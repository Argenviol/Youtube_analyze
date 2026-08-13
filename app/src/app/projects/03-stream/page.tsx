import { Suspense } from "react";
import StreamPageClient from "./StreamPageClient";
import styles from "./page.module.css";

/** 프로젝트 03 · 치지직 방송 패턴. 01의 page.tsx + Suspense 골격을 그대로 따른다. */
export default function Page() {
  return (
    <Suspense fallback={<div className={styles.fallback}>불러오는 중…</div>}>
      <StreamPageClient />
    </Suspense>
  );
}
