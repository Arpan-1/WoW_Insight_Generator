"""
Stage 1: Week-on-Week Percentage Change Calculator
Computes traffic and order changes for each section.
"""

from utils import safe_pct_change, fmt_pct, conversion_rate


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

        cvr_w1 = conversion_rate(w1["orders"], w1["traffic"])
        cvr_w2 = conversion_rate(w2["orders"], w2["traffic"])

        results[section] = {
            "week1_traffic":       w1["traffic"],
            "week2_traffic":       w2["traffic"],
            "traffic_change_pct":  safe_pct_change(w1["traffic"], w2["traffic"]),
            "week1_orders":        w1["orders"],
            "week2_orders":        w2["orders"],
            "orders_change_pct":   safe_pct_change(w1["orders"], w2["orders"]),
            "week1_cvr":           cvr_w1,
            "week2_cvr":           cvr_w2,
            "cvr_change_pct":      safe_pct_change(cvr_w1, cvr_w2) if (cvr_w1 and cvr_w2) else None,
        }

    return results


def format_pct(value):
    """Legacy wrapper — prefer utils.fmt_pct directly."""
    label = fmt_pct(value)
    color = "positive" if (value or 0) >= 0 else "negative"
    return label, color