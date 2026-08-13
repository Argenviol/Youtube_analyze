"use client";

import { useSyncExternalStore } from "react";
import styles from "./ThemeToggle.module.css";

type ThemeChoice = "system" | "light" | "dark";

const STORAGE_KEY = "montage-theme";
const CHANGE_EVENT = "montage-theme-change";

function applyTheme(choice: ThemeChoice) {
  const root = document.documentElement;
  if (choice === "system") {
    root.removeAttribute("data-theme");
  } else {
    root.setAttribute("data-theme", choice);
  }
}

function getSnapshot(): ThemeChoice {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "light" || stored === "dark" ? stored : "system";
}

function getServerSnapshot(): ThemeChoice {
  return "system";
}

function subscribe(callback: () => void) {
  window.addEventListener("storage", callback);
  window.addEventListener(CHANGE_EVENT, callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(CHANGE_EVENT, callback);
  };
}

/**
 * 라이트/다크/시스템 테마 토글.
 * `data-theme` 어트리뷰트를 <html>에 설정하고 localStorage에 저장한다.
 * localStorage를 외부 스토어로 취급해 useSyncExternalStore로 구독한다
 * (effect 안에서 setState 하지 않고, 서버 스냅샷은 항상 "system"이라 하이드레이션도 안전하다).
 * 최초 렌더 시 깜빡임을 막는 인라인 스크립트는 app/layout.tsx에 있다.
 */
export default function ThemeToggle() {
  const choice = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const select = (next: ThemeChoice) => {
    window.localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
    window.dispatchEvent(new Event(CHANGE_EVENT));
  };

  const options: { value: ThemeChoice; label: string }[] = [
    { value: "system", label: "시스템" },
    { value: "light", label: "라이트" },
    { value: "dark", label: "다크" },
  ];

  return (
    <div className={styles.group} role="radiogroup" aria-label="테마 선택">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          role="radio"
          aria-checked={choice === opt.value}
          className={styles.option}
          data-active={choice === opt.value}
          onClick={() => select(opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export const THEME_STORAGE_KEY = STORAGE_KEY;
