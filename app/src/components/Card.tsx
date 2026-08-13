import type { ReactNode } from "react";
import styles from "./Card.module.css";

type CardProps = {
  children: ReactNode;
  href?: string;
  className?: string;
  padding?: "sm" | "md" | "lg";
  /** 외부 링크 카드(07 시장 분석의 정적 HTML 등)용 — 새 탭에서 연다. */
  external?: boolean;
};

/**
 * 기본 카드 컨테이너. Montage 토큰의 elevated 배경 + line + shadow를 쓴다.
 * href가 있으면 클릭 가능한 카드(프로젝트 카드 그리드 등)로 렌더한다.
 * `external`이 true면 새 탭으로 열고 `rel="noopener noreferrer"`를 붙인다
 * (07처럼 Next.js 앱 라우트 밖의 정적 HTML로 나가는 카드).
 */
export default function Card({ children, href, className, padding = "md", external }: CardProps) {
  const classes = [styles.card, styles[`padding-${padding}`], className].filter(Boolean).join(" ");

  if (href) {
    return (
      <a
        href={href}
        className={`${classes} ${styles.clickable}`}
        target={external ? "_blank" : undefined}
        rel={external ? "noopener noreferrer" : undefined}
      >
        {children}
      </a>
    );
  }

  return <div className={classes}>{children}</div>;
}
