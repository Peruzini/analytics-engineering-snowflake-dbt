"""Deterministic 12-month synthetic e-commerce portfolio dataset (stdlib only).

All monetary arithmetic uses integer cents; no randomness, user data or cloud access.
The six source schemas and business keys are backward compatible with MVPs 01–03.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((Path(__file__).with_name("market_config.json")).read_text(encoding="utf-8"))
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

def money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"

def daily_weights() -> list[tuple[date, int]]:
    start = date.fromisoformat(CONFIG["start_date"])
    dates = [start + timedelta(days=d) for d in range(CONFIG["days"])]
    values = []
    for day in dates:
        extra = CONFIG["month_weight_adjustments"][str(day.month)]
        weekend = 16 if day.weekday() >= 5 else -6 if day.weekday() == 0 else 0
        campaign_event = 38 if day.month == 11 and day.day >= 24 else 0
        values.append((day, 100 + extra + weekend + campaign_event))
    return values

def orders_per_day() -> list[tuple[date, int]]:
    weights = daily_weights()
    total = sum(w for _, w in weights)
    quotas = [(CONFIG["orders"] * w) // total for _, w in weights]
    residues = [(CONFIG["orders"] * w) % total for _, w in weights]
    remaining = CONFIG["orders"] - sum(quotas)
    for idx in sorted(range(len(weights)), key=lambda i: (-residues[i], i))[:remaining]:
        quotas[idx] += 1
    return [(weights[i][0], quotas[i]) for i in range(len(weights))]

def build_rows() -> dict[str, list[list[str]]]:
    rows: dict[str, list[list[str]]] = {name: [] for name in HEADERS}
    products = CONFIG["product_catalog"]

    for i in range(1, CONFIG["customers"] + 1):
        created_at = date(2025, 2, 1) + timedelta(days=(i * 13) % 200)
        rows["raw_customers.csv"].append([
            f"C{i:04d}", f"customer{i:04d}@example.test",
            ["SP", "RJ", "MG", "PR", "SC", "RS", "BA"][((i - 1) * 3) % 7],
            created_at.isoformat(),
        ])
    for p in products:
        rows["raw_products.csv"].append([
            p["product_id"], p["product_name"], p["category"], money(p["list_price_cents"])
        ])
    for i in range(1, len(CONFIG["channels"]) * CONFIG["campaigns_per_channel"] + 1):
        channel = CONFIG["channels"][(i - 1) % len(CONFIG["channels"])]
        rows["raw_campaigns.csv"].append([
            f"M{i:03d}", channel, money(80000 + i * 12500)
        ])

    i = 0
    start = date.fromisoformat(CONFIG["start_date"])
    for order_date, count in orders_per_day():
        for _ in range(count):
            i += 1
            day_idx = (order_date - start).days
            order_id = f"O{i:06d}"
            customer_idx = ((i * 73 + (i * i % 97) * 19) % CONFIG["customers"]) + 1
            campaign_idx = 0 if i % 9 == 0 else ((i * 17 + day_idx * 3) % (
                len(CONFIG["channels"]) * CONFIG["campaigns_per_channel"])) + 1
            campaign_id = f"M{campaign_idx:03d}" if campaign_idx else ""
            channel = (CONFIG["channels"][(campaign_idx - 1) % 4]
                       if campaign_idx else "unattributed")
            cancel, refunded, pending = CONFIG["channel_status_thresholds"][channel]
            bucket = (i * 37 + customer_idx * 11 + day_idx * 7) % 100
            if bucket < cancel:
                status = "cancelled"
            elif bucket < cancel + refunded:
                status = "refunded"
            elif bucket < cancel + refunded + pending:
                status = "pending"
            else:
                status = "completed"
            rows["raw_orders.csv"].append([
                order_id, f"C{customer_idx:04d}", campaign_id,
                order_date.isoformat(), status
            ])

            order_total = 0
            for j in range(1 + i % 3):
                product = products[(i * 13 + j * 7 + (i % 47) * 3 + day_idx) % len(products)]
                quantity = 1 + ((i + j) % 3)
                price = product["list_price_cents"]
                gross = price * quantity
                percentage = [0, 0, 500, 1000, 1500][(i + j) % 5]
                if order_date.month == 11 and i % 3 == 0:
                    percentage = min(2000, percentage + 500)
                discount = (gross * percentage + 5000) // 10000
                order_total += gross - discount
                rows["raw_order_items.csv"].append([
                    f"I{i:06d}-{j+1}", order_id, product["product_id"],
                    str(quantity), money(price), money(discount)
                ])
            if status in {"completed", "refunded"}:
                rows["raw_payments.csv"].append([
                    f"PAY{i:06d}", order_id, order_date.isoformat(),
                    money(order_total),
                    "paid" if status == "completed" else "refunded",
                    "pix" if i % 3 == 0 else "card"
                ])
    assert i == CONFIG["orders"]
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
    parser.add_argument("--output-dir", type=Path, default=ROOT / "seeds")
    parser.add_argument("--check", action="store_true", help="Fail if committed CSVs differ")
    args = parser.parse_args()
    if not args.check:
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
