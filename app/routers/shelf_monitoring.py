from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.shelf import ShelfDetection, ShelfDetectionStatus
from app.dependancies import get_current_admin_user
from app.services.shelf_monitoring_service import ShelfMonitoringService
from app.schemas.shelf_monitoring import (
    ShelfAnalysisResult,
    RecentAnalysisListResponse,
    RecentAnalysisItem,
    DetectionBox,
    CategoryBreakdown,
    InsightItem,
    UploadResponse,
)

router = APIRouter(prefix="/api/shelf-monitoring", tags=["Shelf Monitoring"])


def _parse_analysis_id(analysis_id: str) -> int:
    try:
        return int(analysis_id.replace("SM-", "")) - 1000
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analysis id.")


def _to_result_schema(record: ShelfDetection) -> ShelfAnalysisResult:
    breakdown = record.category_breakdown or []
    return ShelfAnalysisResult(
        analysis_id=record.analysis_code,
        status=record.status,
        original_image_url=f"/{record.image_path}",
        detection_image_url=f"/{record.processed_image_path}" if record.processed_image_path else None,
        total_products=record.total_products or 0,
        empty_spaces=record.empty_spaces or 0,
        total_shelf_capacity=(record.total_products or 0) + (record.empty_spaces or 0),
        occupancy_percentage=float(record.occupancy_percentage or 0),
        classes_detected=record.classes_detected or 0,
        avg_confidence=float(record.avg_confidence or 0),
        processing_time_ms=record.processing_time_ms,
        boxes=[DetectionBox(**b) for b in (record.detections or [])],
        category_breakdown=[CategoryBreakdown(**c) for c in breakdown],
        full_category_distribution=[CategoryBreakdown(**c) for c in (record.full_category_distribution or [])],
        insights=[InsightItem(**i) for i in (record.insights or [])],
        most_detected_category=breakdown[0]["category"] if breakdown else None,
        least_detected_category=breakdown[-1]["category"] if breakdown else None,
        created_at=record.created_at,
    )


 
@router.post("/upload", response_model=UploadResponse)
async def upload_shelf_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Stages an uploaded image and creates a pending analysis record."""
    if image.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use JPG, PNG, or JPEG.")
 
    saved_path = ShelfMonitoringService.save_upload_file(image)
    record = ShelfMonitoringService.create_pending_record(db, saved_path, current_admin.id)
    return UploadResponse(analysis_id=record.analysis_code, status=record.status)
 
 
@router.post("/analyze/{analysis_id}", response_model=ShelfAnalysisResult)
async def analyze_shelf_image(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Runs the YOLO detection pipeline on a previously uploaded image."""
    record = ShelfMonitoringService.get_by_id(db, _parse_analysis_id(analysis_id))
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
 
    record = ShelfMonitoringService.run_analysis(db, record)
    if record.status == ShelfDetectionStatus.FAILED:
        raise HTTPException(status_code=500, detail=record.error_message or "Detection failed.")
 
    return _to_result_schema(record)
 
 
@router.get("/recent", response_model=RecentAnalysisListResponse)
async def recent_analyses(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    records = ShelfMonitoringService.get_recent(db)
    items = [
        RecentAnalysisItem(
            analysis_id=r.analysis_code,
            created_at=r.created_at,
            uploaded_by_name=r.uploader.full_name if r.uploader else "Unknown",
            total_products=r.total_products,
            empty_spaces=r.empty_spaces,
            status=r.status,
        )
        for r in records
    ]
    return RecentAnalysisListResponse(items=items)
 
 
@router.get("/{analysis_id}", response_model=ShelfAnalysisResult)
async def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    record = ShelfMonitoringService.get_by_id(db, _parse_analysis_id(analysis_id))
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _to_result_schema(record)
 
 
@router.get("/{analysis_id}/download-result")
async def download_result(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    record = ShelfMonitoringService.get_by_id(db, _parse_analysis_id(analysis_id))
    if not record or not record.processed_image_path:
        raise HTTPException(status_code=404, detail="Result image not found.")
    return FileResponse(record.processed_image_path, filename=f"{record.analysis_code}-detection.jpg")