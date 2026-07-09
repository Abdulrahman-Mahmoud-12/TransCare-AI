"""
Draws bounding boxes + labels onto the original image and saves the
annotated "detection result" image shown next to the original in the UI.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from ai_modules.shelf_monitoring import config

EMPTY_COLOR = (200, 40, 40)      # red outline for empty gaps
PRODUCT_COLOR = (60, 100, 230)   # blue outline for detected products


def draw_detections(image_path: str, detections: list[dict], output_path: str) -> str:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    for det in detections:
        is_empty = det["category"] in config.EMPTY_CLASS_NAMES
        color = EMPTY_COLOR if is_empty else PRODUCT_COLOR
        x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]

        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        label = "Empty" if is_empty else f"{det['category']} {det['confidence']:.2f}"
        text_w = draw.textlength(label, font=font) if hasattr(draw, "textlength") else len(label) * 8
        label_bg = [x1, max(0, y1 - 20), x1 + text_w + 8, y1]
        draw.rectangle(label_bg, fill=color)
        draw.text((x1 + 4, max(0, y1 - 19)), label, fill=(255, 255, 255), font=font)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path, quality=90)
    return output_path