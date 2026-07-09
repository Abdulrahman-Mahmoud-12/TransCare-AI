"""
Business report generation endpoints.
 
Register in app/main.py:
    from app.routers import reports
    app.include_router(reports.router, prefix="/api/admin/reports", tags=["reports"])
 
Depends on two schema classes (ReportCreateRequest, ReportResponse) that
need to be added to app/schemas/report.py — see the snippet at the bottom
of this file's docstring-equivalent chat message for the exact fields
expected. Adjust the import below to match whatever you actually name them.
"""
from typing import List
 
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
 
from app.database import get_db  # adjust import path if get_db lives elsewhere
from app.schemas.report import ReportCreateRequest, ReportResponse
from app.services import report_service
 
router = APIRouter(prefix="/admin/reports", tags=["Report Generation"])
 
 
@router.post("/generate", response_model=ReportResponse)
def generate_report(payload: ReportCreateRequest, db: Session = Depends(get_db)):
    """
    Triggers KPI computation + LLM narrative + PDF rendering.
    Runs synchronously — the LLM step can take a while. Consider a
    background task/job queue for production use.
    """
    report = report_service.create_report(
        db=db,
        title=payload.title,
        date_from=payload.date_from,
        date_to=payload.date_to,
        report_type=payload.report_type,
    )
    if report.status == "failed":
        raise HTTPException(status_code=422, detail=report.error_message)
    return report
 
 
@router.get("", response_model=List[ReportResponse])
def get_reports(limit: int = 50, db: Session = Depends(get_db)):
    return report_service.list_reports(db, limit=limit)
 
 
@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = report_service.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
 
 
@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = report_service.get_report(db, report_id)
    if not report or not report.file_path:
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=f"{report.title}.pdf",
    )
 