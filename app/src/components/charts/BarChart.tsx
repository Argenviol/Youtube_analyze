"use client";

import { defaultValueFormat, memberColor, safeMax } from "./chartUtils";
import styles from "./BarChart.module.css";

export type BarDatum = {
  name_en: string;
  label: string;
  value: number;
};

type BarChartProps = {
  data: BarDatum[];
  /** 접근성용 차트 제목 — 화면에는 안 보이지만 스크린리더가 읽는다. */
  title: string;
  valueFormat?: (v: number) => string;
  onSelect?: (nameEn: string) => void;
  selected?: string | null;
};

const LABEL_W = 108;
const VALUE_W = 76;
const ROW_H = 28;
const ROW_GAP = 8;
const PAD = 8;
const CHART_W = 560;

/**
 * 수평 막대 차트. 막대 끝에 값 라벨을 직접 붙인다 — 11개 시리즈를 색으로만
 * 구분하지 않는다는 원칙(tokens.ts) 때문에, 색 대신 텍스트 라벨이 1차 식별
 * 수단이다. 막대/라벨 클릭 시 `onSelect(name_en)`을 호출한다(FR-2 드릴다운 훅).
 */
export default function BarChart({ data, title, valueFormat = defaultValueFormat, onSelect, selected }: BarChartProps) {
  const barAreaW = CHART_W - LABEL_W - VALUE_W - PAD * 2;
  const max = safeMax(data.map((d) => d.value));
  const height = PAD * 2 + data.length * ROW_H + Math.max(0, data.length - 1) * ROW_GAP;

  return (
    <div className={styles.wrap}>
      <svg
        className={styles.svg}
        viewBox={`0 0 ${CHART_W} ${height}`}
        role="img"
        aria-label={title}
        style={{ minWidth: `${CHART_W * 0.6}px` }}
      >
        {data.map((d, i) => {
          const y = PAD + i * (ROW_H + ROW_GAP);
          const barW = max > 0 ? (d.value / max) * barAreaW : 0;
          const isSelected = selected === d.name_en;
          const interactive = Boolean(onSelect);

          const handleActivate = () => onSelect?.(d.name_en);

          return (
            <g
              key={d.name_en}
              className={styles.row}
              data-interactive={interactive}
              data-selected={isSelected}
              onClick={interactive ? handleActivate : undefined}
              tabIndex={interactive ? 0 : undefined}
              role={interactive ? "button" : undefined}
              aria-label={interactive ? `${d.label} ${valueFormat(d.value)} — 상세 보기` : undefined}
              onKeyDown={
                interactive
                  ? (e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handleActivate();
                      }
                    }
                  : undefined
              }
            >
              <text x={LABEL_W - 8} y={y + ROW_H / 2} className={styles.nameLabel} textAnchor="end" dominantBaseline="middle">
                {d.label}
              </text>
              <rect
                className={styles.bar}
                x={LABEL_W}
                y={y}
                width={Math.max(barW, 1)}
                height={ROW_H}
                rx={4}
                style={{ fill: memberColor(d.name_en) }}
              />
              <text
                x={LABEL_W + barW + 8}
                y={y + ROW_H / 2}
                className={styles.valueLabel}
                textAnchor="start"
                dominantBaseline="middle"
              >
                {valueFormat(d.value)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
