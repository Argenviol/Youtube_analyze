"""
pandas DataFrame <-> SQLite / .sql 덤프 헬퍼.
프로젝트마다 동일한 방식으로 SQL 산출물을 만든다.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


_SQLITE_TO_SQLTYPE = {
    "int64": "INTEGER", "Int64": "INTEGER", "float64": "REAL",
    "bool": "INTEGER", "datetime64[ns]": "TEXT", "object": "TEXT",
}


def _col_type(dtype) -> str:
    return _SQLITE_TO_SQLTYPE.get(str(dtype), "TEXT")


def _sql_literal(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "NULL"
    if isinstance(v, (int,)):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    s = str(v).replace("'", "''")
    return f"'{s}'"


def write_sqlite(db_path: str | Path, tables: dict[str, pd.DataFrame]) -> None:
    """{테이블명: df} 를 SQLite 파일로 저장."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        for name, df in tables.items():
            df.to_sql(name, con, index=False)
    finally:
        con.close()


def dump_schema_sql(path: str | Path, tables: dict[str, pd.DataFrame],
                    primary_keys: dict[str, str] | None = None) -> None:
    """CREATE TABLE 문(schema.sql) 생성."""
    primary_keys = primary_keys or {}
    lines = ["-- 자동 생성된 스키마 (StelLive 분석)\n"]
    for name, df in tables.items():
        cols = []
        for c in df.columns:
            t = _col_type(df[c].dtype)
            pk = " PRIMARY KEY" if primary_keys.get(name) == c else ""
            cols.append(f"    {c} {t}{pk}")
        lines.append(f"DROP TABLE IF EXISTS {name};")
        lines.append(f"CREATE TABLE {name} (\n" + ",\n".join(cols) + "\n);\n")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def dump_insert_sql(path: str | Path, table: str, df: pd.DataFrame) -> None:
    """INSERT 문 덤프."""
    cols = list(df.columns)
    lines = [f"-- {table} 데이터 ({len(df)} rows)\n"]
    collist = ", ".join(cols)
    for _, row in df.iterrows():
        vals = ", ".join(_sql_literal(row[c]) for c in cols)
        lines.append(f"INSERT INTO {table} ({collist}) VALUES ({vals});")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_query(db_path: str | Path, sql: str) -> pd.DataFrame:
    con = sqlite3.connect(db_path)
    try:
        return pd.read_sql_query(sql, con)
    finally:
        con.close()
