from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DetectionBox(BaseModel):
    x: float
    y: float
    w: float
    h: float
    label: str
    category: str
    confidence: float
    is_empty: bool
    shelf_location: Optional[str] = None


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    avg_confidence: float
    shelf_location: Optional[str] = None


class UploadResponse(BaseModel):
    analysis_id: str
    status: str


class InsightItem(BaseModel):
    icon: str
    text: str


class ShelfAnalysisResult(BaseModel):
    analysis_id: str
    status: str
    original_image_url: str
    detection_image_url: Optional[str] = None
    total_products: int
    empty_spaces: int
    total_shelf_capacity: int
    occupancy_percentage: float
    classes_detected: int
    avg_confidence: float
    processing_time_ms: Optional[int] = None
    boxes: List[DetectionBox] = []
    category_breakdown: List[CategoryBreakdown] = []
    full_category_distribution: List[CategoryBreakdown] = []
    insights: List[InsightItem] = []
    most_detected_category: Optional[str] = None
    least_detected_category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecentAnalysisItem(BaseModel):
    analysis_id: str
    created_at: datetime
    uploaded_by_name: str
    total_products: Optional[int] = None
    empty_spaces: Optional[int] = None
    status: str


class RecentAnalysisListResponse(BaseModel):
    items: List[RecentAnalysisItem]