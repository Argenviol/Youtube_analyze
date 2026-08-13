"use client";

import { useEffect, useState } from "react";
import Badge from "./Badge";
import styles from "./Freshness.module.css";

type FreshnessProps = {
  /** 해당 프로젝트 `meta.fetched_at` (ISO8601). */
  fetchedAt: string;
  /** PRD §4 기준 예상 갱신 주기(분). 이 값보다 오래되면 경고 배지. */
  intervalMinutes: number;
  /** "일 1회" 같은 사람이 읽는 주기 표기. */
  cadenceLabel: string;
};

function formatRelativeKo(minutes: number): string {
  if (minutes < 1) return "방금 수집";
  if (minutes < 60) return `${minutes}분 전 수집`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전 수집`;
  const days = Math.floor(hours / 24);
  return `${days}일 전 수집`;
}

/**
 * FR-4 데이터 신선도 배지. `fetched_at`과 "지금"을 비교해 상대 시각을
 * 한국어로 보여주고, 프로젝트별 예상 갱신 주기(`REFRESH_INTERVAL_MIN`)보다
 * 오래됐으면 경고 톤으로 바뀐다.
 *
 * 정적 export라 빌드 시각과 열람 시각이 다르다 — "지금"을 빌드 시점에
 * 계산해 HTML에 굳혀버리면(예: 서버 렌더 중 `Date.now()`) 하이드레이션 시점의
 * 실제 시각과 어긋난다. 그래서 마운트 전에는 자리표시자만 보여주고, 클라이언트에
 * 마운트된 뒤에만 `Date.now()`를 읽는다(ThemeToggle의 FOUC 회피와 같은 이유,
 * 다만 여기선 외부 스토어가 없어 useEffect로 충분하다).
 */
export default function Freshness({ fetchedAt, intervalMinutes, cadenceLabel }: FreshnessProps) {
  const [now, setNow] = useState<number | null>(null);

  useEffect(() => {
    const tick = () => setNow(Date.now());
    // 마운트 직후 첫 값도 setInterval과 동일하게 비동기 콜백으로 넣는다 —
    // effect 본문에서 setState를 동기 호출하면 cascading render 경고가 뜬다.
    const initial = window.setTimeout(tick, 0);
    const interval = window.setInterval(tick, 60_000);
    return () => {
      window.clearTimeout(initial);
      window.clearInterval(interval);
    };
  }, []);

  if (now === null) {
    return (
      <span className={styles.wrap}>
        <Badge tone="neutral">신선도 확인 중…</Badge>
      </span>
    );
  }

  const ageMinutes = Math.max(0, Math.floor((now - new Date(fetchedAt).getTime()) / 60_000));
  const stale = ageMinutes > intervalMinutes;

  return (
    <span className={styles.wrap}>
      <Badge tone={stale ? "negative" : "positive"}>{stale ? "신선도 경고" : "최신"}</Badge>
      <span className={styles.text}>
        {formatRelativeKo(ageMinutes)} · 갱신 주기 {cadenceLabel}
      </span>
    </span>
  );
}
