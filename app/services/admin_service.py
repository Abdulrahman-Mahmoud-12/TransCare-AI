from sqlalchemy.orm import Session
from datetime import datetime, time
from sqlalchemy import func
from app.models.product import Product, Offer
from app.models.category import Category
from app.schemas.admin import ProductCreate, ProductUpdate, CategoryCreate
from typing import Optional

class AdminService:
    @staticmethod
    def add_product(db: Session, product_in: ProductCreate) -> Product:
        """
        Validates and pushes a new product entry into the catalog database space.
        """
        db_product = Product(
            category_id=product_in.category_id,
            barcode=product_in.barcode,
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            cost_price=product_in.cost_price,
            stock_quantity=product_in.stock_quantity,
            min_stock_level=product_in.min_stock_level,
            image_url=product_in.image_url,
            status=product_in.status
        )
        db.add(db_product)
        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def update_product_data(db: Session, product_id: int, product_in: ProductUpdate, updated_by: int) -> Optional[Product]:
        """
        Modifies properties inside a specified inventory product tracking entry.
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
            
        # Extract attributes sent in patch body updates dynamically
        update_data = product_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)
            
        try:
            db.commit()
            db.refresh(product)
            return product
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def add_category(db: Session, category_in: CategoryCreate) -> Category:
        """
        Registers a new merchandise categorization label.
        """
        db_category = Category(
            name=category_in.name,
            description=category_in.description,
            image_url=category_in.image_url
        )
        db.add(db_category)
        try:
            db.commit()
            db.refresh(db_category)
            return db_category
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_dashboard_overview(db: Session, current_user) -> dict:
        """
        Gathers database metrics to populate the Admin Main Overview screen.
        """
        today_start = datetime.combine(datetime.today(), time.min)

        # 1. Gather Operational Summary Counts
        total_products = db.query(Product).count()
        categories_count = db.query(Category).count()
        in_stock_count = db.query(Product).filter(Product.stock_quantity > 0).count()
        out_of_stock_count = db.query(Product).filter(Product.stock_quantity <= 0).count()
        active_promotions = db.query(Offer).filter(Offer.is_active == True).count() # Adjust property name if needed
        
        # Safe mock lookups if Models aren't fully declared yet
        registered_customers = db.query(func.count(current_user.id)).filter(current_user.role == "customer").scalar() or 0 
        # Replace with: db.query(User).filter(User.role == "customer").count()
        orders_today = 86            # Replace with: db.query(Order).filter(Order.created_at >= today_start).count()
        revenue_today = 24860.00     # Replace with: db.query(func.sum(Order.total_amount)).filter(Order.created_at >= today_start).scalar() or 0.0

        # 2. Gather Low Stock warning alerts from DB dynamically
        low_stock_products = db.query(Product).filter(Product.stock_quantity <= Product.minimum_stock).limit(3).all()
        critical_alerts = []
        for p in low_stock_products:
            critical_alerts.append({
                "priority": "high" if p.stock_quantity == 0 else "medium",
                "icon": "📦",
                "text": f"Low stock alert: {p.name} (Qty: {p.stock_quantity})",
                "time": "Just now"
            })
            
        # Fallback default items if database alerts list is brief
        if not critical_alerts:
            critical_alerts.append({
                "priority": "medium",
                "icon": "📷",
                "text": "All primary shelves verified healthy across categories.",
                "time": "Synced now"
            })

        # 3. Microservice/Ecosystem Mock Health Checklist
        system_health = [
            {"name": "Database Status", "status": "Operational", "sync": "Synced just now", "color": "green"},
            {"name": "AI Services Status", "status": "Operational", "sync": "Synced 2 min ago", "color": "green"},
            {"name": "Detection Model Status", "status": "Operational", "sync": "Synced just now", "color": "green"},
            {"name": "Server Status", "status": "Operational", "sync": "Synced just now", "color": "green"},
        ]

        return {
            "admin_first_name": getattr(current_user, "first_name", "Ahmed"),
            "admin_full_name": getattr(current_user, "full_name", "Ahmed Hassan"),
            "active_customers": 64, # Live metric mock or redis session fetch
            "operational_summary": {
                "total_products": total_products,
                "categories_count": categories_count,
                "in_stock_count": in_stock_count,
                "out_of_stock_count": out_of_stock_count,
                "active_promotions": active_promotions,
                "registered_customers": registered_customers,
                "orders_today": orders_today,
                "revenue_today": revenue_today,
            },
            "system_health": system_health,
            "critical_alerts": critical_alerts
        }