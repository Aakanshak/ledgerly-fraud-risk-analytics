"""Load generated Ledgerly CSVs into a portable SQLite database."""
from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent

def load(data_dir: Path = HERE / "generated", db_path: Path = HERE / "ledgerly.db") -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executescript((HERE / "schema.sql").read_text(encoding="utf-8"))
        conn.execute("DELETE FROM chargebacks")
        conn.execute("DELETE FROM user_velocity_features")
        conn.execute("DELETE FROM transactions")
        for table in ("transactions", "user_velocity_features", "chargebacks"):
            pd.read_csv(data_dir / f"{table}.csv").to_sql(table, conn, if_exists="append", index=False, chunksize=10_000)
        conn.execute("ANALYZE")
        counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("transactions", "user_velocity_features", "chargebacks")}
    print(counts)
    print("So what? Analysts can reproduce every aggregate against a portable database with no cloud dependency.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=HERE / "generated")
    parser.add_argument("--db-path", type=Path, default=HERE / "ledgerly.db")
    a = parser.parse_args()
    load(a.data_dir, a.db_path)
