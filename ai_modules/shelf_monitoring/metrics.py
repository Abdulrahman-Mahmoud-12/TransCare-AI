"""
Turns raw YOLO detections into the KPIs, category table, and bounding-box
data shape that shelf-monitoring.js renders.
"""
from ai_modules.shelf_monitoring import config


def _is_empty(category: str) -> bool:
    return category in config.EMPTY_CLASS_NAMES


def to_percentage_boxes(detections: list[dict]) -> list[dict]:
    """Convert pixel xyxy boxes into normalized % x/y/w/h (matches .bbox CSS)."""
    boxes = []
    for det in detections:
        img_w, img_h = det["img_w"], det["img_h"]
        x_pct = (det["x1"] / img_w) * 100
        y_pct = (det["y1"] / img_h) * 100
        w_pct = ((det["x2"] - det["x1"]) / img_w) * 100
        h_pct = ((det["y2"] - det["y1"]) / img_h) * 100
        is_empty = _is_empty(det["category"])

        boxes.append({
            "x": round(x_pct, 2),
            "y": round(y_pct, 2),
            "w": round(w_pct, 2),
            "h": round(h_pct, 2),
            "label": "Empty" if is_empty else f"{det['category']} {det['confidence']:.2f}",
            "category": det["category"],
            "confidence": det["confidence"],
            "is_empty": is_empty,
            # Placeholder until real aisle/shelf mapping is available.
            "shelf_location": "Unassigned",
        })
    return boxes


def build_full_category_distribution(category_breakdown: list[dict], all_category_names: list[str]) -> list[dict]:
    """
    Merges the detected-category breakdown with the full list of category
    names from the store's Category table, so categories that exist in the
    catalog but weren't detected in this image still show up at 0 — used
    for the "distribution per category" bar chart.

    Falls back to the detected categories alone if the catalog list is empty
    (e.g. no categories seeded yet), so the chart is never blank.
    """
    detected = {c["category"]: c for c in category_breakdown}

    names = all_category_names or list(detected.keys())

    result = []
    for name in names:
        if name in detected:
            result.append(detected[name])
        else:
            result.append({
                "category": name,
                "count": 0,
                "avg_confidence": 0.0,
                "shelf_location": None,
            })

    # Any detected category not present in the catalog list (e.g. a class
    # name mismatch) still gets shown rather than silently dropped.
    for name, data in detected.items():
        if name not in names:
            result.append(data)

    return result


def compute_summary(detections: list[dict]) -> dict:
    boxes = to_percentage_boxes(detections)

    product_boxes = [b for b in boxes if not b["is_empty"]]
    empty_boxes = [b for b in boxes if b["is_empty"]]

    total_products = len(product_boxes)
    empty_spaces = len(empty_boxes)
    total_slots = total_products + empty_spaces
    occupancy_pct = round((total_products / total_slots) * 100, 2) if total_slots else 0.0

    categories: dict[str, dict] = {}
    for b in product_boxes:
        cat = b["category"]
        bucket = categories.setdefault(cat, {"count": 0, "confidences": []})
        bucket["count"] += 1
        bucket["confidences"].append(b["confidence"])

    category_breakdown = []
    for cat, data in categories.items():
        avg_conf = sum(data["confidences"]) / len(data["confidences"])
        category_breakdown.append({
            "category": cat,
            "count": data["count"],
            "avg_confidence": round(avg_conf * 100, 1),
            "shelf_location": "Unassigned",
        })
    category_breakdown.sort(key=lambda c: c["count"], reverse=True)

    avg_confidence = (
        round(sum(b["confidence"] for b in product_boxes) / total_products * 100, 1)
        if total_products else 0.0
    )

    most_detected = category_breakdown[0]["category"] if category_breakdown else None
    least_detected = category_breakdown[-1]["category"] if category_breakdown else None

    return {
        "boxes": boxes,
        "total_products": total_products,
        "empty_spaces": empty_spaces,
        "occupancy_percentage": occupancy_pct,
        "classes_detected": len(categories),
        "avg_confidence": avg_confidence,
        "category_breakdown": category_breakdown,
        "most_detected_category": most_detected,
        "least_detected_category": least_detected,
    }