"""Generate deterministic, fictional e-commerce CSV datasets using stdlib only."""
from __future__ import annotations

import argparse
import csv
import io
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

PRODUCTS = [
    ("P001", "Notebook Stand", "accessories", "89.90"),
    ("P002", "USB Hub", "accessories", "129.00"),
    ("P003", "Mechanical Keyboard", "peripherals", "249.90"),
    ("P004", "Wireless Mouse", "peripherals", "119.90"),
    ("P005", "Desk Lamp", "office", "159.00"),
    ("P006", "Notebook", "office", "24.90"),
    ("P007", "Water Bottle", "lifestyle", "49.90"),
    ("P008", "Backpack", "lifestyle", "199.00"),
]
HEADERS = {
    "raw_customers.csv": ["customer_id", "email", "region", "created_at"],
    "raw_products.csv": ["product_id", "product_name", "category", "list_price"],
    "raw_campaigns.csv": ["campaign_id", "channel", "budget_amount"],
    "raw_orders.csv": ["order_id", "customer_id", "campaign_id", "order_date", "order_status"],
    "raw_order_items.csv": [
        "order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount"
    ],
    "raw_payments.csv": [
        "payment_id", "order_id", "payment_date", "amount", "payment_status", "payment_method"
    ],
}


def money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01")))


def build_rows() -> dict[str, list[list[str]]]:
    """Return six related, deterministic datasets without any personal data."""
    rows: dict[str, list[list[str]]] = {name: [] for name in HEADERS}

    for i in range(1, 13):
        created_at = date(2026, 8, 1) + timedelta(days=i - 1)
        rows["raw_customers.csv"].append([
            f"C{i:03d}", f"customer{i:02d}@example.test",
            ["SP", "RJ", "MG", "PR"][(i - 1) % 4], created_at.isoformat()
        ])

    rows["raw_products.csv"] = [list(product) for product in PRODUCTS]

    for i, channel in enumerate(["organic", "paid_search", "social", "email"], start=1):
        rows["raw_campaigns.csv"].append([f"M{i:03d}", channel, money(Decimal(1000 + i * 150))])

    for i in range(1, 37):
        order_id = f"O{i:03d}"
        if i % 7 == 0:
            status = "cancelled"
        elif i % 11 == 0:
            status = "refunded"
        elif i % 13 == 0:
            status = "pending"
        else:
            status = "completed"

        ordered_at = date(2026, 9, 1) + timedelta(days=(i - 1) % 28)
        campaign_id = "" if i % 5 == 0 else f"M{((i - 1) % 4) + 1:03d}"
        rows["raw_orders.csv"].append([
            order_id, f"C{((i - 1) % 12) + 1:03d}",
            campaign_id, ordered_at.isoformat(), status
        ])

        order_total = Decimal("0")
        for j in range(2):
            product = PRODUCTS[(i + j - 1) % len(PRODUCTS)]
            quantity = 1 + ((i + j) % 3)
            discount = Decimal("2.00") if (i + j) % 4 == 0 else Decimal("0.00")
            price = Decimal(product[3])
            order_total += price * quantity - discount
            rows["raw_order_items.csv"].append([
                f"I{i:03d}-{j + 1}", order_id, product[0],
                str(quantity), money(price), money(discount)
            ])

        if status in ("completed", "refunded"):
            rows["raw_payments.csv"].append([
                f"PAY{i:03d}", order_id, ordered_at.isoformat(),
                money(order_total), "paid" if status == "completed" else "refunded",
                "pix" if i % 2 == 0 else "card"
            ])
    return rows


def render_csvs() -> dict[str, str]:
    result = {}
    for filename, records in build_rows().items():
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(HEADERS[filename])
        writer.writerows(records)
        result[filename] = output.getvalue()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("seeds"))
    parser.add_argument("--check", action="store_true", help="Fail if committed CSVs differ")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    mismatches = []
    for filename, content in render_csvs().items():
        target = args.output_dir / filename
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != content:
                mismatches.append(filename)
        else:
            target.write_text(content, encoding="utf-8", newline="")

    if mismatches:
        print("Synthetic seed drift: " + ", ".join(mismatches))
        return 1
    print("Synthetic seeds match fixtures." if args.check else "Synthetic seeds generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
