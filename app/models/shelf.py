from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class ShelfDetectionStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ShelfDetection(Base):
    """
    One row per shelf-image analysis run (an upload + a YOLO inference pass).
    Per-detection bounding boxes and the per-category breakdown table are
    stored inline as JSON (see project decision: JSON column, not a child
    table) rather than in a separate table.
    """
    __tablename__ = "shelf_detections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    image_path = Column(String(255), nullable=False)
    processed_image_path = Column(String(255), nullable=True)

    status = Column(String(20), default=ShelfDetectionStatus.PENDING, nullable=False, index=True)

    total_products = Column(Integer, default=0)
    empty_spaces = Column(Integer, default=0)
    occupancy_percentage = Column(Numeric(5, 2), nullable=True)
    classes_detected = Column(Integer, default=0)
    avg_confidence = Column(Numeric(5, 2), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # [{category, confidence, is_empty, x, y, w, h (all % of image), shelf_location}, ...]
    # x/y/w/h are normalized percentages so they drop straight into the
    # existing .bbox-layer CSS positioning in shelf-monitoring.js.
    detections = Column(JSON, nullable=True)

    # [{category, count, avg_confidence, shelf_location}, ...]
    # Only categories actually detected in this image.
    category_breakdown = Column(JSON, nullable=True)

    # [{category, count, avg_confidence, shelf_location}, ...]
    # Every category in the store's Category table, 0-filled for any
    # category not detected in this particular image. Used for the
    # "distribution per category" bar chart so it reflects the full
    # catalog, not just what happened to appear in this shelf photo.
    full_category_distribution = Column(JSON, nullable=True)

    # [{icon, text}, ...] — generated narrative insights for this analysis.
    insights = Column(JSON, nullable=True)

    error_message = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    uploader = relationship("User", back_populates="shelf_detections")

    @property
    def analysis_code(self) -> str:
        """Public-facing reference code shown in the UI, e.g. SM-1042."""
        return f"SM-{1000 + self.id}"