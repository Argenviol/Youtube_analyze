"use client";

import { defaultValueFormat, memberColor, safeMax } from "./chartUtils";
import styles from "./ScatterPlot.module.css";

export type ScatterDatum = {
  name_en: string;
  label: string;
  x: number;
  y: number;
  /** 버블 크기로 쓸 3번째 값(예: 조회수). 없으면 균일한 크기로 그린다. */
  size?: number;
};

type ScatterPlotProps = {
  data: ScatterDatum[];
  title: string;
  xLabel: string;
  yLabel: string;
  xFormat?: (v: number) => string;
  yFormat?: (v: number) => string;
  onSelect?: (nameEn: string) => void;
  selected?: string | null;
};

const W = 640;
const H = 420;
const MARGIN = { top: 20, right: 24, bottom: 44, left: 64 };
const MIN_R = 7;
const MAX_R = 30;
const TICKS = 5;

function niceTicks(min: number, max: number, count: number): number[] {
  if (min === max) return [min];
  const step = (max - min) / count;
  return Array.from({ length: count + 1 }, (_, i) => min + step * i);
}

/**
 * 산점도 + 버블 크기. 11개 점 전부에 직접 라벨을 붙인다(색만으로 구분하지
 * 않는다는 원칙). 점 클릭 시 `onSelect(name_en)`을 호출한다(FR-2).
 */
export default function ScatterPlot({
  data,
  title,
  xLabel,
  yLabel,
  xFormat = defaultValueFormat,
  yFormat = defaultValueFormat,
  onSelect,
  selected,
}: ScatterPlotProps) {
  const plotW = W - MARGIN.left - MARGIN.right;
  const plotH = H - MARGIN.top - MARGIN.bottom;

  const xs = data.map((d) => d.x);
  const ys = data.map((d) => d.y);
  const xMin = Math.min(...xs, 0);
  const xMax = Math.max(...xs, 1);
  const yMin = Math.min(...ys, 0);
  const yMax = Math.max(...ys, 1);
  const xPad = (xMax - xMin) * 0.08 || 1;
  const yPad = (yMax - yMin) * 0.08 || 1;
  // 값이 전부 0 이상이면 축을 0 아래로 내리지 않는다 (음수 카운트 눈금 방지).
  const xLo = xMin < 0 ? xMin - xPad : 0;
  const xHi = xMax + xPad;
  const yLo = yMin < 0 ? yMin - yPad : 0;
  const yHi = yMax + yPad;

  const sizeMax = safeMax(data.map((d) => d.size ?? 1));

  const toX = (v: number) => MARGIN.left + ((v - xLo) / (xHi - xLo)) * plotW;
  const toY = (v: number) => MARGIN.top + plotH - ((v - yLo) / (yHi - yLo)) * plotH;
  const toR = (size: number | undefined) => {
    if (size === undefined) return MIN_R;
    const t = Math.sqrt(Math.max(size, 0) / sizeMax);
    return MIN_R + t * (MAX_R - MIN_R);
  };

  const xTicks = niceTicks(xLo, xHi, TICKS);
  const yTicks = niceTicks(yLo, yHi, TICKS);

  return (
    <div className={styles.wrap}>
      <svg className={styles.svg} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title} style={{ minWidth: "480px" }}>
        {/* 그리드 + 축 */}
        {yTicks.map((t) => (
          <g key={`y-${t}`}>
            <line x1={MARGIN.left} x2={W - MARGIN.right} y1={toY(t)} y2={toY(t)} className={styles.gridline} />
            <text x={MARGIN.left - 8} y={toY(t)} className={styles.tick} textAnchor="end" dominantBaseline="middle">
              {yFormat(t)}
            </text>
          </g>
        ))}
        {xTicks.map((t) => (
          <g key={`x-${t}`}>
            <text x={toX(t)} y={H - MARGIN.bottom + 18} className={styles.tick} textAnchor="middle">
              {xFormat(t)}
            </text>
          </g>
        ))}
        <line
          x1={MARGIN.left}
          x2={MARGIN.left}
          y1={MARGIN.top}
          y2={H - MARGIN.bottom}
          className={styles.axisLine}
        />
        <line
          x1={MARGIN.left}
          x2={W - MARGIN.right}
          y1={H - MARGIN.bottom}
          y2={H - MARGIN.bottom}
          className={styles.axisLine}
        />

        <text x={(MARGIN.left + W - MARGIN.right) / 2} y={H - 6} className={styles.axisTitle} textAnchor="middle">
          {xLabel}
        </text>
        <text
          x={-((MARGIN.top + H - MARGIN.bottom) / 2)}
          y={14}
          className={styles.axisTitle}
          textAnchor="middle"
          transform="rotate(-90)"
        >
          {yLabel}
        </text>

        {/* 점 */}
        {data.map((d) => {
          const cx = toX(d.x);
          const cy = toY(d.y);
          const r = toR(d.size);
          const isSelected = selected === d.name_en;
          const interactive = Boolean(onSelect);
          const handleActivate = () => onSelect?.(d.name_en);

          return (
            <g
              key={d.name_en}
              className={styles.point}
              data-interactive={interactive}
              data-selected={isSelected}
              onClick={interactive ? handleActivate : undefined}
              tabIndex={interactive ? 0 : undefined}
              role={interactive ? "button" : undefined}
              aria-label={
                interactive
                  ? `${d.label} — ${xLabel} ${xFormat(d.x)}, ${yLabel} ${yFormat(d.y)} — 상세 보기`
                  : undefined
              }
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
              <circle cx={cx} cy={cy} r={r} className={styles.bubble} style={{ fill: memberColor(d.name_en) }} />
              <text x={cx} y={cy - r - 4} className={styles.pointLabel} textAnchor="middle">
                {d.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
