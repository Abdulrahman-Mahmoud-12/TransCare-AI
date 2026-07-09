from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.purchase import Order
from app.schemas.customer import CustomerProfileUpdate
from app.services.customer_service import CustomerService
from app.services.dashboard_service import DashboardService
from app.dependancies import get_current_active_user  
from app.models.product import Offer, Product

router = APIRouter(prefix="/customer", tags=["Customer Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/main", response_class=HTMLResponse)
async def customer_main(
    request: Request, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Renders the unified customer/main.html portal.
    Injects the authentic database profile name and live active offers.
    """
    first_name = current_user.full_name.split()[0] if current_user.full_name else "User"
    
    # Query current active offers based on timestamp logic
    now_ts = datetime.utcnow()
    active_offers = (
        db.query(Offer)
        .join(Product)
        .filter(
            Offer.is_active == True,
            Offer.start_date <= now_ts,
            Offer.end_date >= now_ts
        )
        .all()
    )
    
    # Process dynamic values for the template presentation layer
    processed_offers = []
    for offer in active_offers:
        original_price = float(offer.product.price)
        discount = float(offer.discount_percentage or 0)
        discounted_price = original_price * (1 - (discount / 100))
        
        processed_offers.append({
            "product_name": offer.product.name,
            "discount_percentage": int(discount),
            "original_price": f"{original_price:.2f}",
            "discounted_price": f"{discounted_price:.2f}",
            "end_date_iso": offer.end_date.isoformat() if offer.end_date else "",
            "image_url": offer.product.image_url  # Used for fallback/emoji mapping
        })

    return templates.TemplateResponse(
        request=request,
        name="customer/main.html",
        context={
            "request": request, 
            "user": current_user,
            "first_name": first_name,
            "offers": processed_offers
        }
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def customer_dashboard(
    request: Request, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Renders user-specific purchase analytics metrics and timeline indicators."""
    first_name = current_user.full_name.split()[0] if current_user.full_name else "User"
    return templates.TemplateResponse(
        request=request,
        name="customer/dashboard.html",
        context={
            "request": request, 
            "user": current_user,
            "first_name": first_name
        }
    )

############################
### Dashboard End-Points ###
############################

@router.get("/dashboard/statistics")
async def get_dashboard_metrics(
    period: str = "weekly", 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns aggregated analytic profile properties for current active customer session
    """
    # Pass the timeframe period down directly to get historical arrays sorted
    stats_data = DashboardService.get_summary_statistics(db, customer_id=current_user.id)
    return stats_data

@router.get("/dashboard/spending", response_model=dict)
async def get_dashboard_spending(period: str = "weekly", db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if period not in ["weekly", "monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid timeframe selected.")
    return DashboardService.get_spending_analytics(db, customer_id=current_user.id, period=period)

@router.get("/dashboard/distribution", response_model=dict)
async def get_dashboard_distribution(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return DashboardService.get_category_distribution(db, customer_id=current_user.id)

@router.get("/dashboard/favorite-products", response_model=list)
async def get_dashboard_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return DashboardService.get_favorite_products(db, customer_id=current_user.id)

@router.get("/dashboard/recommendations", response_model=list)
async def get_dashboard_recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return DashboardService.get_main_page_recommendations(db)

@router.get("/dashboard/insights-patterns", response_model=dict)
async def get_dashboard_insights_and_patterns(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return DashboardService.get_shopping_insights_and_patterns(db, customer_id=current_user.id)

@router.get("/dashboard/rewards-tier", response_model=dict)
async def get_dashboard_rewards_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return DashboardService.get_rewards_tier_progress(db, customer_id=current_user.id)


@router.get("/purchases", response_class=HTMLResponse)
async def customer_purchases(
    request: Request, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Queries and displays structural receipt invoices for the customer."""
    orders = db.query(Order).filter(Order.customer_id == current_user.id).order_by(Order.created_at.desc()).all()
    first_name = current_user.full_name.split()[0] if current_user.full_name else "User"

    # Calculate summary metrics dynamically to resolve frontend template expectations
    total_orders = len(orders)
    total_spending = sum(float(order.total_price) for order in orders) if total_orders else 0
    avg_order_value = total_spending / total_orders if total_orders else 0
    
    # Optional fallback/mock structure if these fields aren't completely backed in your schema yet
    purchase_summary = {
        "total_orders": total_orders,
        "total_spending": f"{total_spending:,.2f}",
        "avg_order_value": f"{avg_order_value:,.2f}",
        "total_saved": "850.00",  # Placeholder or can pull dynamically from discounts if available
        "last_order_date": orders[0].created_at.strftime("%b %d, %Y") if total_orders else "No orders yet"
    }

    return templates.TemplateResponse(
        request=request,
        name="customer/purchases.html",
        context={
            "request": request, 
            "user": current_user, 
            "first_name": first_name, 
            "orders": orders,
            "purchase_summary": purchase_summary
        }
    )

@router.get("/purchases/{order_id}/items", response_model=dict)
async def get_order_items_details(
    order_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """Fetches line items for an order dynamically to populate the frontend modal."""
    order = db.query(Order).filter(Order.id == order_id, Order.customer_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Safely convert to format matching your frontend JS expectations
    return {
        "date": order.created_at.strftime("%b %d, %Y"),
        "payment": getattr(order, 'payment_method', 'Credit Card'),
        "status": getattr(order, 'status', 'Delivered'),
        "total": float(order.total_price),
        # Ensure order.items relationship is defined in your Order model setup
        "items": [
            {
                "name": item.product.name,
                "qty": item.quantity,
                "unitPrice": float(item.unit_price),
                "discount": int(getattr(item, 'discount_percentage', 0))
            } for item in order.items
        ]
    }

    

@router.get("/assistant", response_class=HTMLResponse)
async def customer_assistant_page(request: Request, current_user: User = Depends(get_current_active_user)):
    """Renders the UI frame for the RAG-driven Support Agent Chat interface."""
    first_name = current_user.full_name.split()[0]
    return templates.TemplateResponse(
        request=request,
        name="customer/assistant.html",
        context={"request": request, "user": current_user, "first_name": first_name}
    )

@router.patch("/profile/update", response_model=dict)
async def update_profile(
    profile_data: CustomerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Asynchronous JSON data endpoint for modifying user settings."""
    updated = CustomerService.update_profile_meta(db, user_id=current_user.id, data=profile_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not execute profile changes.")
    return {"status": "success", "message": "Information synced successfully."}


from sqlalchemy import text # <--- Add this import at the top of the file

@router.get("/test-db")
def test_database_connection(db: Session = Depends(get_db)):
    try:
        # Wrap the raw string inside text()
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database is active and responding!"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}