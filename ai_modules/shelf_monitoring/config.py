import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to your trained Ultralytics YOLO weights file.
# Drop your .pt file into ai_modules/shelf_monitoring/weights/
WEIGHTS_PATH = os.path.join(BASE_DIR, "weights", "shelf_yolo.pt")

# ⚠️ PLACEHOLDER — replace with your model's real class list/order.
# You can get the authoritative list by running:
#   from ultralytics import YOLO
#   YOLO(WEIGHTS_PATH).names
# and pasting that dict/list here (order matters — it must match training).
CLASS_NAMES = [
    "Dairy",
    "Bakery",
    "Beverages",
    "Snacks",
    "Fruits",
    "Vegetables",
    "Empty",
]

# Class name(s) that represent an empty shelf gap rather than a product.
# Adjust to match whatever your model actually calls the empty-space class.
EMPTY_CLASS_NAMES = {"Empty", "empty", "empty_space", "empty_shelf"}

CONFIDENCE_THRESHOLD = 0.4
IOU_THRESHOLD = 0.5
IMAGE_SIZE = 640

# Runtime storage (shared with app/services/shelf_monitoring_service.py)
STORAGE_UPLOADS_DIR = os.path.join("storage", "uploads")
STORAGE_DETECTED_DIR = os.path.join("storage", "detected_images")