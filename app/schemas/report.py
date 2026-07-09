from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ReportCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    report_type: str = Field(default="custom")  # daily/weekly/monthly/custom
    date_from: datetime
    date_to: datetime

    @field_validator("date_to")
    @classmethod
    def check_date_range(cls, v, info):
        date_from = info.data.get("date_from")
        if date_from and v < date_from:
            raise ValueError("date_to must be after date_from")
        return v


class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: str
    date_from: datetime
    date_to: datetime
    status: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}