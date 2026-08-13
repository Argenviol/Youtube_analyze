import type { ReactNode } from "react";
import styles from "./Badge.module.css";

type BadgeTone = "neutral" | "primary" | "positive" | "cautionary" | "negative";

type BadgeProps = {
  children: ReactNode;
  tone?: BadgeTone;
};

/** 작은 상태 라벨. 신선도/커버리지 경고 등에 쓴다. */
export default function Badge({ children, tone = "neutral" }: BadgeProps) {
  return <span className={`${styles.badge} ${styles[`tone-${tone}`]}`}>{children}</span>;
}
