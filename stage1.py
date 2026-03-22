"""
Stage 1: Week-on-Week Percentage Change Calculator
Computes traffic and order changes for each section.
"""

from utils import safe_pct_change, fmt_pct


def calculate_wow_changes(sections_data: dict) -> dict:
    """
    sections_data: {
        "Streaming": {
            "week1": {"traffic": int, "orders": int},
            "week2": {"traffic": int, "orders": int},
        },
        "Tablet": { ... }
    }
    Returns a dict with percentage changes per section.
    """
    results = {}
    for section, data in sections_data.items():
        w1 = data["week1"]
        w2 = data["week2"]

        results[section] = {
            "week1_traffic":       w1["traffic"],
            "week2_traffic":       w2["traffic"],
            "traffic_change_pct":  safe_pct_change(w1["traffic"], w2["traffic"]),
            "week1_orders":        w1["orders"],
            "week2_orders":        w2["orders"],
            "orders_change_pct":   safe_pct_change(w1["orders"], w2["orders"]),
        }

    return results


def format_pct(value):
    """Legacy wrapper — prefer utils.fmt_pct directly."""
    label = fmt_pct(value)
    color = "positive" if (value or 0) >= 0 else "negative"
    return label, color