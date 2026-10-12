"""Reproducible, descriptive checks for the fictional MVP-04B case study.

Run: python scripts/analyze_business.py
Only reads committed CSV marts; no Snowflake, Power BI or paid services.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from decimal import Decimal
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "powerbi" / "data"
CENT = Decimal("0.01")

def load(table):
    with (DATA / (table + ".csv")).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def amount(rows, column):
    return sum((Decimal(row[column]) for row in rows), Decimal("0"))

def money(value):
    return str(value.quantize(CENT))

def summarize():
    orders = load("fct_orders")
    items = load("fct_order_items")
    daily = load("mart_daily_sales")
    clients = load("mart_customer_ltv")
    channels = load("mart_channel_performance")

    revenue = amount(orders, "recognized_revenue")
    assert revenue == amount(items, "recognized_item_revenue")
    assert revenue == amount(daily, "recognized_revenue")
    assert revenue == amount(clients, "lifetime_recognized_revenue")
    assert revenue == amount(channels, "recognized_revenue")
    assert len(orders) == 4200 and len(items) == 8400
    assert sum(int(c["order_count"]) for c in channels) == len(orders)

    months = defaultdict(list)
    for row in daily:
        months[row["order_date"][:7]].append(row)
    series = {}
    for month, days in sorted(months.items()):
        v = amount(days, "recognized_revenue")
        complete = sum(int(r["completed_orders"]) for r in days)
        series[month] = {
            "days": len(days),
            "orders": sum(int(r["order_count"]) for r in days),
            "completed": complete,
            "revenue": money(v),
            "revenue_per_calendar_day": money(v / len(days)),
            "ticket_completed": money(v / complete) if complete else None
        }

    buyer_count = sum(int(c["completed_orders"]) >= 1 for c in clients)
    repeat_count = sum(int(c["completed_orders"]) >= 2 for c in clients)
    channel_summary = {}
    for c in channels:
        count, completed = int(c["order_count"]), int(c["completed_orders"])
        channel_summary[c["channel"]] = {
            "orders": count,
            "completed": completed,
            "recognized_revenue": c["recognized_revenue"],
            "completion_pct": money(Decimal(100) * completed / count) if count else None,
            "revenue_share_pct": money(Decimal(100) * Decimal(c["recognized_revenue"]) / revenue),
        }

    return {
        "synthetic_data": True,
        "period": [min(d["order_date"] for d in daily), max(d["order_date"] for d in daily)],
        "orders": len(orders),
        "items": len(items),
        "completed_orders": sum(o["order_status"] == "completed" for o in orders),
        "recognized_revenue": money(revenue),
        "buyers": buyer_count,
        "repeat_buyers_2plus_completed": repeat_count,
        "repeat_buyers_pct": money(Decimal(100) * repeat_count / buyer_count) if buyer_count else None,
        "monthly": series,
        "channels": channel_summary
    }

if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, ensure_ascii=False))
