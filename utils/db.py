import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "finance.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def run_query(sql: str, params=()) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def load_sql(filename: str) -> str:
    return (Path(__file__).parent.parent / "queries" / filename).read_text()


def run_sql_file(filename: str) -> pd.DataFrame:
    return run_query(load_sql(filename))
