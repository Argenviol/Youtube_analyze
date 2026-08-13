"use client";

import { useEffect } from "react";
import { getMemberMetricGroups } from "@/data/aggregate";
import { UNIT_LABEL_KO, rosterMember } from "@/data/roster";
import Badge from "./Badge";
import styles from "./MemberDetail.module.css";

type MemberDetailProps = {
  nameEn: string;
  onClose: () => void;
};

/**
 * 드릴다운 패널(FR-2). 차트 요소나 표 행 클릭으로 연다. `name_en` 하나를
 * 받아 동기화된 전 프로젝트(01~06, 08)에서 그 멤버의 지표를 모아 보여준다 —
 * 실제 조인은 `@/data/aggregate`가 한다. 열림 상태는 호출부가
 * `useFilters().detail`로 URL에 반영한다(이 컴포넌트 자체는 URL을 모른다).
 */
export default function MemberDetail({ nameEn, onClose }: MemberDetailProps) {
  const member = rosterMember(nameEn);
  const groups = getMemberMetricGroups(nameEn);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  return (
    <>
      <div className={styles.backdrop} onClick={onClose} />
      <aside className={styles.panel} role="dialog" aria-modal="true" aria-label={`${member?.name_ko ?? nameEn} 상세`}>
        <div className={styles.header}>
          <div>
            <p className={styles.nameKo}>{member?.name_ko ?? nameEn}</p>
            <span className={styles.nameEn}>{nameEn}</span>
            {member ? (
              <div className={styles.badgeRow}>
                <Badge tone="neutral">{UNIT_LABEL_KO[member.unit]}</Badge>
              </div>
            ) : null}
          </div>
          <button type="button" className={styles.closeButton} onClick={onClose} aria-label="닫기">
            ✕
          </button>
        </div>

        <div className={styles.body}>
          {groups.length === 0 ? (
            <p className={styles.empty}>동기화된 프로젝트에서 이 멤버의 데이터를 찾지 못했습니다.</p>
          ) : (
            groups.map((group) => (
              <section key={group.projectId} className={styles.group}>
                <div className={styles.groupHeader}>
                  <span className={styles.groupTitle}>
                    {group.projectId} · {group.title}
                  </span>
                  <a className={styles.groupLink} href={group.href}>
                    프로젝트 열기 →
                  </a>
                </div>
                {group.pending ? <p className={styles.pending}>{group.pending}</p> : null}
                <dl className={styles.metricList}>
                  {group.metrics.map((m) => (
                    <div key={m.label} className={styles.metricRow}>
                      <dt className={styles.metricLabel}>{m.label}</dt>
                      <dd className={styles.metricValue}>{m.value}</dd>
                    </div>
                  ))}
                </dl>
              </section>
            ))
          )}
        </div>
      </aside>
    </>
  );
}
