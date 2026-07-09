"""
YOLO inference wrapper (Ultralytics). The model is loaded once as a
module-level singleton so it isn't reloaded from disk on every request.
"""
from ultralytics import YOLO
from ai_modules.shelf_monitoring import config

_model = None


def get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(config.WEIGHTS_PATH)
    return _model


def detect(image_path: str) -> list[dict]:
    """
    Runs detection on a single image.

    Returns a list of raw detections with pixel-space coordinates:
    [{category, confidence, x1, y1, x2, y2, img_w, img_h}, ...]
    """
    model = get_model()
    results = model.predict(
        source=image_path,
        conf=config.CONFIDENCE_THRESHOLD,
        iou=config.IOU_THRESHOLD,
        imgsz=config.IMAGE_SIZE,
        verbose=False,
    )

    if not results:
        return []

    result = results[0]
    img_h, img_w = result.orig_shape[:2]
    names = result.names or dict(enumerate(config.CLASS_NAMES))

    detections = []
    for box in result.boxes:
        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
        detections.append({
            "category": names.get(cls_id, f"class_{cls_id}"),
            "confidence": round(confidence, 4),
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "img_w": img_w, "img_h": img_h,
        })

    return detections