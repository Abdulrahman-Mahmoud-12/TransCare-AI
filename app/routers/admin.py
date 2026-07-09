from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.schemas.admin import ProductCreate, ProductUpdate, CategoryCreate
from app.services.admin_service import AdminService
from app.schemas.admin import AdminDashboardOverviewResponse
from app.services.shelf_monitoring_service import ShelfMonitoringService
from app.dependancies import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Admin Control Panel"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/overview", response_model=AdminDashboardOverviewResponse)
async def get_admin_dashboard_metrics(db: Session = Depends(get_db)):
    mock_user = type("MockUser", (object,), {"first_name": "Ahmed", "full_name": "Ahmed Hassan"})()
    
    metrics = AdminService.get_dashboard_overview(db=db, current_user=mock_user)
    return metrics

@router.get("/main", response_class=HTMLResponse)
async def admin_main(
    request: Request, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Renders base navigation wrapper frames for managing physical retail spaces.
    Pulls dynamic database aggregates to perfectly replicate the customer main page architecture.
    """
    first_name = current_admin.full_name.split()[0] if current_admin.full_name else "Admin"
    metrics = AdminService.get_dashboard_overview(db=db, current_user=current_admin)

    render_context = {
        "request": request,
        "first_name": first_name,
        "user": current_admin,
        "summary": metrics.get("operational_summary", {}), 
        "critical_alerts": metrics.get("critical_alerts", []),
        "system_health": metrics.get("system_health", []),
        "active_customers": metrics.get("active_customers", 0)
    }

    return templates.TemplateResponse(
        request=request,
        name="admin/main.html",
        context=render_context
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_admin: User = Depends(get_current_admin_user)):
    """Renders cross-sectional insights over predictive models, revenue levels, and alerts."""
    first_name = first_name = current_admin.full_name.split()[0]
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={"request": request, "admin": current_admin, "first_name":first_name}
    )

@router.get("/shelf-monitoring", response_class=HTMLResponse)
async def admin_shelf_monitoring(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Renders the AI shelf monitoring module — upload, detection results, and analysis history."""
    first_name = current_admin.full_name.split()[0] if current_admin.full_name else "Admin"

    def format_analysis_date(dt):
        """Cross-platform equivalent of '%b %-d, %Y · %-I:%M %p' (no leading zeros)."""
        month_day_year = dt.strftime("%b %d, %Y").replace(" 0", " ")  # strip leading zero from day
        time_part = dt.strftime("%I:%M %p")
        if time_part.startswith("0"):
            time_part = time_part[1:]  # strip leading zero from hour
        return f"{month_day_year} · {time_part}"

    recent_records = ShelfMonitoringService.get_recent(db, limit=10)
    recent_analyses = [
    {
        "analysis_id": r.analysis_code,
        "date": format_analysis_date(r.created_at),
        "uploaded_by": r.uploader.full_name if r.uploader else "Unknown",
        "total_products": r.total_products if r.status == "completed" else None,
        "empty_spaces": r.empty_spaces if r.status == "completed" else None,
        "status": r.status,
    }
    for r in recent_records
]

    return templates.TemplateResponse(
        request=request,
        name="admin/shelf_monitoring.html",
        context={
            "request": request,
            "admin": current_admin,
            "first_name": first_name,
            "user": current_admin,
            "recent_analyses": recent_analyses,
        }
    )


@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(get_current_admin_user)
):
    """Registers a clean product entity directly into the store master database catalog."""
    return AdminService.add_product(db, product_in)

@router.patch("/products/{product_id}")
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Alters structural fields inside database metrics and saves modifier logs."""
    updated = AdminService.update_product_data(db, product_id, product_in, updated_by=current_admin.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target product missing.")
    return {"status": "success", "message": "Product altered configuration logged."}



@router.get("/reports", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_admin: User = Depends(get_current_admin_user)):
    """Renders cross-sectional insights over predictive models, revenue levels, and alerts."""
    first_name = current_admin.full_name.split()[0]
    return templates.TemplateResponse(
        request=request,
        name="admin/reports.html",
        context={"request": request, "user": current_admin, "first_name":first_name}
    )