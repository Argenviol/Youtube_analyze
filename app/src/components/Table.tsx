"use client";

import { useMemo, useState, type ReactNode } from "react";
import styles from "./Table.module.css";

export type TableColumn<T> = {
  key: string;
  header: string;
  accessor: (row: T) => string | number;
  align?: "left" | "right";
  render?: (row: T) => ReactNode;
};

type SortDirection = "asc" | "desc";

type TableProps<T> = {
  columns: TableColumn<T>[];
  rows: T[];
  getRowKey: (row: T) => string;
  initialSortKey?: string;
  initialSortDir?: SortDirection;
  caption?: string;
  /** 행 클릭 핸들러 — 드릴다운(FR-2) 등에 쓴다. 넘기면 행이 클릭 가능한 버튼처럼 동작한다. */
  onRowClick?: (row: T) => void;
};

/**
 * 열 클릭으로 정렬 가능한 표. 현재 정렬 기준과 방향을 헤더에 화살표와
 * aria-sort로 시각/접근성 양쪽에 드러낸다 (FR-3).
 * 넓은 표는 자체 컨테이너에서 overflow-x: auto 로 스크롤하고, 페이지 본문은
 * 가로로 스크롤되지 않는다.
 */
export default function Table<T>({
  columns,
  rows,
  getRowKey,
  initialSortKey,
  initialSortDir = "desc",
  caption,
  onRowClick,
}: TableProps<T>) {
  const [sortKey, setSortKey] = useState<string | undefined>(initialSortKey ?? columns[0]?.key);
  const [sortDir, setSortDir] = useState<SortDirection>(initialSortDir);

  const sortedRows = useMemo(() => {
    const col = columns.find((c) => c.key === sortKey);
    if (!col) return rows;
    const withValues = rows.map((row) => ({ row, value: col.accessor(row) }));
    withValues.sort((a, b) => {
      if (typeof a.value === "number" && typeof b.value === "number") {
        return a.value - b.value;
      }
      return String(a.value).localeCompare(String(b.value), "ko");
    });
    if (sortDir === "desc") withValues.reverse();
    return withValues.map((w) => w.row);
  }, [rows, columns, sortKey, sortDir]);

  const handleSort = (key: string) => {
    if (key === sortKey) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  return (
    <div className={styles.scrollArea}>
      <table className={styles.table}>
        {caption ? <caption className={styles.caption}>{caption}</caption> : null}
        <thead>
          <tr>
            {columns.map((col) => {
              const isActive = col.key === sortKey;
              const ariaSort = isActive ? (sortDir === "asc" ? "ascending" : "descending") : "none";
              return (
                <th
                  key={col.key}
                  scope="col"
                  aria-sort={ariaSort}
                  className={col.align === "right" ? styles.alignRight : undefined}
                >
                  <button
                    type="button"
                    className={styles.sortButton}
                    data-active={isActive}
                    onClick={() => handleSort(col.key)}
                  >
                    <span>{col.header}</span>
                    <span className={styles.sortIcon} aria-hidden="true">
                      {isActive ? (sortDir === "asc" ? "▲" : "▼") : "↕"}
                    </span>
                  </button>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row) => (
            <tr
              key={getRowKey(row)}
              className={onRowClick ? styles.clickableRow : undefined}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              tabIndex={onRowClick ? 0 : undefined}
              role={onRowClick ? "button" : undefined}
              onKeyDown={
                onRowClick
                  ? (e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        onRowClick(row);
                      }
                    }
                  : undefined
              }
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={`${col.align === "right" ? styles.alignRight : ""} ${
                    typeof col.accessor(row) === "number" ? "tabular-nums" : ""
                  }`}
                >
                  {col.render ? col.render(row) : col.accessor(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
