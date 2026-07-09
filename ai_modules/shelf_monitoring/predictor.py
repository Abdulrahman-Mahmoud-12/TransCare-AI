"""
High-level entry point used by the service layer: given an image path,
runs detection, draws the annotated result image, and computes the
summary metrics — all in one call.
"""
import time
from ai_modules.shelf_monitoring import detector, visualization, metrics


def run_analysis(image_path: str, output_image_path: str) -> dict:
    start = time.perf_counter()

    raw_detections = detector.detect(image_path)
    summary = metrics.compute_summary(raw_detections)

    visualization.draw_detections(image_path, raw_detections, output_image_path)

    summary["processing_time_ms"] = int((time.perf_counter() - start) * 1000)
    summary["processed_image_path"] = output_image_path

    return summary