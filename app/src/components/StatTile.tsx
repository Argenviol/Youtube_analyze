import type { ReactNode } from "react";
import styles from "./StatTile.module.css";

type StatTileProps = {
  label: string;
  value: ReactNode;
  unit?: string;
  delta?: string;
  deltaTone?: "positive" | "negative" | "neutral";
  caption?: string;
};

/**
 * 라벨 + 큰 수치(tabular-nums) 스탯 타일.
 * 허브의 인사이트 요약, 프로젝트 카드의 대표 지표에 쓴다.
 */
export default function StatTile({ label, value, unit, delta, deltaTone = "neutral", caption }: StatTileProps) {
  return (
    <div className={styles.tile}>
      <span className={styles.label}>{label}</span>
      <div className={styles.valueRow}>
        <span className={`${styles.value} tabular-nums`}>{value}</span>
        {unit ? <span className={styles.unit}>{unit}</span> : null}
      </div>
      {delta ? (
        <span className={`${styles.delta} ${styles[`tone-${deltaTone}`]} tabular-nums`}>{delta}</span>
      ) : null}
      {caption ? <span className={styles.caption}>{caption}</span> : null}
    </div>
  );
}
