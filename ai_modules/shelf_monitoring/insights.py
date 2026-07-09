"""
Generates human-readable insight/recommendation strings from a completed
shelf analysis. Pure logic, no DB or I/O — thresholds below are simple,
documented heuristics you can tune as you get real usage data.
"""
from typing import List, Dict

# A category counts as "low stock" if its count is at or below this
# fraction of the highest-count category in the same image...
LOW_STOCK_RATIO = 0.5
# ...or at or below this absolute count, whichever is more lenient.
LOW_STOCK_ABS_MIN = 3


def generate_insights(
    occupancy_percentage: float,
    empty_spaces: int,
    category_breakdown: List[Dict],
) -> List[Dict]:
    insights: List[Dict] = []
    empty_pct = round(100 - occupancy_percentage, 1)

    # --- Occupancy-level insight ---
    if empty_spaces == 0:
        insights.append({
            "icon": "✅",
            "text": f"This shelf is fully stocked — no empty spaces detected across "
                    f"{len(category_breakdown)} categor{'y' if len(category_breakdown) == 1 else 'ies'}.",
        })
    elif empty_pct >= 30:
        insights.append({
            "icon": "⚠️",
            "text": f"This shelf is {empty_pct}% empty and needs restocking attention soon.",
        })
    else:
        insights.append({
            "icon": "📦",
            "text": f"This shelf is {empty_pct}% empty — within a normal range, but worth monitoring.",
        })

    # --- Category coverage insight ---
    if category_breakdown:
        names = ", ".join(c["category"] for c in category_breakdown)
        insights.append({
            "icon": "🧺",
            "text": f"This shelf contains only {len(category_breakdown)} "
                    f"categor{'y' if len(category_breakdown) == 1 else 'ies'}: {names}.",
        })

    # --- Low-stock categories ---
    if category_breakdown:
        top_count = max(c["count"] for c in category_breakdown)
        for c in category_breakdown:
            if c["count"] == top_count:
                continue
            threshold = max(LOW_STOCK_ABS_MIN, top_count * LOW_STOCK_RATIO)
            if c["count"] <= threshold:
                insights.append({
                    "icon": "🔻",
                    "text": f"{c['category']} is low ({c['count']} detected) — consider restocking soon.",
                })

    return insights