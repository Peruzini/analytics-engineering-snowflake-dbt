"""Build dbt marts in a local DuckDB and export deterministic Power BI CSVs.

Requires installed dbt-duckdb, dbt-snowflake and Python 3.11. No Snowflake access.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from decimal import Decimal
import io
from pathlib import Path
import subprocess
import sys
import tempfile

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "powerbi" / "data"
TABLES = {
    "dim_customers": "customer_id",
    "dim_products": "product_id",
    "fct_orders": "order_id",
    "fct_order_items": "order_item_id",
    "mart_daily_sales": "order_date",
    "mart_customer_ltv": "customer_id",
    "mart_channel_performance": "channel",
}
MONEY = {
    "list_price", "unit_price", "discount_amount", "gross_item_amount",
    "net_item_amount", "recognized_revenue", "refunded_amount", "payment_amount",
    "recognized_item_revenue", "gross_order_amount", "net_order_amount_all_statuses",
    "avg_completed_ticket", "lifetime_recognized_revenue", "lifetime_refunded_amount",
    "planned_budget_amount",
}

def as_csv(cursor, column_names):
    contents = io.StringIO(newline="")
    writer = csv.writer(contents, lineterminator="\n")
    writer.writerow(column_names)
    for row in cursor.fetchall():
        output = []
        for name, value in zip(column_names, row):
            if value is None:
                output.append("")
            elif isinstance(value, (date, datetime)):
                output.append(value.date().isoformat() if isinstance(value, datetime) else value.isoformat())
            elif isinstance(value, (Decimal, int, float)) and name in MONEY:
                output.append(f"{Decimal(str(value)):.2f}")
            else:
                output.append(str(value))
        writer.writerow(output)
    return contents.getvalue()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check against committed files; do not overwrite")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="ae-bi-export-") as temp_dir:
        p = Path(temp_dir)
        profile = p / "profile"
        profile.mkdir()
        dbpath = (p / "bi.duckdb").as_posix()
        (profile / "profiles.yml").write_text(
            "ae_snowflake_portfolio:\n"
            "  target: local\n"
            "  outputs:\n"
            "    local:\n"
            "      type: duckdb\n"
            f"      path: '{dbpath}'\n"
            "      schema: ae_local\n"
            "      threads: 2\n", encoding="utf-8")
        for action in (["seed"], ["run"], ["run", "--select", "fct_orders"], ["snapshot"], ["test"]):
            command = ["dbt", *action, "--profiles-dir", str(profile), "--target", "local"]
            print("Executing:", " ".join(command), flush=True)
            subprocess.run(command, cwd=ROOT, check=True)
        connection = duckdb.connect(dbpath, read_only=True)
        bad = []
        try:
            for name, key in TABLES.items():
                cursor = connection.execute(
                    f'SELECT * FROM "ae_local_analytics"."{name}" ORDER BY "{key}"'
                )
                column_names = [c[0] for c in cursor.description]
                actual = as_csv(cursor, column_names)
                target = DATA / f"{name}.csv"
                if args.check:
                    if not target.exists() or target.read_text(encoding="utf-8") != actual:
                        bad.append(name)
                else:
                    DATA.mkdir(parents=True, exist_ok=True)
                    target.write_text(actual, encoding="utf-8", newline="")
                print(name, "rows:", len(actual.splitlines())-1)
        finally:
            connection.close()
    if bad:
        print("POWERBI_EXPORT_DRIFT:", ", ".join(bad), file=sys.stderr)
        return 1
    print("POWERBI_EXPORT_MATCH" if args.check else "POWERBI_EXPORT_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
