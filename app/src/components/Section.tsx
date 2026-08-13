import type { ReactNode } from "react";
import styles from "./Section.module.css";

type SectionProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
};

/** 페이지 내 섹션 제목. eyebrow(상위 라벨) + title + 설명 + 우측 액션 슬롯. */
export default function Section({ eyebrow, title, description, action }: SectionProps) {
  return (
    <div className={styles.section}>
      <div className={styles.text}>
        {eyebrow ? <p className={styles.eyebrow}>{eyebrow}</p> : null}
        <h2 className={styles.title}>{title}</h2>
        {description ? <p className={styles.description}>{description}</p> : null}
      </div>
      {action ? <div className={styles.action}>{action}</div> : null}
    </div>
  );
}
