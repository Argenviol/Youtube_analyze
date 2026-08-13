import { Suspense } from "react";
import KirinukiPageClient from "./KirinukiPageClient";
import styles from "./page.module.css";

/** 프로젝트 04 · 키리누키(팬 클립) 생태계. 01의 page.tsx + Suspense 골격을 그대로 따른다. */
export default function Page() {
  return (
    <Suspense fallback={<div className={styles.fallback}>불러오는 중…</div>}>
      <KirinukiPageClient />
    </Suspense>
  );
}
