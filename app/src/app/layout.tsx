import type { Metadata } from "next";
import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";
import "./globals.css";
import styles from "./layout.module.css";

export const metadata: Metadata = {
  title: "StelLive 팬덤 애널리틱스 대시보드",
  description: "스텔라이브 팬덤 데이터 분석 허브 — 채널·커버곡·방송·여론·경쟁사·동시시청자",
};

// data-theme 결정을 첫 페인트 전에 끝내 깜빡임(FOUC)을 막는다.
// localStorage에 저장된 선택이 없으면 시스템 설정(prefers-color-scheme)을 따른다.
const THEME_INIT_SCRIPT = `
(function () {
  try {
    var stored = window.localStorage.getItem("montage-theme");
    if (stored === "light" || stored === "dark") {
      document.documentElement.setAttribute("data-theme", stored);
    }
  } catch (e) {}
})();
`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ko">
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body>
        <div className={styles.shell}>
          <nav className={styles.nav}>
            <Link href="/" className={styles.brand}>
              StelLive Analytics
            </Link>
            <div className={styles.navLinks}>
              <Link href="/methodology" className={styles.navLink}>
                방법론
              </Link>
              <ThemeToggle />
            </div>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}
