import styles from "./FilterChip.module.css";

type FilterChipProps = {
  label: string;
  active?: boolean;
  onClick?: () => void;
  disabled?: boolean;
};

/** 멤버/유닛/기간 등 전역 필터에 쓰는 토글형 칩. */
export default function FilterChip({ label, active = false, onClick, disabled = false }: FilterChipProps) {
  return (
    <button
      type="button"
      className={styles.chip}
      data-active={active}
      onClick={onClick}
      disabled={disabled}
      aria-pressed={active}
    >
      {label}
    </button>
  );
}
