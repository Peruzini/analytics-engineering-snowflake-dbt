"""Compare or export canonical dbt/DuckDB marts to versioned Power BI CSVs.

Examples:
  python scripts/export_powerbi.py --check
  python scripts/export_powerbi.py --check --duckdb-path /tmp/portfolio.duckdb

Default uses a disposable local dbt DuckDB. --duckdb-path reads an existing
database (no second dbt run); restricted to --check for safe one-pass QA.
No Snowflake connection or hosted Actions.
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

def first_difference(expected, actual):
    old = expected.splitlines()
    new = actual.splitlines()
    for lineno in range(max(len(old), len(new))):
        left = old[lineno] if lineno < len(old) else "<missing>"
        right = new[lineno] if lineno < len(new) else "<missing>"
        if left != right:
            return f"line {lineno + 1}: committed={left[:120]!r}, dbt={right[:120]!r}"
    return "unknown byte difference"

def verify_or_export(dbpath: Path, check: bool):
    mismatches = []
    connection = duckdb.connect(dbpath.as_posix(), read_only=True)
    try:
        for table, key in TABLES.items():
            cursor = connection.execute(
                f'SELECT * FROM "ae_local_analytics"."{table}" ORDER BY "{key}"'
            )
            columns = [x[0] for x in cursor.description]
            actual = as_csv(cursor, columns)
            target = DATA / f"{table}.csv"
            if check:
                expected = target.read_text(encoding="utf-8") if target.is_file() else ""
                if expected != actual:
                    mismatches.append(table)
                    print(f"DRIFT {table}: {first_difference(expected, actual)}", file=sys.stderr)
            else:
                DATA.mkdir(parents=True, exist_ok=True)
                target.write_text(actual, encoding="utf-8", newline="")
            print(f"{table}: {len(actual.splitlines())-1} rows", flush=True)
    finally:
        connection.close()
    if mismatches:
        print("POWERBI_EXPORT_DRIFT: " + ", ".join(mismatches), file=sys.stderr)
        return 1
    print("POWERBI_EXPORT_MATCH" if check else "POWERBI_EXPORT_WRITTEN")
    return 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Fail on any byte difference from committed CSVs")
    parser.add_argument("--duckdb-path", type=Path,
                        help="Reuse an existing local dbt DuckDB without running dbt again")
    args = parser.parse_args()
    if args.duckdb_path:
        if not args.check:
            parser.error("--duckdb-path requires --check (read-only)")
        if not args.duckdb_path.is_file():
            parser.error(f"DuckDB database not found: {args.duckdb_path}")
        return verify_or_export(args.duckdb_path, check=True)
    with tempfile.TemporaryDirectory(prefix="ae-bi-export-") as tempdir:
        temp = Path(tempdir)
        profile = temp / "profile"
        profile.mkdir()
        dbpath = temp / "bi.duckdb"
        (profile / "profiles.yml").write_text(
            "ae_snowflake_portfolio:\n"
            "  target: local\n"
            "  outputs:\n"
            "    local:\n"
            "      type: duckdb\n"
            f"      path: '{dbpath.as_posix()}'\n"
            "      schema: ae_local\n"
            "      threads: 2\n", encoding="utf-8")
        for action in (["seed"], ["run"], ["run", "--select", "fct_orders"], ["snapshot"], ["test"]):
            command = ["dbt", *action, "--profiles-dir", str(profile), "--target", "local"]
            print("Executing:", " ".join(command), flush=True)
            subprocess.run(command, cwd=ROOT, check=True)
        return verify_or_export(dbpath, args.check)

if __name__ == "__main__":
    raise SystemExit(main())
