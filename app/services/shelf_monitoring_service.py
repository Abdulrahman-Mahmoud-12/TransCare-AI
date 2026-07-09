import os
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.shelf import ShelfDetection, ShelfDetectionStatus
from app.models.category import Category
from ai_modules.shelf_monitoring import predictor
from ai_modules.shelf_monitoring import metrics as ai_metrics
from ai_modules.shelf_monitoring import insights as ai_insights
from ai_modules.shelf_monitoring import config as ai_config

UPLOAD_DIR = ai_config.STORAGE_UPLOADS_DIR
DETECTED_DIR = ai_config.STORAGE_DETECTED_DIR


class ShelfMonitoringService:

    @staticmethod
    def save_upload_file(file: UploadFile) -> str:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(file.filename or "")[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(file.file.read())
        return path

    @staticmethod
    def create_pending_record(db: Session, image_path: str, uploaded_by: int) -> ShelfDetection:
        record = ShelfDetection(
            uploaded_by=uploaded_by,
            image_path=image_path,
            status=ShelfDetectionStatus.PENDING,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def run_analysis(db: Session, record: ShelfDetection) -> ShelfDetection:
        os.makedirs(DETECTED_DIR, exist_ok=True)
        output_path = os.path.join(DETECTED_DIR, f"{record.id}_detected.jpg")

        try:
            summary = predictor.run_analysis(record.image_path, output_path)

            record.processed_image_path = summary["processed_image_path"]
            record.total_products = summary["total_products"]
            record.empty_spaces = summary["empty_spaces"]
            record.occupancy_percentage = summary["occupancy_percentage"]
            record.classes_detected = summary["classes_detected"]
            record.avg_confidence = summary["avg_confidence"]
            record.processing_time_ms = summary["processing_time_ms"]
            record.detections = summary["boxes"]
            record.category_breakdown = summary["category_breakdown"]

            all_category_names = [c.name for c in db.query(Category.name).all()]
            record.full_category_distribution = ai_metrics.build_full_category_distribution(
                summary["category_breakdown"], all_category_names
            )
            record.insights = ai_insights.generate_insights(
                occupancy_percentage=summary["occupancy_percentage"],
                empty_spaces=summary["empty_spaces"],
                category_breakdown=summary["category_breakdown"],
            )

            record.status = ShelfDetectionStatus.COMPLETED
            record.error_message = None

        except Exception as e:
            record.status = ShelfDetectionStatus.FAILED
            record.error_message = str(e)

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_by_id(db: Session, record_id: int) -> Optional[ShelfDetection]:
        return db.query(ShelfDetection).filter(ShelfDetection.id == record_id).first()

    @staticmethod
    def get_recent(db: Session, limit: int = 10) -> List[ShelfDetection]:
        return (
            db.query(ShelfDetection)
            .order_by(ShelfDetection.created_at.desc())
            .limit(limit)
            .all()
        )