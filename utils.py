"""
Shared utility helpers for the Telstra WoW Intelligence Tool.
"""


def fmt_number(n: int | float) -> str:
    """Format large numbers with commas. e.g. 10000 → '10,000'"""
    return f"{n:,.0f}"


def fmt_pct(value: float | None, decimals: int = 2) -> str:
    """
    Return a signed percentage string with arrow.
    e.g. 15.0 → '▲ 15.00%'   -8.3 → '▼ 8.30%'
    """
    if value is None:
        return "N/A"
    arrow = "▲" if value >= 0 else "▼"
    return f"{arrow} {abs(value):.{decimals}f}%"


def pct_color_class(value: float | None) -> str:
    """Return CSS class name based on positive/negative direction."""
    if value is None or value >= 0:
        return "metric-change-pos"
    return "metric-change-neg"


def safe_pct_change(old: int | float, new: int | float) -> float | None:
    """Percentage change from old → new. Returns None if old is 0."""
    if old == 0:
        return None
    return ((new - old) / old) * 100


def summarise_gsc(gsc: dict) -> dict:
    """
    Compute WoW % changes for GSC metrics.
    Input keys: clicks_w1, clicks_w2, impressions_w1, impressions_w2, keywords_w1, keywords_w2
    """
    return {
        "clicks_change": safe_pct_change(gsc["clicks_w1"], gsc["clicks_w2"]),
        "impressions_change": safe_pct_change(gsc["impressions_w1"], gsc["impressions_w2"]),
        "keywords_change": safe_pct_change(gsc["keywords_w1"], gsc["keywords_w2"]),
    }