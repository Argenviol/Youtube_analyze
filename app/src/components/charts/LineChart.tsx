"use client";

import { defaultValueFormat, memberColor } from "./chartUtils";
import styles from "./LineChart.module.css";

export type LinePoint = { x: number; y: number };

export type LineSeriesDatum = {
  name_en: string;
  label: string;
  points: LinePoint[];
};

type LineChartProps = {
  series: LineSeriesDatum[];
  title: string;
  xFormat?: (v: number) => string;
  yFormat?: (v: number) => string;
  onSelect?: (nameEn: string) => void;
  selected?: string | null;
};

const W = 640;
const H = 320;
const MARGIN = { top: 16, right: 88, bottom: 32, left: 56 };
const TICKS = 5;

function niceTicks(min: number, max: number, count: number): number[] {
  if (min === max) return [min];
  const step = (max - min) / count;
  return Array.from({ length: count + 1 }, (_, i) => min + step * i);
}

/**
 * 다중 시리즈 시계열 라인차트. 각 선 끝에 직접 라벨을 붙이고, 아래에 클릭
 * 가능한 범례(legend)도 함께 둔다 — 얇은 선을 정확히 클릭하기 어려운 문제를
 * 범례 버튼으로 보완한다. 둘 다 `onSelect(name_en)`을 호출한다(FR-2).
 */
export default function LineChart({ series, title, xFormat = defaultValueFormat, yFormat = defaultValueFormat, onSelect, selected }: LineChartProps) {
  const plotW = W - MARGIN.left - MARGIN.right;
  const plotH = H - MARGIN.top - MARGIN.bottom;

  const allPoints = series.flatMap((s) => s.points);
  const xs = allPoints.map((p) => p.x);
  const ys = allPoints.map((p) => p.y);
  const xLo = xs.length ? Math.min(...xs) : 0;
  const xHi = xs.length ? Math.max(...xs) : 1;
  const yLoRaw = ys.length ? Math.min(...ys, 0) : 0;
  const yHiRaw = ys.length ? Math.max(...ys, 1) : 1;
  const yPad = (yHiRaw - yLoRaw) * 0.08 || 1;
  // 값이 전부 0 이상이면 축을 0 아래로 내리지 않는다.
  // 그러지 않으면 동시시청자 같은 카운트 지표에 "-231명" 같은 눈금이 찍힌다.
  const yLo = yLoRaw < 0 ? yLoRaw - yPad : 0;
  const yHi = yHiRaw + yPad;

  const toX = (v: number) => MARGIN.left + (xHi === xLo ? 0 : ((v - xLo) / (xHi - xLo)) * plotW);
  const toY = (v: number) => MARGIN.top + plotH - ((v - yLo) / (yHi - yLo)) * plotH;

  const xTicks = niceTicks(xLo, xHi, Math.min(TICKS, Math.max(1, allPoints.length - 1)));
  const yTicks = niceTicks(yLo, yHi, TICKS);

  const hasSelection = Boolean(selected);

  return (
    <div className={styles.wrap}>
      <div className={styles.scroll}>
        <svg className={styles.svg} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title} style={{ minWidth: "480px" }}>
          {yTicks.map((t) => (
            <g key={`y-${t}`}>
              <line x1={MARGIN.left} x2={W - MARGIN.right} y1={toY(t)} y2={toY(t)} className={styles.gridline} />
              <text x={MARGIN.left - 8} y={toY(t)} className={styles.tick} textAnchor="end" dominantBaseline="middle">
                {yFormat(t)}
              </text>
            </g>
          ))}
          {xTicks.map((t) => (
            <text key={`x-${t}`} x={toX(t)} y={H - MARGIN.bottom + 18} className={styles.tick} textAnchor="middle">
              {xFormat(t)}
            </text>
          ))}
          <line x1={MARGIN.left} x2={MARGIN.left} y1={MARGIN.top} y2={H - MARGIN.bottom} className={styles.axisLine} />
          <line
            x1={MARGIN.left}
            x2={W - MARGIN.right}
            y1={H - MARGIN.bottom}
            y2={H - MARGIN.bottom}
            className={styles.axisLine}
          />

          {series.map((s) => {
            if (s.points.length === 0) return null;
            const sorted = [...s.points].sort((a, b) => a.x - b.x);
            const path = sorted.map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.x)},${toY(p.y)}`).join(" ");
            const last = sorted[sorted.length - 1];
            const color = memberColor(s.name_en);
            const isSelected = selected === s.name_en;
            const interactive = Boolean(onSelect);
            const handleActivate = () => onSelect?.(s.name_en);

            return (
              <g
                key={s.name_en}
                className={styles.series}
                data-interactive={interactive}
                data-selected={isSelected}
                data-dimmed={hasSelection && !isSelected}
                onClick={interactive ? handleActivate : undefined}
                tabIndex={interactive ? 0 : undefined}
                role={interactive ? "button" : undefined}
                aria-label={interactive ? `${s.label} — 상세 보기` : undefined}
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
                <path d={path} className={styles.line} style={{ stroke: color }} />
                <text x={toX(last.x) + 6} y={toY(last.y)} className={styles.endLabel} style={{ fill: color }} dominantBaseline="middle">
                  {s.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div className={styles.legend}>
        {series.map((s) => (
          <button
            key={s.name_en}
            type="button"
            className={styles.legendItem}
            data-selected={selected === s.name_en}
            onClick={() => onSelect?.(s.name_en)}
          >
            <span className={styles.legendSwatch} style={{ background: memberColor(s.name_en) }} />
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
