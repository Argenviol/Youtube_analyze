"use client";

import { defaultValueFormat } from "./chartUtils";
import styles from "./HeatMap.module.css";

export type HeatMapProps = {
  /** 접근성용 차트 제목 — 화면에는 안 보이지만 스크린리더가 읽는다. */
  title: string;
  /** 행 라벨(화면 표시용, 예: 요일 또는 멤버 한글명). */
  rowLabels: string[];
  /** 열 라벨(화면 표시용, 예: 시각 또는 화제명). */
  colLabels: string[];
  /** `values[row][col]`. */
  values: number[][];
  valueFormat?: (v: number) => string;
  /**
   * 행별 조인 키(예: name_en). 넘기지 않으면 `rowLabels`를 그대로 키로 쓴다.
   * 05처럼 표시는 name_ko, 조인/선택 상태는 name_en으로 유지해야 하는 경우에 쓴다.
   */
  rowKeys?: string[];
  onSelectRow?: (key: string) => void;
  selected?: string | null;
  cellWidth?: number;
  cellHeight?: number;
  rowLabelWidth?: number;
  colLabelHeight?: number;
  /** 열 라벨이 길 때(화제명 등) 겹치지 않도록 기울여 그린다. */
  rotateColLabels?: boolean;
};

const PAD = 4;

function safeMax2d(values: number[][]): number {
  let max = 0;
  for (const row of values) {
    for (const v of row) {
      if (v > max) max = v;
    }
  }
  return max > 0 ? max : 1;
}

/**
 * 행×열 히트맵. 색 농도(하나의 accent 색조 위에 값 비율만큼 불투명도)로 값
 * 크기를 나타내되, 색에만 의존하지 않도록 칸마다 실제 값을 직접 라벨로
 * 찍는다(11개 시리즈 색 구분 원칙과 별개로, 단일 지표 농도 인코딩 자체는
 * 히트맵의 표준 관례다 — 다만 여기서도 direct label을 병행한다).
 * 03(요일×시간)과 05(멤버×화제)가 이 컴포넌트를 공유한다.
 */
export default function HeatMap({
  title,
  rowLabels,
  colLabels,
  values,
  valueFormat = defaultValueFormat,
  rowKeys,
  onSelectRow,
  selected,
  cellWidth = 28,
  cellHeight = 26,
  rowLabelWidth = 100,
  colLabelHeight = 22,
  rotateColLabels = false,
}: HeatMapProps) {
  const max = safeMax2d(values);
  const width = rowLabelWidth + colLabels.length * cellWidth + PAD * 2;
  const height = PAD + colLabelHeight + rowLabels.length * cellHeight + PAD;

  return (
    <div className={styles.wrap}>
      <svg
        className={styles.svg}
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={title}
        style={{ minWidth: `${Math.min(width, 640)}px` }}
      >
        {colLabels.map((label, ci) => {
          const x = rowLabelWidth + ci * cellWidth + cellWidth / 2;
          const y = PAD + colLabelHeight - 6;
          return rotateColLabels ? (
            <text
              key={`col-${label}-${ci}`}
              x={x - 4}
              y={y}
              className={styles.colLabel}
              textAnchor="start"
              transform={`rotate(-38 ${x - 4} ${y})`}
            >
              {label}
            </text>
          ) : (
            <text key={`col-${label}-${ci}`} x={x} y={y} className={styles.colLabel} textAnchor="middle">
              {label}
            </text>
          );
        })}

        {rowLabels.map((label, ri) => {
          const key = rowKeys?.[ri] ?? label;
          const isSelected = selected === key;
          const interactive = Boolean(onSelectRow);
          const handleActivate = () => onSelectRow?.(key);
          const rowY = PAD + colLabelHeight + ri * cellHeight;

          return (
            <g
              key={`row-${key}-${ri}`}
              className={styles.row}
              data-interactive={interactive}
              data-selected={isSelected}
              onClick={interactive ? handleActivate : undefined}
              tabIndex={interactive ? 0 : undefined}
              role={interactive ? "button" : undefined}
              aria-label={interactive ? `${label} — 상세 보기` : undefined}
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
              <text
                x={rowLabelWidth - 8}
                y={rowY + cellHeight / 2}
                className={styles.rowLabel}
                textAnchor="end"
                dominantBaseline="middle"
              >
                {label}
              </text>
              {(values[ri] ?? []).map((v, ci) => {
                const t = Math.max(0, v) / max;
                const x = rowLabelWidth + ci * cellWidth;
                return (
                  <g key={`cell-${ri}-${ci}`}>
                    <rect
                      className={styles.cell}
                      x={x}
                      y={rowY}
                      width={cellWidth - 2}
                      height={cellHeight - 2}
                      rx={3}
                      style={{ fill: "var(--primary)", fillOpacity: 0.06 + t * 0.82 }}
                    >
                      <title>{`${label} · ${colLabels[ci]}: ${valueFormat(v)}`}</title>
                    </rect>
                    {v !== 0 ? (
                      <text
                        x={x + (cellWidth - 2) / 2}
                        y={rowY + (cellHeight - 2) / 2}
                        className={styles.cellLabel}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        {valueFormat(v)}
                      </text>
                    ) : null}
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
